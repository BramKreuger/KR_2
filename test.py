# New extraction steps
# 1. Read subClasses.nt -> extract two variables
# 2. From exp.omn extract all variables
# 3. From all variables subract two variables

def parseOMN(subClasses_file, omn_file):
    # STEP 1.

    myfile = open(subClasses_file, "rt")        # open lorem.txt for reading text
    contents = myfile.read()         # read the entire file to string
    myfile.close()                   # close the file

    contents = contents.split(' .\n')[:-1]
    entailment_variables = []
    for line in contents:
        split_position = 0
        result = ""
        found_arrow = False
        for pointer in line:
            split_position += 1         
            if pointer == '<':  
                found_arrow = True          
            if(not pointer == '>' and found_arrow == True):
                result += pointer
            else:
                found_arrow = False
        # Reverse the strings back, remove the last '>', split the vars on '>'
        split_result = result.split('<')
        print("Entailment:", split_result[1], " to ", split_result[3])
        entailment_variables.append([split_result[1], split_result[3]])

    # STEP 2.

    myfile = open(omn_file, "rt")    # open lorem.txt for reading text
    contents = myfile.read()                # read the entire file to string
    myfile.close() 

    all_variables = []
    split_contents = contents.split(">")[1:-1]
    for line in split_contents:
        all_variables.append(line.split("<")[1])

    # STEP 3.
    list_wo_doubles = list(dict.fromkeys(all_variables))    
    return list_wo_doubles, entailment_variables
    


x, y = parseOMN("datasets/subClasses.nt", "datasets/exp1-1.omn")
print(x)

