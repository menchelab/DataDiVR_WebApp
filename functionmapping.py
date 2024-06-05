# mypythonfile.py
import nltk

# import functions here

def function_XY():
    return "Function XY executed"

def function_AB():
    return "Function AB executed"

# Mapping of commands to functions
command_to_function = {
    "calculate x and y": function_XY,
    "open project": function_AB
}

def process_input(user_input):
    tokens = nltk.word_tokenize(user_input)
    command = " ".join(tokens)
    
    if command in command_to_function:
        result = command_to_function[command]()
        return result
    else:
        return "Command not recognized"

# Ensure you have the NLTK data required
nltk.download('punkt')

# Example usage
if __name__ == "__main__":
    user_input = "do XY"
    print(process_input(user_input))  # This will print "Function XY executed"
