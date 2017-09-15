def linear_tree(l_list, count=0):

    newbranch = []
    tmp = l_list[:]

    count += 1

    for w in l_list:

        if len(w) == count:

            tmp.remove(w)

            newbranch = [w, linear_tree(tmp, count=count)]

            return newbranch

    return 'Node'




def branched_tree(l_list, important, search_word=None):

    '''
    Function takes in a set of important key words and a list (with no duplicates)
    and from it creates an abstract syntax tree. The structure of the tree is as follows

    Given a list of something like

    ['A', 'ABC', 'AD', 'B', 'BF', 'BFG']

    The output shoud be

    ['A', ['AB', ['ABC', 'END'], 'AD', 'END'], 'B', ['BF', ['BFG', 'END']]]

    NOTE: l_list CANNOT HAVE DUPLICATES. convert into a set first and then a list

    '''

    print 'new recursion'

    newbranch, branches = [], set()
    tmp = l_list[:]

    for w in l_list:

        if search_word == None and len(w) == 1:
            print 'first letters', w
            branches.add(w)
            continue

        if search_word != None and (len(w) > len(search_word)) and (search_word == w[:len(search_word)]):
            w = w[:len(search_word)+1]
            print 'recursion letters', w
            branches.add(w)

    for w in branches:

        leaf = w

        if w in tmp:
            tmp.remove(w)

        if w in important:
            leaf = (w, '*')

        subbranch = branched_tree(tmp, important, search_word = w)

        newbranch.append(leaf)
        newbranch.append(subbranch)

    if not newbranch:
        return 'END'
    else:
        return newbranch



b = ['A', 'AD', 'AR', 'AM', 'AMR', 'AMD', 'ADE', 'B', 'BF', 'BG', 'BGE']
print b
important_set = set(['A', 'AR', 'AMD', 'ADE'])
print branched_tree(b, important_set)
