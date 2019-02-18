import sys
from proto.Poem_pb2 import *

'''
Load Data on Poem objects.
'''
class DataLoader(object):

    '''
    Load data from poems into memory.
    '''
    def __init__(self, file):
        self.poems = {}
        poem_strings = open(file, 'r')
        for poem_string in poem_strings.readlines():
            poem = Poem()
            poem.ParseFromString(poem_string)
            self.poems[poem.title] = poem
        poem_strings.close()

    '''
    Serialize Poem proto data to a file.
    '''
    def write(self, file):
        poem_file = open(file, 'r')
        for poem in self.poems:
            poem_file.write(poem.SerializeToString() + '\n')
        poem_file.close()
