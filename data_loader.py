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
        self._dir = dir
        for filename in os.listdir(dir):
            if filename.endswith(".txt"):
                path = dir + filename
                with open(path, 'rb') as file:
                    poem = Poem()
                    poem.ParseFromString(file.read())
                    self.poems[poem.title] = poem

    '''
    Write all updated poems to memory.
    '''
    def write(self):
        for poem in self.poems.values():
            path = self._dir + poem.title + ".txt"
            with open(path, 'wb') as file:
                file.write(poem.SerializeToString())
