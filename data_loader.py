import sys
import os
from proto.Poem_pb2 import *

'''
Load Data on Poem objects.
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
