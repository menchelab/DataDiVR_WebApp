import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet as wn
from rapidfuzz import fuzz
from spellchecker import SpellChecker
import re
import GlobalData as GD

# ------------------------------------------------
# import functions here
# ------------------------------------------------
from event_handler.execute_events.drop_down_events import trigger_change_project_to
from analytics import analytics_shortest_path


all_projects = [i+"\n" for i in GD.listProjects()]



# ------------------------------------------------
# Mapping commands to functions
# ------------------------------------------------
def mapped_function_XY():
    return "Function XY executed"

def mapped_search_project(project_name):
    matching_projects = [project for project in GD.listProjects() if project_name.lower() in project.lower()]
    if matching_projects:
        # open the project 
        trigger_change_project_to(project_name)

        return f"Matching project: {(project_name)}"
    else:
        return "No matching projects found."
    


    
# def mapped_analytics_shortest_path():
#     # get graph from project 
#     graph = GD.data["actPro"]

#     # get node a and node b
    
#     # calculate shortest path 
#     return print("in mapped_analytics_shortest_path: GD.data = ", GD.data["actPro"]) #analytics_shortest_path()



# ------------------------------------------------
# Mapping of command patterns to functions with a pattern and a function reference
# ------------------------------------------------
command_to_function = {
    

    #(r"calculate shortest path", r"find shortest path"): mapped_analytics_shortest_path,

    (r"do XY", r"do AB(?: (.*))?"): mapped_function_XY,

    (r"open project (.+)", r"search project (.+)"): mapped_search_project,
}




# spell check for typos
# synonyms for meaning 

spell = SpellChecker()

# ISSUE with spelling: project names are not recognized as correct spelling
# def correct_spelling(user_input):
#     corrected = []
#     for word in word_tokenize(user_input):
#         corrected.append(spell.correction(word))
#     return ' '.join(corrected)

def preprocess_input(user_input):
    # Correct spelling mistakes
    corrected_input = user_input #correct_spelling(user_input)
    
    # Tokenize the input
    tokens = word_tokenize(corrected_input.lower())
    
    # Remove stopwords
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    return ' '.join(tokens)

def find_best_match(user_input, patterns):
    best_match = None
    highest_ratio = 0
    for pattern in patterns:
        ratio = fuzz.partial_ratio(pattern, user_input)
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = pattern
    return best_match if highest_ratio > 80 else None  # Use a threshold to determine match quality

def process_input(user_input):
    preprocessed_input = preprocess_input(user_input)

    for patterns, func in command_to_function.items():
        best_pattern = find_best_match(preprocessed_input, patterns)
        if best_pattern:
            match = re.match(best_pattern, preprocessed_input, re.IGNORECASE)
            if match:
                if match.groups():
                    # Pass the matched groups as parameters to the function
                    result = func(*match.groups())
                else:
                    result = func()
                return result
    return "Command not recognized"



# Ensure you have the NLTK data required
nltk.download('punkt')
nltk.download('stopwords')