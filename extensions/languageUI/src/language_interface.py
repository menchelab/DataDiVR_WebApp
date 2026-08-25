import openai
import os
import re
import time
import random
import ast
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz, process as rf_process

from extensions.languageUI.src.lui_helpers import load_project_info
import GlobalData as GD

from langchain.memory import ConversationBufferMemory


def _extract_json(text: str) -> str:
    """Strip markdown fences and return the first balanced {...} JSON object."""
    text = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    # Some agent-tuned free models emit their native tool-call format even
    # though we never passed the `tools` API param, so it's never parsed out
    # into a separate field - it just leaks into plain text, e.g.
    # "<|tool_call_start|>[foo(bar(...))]<|tool_call_end|>". Strip the
    # wrapper tokens; the {...} extraction below still runs on what's left.
    text = re.sub(r"<\|tool_call_(?:start|end)\|>", "", text)
    text = re.sub(r"</?tool_call>", "", text)
    start = text.find('{')
    if start == -1:
        return text
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return text[start:]


def _extract_tool_call_action(text: str) -> Optional[dict]:
    """
    Best-effort fallback for when a model leaks its native tool-call format
    as plain text instead of JSON (happens with agent-tuned free models even
    though we never pass the `tools` API param - nothing parses it out into
    a separate field, so it just shows up in the content), e.g.:
        "<|tool_call_start|>[cdk5(select_layout_event(message={'msg': '...',
        'usr': 'user'}, room='/main'))]<|tool_call_end|>"
    That's syntactically valid Python, regardless of how it's wrapped/nested
    - parse it as an expression with `ast` and pull out the first call to a
    function we actually recognize, rather than round-tripping to the LLM
    again just to ask for the same thing reformatted.
    """
    cleaned = re.sub(r"<\|tool_call_(?:start|end)\|>", "", text)
    cleaned = re.sub(r"</?tool_call>", "", cleaned).strip()
    try:
        tree = ast.parse(cleaned, mode="eval")
    except (SyntaxError, ValueError):
        return None

    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        func_name = node.func.id
        if func_name not in ACTION_REGISTRY:
            continue
        try:
            kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords if kw.arg}
        except (ValueError, SyntaxError):
            continue
        # keep dict-shaped kwargs (e.g. "message={...}") as the action args;
        # if none were dicts, fall back to whatever kwargs there were
        args = {k: v for k, v in kwargs.items() if isinstance(v, dict)} or kwargs
        return {"type": "action", "function": func_name, "args": args}
    return None


def _quick_respond(user_input: str) -> Optional[dict]:
    """Return instant responses for queries that don't need the LLM at all."""
    lower = user_input.lower()

    # Project listing
    if any(kw in lower for kw in ("list project", "show project", "available project", "what project", "which project", "all project")):
        projects = GD.plist if hasattr(GD, "plist") else []
        project_list = "\n".join(f"- {p}" for p in projects)
        return {
            "type": "general_query",
            "quick_response": f"**Available projects:**\n{project_list}"
        }

    return None




FUNCTION_FN_MAPPING = {

    # register DataDiVR modules here
    # pattern: "python module name" : "fn value in message"
    # the "fn" value is handled in "handle_execute_socket" in event_handler/__init__.py

    "analytics_events": "analytics",
    "search_events": "node",
    "nodeinfo_events": "node",
    "project_events": "dropdown",
    "layout_events": "layout",

    # add others ... 
}




# ----------------------------------------
# MODELS + APIs
# ----------------------------------------

