import os, glob, re, shutil, sys, copy, csv
import subprocess, time, random, argparse
from collections import Counter 

inputSubclassStatements = "datasets/subClasses.nt" # this file can be generated using the second command (saveAllSubClasses)

# Decide on a method for the forgetter (check the papers of LETHE to understand the different options).
# The default is 1, I believe.
# 1 - ALCHTBoxForgetter
# 2 - SHQTBoxForgetter
# 3 - ALCOntologyForgetter
method = "2"

# Remove everything in the results folder
def cleanDirectories():
    # Remove results dir
    try: shutil.rmtree("results")
    except OSError: print("Removing of the directory %s failed" % "results")
    else: print("Successfully removed the directory %s " % "results")
    
    # Check if results directory exists, otherwise create it
    try: os.makedirs("results")
    except OSError: print("Creation of the directory %s failed" % "results")
    else: print("Successfully created the directory %s " % "results")

    # Remove all eplanation files before beginning
    for file in glob.glob("datasets/exp*"): os.remove(file)

def saveSubclassStatements(inputOntology):
    # 1. PRINT ALL SUBCLASSES (inputOntology):
    # print all subClass statements (explicit and inferred) in the inputOntology
    # --> uncomment the following line to run this function
    #os.system('java -jar kr_functions.jar ' + 'printAllSubClasses' + " " + inputOntology)

    # 2. SAVE ALL SUBCLASSES (inputOntology):
    # save all subClass statements (explicit and inferred) in the inputOntology to file datasets/subClasses.nt
    # --> uncomment the following line to run this function
    #os.system('java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + inputOntology)
    subprocess.Popen('java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + inputOntology, shell = True, stdout = subprocess.DEVNULL).wait()

    # 3. PRINT ALL EXPLANATIONS (inputOntology, inputSubclassStatements):
    # print explanations for each subClass statement in the inputSubclassStatements
    # --> uncomment the following line to run this function
    #os.system('java -jar kr_functions.jar ' + 'printAllExplanations' + " " + inputOntology + " " + inputSubclassStatements)

    # 4. SAVE ALL EXPLANATIONS (inputOntology, inputSubclassStatements):
    # save explanations for each subClass statement in the inputSubclassStatements to file dataset/exp-#.owl
    # --> uncomment the following line to run this function
    subprocess.Popen('java -jar kr_functions.jar ' + 'saveAllExplanations' + " " + inputOntology + " " + inputSubclassStatements, shell = True, stdout = subprocess.DEVNULL).wait()

# New extraction steps
# 1. Read subClasses.nt -> extract two variables
# 2. From exp.omn extract all variables
# 3. From all variables subract two variables
def parseOMN(subClasses_file, omn_file):
    # STEP 1.
    myfile = open(subClasses_file, "rt")  # open lorem.txt for reading text
    contents = myfile.read()              # read the entire file to string
    myfile.close()                        # close the file
    contents = contents.split(' .\n')[:-1]
    entailment_variables = []
    for line in contents:
        split_position = 0
        result = ""
        found_arrow = False
        for pointer in line:
            split_position += 1         
            if pointer == '<': found_arrow = True
            if not pointer == '>' and found_arrow == True: result += pointer
            else: found_arrow = False
        # Reverse the strings back, remove the last '>', split the vars on '>'
        split_result = result.split('<')
        entailment_variables.append([split_result[1], split_result[3]])

    # STEP 2.
    myfile = open(omn_file, "rt") # open lorem.txt for reading text
    contents = myfile.read()      # read the entire file to string
    myfile.close()
    all_variables = []
    split_contents = contents.split(">")[1:-1]
    for line in split_contents: all_variables.append(line.split("<")[1])

    # STEP 3.
    # Removed list without doubles, since we need the doubles for the heuristics    
    return all_variables, entailment_variables

# writes the vars into signature.txt
def writeVariablesToFile(path, name, all_variables, entailment_variables, which_line, heuristic):
    # Decide on heuristic here
    ordered_variables = []
    if(heuristic == 1):   # MOV
       ordered_variables = [item for items, c in Counter(all_variables).most_common() for item in [items] * c] 
    elif(heuristic == 2): # LOV
        ordered_variables = [item for items, c in Counter(all_variables).most_common() for item in [items] * c] 
        ordered_variables[::-1]
    else:                 # Extensive search
        ordered_variables = list(dict.fromkeys(all_variables))

    variables_to_forget = copy.deepcopy(ordered_variables)
    # Check if variables are not in entailment
    for var in ordered_variables:
        if var == entailment_variables[which_line][0] or var == entailment_variables[which_line][1]: variables_to_forget.remove(var)

    # If the heuristic is 1 or 2, pick the first eligable LOV / MOV
    if(heuristic != 3 and len(variables_to_forget) > 0): 
        rand_int = random.randint(0, len(variables_to_forget) - 1)
        variables_to_forget = [variables_to_forget[rand_int]]

    var_counter = 1
    for var in variables_to_forget:
        f = open(path + name + "-var-" + str(var_counter) + ".txt", "w+")
        f.write(var + "\n")
        f.close()
        var_counter += 1

def forgetExplanation(new_file_path, method, var_counter, heuristic, old_number_of_variables):
    owl_counter = 1
    # For each result-#.owl file
    for file in glob.glob(new_file_path + "/result*.owl"):
        newest_file_path = new_file_path + "/" + str(owl_counter)
        
        # for each subsequent explanation, create a folder
        try: os.makedirs(newest_file_path)
        except OSError: print ("Creation of the directory %s failed" % newest_file_path)
        else: print ("Successfully created the directory %s " % newest_file_path)

        # Run Save subclasses and explanations on the new .owl file
        subprocess.Popen('java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + file, shell = True, stdout=subprocess.DEVNULL).wait()
        subprocess.Popen('java -jar kr_functions.jar ' + 'saveAllExplanations' + " " + file + " " + inputSubclassStatements, shell = True, stdout = subprocess.DEVNULL).wait()

        # Move all .omn file to respective folder
        omn_counter = 1
        for omn_file in glob.glob(new_file_path + "/*.omn"):
            new_omn_file_path  = newest_file_path + "/" + str(omn_counter) + ".omn"
            shutil.move(omn_file, new_omn_file_path)
            parsed_vars, entailment_variables = parseOMN(inputSubclassStatements, new_omn_file_path)

            new_number_of_variables = len(parsed_vars)

            if(new_number_of_variables < old_number_of_variables):
                writeVariablesToFile(newest_file_path + "/", str(omn_counter), parsed_vars, entailment_variables, omn_counter - 1, heuristic)            
                # For each variable from the explanation
                for var in glob.glob(newest_file_path + "/*.txt"):
                    subprocess.Popen('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' +
                    new_omn_file_path + ' --method ' + method  + ' --signature ' + var, shell = True, stdout = subprocess.DEVNULL).wait()
                    shutil.move("result.owl", newest_file_path + "/result-" + str(var_counter) + ".owl")

                # Extract one from the var counter because it starts with 1 for naming pourposes
                forgetExplanation(newest_file_path, method, var_counter - 1, heuristic, new_number_of_variables)
                omn_counter += 1
        owl_counter += 1

def createExpFolders(heuristic):
    # For each initial explanation
    exp_cntr = 0
    for file in glob.glob("datasets/exp*"):
        file_name = file.split(os.sep)[1].split('.')[0]
        
        # Now for each initial explanation, create a folder
        os.makedirs("results/" + file_name)
        new_file_path = "results/" + file_name + "/" + file_name + ".owl"
        shutil.move(file, new_file_path)
        parsed_vars, entailment_variables = parseOMN(inputSubclassStatements, new_file_path)
        writeVariablesToFile("results/" + file_name + "/", file_name, parsed_vars, entailment_variables, exp_cntr, heuristic)
        
        # For each variable from the explanation
        var_counter = 1
        for var in glob.glob("results/" + file_name + "/*.txt"):
            subprocess.Popen('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' +
            new_file_path + ' --method ' + method  + ' --signature ' + var, shell = True, stdout = subprocess.DEVNULL).wait()
            shutil.move("result.owl", "results/" + file_name + "/result-" + str(var_counter) + ".owl")
            var_counter += 1

        # Go in the recursive forgetter, Only if there are more then two variables
        forgetExplanation("results/" + file_name, method, var_counter, heuristic, len(parsed_vars))
        exp_cntr += 1

def removeEmptyFolders(path, removeRoot = True):
  'Function to remove empty folders'
  if not os.path.isdir(path): return

  # remove empty subfolders
  files = os.listdir(path)
  if len(files):
    for f in files:
      fullpath = os.path.join(path, f)
      if os.path.isdir(fullpath): removeEmptyFolders(fullpath)

  # if folder empty, delete it
  files = os.listdir(path)
  if len(files) == 0 and removeRoot:
    print("Removing empty folder:", path)
    os.rmdir(path)

# Compute complexity
def computeComplexityScore(subclasses_file, file):
    axioms = getAxioms(file)
    nr_of_axioms = nrOfAxioms(axioms)
    nr_of_constructors = nrOfConstructors(axioms)
    score = 100 * nr_of_axioms + 10 * nr_of_constructors + 50 * modalDepth(file) + 50 * signatureDifference(subclasses_file, file)
    return score

# Calculate number of types of axioms
def nrOfAxioms(axioms):
    subclass, equivalence = 0, 0
    for axiom in axioms:
        if "SubClassOf" in axiom: subclass = 1
        elif "EquivalentClasses" in axiom: equivalence = 1
    return subclass + equivalence

# Calculate number of constructors, i.e. class expressions
def nrOfConstructors(axioms):
    constructors = 0
    for axiom in axioms:
        if ("ObjectIntersectionOf" or "ObjectUnionOf" or "ObjectComplementOf") in axiom: constructors += 1
    return constructors

# Calculate signature difference, i.e., Signature(eta) \ Signature(J)
def signatureDifference(subclasses_file, file):
    exp_variables, entailment_variables = parseOMN(subclasses_file, file)

    if(len(exp_variables) == 0 or len(entailment_variables) == 0):
        return 0

    flat_list = [item for sublist in entailment_variables for item in sublist]
    return len(set(exp_variables).difference(set(flat_list)))

# Calculate number of axioms for a given explanation
def getAxioms(file):
    myfile = open(file, "rt")   # open lorem.txt for reading text
    contents = myfile.read()    # read the entire file to string
    myfile.close()              # close the file
    resulted_axioms = []
    split_text = contents.split("\n")
    split_text.pop(0)           # remove the first row that we do not use
    split_text.pop()            # remove the parenthesis from the end
    for token in split_text: resulted_axioms.append(token.split("(")[0])
    return list(set(resulted_axioms))

# Compute the modal depth in each exp.owl file
def modalDepth(file):
    myfile = open(file, "rt")   # open lorem.txt for reading text
    contents = myfile.read()    # read the entire file to string
    myfile.close()              # close the file
    resulted_axioms = []
    split_text = contents.split("\n")
    split_text.pop(0)           # remove the first row that we don't use
    split_text.pop()            # remove the parenthesis from the end
    axioms = []
    for token in split_text:
        if ("<" and ">") in token: axioms.append(token)  # I'm taking each statment
    entities = []
    # there might be constructors inside the sub-class axiom, thus we need to count the number of occurrences of the substring "SubClassOf"
    for element in axioms: entities.append(element.count("SubClassOf")) # count the individuals
    max = 0
    for element in entities:
        if element > max: max = element
    return max # max instead of max / 2?

# Iterate through all explanation files and calculate a score
def getComplexityScores():
    file_names, scores = [], []   
    subclasses_file = "" 
    for subdir, dir, files in os.walk(r'results'):
        print(subdir + "\\*")

        # Get the proper subClasses file 
        for file in files: 
            filepath = subdir + os.sep + file            
            if(filepath.endswith(".nt")):
                subclasses_file = filepath    

        # Check if there is a folder in the dir  
        if(len(dir) > 0 or files[0].endswith('.omn')):         
            for file in files: 
                filepath = subdir + os.sep + file
                if (filepath.endswith(".owl") and file.startswith("exp")) or filepath.endswith(".omn"):
                    file_names.append(file)
                    scores.append(computeComplexityScore(subclasses_file, filepath))
    return file_names, scores

def printScores(csv_results_name, file_names, scores):
    print("== CoMpLeXiTy ScOrEs ==\nFile name\tScore")
    print("File name\tScore")
    for i in range(len(file_names)): print(file_names[i] + "\t", scores[i])

    csv_results_name = csv_results_name + ".csv"

    try:
        os.remove(csv_results_name)
    except OSError:
        pass

    with open(csv_results_name, mode='w') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for i in range(0, len(file_names), 2):
            results_writer.writerow([scores[i], scores[i + 1]])
    print("=======================")

def boolean_string(s):
    if s not in {'False', 'True'}:
        raise ValueError('Not a valid boolean string')
    return s == 'True'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('result', metavar='R', type=str,
                    help='saves results to this filename')
    parser.add_argument('ontology', metavar='O', type=str,
                    help='filename of the ontology to load') 
    parser.add_argument('heuristic', metavar='H', type=int, choices=[1, 2, 3],
                    help='Which heuristic to run. 1: LOV, 2: MOV, 3: Extensive')
    parser.add_argument('generate', metavar='C', type=boolean_string,
                    help='True: GNERATE all files and calculate complexity. False: ONLY calculate complexity')              
    args = parser.parse_args()
   
    print(args)

    # Start timing
    start = time.perf_counter()
    
    # Only (re)generate all files when argument complexity is 1.
    if(args.generate == True):
        cleanDirectories()
        saveSubclassStatements(args.ontology)
        createExpFolders(args.heuristic)
        removeEmptyFolders("results", False)
        finish = time.perf_counter()
        print(f"Finished in {finish - start:0.4f} seconds")

    file_names, scores = getComplexityScores()
    printScores(args.result, file_names, scores)

main()

# TODO: Forgetting the right variables. Which aren't neccecery for entailment
# TODO: Implementing heuristics
