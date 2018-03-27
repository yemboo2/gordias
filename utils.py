from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn

def penn_to_wn(tag):
    """ Convert between a Penn Treebank tag to a simplified Wordnet tag """
    if tag.startswith('N'):
        return 'n'

    if tag.startswith('V'):
        return 'v'

    if tag.startswith('J'):
        return 'a'

    if tag.startswith('R'):
        return 'r'

    return None

def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None

    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None

def phrase_similarity(phrase1, phrase2):
    """ compute the phrase similarity using Wordnet """
    # Tokenize and tag
    phrase1 = pos_tag(word_tokenize(phrase1))
    phrase2 = pos_tag(word_tokenize(phrase2))

    # Get the synsets for the tagged words
    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in phrase1]
    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in phrase2]

    # Filter out the Nones
    synsets1 = [ss for ss in synsets1 if ss]
    synsets2 = [ss for ss in synsets2 if ss]

    score, count = 0.0, 0

    # For each word in the first phrase
    for synset in synsets1:
        sim_list = list(map((lambda x: synset.path_similarity(x)), synsets2))
        if (None in sim_list) | (not sim_list):
            continue
        best_score = max(sim_list)
        score += best_score
        count += 1

    # Average the values
    if count == 0:
        return 0
    score /= count
    return score

def symmetric_phrase_similarity(phrase1, phrase2):
    """ compute the symmetric phrase similarity using Wordnet """
    return (phrase_similarity(phrase1, phrase2) + phrase_similarity(phrase2, phrase1)) / 2

def similar(phrase1, phrase2, treshold):
    if (not phrase1) | (not phrase2):
        return False

    sim1 = phrase_similarity(phrase1, phrase2)
    sim2 = phrase_similarity(phrase2, phrase1)
    sim3 = symmetric_phrase_similarity(phrase1, phrase2)

    return (sim1 > treshold) | (sim2 > treshold) | (sim3 > treshold)