# Free OpenRouter models to try, in order of preference.
# NOTE: OpenRouter's roster of ':free' models changes often - models get
# retired from the free tier (they then 404 with "This model is unavailable
# for free ... use this slug instead: <paid-slug>") or get overloaded and
# 429. Verified against https://openrouter.ai/api/v1/models (pricing
# prompt=0/completion=0) - re-check that endpoint if these start 404ing too.
MODEL_CANDIDATES = [
    "liquid/lfm-2.5-2.6b:free",          # 2.6B, explicitly tuned for agent workflows / data extraction - best fit for strict JSON routing
    "nvidia/nemotron-3.5-lightning:free",  # 3B active / 30B MoE, agentic workloads, 1M context - fallback
    "poolside/laguna-s-2.1:free",        # 8B active MoE - last-resort fallback
]
llm_from_openrouterai = MODEL_CANDIDATES[0]  # kept for backwards compatibility / logging

# API / Model keys - Load .env and init OpenAI
load_dotenv()

# Read the API key from the text file

# determine default token file path
default_token_path = os.path.join("extensions", "languageUI", "LUI_funcs", "token_doNOTcommit.txt")

def _read_key_from_file(path):
    try:
        with open(path, "r") as key_file:
            return key_file.read().strip()
    except Exception:
        return None

# Try default file first
api_key = _read_key_from_file(default_token_path)

# Fallback to common env vars
if not api_key:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_APIKEY")

# If still missing, prompt the user for a path or to use env var
if not api_key:
    while True:
        try:
            prompt = (
                f"Token file not found at '{default_token_path}'.\n"
                "Enter full path to token file."
            )
            user_input = input(prompt).strip()
        except Exception:
            user_input = ""

        # Expand ~ and strip surrounding quotes if any
        user_path = os.path.expanduser(user_input.strip('"').strip("'"))
        if os.path.exists(user_path):
            api_key = _read_key_from_file(user_path)
            if api_key:
                break
            print(f"Could not read a key from file: {user_path}")
        else:
            print(f"File not found: {user_path}")

# Final guard
if not api_key:
    raise RuntimeError("API key not found. Set API_KEY or provide a valid token file path.")

# Assign the API key to OpenAI
openai.api_key = api_key

# Initialize the OpenAI client (if needed)
# - timeout: the SDK default is 10 minutes per request - way too long for an
#   interactive router. A slow/overloaded free model should fail fast so our
#   own retry/fallback logic (below) can move on, not hang silently.
# - max_retries=0: the SDK retries transient errors internally by default
#   (2 more attempts), which would silently stack under our own retry loop
#   and multiply wait times. We already handle retries/backoff/fallback
#   ourselves in _chat_completion_with_retry, so disable the SDK's.
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    timeout=25.0,
    max_retries=0,
)


# ----------------------------------------
# 429 / rate-limit resilient chat completion
# ----------------------------------------
def _chat_completion_with_retry(messages, temperature=0.0, max_tokens=256, max_retries=3):
    """
    Calls OpenRouter chat completions, handling failures gracefully:
      - 429 (rate limit / overloaded): retries the same model with exponential
        backoff + jitter (handles brief upstream overload / hitting the
        per-minute free-tier limit).
      - 404 (model no longer offered for free): skips straight to the next
        model - retrying the same model would just 404 again.
      - Either way, falls back to the next model in MODEL_CANDIDATES once the
        current one is exhausted (handles a specific free model being
        saturated or retired).
    Raises the last error if every model/attempt is exhausted.
    """
    last_error = None
    for model in MODEL_CANDIDATES:
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if model != MODEL_CANDIDATES[0]:
                    print(f"C_DEBUG: Fell back to model '{model}' successfully.")
                return response
            except openai.RateLimitError as e:
                last_error = e
                wait = (2 ** attempt) + random.uniform(0, 1)
                print(f"C_DEBUG: 429 rate limit on '{model}' (attempt {attempt + 1}/{max_retries}). Waiting {wait:.1f}s...")
                time.sleep(wait)
            except openai.NotFoundError as e:
                # Model has been pulled from the free tier (or renamed) - no point retrying it.
                last_error = e
                print(f"C_DEBUG: '{model}' is no longer available for free (404): {e}. Skipping to next model.")
                break
            except openai.APIStatusError as e:
                # Some overloaded free models come back as a generic 5xx/429-like status
                # rather than a typed RateLimitError - treat 429 the same way here.
                if e.status_code == 429:
                    last_error = e
                    wait = (2 ** attempt) + random.uniform(0, 1)
                    print(f"C_DEBUG: 429 (APIStatusError) on '{model}' (attempt {attempt + 1}/{max_retries}). Waiting {wait:.1f}s...")
                    time.sleep(wait)
                elif e.status_code == 404:
                    last_error = e
                    print(f"C_DEBUG: '{model}' returned 404: {e}. Skipping to next model.")
                    break
                else:
                    raise
        print(f"C_DEBUG: Model '{model}' exhausted retries, trying next fallback model...")

    raise last_error or RuntimeError("All models exhausted with no response.")


