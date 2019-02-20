from collections import defaultdict
from data_loader import DataLoader
from rhyme_labeler import RhymeLabeler
from proto.Poem_pb2 import *

import itertools
import matplotlib.pyplot as plt
import networkx as nx

class SequenceStats(object):

    def __init__(self, title, data, rhyme_labeler):
        self.title = title
        self.data = data
        self.rhyme_labeler = rhyme_labeler

    def _label_rhymes(self):
        for poem in self.data.poems.values():
            scheme = self.rhyme_labeler.get_rhyme_scheme(poem)
            for group in scheme:
                set = RhymeSet()
                set.rhyme_indices.extend(group)
                poem.rhyme_sets.add().CopyFrom(set)

    def _construct_graph(self):
        matches = defaultdict(list)
        for poem in self.data.poems.values():
            lines = [entity.line for entity in poem.entity]
            words = [line.text.split()[-1] for line in lines]
            for set in poem.rhyme_sets:
                for pair in itertools.combinations(set.rhyme_indices, r=2):
                    rhyme_pair = tuple(sorted((words[pair[0]], words[pair[1]])))
                    matches[rhyme_pair].append(poem.title)

        G = nx.Graph()
        for rhyme_pair in matches:
            poems = matches[rhyme_pair]
            for pair in itertools.combinations(poems, r=2):
                G.add_edge(*pair)
        return G

    def build(self):
        self._label_rhymes()
        self.data.write()
        G = self._construct_graph()
        nx.draw_networkx(G)
        plt.show()
