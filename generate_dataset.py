'''
This script generates Poem protos from scraped sonnets
and does not annotate any of the poems with useful data.
It is only meant for generating the dataset; you most likely
do not need to use it. Instead, download/use the dataset
sonnets_info with the DataLoader.

::author:: Kara Schechtman
::version:: 2.0
'''

import optparse
import os
import urllib
import sys

from bs4 import BeautifulSoup
from util.dataset_utils import *
from proto.Poem_pb2 import *

# Sidney constants.
SIDNEY = "Philip Sidney"
OLD_SIDNEY_URL = "http://www.luminarium.org/renascence-editions/stella.html"
SIDNEY_STORE = "./data/sidney_astrophil"

# Shakespeare constants.
NUM_SHAKESPEARE_POEMS = 154
SHAKESPEARE = "William Shakespeare"
SHAKESPEARE_START = 2 # first line of scraped poems
SHAKESPEARE_END = 16 # last line of scraped poems
SHAKESPEARE_URL = "http://shakespeare.mit.edu/Poetry/sonnet."
SHAKESPEARE_STORE = "./data/shakespeare_sonnets"

# Spenser constants.
NUM_SPENSER_PARTS = 3
SPENSER = "Edmund Spenser"
SPENSER_PART_URL = "http://www.theotherpages.org/poems/spenser"
SPENSER_STORE = "./data/spenser_amoretti"

# General constants.
HTML = ".html"
PARSER = "html.parser"

def IngestShakespeareSonnets():
    store = open(SHAKESPEARE_STORE, "w")
    for i in range(1, NUM_SHAKESPEARE_POEMS + 1):
        page = urllib.urlopen(SHAKESPEARE_URL + GetRoman(i) +
                               HTML)
        soup = BeautifulSoup(page, PARSER)
        lines = soup.getText().split("\n")[SHAKESPEARE_START:
                                           SHAKESPEARE_END]
        poem = GeneratePoem(lines, str(i), SHAKESPEARE)
        store.write(poem.SerializeToString() + '\n')

    store.close()

def IngestSpenserSonnets():
    store = open(SPENSER_STORE, "w")
    count = 1
    for i in range(1, NUM_SPENSER_PARTS + 1):
        url = SPENSER_PART_URL + str(i) + HTML
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page, PARSER)
        for poem in soup.select('ul dl'):
            lines = poem.getText().splitlines()[1:] # first line blank
            poem = GeneratePoem(lines, str(count), SPENSER)
            count +=1
            store.write(poem.SerializeToString() + '\n')

    store.close()

def IngestSidneySonnets():
    store = open(SIDNEY_STORE, "w")
    page = urllib2.urlopen(OLD_SIDNEY_URL)
    soup = BeautifulSoup(page, PARSER)
    count = 1
    for poem in soup.select('blockquote'):
        poem_split_first = poem.getText().splitlines()[1:-1]
        # Put together first line
        lines = [poem_split_first[0] + ' ' + poem_split_first[1]]
        for line in poem_split_first[2:]:
            lines.append(line)
        if len(lines) <= 14:
            poem = GeneratePoem(lines, str(count), SIDNEY)
            count+=1
            store.write(poem.SerializeToString() + '\n')

def main():
    parser = optparse.OptionParser()
    parser.add_option("--sidney",
                      help="Ingest Sidney's sonnets.",
                      action="store_true",
                      default=False)

    parser.add_option("--shakespeare",
                      help="Ingest Shakespeare's sonnets.",
                      action="store_true",
                      default=False)
    parser.add_option("--spenser",
                      help="Ingest Spenser's sonnets.",
                      action="store_true",
                      default=False)
    (options, args) = parser.parse_args()
    if options.sidney:
        IngestSidneySonnets()
    if options.shakespeare:
        IngestShakespeareSonnets()
    if options.spenser:
        IngestSpenserSonnets()


if __name__ == "__main__":
    main()