# ----------------------------------------
# CREATE FUNCTION REGISTRY
# ----------------------------------------

def get_action_registry_from_DataDiVR():
    """
    Dynamically load all functions with docstrings from Python files in the DataDiVR_WebApp/event_handler/execute_events folder.
    This function inspects all .py files in the specified folder and registers only functions that have docstrings.
    
    Returns:
        dict: A dictionary mapping function names to their corresponding functions, documentation, and file paths.
    """
    import inspect
    import os
    import sys

    # Define the absolute path to the event_handler/execute_events folder
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file
    project_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))  # Adjust to point to the root of the project
    directory = os.path.join(project_root, "event_handler", "execute_events")
    
    registry = {}

    # Debugging: Print the constructed directory path
    print(f"Scanning directory: {directory}")

    # Add the project root to sys.path if not already present
    if project_root not in sys.path:
        sys.path.append(project_root)

    # Iterate through all Python files in the target directory
    try:
        for file in os.listdir(directory):
            if file.endswith(".py"):  # Include all .py files
                file_path = os.path.join(directory, file)
                module_name = file[:-3]  # Remove the .py extension

                try:
                    # Open the file and execute its content in a temporary namespace
                    namespace = {}
                    with open(file_path, "r") as f:
                        exec(f.read(), namespace)

                    # Inspect the namespace for all functions
                    for name, func in namespace.items():
                        if inspect.isfunction(func) and func.__doc__:  # Only register functions with docstrings
                            registry[name] = {
                                "function": func,
                                "doc": func.__doc__.strip(),
                                "file_path": file_path  # Add the file path to the registry
                            }
                except Exception as e:
                    print(f"Error processing file {file}: {e}")
    except FileNotFoundError as e:
        print(f"Error: Directory not found - {directory}")
        return {}

    # Print the resulting registry
    print("Registered functions:")
    for func_name, meta in registry.items():
        print(f"- {func_name}: {meta['file_path']}")
    
    return registry



registry_VR = get_action_registry_from_DataDiVR()
ACTION_REGISTRY = {**registry_VR}

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
print("C_DEBUG: Initialized conversation memory.", memory)
print("C_DEBUG: Initial memory state:", memory.load_memory_variables({})["chat_history"])


# ----------------------------------------
# Local intent classifier - routes without calling the LLM
# ----------------------------------------
# Every registered function already needs a docstring to show up in
# ACTION_REGISTRY at all, so it doubles as training data here: TF-IDF +
# cosine similarity against those docstrings classifies user input locally,
# instantly, with no network call and no dependence on how well a given free
# LLM follows the JSON prompt template. Only fires when confident; anything
# below threshold (including genuine general questions) falls through to the
# LLM router unchanged - so this never reduces coverage, only latency.
#
# To make a new function routable this way: just give it a clear docstring
# (first line/paragraph = what it does; quote a couple of example phrasings
# the way project_main/search_event/node_event already do). Nothing else to
# register or maintain here.

_REJECT_INTENT = "__general_query__"
_REJECT_TRAINING_TEXT = (
    "Hello how are you doing today. Tell me a joke. What is the weather like. "
    "Thank you very much for your help. Can you explain what this tool does. "
    "What can I ask you. This is general conversation, not a specific command. "
    "Nice to meet you. Goodbye. What is your name."
)

