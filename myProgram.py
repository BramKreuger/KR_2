import os, glob, re

inputOntology = "datasets/abstract_uvw.owl"

inputSubclassStatements = "datasets/subClasses.nt" # this file can be generated using the second command (saveAllSubClasses)

# Decide on a method for the forgetter (check the papers of LETHE to understand the different options).
# The default is 1, I believe.
# 1 - ALCHTBoxForgetter
# 2 - SHQTBoxForgetter
# 3 - ALCOntologyForgetter
method = "2" #

# Choose the symbols which you want to forget.
signature = "datasets/signature.txt"

# 1. PRINT ALL SUBCLASSES (inputOntology):
# print all subClass statements (explicit and inferred) in the inputOntology
# --> uncomment the following line to run this function
#os.system('java -jar kr_functions.jar ' + 'printAllSubClasses' + " " + inputOntology)

# 2. SAVE ALL SUBCLASSES (inputOntology):
# save all subClass statements (explicit and inferred) in the inputOntology to file datasets/subClasses.nt
# --> uncomment the following line to run this function
os.system('java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + inputOntology)

# 3. PRINT ALL EXPLANATIONS (inputOntology, inputSubclassStatements):
# print explanations for each subClass statement in the inputSubclassStatements
# --> uncomment the following line to run this function
#os.system('java -jar kr_functions.jar ' + 'printAllExplanations' + " " + inputOntology + " " + inputSubclassStatements)

# 4. SAVE ALL EXPLANATIONS (inputOntology, inputSubclassStatements):
# save explanations for each subClass statement in the inputSubclassStatements to file dataset/exp-#.owl
# --> uncomment the following line to run this function
os.system('java -jar kr_functions.jar ' + 'saveAllExplanations' + " " + inputOntology + " " + inputSubclassStatements)

#for explanation in explanations:
#    forgetOntology = "datasets/university-example.owl"
 #   for variable in variables:
    # For running LETHE forget command:
    # --> uncomment the following line to run this function
#os.system('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication $*')

def parseOMN(file):
    myfile = open(file, "rt")        # open lorem.txt for reading text
    contents = myfile.read()         # read the entire file to string
    myfile.close()                   # close the file

    # 1. loop through string to find >
    # 2. loop back to find first /, 
    # 3. remove everything left of > #(split_position)
    # 4. repeat

    split_position = 0
    result = ""
    for pointer in contents:
        split_position += 1 
        if pointer == '>':
            for result_character in reversed(contents[:split_position]):
                if(not result_character == '<'):
                    result += result_character
                else:
                    break
    result = ((result[::-1])[:len(result) - 1]).split('>') # Reverse the strings back, remove the last '>', split the vars on '>'
    return result[:len(result) - 1] # remove the last element, which is always explanation some number

# Flattens list, removes doubles, writes the vars into signature.txt
def extract_varables(list_of_results):
    flat_list = [item for sublist in list_of_results for item in sublist]    
    list_wo_doubles = list(dict.fromkeys(flat_list))

    if os.path.exists("signature.txt"):
        os.remove("signature.txt")
    
    f = open("signature.txt", "w+")
    for var in list_wo_doubles:
        f.write(var + "\n")
    f.close()

    

os.chdir("D:\git\KR_FORGETTING\datasets")
all_parsed_results = []
for file in glob.glob("exp*"):
    all_parsed_results.append(parseOMN(file)) # Extract all the variables from the omn files

extract_varables(all_parsed_results) # Save all variables in the signature.txt

for file in glob.glob("exp*"):
    os.system('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' + inputOntology + ' --method ' + method  + ' --signature ' + signature)