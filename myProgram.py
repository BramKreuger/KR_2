import os, glob, re, shutil, sys
import subprocess, time

# Start timing 
start = time.perf_counter()

inputOntology = "datasets/university-example.owl"

inputSubclassStatements = "datasets/subClasses.nt" # this file can be generated using the second command (saveAllSubClasses)

# Decide on a method for the forgetter (check the papers of LETHE to understand the different options).
# The default is 1, I believe.
# 1 - ALCHTBoxForgetter
# 2 - SHQTBoxForgetter
# 3 - ALCOntologyForgetter
method = "2" 

# Remove everything in the results folder
def clean_directories():

    # Remove results dir
    try:
        shutil.rmtree("results")
    except OSError:
        print ("Removing of the directory %s failed" % "results")
    else:
        print ("Successfully removed the directory %s " % "results") 
    
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

# Set up all the directories
clean_directories()

# 1. PRINT ALL SUBCLASSES (inputOntology):
# print all subClass statements (explicit and inferred) in the inputOntology
# --> uncomment the following line to run this function
#os.system('java -jar kr_functions.jar ' + 'printAllSubClasses' + " " + inputOntology)

# 2. SAVE ALL SUBCLASSES (inputOntology):
# save all subClass statements (explicit and inferred) in the inputOntology to file datasets/subClasses.nt
# --> uncomment the following line to run this function
#os.system('java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + inputOntology)
subprocess.Popen('java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + inputOntology, shell=True, stdout=subprocess.DEVNULL).wait()

# 3. PRINT ALL EXPLANATIONS (inputOntology, inputSubclassStatements):
# print explanations for each subClass statement in the inputSubclassStatements
# --> uncomment the following line to run this function
#os.system('java -jar kr_functions.jar ' + 'printAllExplanations' + " " + inputOntology + " " + inputSubclassStatements)

# 4. SAVE ALL EXPLANATIONS (inputOntology, inputSubclassStatements):
# save explanations for each subClass statement in the inputSubclassStatements to file dataset/exp-#.owl
# --> uncomment the following line to run this function
subprocess.Popen('java -jar kr_functions.jar ' + 'saveAllExplanations' + " " + inputOntology + " " + inputSubclassStatements, shell=True, stdout=subprocess.DEVNULL).wait()

# extract all the variables which aren't neccecery for entailment
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
    # Reverse the strings back, remove the last '>', split the vars on '>'
    result = ((result[::-1])[:len(result) - 1]).split('>') 
    # remove the last element, which is always explanation some number and finaly reverse the list
    list_with_single_elements = (result[:len(result) - 1])[::-1] 

    list_with_tuples = []
    for i in range(0, len(list_with_single_elements), 2):
        list_with_tuples.append( (list_with_single_elements[i], list_with_single_elements[i + 1]) )

    # list_with_tuples is the bag
    ordered_list_with_tuples = [list_with_tuples[0]]
    list_with_tuples.remove(list_with_tuples[0]) 

    # if there are still elements in the bag
    while(len(list_with_tuples) > 0): 
        for tup in list_with_tuples:
            # Is the second variable of the last tuple the same as the first var of tup?
            if(ordered_list_with_tuples[-1][1] == tup[0]):
                ordered_list_with_tuples.append(tup)
                list_with_tuples.remove(tup)
                break
            # Is the first variable of the first tuple the same as the second var of tup?
            elif(ordered_list_with_tuples[0][0] == tup[1]):
                ordered_list_with_tuples.insert(0, tup)
                list_with_tuples.remove(tup)
                break

    variables_to_forget = [ordered_list_with_tuples[0][1], ordered_list_with_tuples[-1][0]]
    if( len(ordered_list_with_tuples) > 1):
        for tup in ordered_list_with_tuples[1:-1]:
            variables_to_forget.append(tup[0])
            variables_to_forget.append(tup[1])

    print("Entailment:", ordered_list_with_tuples[0][0].split('/')[-1], " TO ", ordered_list_with_tuples[-1][1].split('/')[-1])
    return variables_to_forget

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
            try:
                os.makedirs(newest_file_path)
            except OSError:
                print ("Creation of the directory %s failed" % newest_file_path)
            else:
                print ("Successfully created the directory %s " % newest_file_path) 


            # Run Save subclasses and explanations on the new .owl file
            subprocess.Popen('java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + file, shell=True, stdout=subprocess.DEVNULL).wait()
            subprocess.Popen('java -jar kr_functions.jar ' + 'saveAllExplanations' + " " + file + " " + inputSubclassStatements, shell=True, stdout=subprocess.DEVNULL).wait()

            # Move all .omn file to respective folder
            omn_counter = 1
            for omn_file in glob.glob(new_file_path + "/*.omn"):
                new_omn_file_path = newest_file_path + "/" + str(omn_counter) + ".omn"
                shutil.move(omn_file, new_omn_file_path)

                parsed_vars = parseOMN(new_omn_file_path)
                write_variables_to_file(newest_file_path + "/", str(omn_counter), parsed_vars)

                new_var_counter = len(parsed_vars)

                # For each variable from the explanation
                for var in glob.glob(newest_file_path + "/*.txt"):
                    subprocess.Popen('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' + 
                    new_omn_file_path + ' --method ' + method  + ' --signature ' + var, shell=True, stdout=subprocess.DEVNULL).wait()
                    shutil.move("result.owl", newest_file_path + "/result-" + str(var_counter) + ".owl")

                # Extract one from the var counter because it starts with 1 for naming pourposes
                #if(new_var_counter < var_counter - 1):
                forget_explanation(newest_file_path, method, var_counter - 1) 
                #else:
                #    break

                omn_counter += 1
            
            owl_counter += 1

# For each initial explanation
for file in glob.glob("datasets/exp*"):
    #file = "datasets\\exp1-1.omn"
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
        subprocess.Popen('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' + 
        new_file_path + ' --method ' + method  + ' --signature ' + var, shell=True, stdout=subprocess.DEVNULL).wait()
        shutil.move("result.owl", "results/" + file_name + "/result-" + str(var_counter) + ".owl")
        var_counter += 1

    # Go in the recursive forgetter, Only if there are more then two variables
    forget_explanation("results/" + file_name, method, var_counter)

def removeEmptyFolders(path, removeRoot=True):
  'Function to remove empty folders'
  if not os.path.isdir(path):
    return

  # remove empty subfolders
  files = os.listdir(path)
  if len(files):
    for f in files:
      fullpath = os.path.join(path, f)
      if os.path.isdir(fullpath):
        removeEmptyFolders(fullpath)

  # if folder empty, delete it
  files = os.listdir(path)
  if len(files) == 0 and removeRoot:
    print ("Removing empty folder:", path)
    os.rmdir(path)
    
removeEmptyFolders("results", False)

finish = time.perf_counter()

print(f"Finished in {finish - start:0.4f} seconds")

# TODO: Forgetting the right variables. Which aren't neccecery for entailment
# TODO: Implementing heuristics

