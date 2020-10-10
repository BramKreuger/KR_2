import os, glob, re, shutil

inputOntology = "datasets/simple-deep-ontology.owl"

inputSubclassStatements = "datasets/subClasses.nt" # this file can be generated using the second command (saveAllSubClasses)

# Decide on a method for the forgetter (check the papers of LETHE to understand the different options).
# The default is 1, I believe.
# 1 - ALCHTBoxForgetter
# 2 - SHQTBoxForgetter
# 3 - ALCOntologyForgetter
method = "2" #

# Remove everything in the results folder
def clean_directories():

    # Remove results dir
    shutil.rmtree("results")
    
    # Check if results directory exists, otherwise create it
    try:
        os.makedirs("results")
    except OSError:
        print ("Creation of the directory %s failed" % "results")
    else:
        print ("Successfully created the directory %s " % "results") 

    # Remove all eplanation files before beginning
    for file in glob.glob("datasets/exp*"):
        os.remove(file)
    os.chdir("D:\git\KR_FORGETTING")    
# Set up all the directories
clean_directories()

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

def parseOMN(file):
    myfile = open(file, "rt")        # open lorem.txt for reading text
    contents = myfile.read()         # read the entire file to string
    myfile.close()                   # close the file

    # 1. loop through string to find >
    # 2. loop back to find first <, 
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
def write_variables_to_file(path, name, list_of_results):
    #flat_list = [item for sublist in list_of_results for item in sublist] # flatten   
    list_wo_doubles = list(dict.fromkeys(list_of_results))     
    
    var_counter = 1
    for var in list_wo_doubles:
        f = open(path + name + "-var-" + str(var_counter) + ".txt", "w+")
        f.write(var + "\n")
        f.close()
        var_counter += 1

def forget_explanation(new_file_path, method, var_counter):
    if(var_counter > 2):

        owl_counter = 1
        # For each result-#.owl file
        for file in glob.glob(new_file_path + "/result*.owl"):
            
            newest_file_path = new_file_path + "/" + str(owl_counter)

            # for each subsequent explanation, create a folder
            os.makedirs(newest_file_path)

            # Run Save subclasses and explanations on the new .owl file
            os.system('java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + file)
            os.system('java -jar kr_functions.jar ' + 'saveAllExplanations' + " " + file + " " + inputSubclassStatements)

            # Move all .omn file to respective folder
            omn_counter = 1
            for omn_file in glob.glob(new_file_path + "/*.omn"):
                #os.makedirs(newest_file_path + "/" + str(omn_counter))
                new_omn_file_path = newest_file_path + "/" + str(omn_counter) + ".omn"
                shutil.move(omn_file, new_omn_file_path)

                parsed_vars = parseOMN(new_omn_file_path)
                write_variables_to_file(newest_file_path + "/", str(omn_counter), parsed_vars)

                # For each variable from the explanation
                var_counter = 1
                for var in glob.glob(newest_file_path + "/*.txt"):
                    os.system('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' + 
                    new_omn_file_path + ' --method ' + method  + ' --signature ' + var)
                    shutil.move("result.owl", newest_file_path + "/result-" + str(var_counter) + ".owl")
                    var_counter += 1

                forget_explanation(newest_file_path, method, var_counter - 1) # Extract one from the var counter because it starts with 1 for naming pourposes

                omn_counter += 1
            
            owl_counter += 1

# For each initial explanation
#for file in glob.glob("datasets/exp*"):
file = "datasets\\exp1-1.omn"
file_name = file.split("\\")[1].split('.')[0]

# Now for each initial explanation, create a folder
os.makedirs("results/" + file_name)
new_file_path = "results/" + file_name + "/" + file_name + ".owl"
shutil.move(file, new_file_path)

parsed_vars = parseOMN(new_file_path)
write_variables_to_file("results/" + file_name + "/", file_name, parsed_vars)

# For each variable from the explanation
var_counter = 1
for var in glob.glob("results/" + file_name + "/*.txt"):
    os.system('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' + 
    new_file_path + ' --method ' + method  + ' --signature ' + var)
    shutil.move("result.owl", "results/" + file_name + "/result-" + str(var_counter) + ".owl")
    var_counter += 1

# Go in the recursive forgetter, Only if there are more then two variables
forget_explanation("results/" + file_name, method, var_counter)


    # recheck for variables before you do lethe again
