''' Defines common utilities for ingestion.
::author:: Kara Schechtman
::version:: 2.0
'''
import string
import sys

sys.path.append('../')

from collections import OrderedDict
from proto.Poem_pb2 import *

'''
Get the roman numeral representation of an integer.
::param:: num the integer to convert
::return:: the roman numeral representation of that numeral
'''
def GetRoman(num):
    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num > 0:
                roman_num(num)
            else:
                break

    return "".join([a for a in roman_num(num)])

'''
Generate a Poem proto from the lines of the poem, its title,
and its author. Meant for use during the ingestion process.
Will not generate stanzas.
::param:: lines the lines of the poem.
'''
def GeneratePoem(sentences, title, author, verbose):
    poem = Poem()
    poem.title = title
    poem.author = author
    j = 0
    for sentence in sentences:
        line = Line()
        line.text = _CleanLine(sentence)
        line.index = j
        j+=1
        entity = poem.entity.add()
        entity.line.CopyFrom(line)
    if verbose:
        print('Generated poem %s by %s.' % (poem.title, poem.author))
    return poem

'''
Remove superfluous punctuation and digits from a line of poetry.
::param:: line the line to clean
::return:: the cleaned line
'''
def _CleanLine(line):
    words = [x.strip().strip(string.punctuation).strip(string.digits)
             for x in line.split()]
    s = ' '.join(words)
    return s
