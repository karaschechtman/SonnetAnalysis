from proto.Poem_pb2 import *
from datamuse import datamuse

api = datamuse.Datamuse()

FOUR_SCHEMES = [[[0,3],[2,1]], [[0,2],[1,3]],[[0,1],[2,3]]]
SIX_SCHEMES = [[[0,3],[1,4],[2,5]],[[0,1],[2,5],[3,4]]]
DATAMUSE_MAX = 50

"""
Test different labeling schemes of a poem and label its rhyme groups.
::param:: poem the Poem proto to which to add the rhyme groups.
"""
def label_rhyme_groups(poem):
    # Divide and label the octave.
    words_quatrain_1 = __AddStanzaAndCollectRhymes(poem, lines[0:3])
    words_quatrain_2 = __AddStanzaAndCollectRhymes(poem, lines[4:7])
    scheme_quatrain_1, score_quatrain_1 = _LabelStanza(words_quatrain_1, FOUR_SCHEMES)
    scheme_quatrain_2, score_quatrain_2 = _LabelStanza(words_quatrain_2, FOUR_SCHEMES)
    scheme_octave = scheme_quatrain_1 if score_quatrain_1 > score_quatrain_2 else scheme_quatrain_2

    # Try dividing the sestet into a quatrain and a couplet.
    words_quatrain_3 = _CollectRhymes(lines[8:11]) # No need to label the couplet
    scheme_quatrain_3, score_quatrain_3 = _LabelStanza(words_quatrain_3, FOUR_SCHEMES)

    # Try labeling the sestet as two tercets.
    words_sestet_3 = _CollectRhymes(lines[8:])
    scheme_sestet_3, score_sestet_3 = _LabelStanza(words_sestet_3, SIX_SCHEMES)

    # Evaluate options for labeling the sestet.
    if score_sestet_3 >= score_quatrain_3:
        scheme_sestet = scheme_sestet_3
    else:
        scheme_sestet = scheme_quatrain_3 + [4,5]

    # TODO:
    # Check all the rhymegroups and see if there are
    # strong links between them

    # Create word groups.
    for group in scheme_octave:
        q1_set = RhymeSet().rhyme_indices.extend(group)
        poem.rhyme_sets.add().copyFrom(q1_set)
        q2 = [i + 4 for i in group]
        q2_set = RhymeSet().rhyme_indices.extend(q2)
        poem.rhyme_sets.add().copyFrom(q2_set)

    for group in scheme_sestet:
        s_set = RhymeSet().rhyme_indices.extend([i + 8 for i in group])
        poem.rhyme_sets.add().copyFrom(s_set)

'''
Create and add a stanza to the Poem proto and return the last words of each line.
::param:: poem the Poem proto to which to add the Lines.
::param:: lines the Line protos to add to the stanza.
::return:: a list of the rhyme words ending each line.
'''
def __AddStanzaAndCollectRhymes(poem, lines):
    stanza = Stanza()
    rhyme_words = []
    for line in lines:
        rhyme_words.append(line.text.split()[-1])
        stanza_line = stanza.lines.add()
        stanza_line.copyFrom(line)
    entity = poem.entity.add()
    entity.stanza.copyFrom(stanza_1)
    return rhyme_words

'''
Return the last words of each line passed in.
::param:: lines the Line protos from which to get words.
::return:: a list of the rhyme words ending each line.
'''
def _CollectRhymes(lines):
    for line in lines:
        rhyme_words.append(line.text.split()[-1])

'''
Choose the best possible stanza label.
::param:: words a list of the last words of each line of the stanza.
::param:: possible_schemes possible rhyme schemes for the stanza
::return:: the best scheme and the best score.
'''
def _LabelStanza(words, possible_schemes):
    best_score = 0
    best_scheme = possible_schemes[0]
    for scheme in possible_schemes:
        score = 0
        for group in possible_schemes:
            score += _Evaluate(words[group[0]], words[group[1]])
        if score > best_score:
            best_scheme, best_score = scheme, score
    return best_scheme, best_score

def _Evaluate(first_word, second_word):
    rhymes = api.words(rel_rhy=first_word, max=MAX)
    if second_word in [rhyme['word'] for rhyme in rhymes]:
        return 1
    return 0