INTENT_CONFIDENCE_THRESHOLD = 0.30  # top match must clear this cosine similarity...
INTENT_MARGIN_THRESHOLD = 0.05      # ...and beat the runner-up by at least this much

# Only these modules have argument-filling logic in _quick_route_from_intent
# below (mirroring create_message()'s special-cased branches). A confident
# match on a function from any other module still falls through to the LLM,
# since we don't yet know how to build valid args for it.
_SLOT_FILLABLE_MODULES = {"project_events", "search_events", "nodeinfo_events", "layout_events"}

# Layout names (e.g. "09-CDK5-hyperactive_diseaseInference") are technical,
# hyphenated, project-specific strings - rapidfuzz only reliably resolves
# near-verbatim mentions ("load the alzheimers layout") this way. Looser,
# conceptual phrasing ("show me the disease landscape") needs real semantic
# understanding, which is exactly what the LLM fallback + the layout list
# injected into build_system_prompt() is for - so this threshold is
# deliberately conservative, unlike the project-name threshold.
LAYOUT_MATCH_THRESHOLD = 65


def _resolve_layout(raw: str):
    """Resolve a layout name/description against the current project's
    GD.pfile['layouts']. Returns (index, name) on a confident match, else
    None. Tries an exact (case-insensitive) match first, then fuzzy."""
    layouts = GD.pfile.get("layouts", []) if hasattr(GD, "pfile") else []
    if not layouts or not raw:
        return None

    lowered = [l.lower() for l in layouts]
    if raw.strip().lower() in lowered:
        idx = lowered.index(raw.strip().lower())
        return idx, layouts[idx]

    # a single bare number anywhere in the input ("load layout 3") is a
    # direct index - but only if it's the *only* number present, so this
    # doesn't misfire on layout names that themselves contain digits
    # (e.g. "09-CDK5-hyperactive_diseaseInference" has two digit runs).
    numbers = re.findall(r"\d+", raw)
    if len(numbers) == 1:
        idx = int(numbers[0])
        if 0 <= idx < len(layouts):
            return idx, layouts[idx]

    best = rf_process.extractOne(raw, layouts, scorer=fuzz.WRatio)
    if not best or best[1] < LAYOUT_MATCH_THRESHOLD:
        return None
    return layouts.index(best[0]), best[0]

_ENTITY_STOPWORDS = {
    "search", "for", "find", "look", "up", "show", "me", "about", "details",
    "node", "info", "information", "the", "a", "an", "of", "on", "please",
}


def _condense_docstring(doc: str) -> str:
    """Keep the summary + any quoted example phrasings, drop the
    Args/Returns/... boilerplate - docstrings are written for developers and
    are mostly noise for matching against short natural-language input."""
    summary = re.split(r"\n\s*(?:Args|Returns|Emits|Workflow|Behavior|Notes):", doc)[0].strip()
    examples = re.findall(r'"([^"]{4,60})"', doc)
    return summary + " " + " ".join(examples)


def _build_intent_index(registry):
    names, corpus = [], []
    for fname, meta in registry.items():
        names.append(fname)
        corpus.append(_condense_docstring(meta["doc"]))
    names.append(_REJECT_INTENT)
    corpus.append(_REJECT_TRAINING_TEXT)

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(corpus)
    return vectorizer, matrix, names


_intent_vectorizer, _intent_matrix, _intent_names = _build_intent_index(ACTION_REGISTRY)


def _classify_intent(user_input: str):
    """Returns (function_name, score) for a confident local match, else None."""
    qvec = _intent_vectorizer.transform([user_input])
    sims = cosine_similarity(qvec, _intent_matrix)[0]
    order = sims.argsort()[::-1]
    top, runner_up = order[0], order[1]

    if _intent_names[top] == _REJECT_INTENT:
        return None
    if sims[top] < INTENT_CONFIDENCE_THRESHOLD:
        return None
    if (sims[top] - sims[runner_up]) < INTENT_MARGIN_THRESHOLD:
        return None
    return _intent_names[top], float(sims[top])


