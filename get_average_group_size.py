from data_loader import DataLoader
from datamuse import datamuse
from rhyme_labeler import RhymeLabeler
import statistics

DATAMUSE_MAX = 100
api = datamuse.Datamuse()

# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def print_progress(iteration, total, prefix = '', suffix = '',
                   decimals = 1, length = 50, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def add_rhymes(words, rhyme_dict):
    for word in words:
        if word not in rhyme_dict:
            rhyme_dict[word] = [d['word'] for d in api.words(rel_rhy=word, max=DATAMUSE_MAX)]

# Create rhyme labeler.
rhyme_labeler = RhymeLabeler(add_rhymes)

# SHAKESPEARE
shakespeare_data = DataLoader("data/shakespeare_sonnets/")
group_sizes = []
i = 0
l = len(shakespeare_data.poems)
print('Shakespeare - Sonnets:')
print_progress(0, l, prefix = 'Progress:', suffix = 'Complete')
for poem in shakespeare_data.poems.values():
    groups = rhyme_labeler.label_poem_rhymes(poem)
    group_sizes += [len(group) for group in groups]
    i += 1
    print_progress(i, l, prefix = 'Progress:', suffix = 'Complete')

print('Average group size: %f' % (sum(group_sizes)/len(group_sizes)))
print('Largest group size: %d' % (max(group_sizes)))
print('Standard deviation: %f' % (statistics.stdev(group_sizes)))


# SPENSER
spenser_data = DataLoader("data/spenser_amoretti/")
group_sizes = []
l = len(spenser_data.poems)
i = 0
print('Spenser - Amoretti:')
print_progress(i, l, prefix = 'Progress:', suffix = 'Complete')
for poem in spenser_data.poems.values():
    groups = rhyme_labeler.label_poem_rhymes(poem)
    group_sizes += [len(group) for group in groups]
    i += 1
    print_progress(i, l, prefix = 'Progress:', suffix = 'Complete')

print('Average group size: %f' % (sum(group_sizes)/len(group_sizes)))
print('Largest group size: %d' % (max(group_sizes)))
print('Standard deviation: %f' % (statistics.stdev(group_sizes)))

# SIDNEY
sidney_data = DataLoader("data/sidney_astrophil/")
group_sizes = []
i = 0
l = len(sidney_data.poems)
print('Sidney - Astrophil:')
print_progress(0, l, prefix = 'Progress:', suffix = 'Complete')
for poem in sidney_data.poems.values():
    groups = rhyme_labeler.label_poem_rhymes(poem)
    group_sizes += [len(group) for group in groups]
    i += 1
    print_progress(i, l, prefix = 'Progress:', suffix = 'Complete')

print('Average group size: %f' % (sum(group_sizes)/len(group_sizes)))
print('Largest group size: %d' % (max(group_sizes)))
print('Standard deviation: %f' % (statistics.stdev(group_sizes)))
