def parse(file):
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
    return result[:len(result) - 1]

r = parse("datasets/exp1-1.omn")
print(r)