def _extract_entity(user_input: str) -> str:
    """Generic fallback slot-filler: strip common trigger/stopwords, return
    whatever content remains (the project/node name the user meant)."""
    tokens = re.findall(r"[\w\-]+", user_input)
    remaining = [t for t in tokens if t.lower() not in _ENTITY_STOPWORDS]
    return " ".join(remaining).strip()


def _quick_route_from_intent(func_name: str, user_input: str) -> Optional[dict]:
    """Builds an action dict for a locally-classified intent, or None if we
    can't confidently fill its arguments (caller falls through to the LLM)."""
    meta = ACTION_REGISTRY.get(func_name)
    if not meta:
        return None
    module_name = os.path.splitext(os.path.basename(meta["file_path"]))[0]
    if module_name not in _SLOT_FILLABLE_MODULES:
        return None

    if module_name == "project_events":
        projects = GD.plist if hasattr(GD, "plist") else []
        if not projects:
            return None
        best = rf_process.extractOne(user_input, projects, scorer=fuzz.partial_ratio)
        if not best or best[1] < 70:
            return None
        return {
            "type": "action",
            "function": "project_main",
            "args": {"message": {"msg": best[0], "id": "projDD", "usr": "user"}},
        }

    if module_name in ("search_events", "nodeinfo_events"):
        entity = _extract_entity(user_input)
        if not entity:
            return None
        # A bare numeric value is a direct node index (node_event); anything
        # else is a name to look up (search_event resolves name -> node).
        target_func = "node_event" if entity.isdigit() else "search_event"
        return {
            "type": "action",
            "function": target_func,
            "args": {"message": {"val": entity, "id": "search", "usr": "user"}},
        }

    if module_name == "layout_events":
        resolved = _resolve_layout(user_input)
        if not resolved:
            # Likely a conceptual/descriptive phrasing ("disease landscape")
            # rather than a near-verbatim layout name - needs the LLM's
            # semantic judgment against the injected layout list instead.
            return None
        index, name = resolved
        return {
            "type": "action",
            "function": "select_layout_event",
            "args": {"message": {"msg": name, "val": index, "usr": "user"}},
        }

    return None


def _quick_route(user_input: str) -> Optional[dict]:
    """
    Deterministically resolve unambiguous commands without calling the LLM:
    classify intent locally, then fill its args. Returns an action dict in
    the same shape route_command's LLM path produces, or None if nothing
    matched confidently (falls through to the LLM as usual).
    """
    classified = _classify_intent(user_input)
    if not classified:
        return None
    func_name, score = classified
    action = _quick_route_from_intent(func_name, user_input)
    if action:
        print(f"C_DEBUG: Quick-routed (no LLM) to '{action['function']}' via intent '{func_name}' (score {score:.2f})")
    return action


