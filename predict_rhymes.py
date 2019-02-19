from proto.Poem_pb2 import *
from datamuse import datamuse

import networkx as nx

api = datamuse.Datamuse()

# Rhyme schemes.
TWO_SCHEMES = [[[0,1]]]
FOUR_SCHEMES = [[[0,3],[1,2]], [[0,2],[1,3]],[[0,1],[2,3]]]
SIX_SCHEMES = [[[0,3],[1,4],[2,5]],[[0,1],[2,5],[3,4]]]
DATAMUSE_MAX = 100

# Rhymes from Datamuse.
# Stored statically to minimize API calls.
rhymes = {}

'''
Return the last words of each line passed in.
:param lines: the Line protos from which to get words.
:return: a list of the rhyme words ending each line.
'''
def _collect_rhymes(lines):
    rhyme_words = []
    for line in lines:
        rhyme_words.append(line.text.split()[-1])
    return rhyme_words

"""
Helper to try different labelings of the octave.
Tries ABBA CDDC, ABAB CDCD, and AABB CCDD.
"""
def _label_octave(lines):
    # Try different labelings of the quatrains.
    words_quatrain_1 = _collect_rhymes(lines[0:4])
    words_quatrain_2 = _collect_rhymes(lines[4:8])
    scheme_quatrain_1, score_quatrain_1 = _test_rhyme_scheme(words_quatrain_1, FOUR_SCHEMES)
    scheme_quatrain_2, score_quatrain_2 = _test_rhyme_scheme(words_quatrain_2, FOUR_SCHEMES)

    # Choose the scheme with the higher rating.
    scheme_octave = scheme_quatrain_1 if score_quatrain_1 > score_quatrain_2 else scheme_quatrain_2
    return scheme_octave + _shift_rhyme_scheme(scheme_octave, 4)

"""
Helper to try different labelings of the sestet.
Tries EFEF GG, EFFE GG, EEFFGG, and EFG EFG.
"""
def _label_sestet(lines):
    # Try dividing the sestet into a quatrain and a couplet.
    words_quatrain_3 = _collect_rhymes(lines[8:12])
    words_couplet_3 = _collect_rhymes(lines[12:])
    scheme_quatrain_3, score_quatrain_3 = _test_rhyme_scheme(words_quatrain_3, FOUR_SCHEMES)
    scheme_couplet_3, score_couplet_3 = _test_rhyme_scheme(words_couplet_3, TWO_SCHEMES)
    score_c_q = score_quatrain_3 + score_couplet_3

    # Try labeling the sestet as two tercets.
    words_sestet_3 = _collect_rhymes(lines[8:])
    scheme_sestet_3, score_sestet_3 = _test_rhyme_scheme(words_sestet_3, SIX_SCHEMES)

    # Evaluate options for labeling the sestet.
    if score_sestet_3 > score_c_q:
        scheme_sestet = scheme_sestet_3
    else:
        scheme_sestet = scheme_quatrain_3 + [[4,5]]

    return _shift_rhyme_scheme(scheme_sestet, 8)

"""
Shift the indices of the rhyme scheme to match the poem.
:param shift_num: the number by which to shift the indices.
"""
def _shift_rhyme_scheme(scheme, shift_num):
    shifted_scheme = []
    for pair in scheme:
        shifted_pair = []
        for num in pair:
            shifted_pair.append(num+shift_num)
        shifted_scheme.append(shifted_pair)
    return shifted_scheme

'''
For scheme labeling: test traditional rhyme scheme divisions.
:param words: a list of the last words of each line of the stanza.
:param possible_schemes: possible rhyme schemes for the stanza
:return: the best scheme and the best score.
'''
def _test_rhyme_scheme(words, possible_schemes):
    best_score = 0
    best_scheme = possible_schemes[0]

    # Add to rhyme dictionary, if necessary.
    for word in words:
        if word not in rhymes:
            rhymes[word] = [d['word'] for d in api.words(rel_rhy=word, max=DATAMUSE_MAX)]

    for scheme in possible_schemes:
        # Score the rhyme scheme.
        score = 0
        for pair in scheme:
            if words[pair[1]] in rhymes[words[pair[0]]]:
                score += 1
            if words[pair[0]] in rhymes[words[pair[1]]]:
                score += 1
        # Check if the best rhyme scheme.
        if score > best_score:
            best_scheme, best_score = scheme, score

    return best_scheme, best_score

'''
For group labeling: get all groups of rhymes based on a
rhyme dictionary.
:param lines: the lines of the poem.
:return: rhyme groups.
'''
def _get_rhyme_groups(lines):
    # Make graph.
    words = _collect_rhymes(lines)
    G = nx.Graph()
    G.add_nodes_from(range(len(words)))

    # Add edges
    for i in range(len(words)):
        word = words[i]
        if word not in rhymes:
            rhymes[word] = [d['word'] for d in api.words(rel_rhy=word, max=DATAMUSE_MAX)]
        for j in range(len(words)):
            other_word = words[j]
            if other_word in rhymes[word]:
                G.add_edge(i, j)
    return [list(s) for s in list(nx.connected_components(G))]

'''
For hybrid labeling: merge rhyme groups. 
'''
def _combine_groups(rhyme_groups, rhyme_groups_2):
    G = nx.Graph()
    for group in rhyme_groups:
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                G.add_edge(group[i], group[j])

    for group in rhyme_groups_2:
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                G.add_edge(group[i], group[j])

    return [list(s) for s in list(nx.connected_components(G))]

"""
Label a poem's rhyme groups by determining the indices of
lines that rhyme with one another.
There are three methods:
- Scheme: Assign from the best-fitting of a list of common partitions.
- Group: Group based on rhymes.
- Blended: Start with scheming and fall back to grouping.

:param poem: the Poem proto to which to add the rhyme groups.
:param scheme: set to True, the labeling will try to deduce the rhyme scheme.
:param group: set to True, the labeling will match all lines that rhyme.
"""
def predict_poem_rhyme_groups(poem, scheme=True, group=True):
    lines = [entity.line for entity in poem.entity]
    rhyme_groups = []

    if scheme and not group:
        if len(lines) == 14: # Method will not work if not.
            # Divide and label the octave and sestet.
            scheme_octave = _label_octave(lines)
            scheme_sestet = _label_sestet(lines)
            rhyme_groups = scheme_octave + scheme_sestet

    elif group and not scheme:
        rhyme_groups = _get_rhyme_groups(lines)

    elif group and scheme:
        scheme_octave = _label_octave(lines)
        scheme_sestet = _label_sestet(lines)
        if len(lines) == 14:
            rhyme_groups = scheme_octave + scheme_sestet
        rhyme_groups_2 = _get_rhyme_groups(lines)
        rhyme_groups = _combine_groups(rhyme_groups, rhyme_groups_2)

    else:
        raise ValueError("scheme, group, or both must be True.")

    return rhyme_groups
