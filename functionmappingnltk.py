import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet as wn
nltk.download('punkt_tab')


from rapidfuzz import fuzz
from spellchecker import SpellChecker
import re
import GlobalData as GD

import flask
from flask_socketio import emit

# ------------------------------------------------
# import functions here
# ------------------------------------------------
from analytics import analytics_shortest_path

all_projects_text = '\n'.join(GD.listProjects())

# ------------------------------------------------
# Mapping commands to functions
# ------------------------------------------------
def mapped_show_allprojects():
    return all_projects_text

def mapped_search_project(project_name):
    for proj in GD.listProjects():
        if project_name.lower() == proj.lower():
            #print("C_DEBUG: Project found: ", proj)
            
            GD.data["actPro"] = proj
            GD.saveGD()
            GD.loadGD()
            GD.loadPFile()
            GD.loadPD()
            GD.loadColor()
            GD.loadLinks()
            GD.load_annotations()

            namespace = proj
            room = flask.session.get("room") 
            usr = flask.session.get("usr")

            #print("C_DEBUG: namespace: ", namespace)
            #print("C_DEBUG: room: ", room)

            response = {}
            response["val"] = proj
            response["fn"] = "project"

            emit("ex", response, usr = usr, room=room, namespace=namespace) 

            return f"Project {(proj)} opened successfully."
        
    return "No matching projects found. Please try again. \n Here is a list of all projects : "+ all_projects_text

    


# ------------------------------------------------
# Mapping of command patterns to functions with a pattern and a function reference
# ------------------------------------------------
command_to_function = {
    

    #(r"calculate shortest path", r"find shortest path"): mapped_analytics_shortest_path,

    (r"show all projects", r"project list", r"project collection"): mapped_show_allprojects,

    (r"open project (.+)", r"search project (.+)", r"show project (.+)", r"(.+) project (.+)"): mapped_search_project,
}




# spell check for typos
# synonyms for meaning 

spell = SpellChecker()

# ISSUE with spelling: project names are not recognized as correct spelling
# def correct_spelling(lui_user_input):
#     corrected = []
#     for word in word_tokenize(lui_user_input):
#         corrected.append(spell.correction(word))
#     return ' '.join(corrected)

def preprocess_input(lui_user_input):
    # Correct spelling mistakes
    corrected_input = lui_user_input #correct_spelling(lui_user_input)
    
    # Tokenize the input
    tokens = word_tokenize(corrected_input.lower())
    
    # Remove stopwords
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    return ' '.join(tokens)

def find_best_match(lui_user_input, patterns):
    best_match = None
    highest_ratio = 0
    for pattern in patterns:
        ratio = fuzz.partial_ratio(pattern, lui_user_input)
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = pattern
    return best_match if highest_ratio > 80 else None  # Use a threshold to determine match quality

def process_input(lui_user_input):
    preprocessed_input = preprocess_input(lui_user_input)

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
    return "Command not recognized. Please try again. \n Here is a list of all projects : "+ all_projects_text



# Ensure you have the NLTK data required
nltk.download('punkt')
nltk.download('stopwords')