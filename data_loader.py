import sys
import os
from proto.Poem_pb2 import *

'''
Load Data on Poem objects for a particular sequence.
'''
class DataLoader(object):

    '''
    Load data from poems into memory.
    '''
    def __init__(self, dir):
        self.poems = {}
        for filename in os.listdir(dir):
            if filename.endswith(".txt"):
                path = dir + filename
                with open(path, 'rb') as file:
                    poem = Poem()
                    poem.ParseFromString(file.read())
                    self.poems[poem.title] = poem

    '''
    Update a poem object within the sonnet sequence.
    '''
    def update_poem(poem):
        self.poems[poem.title] = poem

    def write(self):
        # TODO(karaschechtman)
        return None
