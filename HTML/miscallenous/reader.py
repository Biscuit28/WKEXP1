
import pymongo, urllib2, logging, pyquery, re
#NOTE do not read empty strings
#
#NOTE Stack implementation to read nested html elements.
class HTMLRead:
    '''
    reads only neccessary data from a HTML file

    '''


    def __init__(self, url):
        self.data = ""
        self.links = ""
        self.headings = ""
        self.target = url
        self.stack = [] #this will indicate where we are
        self.documents = []
        self.elements = set(['li ', 'li>', 'ul ', 'ul>', 'a ', 'p ', 'p>',
                        'em ','em>', 'h1 ','h1>', 'h2 ', 'h2>', 'h3 ',
                        'h3>', 'h4 ','h4>', 'h5 ', 'h5>', 'h6 ', 'h6>',
                        'title ', 'title>', 'span ', 'span>', 'i ', 'i>'])
        self.dynamic_elements = ['li ', 'li>', 'ul ', 'ul>', 'a ', 'p ', 'p>',
                        'em ','em>', 'h1 ','h1>', 'h2 ', 'h2>', 'h3 ',
                        'h3>', 'h4 ','h4>', 'h5 ', 'h5>', 'h6 ', 'h6>',
                        'title ', 'title>', 'span ', 'span>', 'i ', 'i>']
        #problem arises when we match say a word like li, but then it turns out to be a list
    def read_url(self, amnt=None):
        #using the urllib2 library
        if isinstance(amnt, int):
            self.data = urllib2.urlopen(self.target, timeout=20).read(amnt)
        else:
            self.data = urllib2.urlopen(self.target, timeout=20).read()

        #print self.data
        #print '----------------------------------------------------------------'

    def match_machine(self, word):
        '''finds if the word is a matching html element. if it goes that
        that it matches with an element ending with white space, then
        we dont proceed (we have to wait for ">" character). Else, if we
        find that our word is a success and ends with '>', we do infact proceed'''
        dead_list = []
        #this shoudl match well.
        # 0 = we continue to match
        # 1 = we found a match! but we still have to listen for >
        # 2 = we found a match! We also found! proceed to read stuff!
        # 3 = we couldnt find anything. go back to listening!
        if word in self.elements:
            self.dynamic_elements = ['li ', 'li>', 'ul ', 'ul>', 'a ', 'p ', 'p>',
                            'em ','em>', 'h1 ','h1>', 'h2 ', 'h2>', 'h3 ',
                            'h3>', 'h4 ','h4>', 'h5 ', 'h5>', 'h6 ', 'h6>',
                            'title ', 'title>', 'span ', 'span>', 'i ', 'i>']
            if word[-1] == ' ':
                #print 'matched! ' + word + ' no >'
                return 1
            else:
                #print 'matched! ' + word + ' yes >'
                return 2
        #this finds all the elements that dont meet the criteria, and stores it
        for element in self.dynamic_elements:
            if word not in element:
                dead_list.append(element)
        #this items that do not meet the criteria is then removed from our list.
        for j in dead_list:
            if j in self.dynamic_elements:
                self.dynamic_elements.remove(j)
        #when our list is empty it must imply that we cant find any matches
        if len(self.dynamic_elements) == 0:
            #print 'no match found, terminating'
            self.dynamic_elements = ['li ', 'li>', 'ul ', 'ul>', 'a ', 'p ', 'p>',
                            'em ','em>', 'h1 ','h1>', 'h2 ', 'h2>', 'h3 ',
                            'h3>', 'h4 ','h4>', 'h5 ', 'h5>', 'h6 ', 'h6>',
                            'title ', 'title>', 'span ', 'span>', 'i ', 'i>']
            return 3
        #print self.dynamic_elements
        return 0

    def reader(self):
        '''FOLLOW THE STATEMACHINE

        IDEA: As long as we are in the stack we should still read
        '''
        #initializing all the states
        # 0        1     2      3     4      5
        #Listen, Alert, Match, Wait, Read, Uncertain
        (Listen, Alert, Match, Wait, Read, Uncertain) = self.switch_states(0) #start by listening
        text, document = '', ''

        for char in self.data:
            if Listen:
                #print 'on LISTEN MODE'
                if char == '<': #switch to ALERT
                    (Listen, Alert, Match, Wait, Read, Uncertain) = self.switch_states(1)
            elif Alert:
                if char == '/': #this is the condition for right after we get from reading state.
                    #if this is the case we should be listening
                    (Listen, Alert, Match, Wait, Read, Uncertain) = self.switch_states(0)
                #print 'on ALERT MODE'
                text = text + char
                res = self.match_machine(text)
                #if we get a bad match, continue on listening, bad match = [0, 0, ]
                if res == 1: #match, but we have to be cautious, proceed to wait
                    (Listen, Alert, Match, Wait, Read, Uncertain) = self.switch_states(3)
                    #print 'on WAIT MODE'
                    #return None
                if res == 2: #match, but we are ready to read
                    (Listen, Alert, Match, Wait, Read, Uncertain) = self.switch_states(4)
                    #print 'on READ MODE'
                    #return None
                if res == 3: #couldnt find anything, go back to listening. RESET OUR TEXT
                    text = ''
                    (Listen, Alert, Match, Wait, Read, Uncertain) = self.switch_states(0)
            elif Wait:  #now were waiting for > so we can start reading!
                if char == '>': #found it, time to start reading.
                    (Listen, Alert, Match, Wait, Read, Uncertain) = self.switch_states(4)
            elif Read: #now were Reading, need somewhere to store it
                if char == '<': #uh oh we should stop reading, going back to alert?
                    self.documents.append(document) #throwing our document in to collection NOTE you might want to check the logic here
                    document = '' #resetting our document
                    (Listen, Alert, Match, Wait, Read, Uncertain) = self.switch_states(1)
                else:
                    document = document + char


    def switch_states(self, state):
        if state == 0: #LISTEN
            return(True, False, False, False, False, False)
        if state == 1: #ALERT
            return(False, True, False, False, False, False)
        if state == 2: #MATCH
            return(False, False, True, False, False, False)
        if state == 3: #WAIT
            return(False, False, False, True, False, False)
        if state == 4: #READ
            return(False, False, False, False, True, False)
        if state == 5: #UNCERTAIN
            return(False, False, False, False, False, True)
    #NOTE need to work on it
    def clean_document(self):
        '''
        Method removes any blanks and /n's
        '''
        cleandoc = []
        for element in self.documents:
            temp = self.remove_whitespace(element)
            if temp != '' and temp != '\n':
                cleandoc.append(temp)

        print cleandoc


    def remove_whitespace(self, doc_ele):
        #RULES:  if the first element is a white space, delete it.
                #if the first element right after the letter is a white space, keep it
                #any subsequent white space remove it.
                #if we see /n, we remove it.
        temp = ''
        if len(doc_ele) <= 1:
            return ''
        for i in range(0, len(doc_ele)-2):
            if doc_ele[i] != ' ': #remove the white space at the back.
                temp = temp + doc_ele[i]
            if doc_ele[i] == ' ' and doc_ele[i+1] != ' ':
                temp = temp + ' '
        if doc_ele[-2] != ' ' and doc_ele[-1] != ' ':
            temp = temp + doc_ele[-2:]
        if doc_ele[-2] != ' ' and doc_ele[-1] == ' ':
            temp = temp + doc_ele[-2]
        if doc_ele[-2] == ' ' and doc_ele[-1] != ' ':
            temp = temp + ' ' + doc_ele[-1]

        if temp[0] == ' ':
            temp = temp[1:]

        return temp




#http://www.wikihow.com/Make-Pizza-from-Scratch
#http://www.berkshirehathaway.com
#http://www.wikihow.com/Make-Pizza-from-Scratch

test = HTMLRead("http://www.wikihow.com/Make-Pizza-from-Scratch")
test.read_url()
test.reader()
#print test.documents
test.clean_document()

#print test.remove_whitespace('    dsadksajkl  Hello    My awesome   Friends! Yea LOTS OF        WHITE SPACES      LOL')
