from proto.Poem_pb2 import *

import networkx as nx

# Rhyme schemes.
TWO_SCHEMES = [[[0,1]]]
FOUR_SCHEMES = [[[0,3],[1,2]], [[0,2],[1,3]],[[0,1],[2,3]]]
SIX_SCHEMES = [[[0,3],[1,4],[2,5]],[[0,1],[2,5],[3,4]]]

# Stanza lengths.
COUPLET_LENGTH = 2
QUATRAIN_LENGTH = 4
SESTET_LENGTH = 6
OCTAVE_LENGTH = 8
THREE_QUATRAINS_LENGTH = 12
SONNET_LENGTH = 14

class RhymeLabeler(object):
    '''
    Predict the rhymes of poem using a variety of methods,
    and create rhyme dictionaries based on the results.
    '''

    def __init__(self, add_rhymes, rhyme_dict={}, collect_inferred=False):
        '''
        Constructor of a RhymeCalculator.
        :param add_rhyme: A mutator function to add rhymes
        to the rhyme dictionary. Takes in a word, all the
        words in a particular poem, and the rhyme_dict and
        adds the word. No return value.
        :param rhyme_dict: the initial rhyme dictionary
        used for the class. Keys are words, values are rhyme
        matches in a list.
        :param collect_inferred: if set to True, inferred
        rhymes will be added to the dictionary (if they are
        inferred with sufficient confidence).
        '''
        self.rhyme_dict = rhyme_dict
        self.collect_inferred = collect_inferred
        self.add_rhymes = add_rhymes

    @classmethod
    def from_file(cls, filename, add_rhymes,
                  collect_inferred=False):
        '''
        Constructor of a RhymeCalculator from a rhyme
        dictionary file, rather than a dictionary object.
        :param filename: the name of the file
        :param add_rhymes: A mutator function to add rhymes
        to the rhyme dictionary. Takes in all the words in
        a particular poem, and the rhyme_dict and
        adds the word. No return value.
        :param collect_inferred: if set to True, inferred
        rhymes will be added to the dictionary (if they are
        inferred with sufficient confidence).
        '''
        rhyme_dict = {}
        with open(filename, 'r') as rhyme_file:
            for line in rhyme_file.readlines():
                if line != '\n':
                    rhymes = line.split(', ')
                    rhyme_dict[rhymes[0]] = rhymes[1:]
        return cls(rhyme_dict, collect_inferred, add_rhymes)

    def export_rhyme_dict_to_file(self, filename):
        '''
        Save the rhyme dictionary of this class to a file.
        File format is a csv, with the first column of a row
        referring to the rhyme scheme.
        :param filename: the file to save to.
        '''
        with open(filename, 'w') as rhyme_file:
            for rhyme in self.rhyme_dict:
                rhyme_file.write(', '.join([rhyme] +
                                      self.rhyme_dict[rhyme]))
                rhyme_file.write('\n')

    # ------------------ SCHEME LABELING -------------------

    def _shift_rhyme_scheme(self, scheme, shift_num):
        '''
        For scheme labeling: Shift the indices of the rhyme
        scheme to match the poem.
        :param shift_num: the number by which to shift the
        indices.
        :return: the shifted rhyme scheme.
        '''
        shifted_scheme = []
        for pair in scheme:
            shifted_pair = []
            for num in pair:
                shifted_pair.append(num+shift_num)
            shifted_scheme.append(shifted_pair)
        return shifted_scheme

    def _pick_rhyme_scheme(self, words, possible_schemes):
        '''
        Helper for scheme labeling to test different scheme
        divisions and find the best one.
        :param words: a list of the last words of each line
        of the stanza.
        :param possible_schemes: possible rhyme schemes
        for the stanza.
        :return: the best scheme and the best score.
        '''
        best_score = 0
        best_scheme = possible_schemes[0]

        # Add words to the rhyme dictionary.
        self.add_rhymes(words, self.rhyme_dict)

        # Score the rhyme scheme.
        for scheme in possible_schemes:
            score = 0
            for pair in scheme:
                if (words[pair[1]] in self.rhyme_dict[words[pair[0]]]
                    or words[pair[0]] in self.rhyme_dict[words[pair[1]]]):
                    score += 1

            # Check if the best rhyme scheme.
            if score > best_score:
                best_scheme, best_score = scheme, score

        return best_scheme, best_score

    def _label_octave(self, words):
        '''
        Helper for scheme labeling: Helper to try different
        labelings of the octave, specifically: ABBA CDDC,
        ABAB CDCD, and AABB CCDD.
        :param words: the words of the last lines of the
        poem, in order.
        :return: the octave scheme.
        '''
        # Try different labelings of the quatrains.
        scheme_q1, score_q1 = self._pick_rhyme_scheme(words[0:QUATRAIN_LENGTH], FOUR_SCHEMES)
        scheme_q2, score_q2 = self._pick_rhyme_scheme(words[QUATRAIN_LENGTH:OCTAVE_LENGTH], FOUR_SCHEMES)

        # Choose the scheme with the higher rating.
        scheme_octave = scheme_q1 if score_q1 > score_q2 else scheme_q2
        return scheme_octave + self._shift_rhyme_scheme(scheme_octave, QUATRAIN_LENGTH)

    def _label_sestet(self, words):
        '''
        For scheme labeling: Helper to try different
        labelings of the sestet.
        Tries EFEF GG, EFFE GG, EE FF GG, and EFG EFG.
        :param words: the words of the last lines of the
        poem, in order.
        :return: the sestet scheme.
        '''
        # Try dividing the sestet into a quatrain and a couplet.
        scheme_quatrain_3, score_quatrain_3 = self._pick_rhyme_scheme(words[QUATRAIN_LENGTH:THREE_QUATRAINS_LENGTH], FOUR_SCHEMES)
        scheme_couplet_3, score_couplet_3 = self._pick_rhyme_scheme(words[THREE_QUATRAINS_LENGTH:], TWO_SCHEMES)
        score_q_c = score_quatrain_3 + score_couplet_3

        # Try labeling the sestet as two tercets.
        scheme_sestet_3, score_sestet_3 = self._pick_rhyme_scheme(words[OCTAVE_LENGTH:], SIX_SCHEMES)

        # Evaluate options for labeling the sestet.
        if score_sestet_3 > score_q_c:
            scheme_sestet = scheme_sestet_3
        else:
            scheme_sestet = scheme_quatrain_3 + [[4,5]]

        return self._shift_rhyme_scheme(scheme_sestet,
                                        OCTAVE_LENGTH)

    # ------------------- GROUP LABELING -------------------

    def _get_rhyme_groups(self, words):
        '''
        Helper for group labeling. Get all groups of rhymes
        based on the class rhyme dictionary.
        :param words: the words of the last lines of the poem,
        in order.
        :return: rhyme scheme.
        '''
        # Make graph.
        G = nx.Graph()
        G.add_nodes_from(range(len(words)))

        # Add edges to graph.
        self.add_rhymes(words, self.rhyme_dict)
        for i in range(len(words)):
            word = words[i]
            for j in range(len(words)):
                other_word = words[j]
                if other_word in self.rhyme_dict[word]:
                    G.add_edge(i, j)
        return [list(s) for s in list(nx.connected_components(G))]

    # ------------------ HYBRID LABELING -------------------

    def _combine_schemes(self, rhyme_scheme, rhyme_scheme_2):
        '''
        Helper for hybrid labeling. Given two rhyme schemes,
        combine them into one scheme by conglomerating
        their groups of rhymes.
        :param rhyme_scheme: the first rhyme scheme.
        :param rhyme_scheme_2: the second rhyme scheme.
        :return: the hybrid rhyme scheme.
        '''
        G = nx.Graph()
        for group in rhyme_scheme:
            for i in range(len(group)):
                for j in range(i+1, len(group)):
                    G.add_edge(group[i], group[j])

        for group in rhyme_scheme_2:
            for i in range(len(group)):
                for j in range(i+1, len(group)):
                    G.add_edge(group[i], group[j])

        return [list(s) for s in list(nx.connected_components(G))]

    # ---------------------- PREDICT -----------------------

    def label_poem_rhymes(self, poem, scheme=True, group=True):
        # TODO(karaschechtman): in hybrid,only accept scheme
        # labels with a certain level of confidence.
        '''
        Get the rhyme scheme of a poem.

        There are three options for how to do this:
        - Scheme: Assign from the best-fitting of a list of
        common sonnet rhyme schemes.
        - Group: Group based on rhymes.
        - Hybrid: Combines the results of scheme and group
        labeling.

        :param poem: the Poem proto to which to add the
        rhyme groups.
        :param scheme: set to True, the labeling will try to
        deduce the rhyme scheme from traditional sonnet
        schemes.
        :param group: set to True, the labeling will rely on
        the rhyme dictionary and map
        :return: the rhyme scheme, in the form of a list
        of lists. Each list
        '''
        lines = [entity.line for entity in poem.entity]
        words = [line.text.split()[-1] for line in lines]
        rhyme_scheme = []

        if scheme and not group:
            if len(words) == SONNET_LENGTH:
                # Divide and label the octave and sestet.
                scheme_octave = self._label_octave(words)
                scheme_sestet = self._label_sestet(words)
                rhyme_scheme = scheme_octave + scheme_sestet

        elif group and not scheme:
            rhyme_scheme = self._get_rhyme_groups(words)

        elif group and scheme:
            rhyme_scheme_1 = []
            if len(words) == SONNET_LENGTH:
                scheme_octave = self._label_octave(words)
                scheme_sestet = self._label_sestet(words)
                rhyme_scheme_1 = scheme_octave + scheme_sestet
            rhyme_scheme_2 = self._get_rhyme_groups(words)
            rhyme_scheme = self._combine_schemes(rhyme_scheme_1,
                                                 rhyme_scheme_2)

        else:
            raise ValueError("One rhyming option must be True.")

        return sorted([sorted(group) for group in rhyme_scheme],
                       key=lambda x: x[0])