# ----------------------------------------
# Use LLM to match input to a function
# ----------------------------------------
# Build a system prompt for the LLM based on the action registry
# This prompt will be used to instruct the LLM to map user input to a specific function
# and its arguments.
def build_system_prompt(registry):
    lines = []
    for fname, meta in registry.items():
        module_name = os.path.splitext(os.path.basename(meta["file_path"]))[0]
        fn_value = FUNCTION_FN_MAPPING.get(module_name, "general")
        lines.append(f"- `{fname}(...)` (fn: `{fn_value}`): {meta['doc']}")

    project_data = load_project_info()
    project_name = project_data.get("name", "Unknown Project")
    all_projects = GD.plist if hasattr(GD, "plist") else []
    all_layouts = GD.pfile.get("layouts", []) if hasattr(GD, "pfile") else []

    example_project = all_projects[0] if all_projects else "SomeProject"
    example_layout = all_layouts[0] if all_layouts else "SomeLayout"
    return (
        "You are a router. Classify the user input and return ONLY a JSON object.\n\n"
        f"Current project: {project_name}\n"
        f"Available projects: {', '.join(all_projects)}\n\n"
        f"Available layouts for the current project: {', '.join(all_layouts)}\n"
        "Layout names often hint at what they show (a disease name, a process, a "
        "protein complex, etc.) - match the user's description to the layout name "
        "whose meaning fits best, even if the words don't match literally "
        "(e.g. \"show me the disease view\" could mean a layout named "
        "\"...diseaseInference\").\n\n"
        "Available functions:\n"
        + "\n".join(lines) +
        "\n\n"
        "If the input maps to a function, return:\n"
        '{"type": "action", "function": "function_name", "args": {"arg1": "value1"}}\n'
        "Otherwise return:\n"
        '{"type": "general_query"}\n\n'
        "Example — any phrasing that means opening/switching/navigating to a project:\n"
        f'User: "open project {example_project}" → '
        '{{"type": "action", "function": "project_main", "args": {{"message": {{"msg": "{example_project}", "id": "projDD", "usr": "user"}}}}}}\n\n'
        "Example — any phrasing that means switching to a specific layout (pick the "
        "closest-matching name from 'Available layouts' above, by meaning, not just spelling):\n"
        f'User: "show me the {example_layout} view" → '
        '{{"type": "action", "function": "select_layout_event", "args": {{"message": {{"msg": "'
        + example_layout + '", "usr": "user"}}}}}}\n\n'
        "Formatting rules (follow exactly):\n"
        "- Output ONLY the JSON object, nothing else — no explanation, no markdown, no ``` code fences.\n"
        "- Do NOT use tool-calling / function-calling syntax (no <|tool_call_start|> tokens, no "
        "python-style function(arg=value) calls). This is plain JSON text, not a tool call.\n"
        "- Output it as a SINGLE LINE. Do NOT pretty-print or indent it.\n"
        "- Keep it minimal - no extra keys beyond what's needed."
    )





def route_command(user_input: str) -> dict:
    """Routes user input to an action or general_query. Returns minimal JSON — no response text."""
    quick = _quick_respond(user_input)
    if quick:
        return quick

    quick_action = _quick_route(user_input)
    if quick_action and quick_action.get("function") in ACTION_REGISTRY:
        memory.chat_memory.add_user_message(user_input)
        memory.chat_memory.add_ai_message(f"(quick-routed to {quick_action['function']})")
        return quick_action

    memory.chat_memory.add_user_message(user_input)

    system_prompt = build_system_prompt(ACTION_REGISTRY)
    chat_history = [
        {"role": "user" if m.type == "human" else "assistant", "content": m.content}
        for m in memory.load_memory_variables({})["chat_history"]
    ]
    messages = [{"role": "system", "content": system_prompt}] + chat_history

    try:
        response = _chat_completion_with_retry(messages, temperature=0.0, max_tokens=500)
        llm_response = (response.choices[0].message.content or "").strip()
        print("Routing response:", llm_response)
        if not llm_response:
            return {"type": "general_query"}
        extracted = _extract_json(llm_response)
        if not extracted.startswith('{'):
            tool_call_action = _extract_tool_call_action(llm_response)
            if tool_call_action:
                print("C_DEBUG: Response wasn't JSON but parsed as a leaked tool-call:", tool_call_action)
                return validate_llm_response(tool_call_action)
            print("C_DEBUG: Routing response not JSON, falling back to general_query")
            return {"type": "general_query"}

        try:
            parsed = json.loads(extracted)
        except json.JSONDecodeError as decode_err:
            # Might be a leaked native tool-call (e.g. Python call syntax
            # with single-quoted dicts) rather than truncated/malformed JSON
            # - try parsing that before spending a whole extra LLM round trip.
            tool_call_action = _extract_tool_call_action(llm_response)
            if tool_call_action:
                print("C_DEBUG: JSON parse failed, but parsed as a leaked tool-call instead:", tool_call_action)
                return validate_llm_response(tool_call_action)

            # Otherwise likely truncated (ran out of max_tokens) or malformed
            # (small model ignored the single-line/no-fence instructions).
            # Give the model one more chance with an explicit correction
            # instead of surfacing a raw error to the user.
            print(f"C_DEBUG: Malformed JSON from routing model ({decode_err}). Retrying once with a correction nudge.")
            retry_messages = messages + [
                {"role": "assistant", "content": llm_response},
                {"role": "user", "content": (
                    "That was not valid JSON (it may have been truncated or pretty-printed). "
                    "Reply again with ONLY the same JSON object, compact on a single line, "
                    "no markdown fences, no line breaks."
                )},
            ]
            try:
                retry_response = _chat_completion_with_retry(retry_messages, temperature=0.0, max_tokens=500)
                retry_text = (retry_response.choices[0].message.content or "").strip()
                print("Routing response (retry):", retry_text)
                extracted_retry = _extract_json(retry_text)
                if not extracted_retry.startswith('{'):
                    return {"type": "general_query"}
                parsed = json.loads(extracted_retry)
            except Exception as retry_err:
                print(f"C_DEBUG: Retry also failed to produce valid JSON ({retry_err}). Falling back to general_query.")
                return {"type": "general_query"}

        return validate_llm_response(parsed)

    except Exception as e:
        print("C_DEBUG: Error in route_command:", str(e))
        return {"type": "error", "feedback": f"An error occurred: {str(e)}"}
 


