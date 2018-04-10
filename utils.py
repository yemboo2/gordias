# utils.py
# gordias
# By Markus Ehringer
# Date: 05.04.2018

import json
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
from googletrans import Translator

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

def similar(phrase1, phrase2, threshold):
    sim1 = phrase_similarity(phrase1, phrase2)
    sim2 = phrase_similarity(phrase2, phrase1)
    sim3 = symmetric_phrase_similarity(phrase1, phrase2)
    
    return (sim1 > threshold) | (sim2 > threshold) | (sim3 > threshold)

def sim(phrase1, phrase2, threshold):
    if ((not phrase1) | (not phrase2)):
        return False

    translator = Translator()
    phrase1_trans = translator.translate(phrase1)
    phrase2_trans = translator.translate(phrase2)

    return (similar(phrase1_trans.origin, phrase2_trans.origin, threshold) | 
        similar(phrase1_trans.text, phrase2_trans.origin, threshold) |
        similar(phrase1_trans.origin, phrase2_trans.text, threshold) |
        similar(phrase1_trans.text, phrase2_trans.text, threshold) |
        (phrase1.lower() in phrase2.lower()) | (phrase2.lower() in phrase1.lower()))

def description_orga_sim(description, organization, threshold):
    if not description:
        return False
    
    try:
        translator = Translator()
        description_trans = translator.translate(description)
        organization_trans = translator.translate(organization)
        return (sim(description, organization, threshold) |
            (organization_trans.origin.lower() in description_trans.origin.lower()) |
            (organization_trans.text.lower() in description_trans.origin.lower()) |
            (organization_trans.origin.lower() in description_trans.text.lower()) |
            (organization_trans.text.lower() in description_trans.text.lower()))
    except json.decoder.JSONDecodeError:
        return sim(description, organization, threshold)

def keyword_in_description(description = ""):
    keyword_list = ["blockchain", "bitcoin"]

    for keyword in keyword_list:
        if keyword in description.lower():
            return True
    return False