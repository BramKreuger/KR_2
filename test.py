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

    return variables_to_forget



x = parseOMN("exp5-1.owl")
print(x)