def validate_llm_response(parsed_response):
    print("C_DEBUG: Routing decision:", parsed_response)
    if parsed_response.get("type") == "action":
        if "function" in parsed_response and "args" in parsed_response:
            return parsed_response
    return {"type": "general_query"}



def generate_general_response() -> str:
    """Free-form LLM call that returns plain markdown text. No JSON parsing."""
    project_data = load_project_info()
    project_name = project_data.get("name", "Unknown Project")
    project_info = project_data.get("info", "No description available.")
    all_projects = GD.plist if hasattr(GD, "plist") else []

    system_prompt = (
        "You are a helpful assistant for DataDiVR, a network visualization tool.\n"
        f"Current project: {project_name}\n"
        f"Project description: {project_info}\n"
        f"Available projects: {', '.join(all_projects)}\n\n"
        "Answer the user's question concisely. You may use markdown for formatting."
    )

    chat_history = [
        {"role": "user" if m.type == "human" else "assistant", "content": m.content}
        for m in memory.load_memory_variables({})["chat_history"]
    ]
    messages = [{"role": "system", "content": system_prompt}] + chat_history

    try:
        response = _chat_completion_with_retry(messages, temperature=0.5, max_tokens=1024)
        result = (response.choices[0].message.content or "").strip()
        memory.chat_memory.add_ai_message(result)
        print("C_DEBUG: General response:", result)
        return result
    except Exception as e:
        print("C_DEBUG: Error in generate_general_response:", str(e))
        return f"An error occurred: {str(e)}"







def create_message(func_name: str, args: dict, file_path: str) -> dict:
    """
    Creates a structured message dynamically based on the matched function and its arguments.
    Dynamically sets the `fn` value based on the module (e.g., analytics_events, layout_events).

    Args:
        func_name (str): The name of the matched function.
        args (dict): The arguments for the matched function.
        file_path (str): The path to the Python file containing the function.

    Returns:
        dict: A dynamically generated message.
    """
    # Extract the module name from the file path
    module_name = os.path.splitext(os.path.basename(file_path))[0]  # e.g., "analytics_events"

    # Default message structure
    message = {
        "usr": args.get("usr", "default_user"),
        "msg": None,
        "id": None,
        "parent": args.get("parent", None),
        "val": args.get("val", None),
        "fn": None,  # To be determined dynamically
        "feedback": f"'{func_name}' has been triggered successfully."
    }

    # Set the `fn` value based on the module name
    message["fn"] = FUNCTION_FN_MAPPING.get(module_name, "general")  # Default to "general" if not found


    #-------------------------------------------------------------------
    # MODULE CATCH CASES HERE: 
    # Dynamically extract the `id` and 'msg' value from the file

    # catch if analytics module
    if module_name == "analytics_events":
        print("C_DEBUG: in analytics events module...")
        func_name_generated = func_name.split("_")[0]  # Extract the first term before "_"
        id_value = rf'"analytics{func_name_generated.capitalize()}Run"'
        if id_value and isinstance(id_value, str) and id_value.startswith('"') and id_value.endswith('"'):
            id_value = id_value.strip('"')  # Remove quotes if present
            msg_msg = "RUN"
            message["msg"] = msg_msg
            
    # catch if search module
    if module_name == "search_events":
        print("C_DEBUG: in search events module...")
        id_value = "search"
        if "message" in args:      
            msg_value = args.get("message", {}).get("val", "")
            node_id = args.get("message", {}).get("id", "")
        else:
            msg_value = args.get("val", "")
            node_id = args.get("id", "")
        message["val"] = msg_value

    # catch if nodeinfo module
    if module_name == "nodeinfo_events":
        print("C_DEBUG: in nodeinfo events module...")
        id_value = None
        node_name = args.get("message", {}).get("val", "")
        node_id = args.get("message", {}).get("id", "")
        message["val"] = node_id
        message["msg"] = node_name
        message["fn"] = "node"

    # catch if project module
    if module_name == "project_events":
        print("C_DEBUG: in project events module...")
        id_value = "projDD"
        message["fn"] = "dropdown"
        message["parent"] = "projDD"

        # get project name and index
        projectname_raw = args.get("message", {}).get("msg", "")
        all_projects = GD.plist
        all_projects_upper = [proj.upper() for proj in all_projects]
        projectname = projectname_raw.upper()

        if projectname in all_projects_upper:
            project_index = all_projects_upper.index(projectname) # get index of matched project name     
            message["feedback"] = f"Project '{projectname}' selected successfully."
        else:
            message["feedback"] = f"No project name provided. Selecting default project. Choose from available projects: {', '.join(all_projects)}"
            project_index = 0
            projectname = all_projects[project_index]

        message["msg"] = projectname
        message["val"] = project_index
        print("C_DEBUG: matched project name:", projectname)
        print("C_DEBUG: matched project index:", project_index)

    # catch if layout module
    if module_name == "layout_events":
        print("C_DEBUG: in layout events module...")
        id_value = "layoutSelect"
        message["fn"] = "layout"

        layout_raw = args.get("message", {}).get("msg") or str(args.get("message", {}).get("val", ""))
        resolved = _resolve_layout(layout_raw)
        layouts = GD.pfile.get("layouts", []) if hasattr(GD, "pfile") else []

        if resolved:
            layout_index, layout_name = resolved
            message["feedback"] = f"Layout '{layout_name}' selected successfully."
        elif layouts:
            layout_index, layout_name = 0, layouts[0]
            message["feedback"] = f"Could not match a layout to '{layout_raw}'. Selecting default layout. Choose from available layouts: {', '.join(layouts)}"
        else:
            layout_index, layout_name = 0, None
            message["feedback"] = "No layouts available for the current project."

        message["msg"] = layout_name
        message["val"] = layout_index
        print("C_DEBUG: matched layout name:", layout_name)
        print("C_DEBUG: matched layout index:", layout_index)


    #-------------------------------------------------------------------


    message["id"] = id_value

    print("C_DEBUG - LANGUAGE_INTERFACE.PY - Created message:", message)

    return message









def clear_memory():
    """
    Clears the conversation memory buffer.
    """
    memory.chat_memory.clear()
    print("C_DEBUG: Memory buffer cleared.")

