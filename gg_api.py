'''Version 0.35'''
import json
import sys
import textblob.download_corpora as download_corpora
from textblob import TextBlob
import heapq
from urllib import request
import gzip
import re
import Levenshtein as lev
import spacy
from os import path
from fuzzywuzzy import fuzz
from collections import Counter

from collections import OrderedDict
from nltk import FreqDist


OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama',
                        'best performance by an actress in a motion picture - drama',
                        'best performance by an actor in a motion picture - drama',
                        'best motion picture - comedy or musical',
                        'best performance by an actress in a motion picture - comedy or musical',
                        'best performance by an actor in a motion picture - comedy or musical',
                        'best animated feature film', 'best foreign language film',
                        'best performance by an actress in a supporting role in a motion picture',
                        'best performance by an actor in a supporting role in a motion picture',
                        'best director - motion picture', 'best screenplay - motion picture',
                        'best original score - motion picture', 'best original song - motion picture',
                        'best television series - drama',
                        'best performance by an actress in a television series - drama',
                        'best performance by an actor in a television series - drama',
                        'best television series - comedy or musical',
                        'best performance by an actress in a television series - comedy or musical',
                        'best performance by an actor in a television series - comedy or musical',
                        'best mini-series or motion picture made for television',
                        'best performance by an actress in a mini-series or motion picture made for television',
                        'best performance by an actor in a mini-series or motion picture made for television',
                        'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television',
                        'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy',
                        'best performance by an actress in a motion picture - drama',
                        'best performance by an actor in a motion picture - drama',
                        'best performance by an actress in a motion picture - musical or comedy',
                        'best performance by an actor in a motion picture - musical or comedy',
                        'best performance by an actress in a supporting role in any motion picture',
                        'best performance by an actor in a supporting role in any motion picture',
                        'best director - motion picture', 'best screenplay - motion picture',
                        'best motion picture - animated', 'best motion picture - foreign language',
                        'best original score - motion picture', 'best original song - motion picture',
                        'best television series - drama', 'best television series - musical or comedy',
                        'best television limited series or motion picture made for television',
                        'best performance by an actress in a limited series or a motion picture made for television',
                        'best performance by an actor in a limited series or a motion picture made for television',
                        'best performance by an actress in a television series - drama',
                        'best performance by an actor in a television series - drama',
                        'best performance by an actress in a television series - musical or comedy',
                        'best performance by an actor in a television series - musical or comedy',
                        'best performance by an actress in a supporting role in a series, limited series or motion picture made for television',
                        'best performance by an actor in a supporting role in a series, limited series or motion picture made for television',
                        'cecil b. demille award']

# optimize with heap
# needs IMDB Data to filter out names/movies (may need database for this). Knowledge Base
# "X won Y" needs to find a binding list where X is a movie and Y is an award
# Needs to find a way to combine first name entries and full name entries
sentiments = {}
dresses = {}

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    try:
        with open('directors.txt', 'r', encoding='UTF-8') as f:
            directors = f.read().splitlines()
            directors = set(directors)
        with open('gg' + str(year) + ".json") as f:
            data = json.load(f)
    except IOError or FileNotFoundError:
        print("File not found. Run Preceremony individually")
        sys.exit()
    names = {}
    processed_data = [x for x in data if 'Host' in x['text'] or 'host' in x['text'] and 'next year' not in x['text']]
    counter = 0
    freq_map = []
    for tweet in processed_data:
        text = re.sub('[^a-zA-Z0-9 ]', '', tweet['text'])
        sentence = TextBlob(text).sentences[0]
        capitalized_words = []
        temp = ""
        for word in sentence.tokens:
            if len(word) > 0 and word[0].isupper():
                temp += " " + word
            elif temp != "":
                noun = temp.lower()[1:]
                capitalized_words.append(temp.lower()[1:])
                if noun in directors:
                    sentiments[noun] = sentiments.get(noun, 0) + sentence.polarity * sentence.subjectivity
                temp = ""
        if temp != "":
            noun = temp.lower()[1:]
            if noun in directors:
                sentiments[noun] = sentiments.get(noun, 0) + sentence.polarity * sentence.subjectivity
            capitalized_words.append(temp.lower()[1:])
        names_in_tweet = [x for x in capitalized_words if x in directors and not any(y.startswith(x) and y != x for y in freq_map[:10])]
        # for x in capitalized_words:
        #         for y in sentiments.keys():
        #             if y.startswith(x) and y != x:
        #                 sentiments[y] = sentiments.get(y, 0) + sentence.polarity * sentence.subjectivity
        freq_map.extend(names_in_tweet)
    freq_map = FreqDist(freq_map)
    freq_map = freq_map.most_common(2)
    return [freq_map[0][0], freq_map[1][0]]

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    try:
        with open('gg' + str(year) + ".json") as f:
            data = json.load(f)
        with open('directors.txt', 'r', encoding='UTF-8') as f:
            directors = f.read().splitlines()
            directors = set(directors)
    except IOError or FileNotFoundError:
        print("File not found. Run Preceremony individually")
        sys.exit()
    award_words = ['best', 'motion', 'picture', 'performance', 'actor', 'actress', 'supporting', 'director', 'screenplay', 'drama', 'comedy', 'musical', 'animated', 'feature', 'film', 'foreign', 'language', 'original', 'song', 'screenplay', 'score', 'television', 'series', 'tv']
    award_fluff = ['a', 'an', 'by', 'for', 'in', 'or']
    abridged_names = {}
    full_names = {}
    bigrams = {}

    processed_data = [x for x in data if "won " in x["text"] or "wins " in x["text"] or "goes to " in x["text"] or "Won " in x["text"] or "Wins " in x["text"] or "Goes to " in x["text"]]

    for tweet in processed_data:
        s_tweet = re.findall('[a-zA-Z0-9]+', tweet["text"].lower())
        if 'dress' in tweet['text'].lower():
            textb = TextBlob(' '.join(s_tweet))
            for noun in textb.noun_phrases:
                if noun in directors:
                    dresses[noun] = dresses.get(noun, 0) + textb.sentences[0].polarity * textb.sentences[0].subjectivity
                for y in dresses.keys():
                    if y.startswith(noun) and y != noun:
                        dresses[y] = sentiments.get(y, 0) + textb.sentences[0].polarity * textb.sentences[0].subjectivity
        if "won" in s_tweet:
            s_tweet = s_tweet[s_tweet.index("won")+1:]
        elif "wins" in s_tweet:
            s_tweet = s_tweet[s_tweet.index("wins")+1:]
        elif "goes" in s_tweet:
            s_tweet = s_tweet[:s_tweet.index("goes")]
        else:
            continue
        found = False
        for i, w_ in enumerate(s_tweet):
            if w_ in award_words:
                if not found:
                    start = i
                    end = i
                    found = True
                else:
                    end = i
        name = []
        name_abr = []
        try:
            i = start
            while i <= end:
                if s_tweet[i] in award_words:
                    if s_tweet[i] == 'tv':
                        name.append('television')
                        name_abr.append('television')
                    else:
                        name.append(s_tweet[i])
                        name_abr.append(s_tweet[i])
                elif s_tweet[i] in award_fluff:
                    name.append(s_tweet[i])
                i += 1

            if len(name_abr) >= 2:
                award = ' '.join(sorted(set(name), key=lambda x: s_tweet.index(x)))
                award_abr = ' '.join(sorted(set(name_abr), key=lambda x: s_tweet.index(x)))
                if len(award_abr) >= 1:
                    if award_abr not in abridged_names:
                        abridged_names[award_abr] = [award]
                    elif award not in abridged_names[award_abr]:
                        abridged_names[award_abr].append(award)
                    full_names[award] = 1 if award not in full_names else full_names[award] + 1

                bg = []
                for i in range(len(name_abr)-1):
                    bg.append(name_abr[i] + ' ' + name_abr[i+1])

                for b_ in bg:
                    bigrams[b_] = 1 if b_ not in bigrams else bigrams[b_] + 1
        except Exception as e:
            pass
    mcbg = []
    appearances = 25
    for b_ in list(bigrams.keys()):
        if bigrams[b_] >= appearances:
            mcbg.append(b_)
    def cbg_count(a_):
        count = 0
        for b_ in mcbg:
            if b_ in a_:
                count += 1
        return count
    final_a_list = []
    for n_ in list(abridged_names.keys()):
        max_ = -1
        name_ = ''
        for award in abridged_names[n_]:
            if full_names[award] > max_:
                max_ = full_names[award]
                name_ = award
        if cbg_count(name_) >= 3:
            final_a_list.append(name_)
    final_a_list = [x for x in sorted(final_a_list, key=lambda x: len(x.split()), reverse=True) if x[:4] == "best"]
    return final_a_list


def get_nominees(year):
    with open('gg' + year + '.json') as f:
        data = json.load(f)
    with open(year + '_titles.txt', encoding='UTF-8') as f:
        titles = f.read().splitlines()
        titles = set(titles)
    with open('actors.txt', 'r', encoding='UTF-8') as f:
        actors = f.read().splitlines()
        actors = set(actors)
    with open('actresses.txt', 'r', encoding='UTF-8') as f:
        actresses = f.read().splitlines()
        actresses = set(actresses)
    with open('directors.txt', 'r', encoding='UTF-8') as f:
        directors = f.read().splitlines()
        directors = set(directors)
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    nominees = {}
    names = {}
    real_awards = []
    if year == '2013' or year == '2015':
        real_awards = OFFICIAL_AWARDS_1315
    else:
        real_awards = OFFICIAL_AWARDS_1819
    nlp = spacy.load("en_core_web_sm")
    all_stopwords = nlp.Defaults.stop_words
    all_stopwords.update(['motion picture', 'goldenglobe', 'goldenglobes', 'golden globes', 'golden globe', 'congrats', 'congratulations', 'hbo', 'tonight', 'television','showtime','definitely','yay', 'drama', 'certainly', 'musical', 'globes', 'yey'])
    sensitive_words = ['supporting', 'actor','actress','of']
    relevant_words = ['wish', 'hope', 'hoped', 'deserves', 'deserved', 'nominated', 'deserve', 'nominate', 'nominee', 'nominees', 'should', 'pick', 'picked', 'picks', 'predict', 'predicted', 'predicts', 'think', 'thinks', 'goes to']
    # processed_data = [x for x in data if 'best motion picture - drama' in x['text'] or 'Best Motion Picture - Drama' in x['text']]
    processed_data = []
    for tweet_obj in data:
        # tweet = re.sub(r'[^\w\s]','', tweet_obj['text'])
        if any(word in tweet_obj['text'] for word in relevant_words):
            processed_data.append(tweet_obj)
    # processed_data = [x for x in data if 'wish' in x['text'].lower() or 'hope' in x['text'] or 'should\'ve' in x['text'] or
    #                   ('hoped' in x['text'] or 'deserves' in x['text'].split() or 'deserved' in x['text'].split() or 'nominated' in x['text'].split() or 'nominee' in x['text'].lower())]
    for tweet in processed_data:
        words = tweet['text'].split()
        words = ' '.join([x.capitalize() if x.lower() in sensitive_words else x for x in words if '@' not in x and not x == 'RT' and '#GoldenGlobe' not in x and '#goldenglobe' not in x and x != 'or'])
        for sensitive_word in sensitive_words:
            words = re.compile(re.escape(sensitive_word), re.IGNORECASE).sub(sensitive_word.capitalize(), words)
        words = re.compile(re.escape('movie'),re.IGNORECASE).sub('Motion Picture', words)
        words = re.compile(re.escape('tv'),re.IGNORECASE).sub('Television', words)
        words = re.compile(re.escape('in a')).sub('In A', words)
        words = re.compile(re.escape('miniseries'),re.IGNORECASE).sub('Mini-Series', words)
        words = re.sub(r'[^a-zA-Z0-9#: .\-]+', ' ', words)
        textb = TextBlob(words)
        capitalized_words = []
        #if 'nominate' in tweet['text']:
            #print()
        for sentence in textb.sentences:
            # split_sentence = re.sub(r'[^A-Za-z0-9#: \-]+', ' ', sentence.raw).split()
            split_sentence = sentence.tokens
            # split_sentence = words.split()
            temp = ""
            checkHashtag = False
            for word in split_sentence:
                if checkHashtag and len(word) > 0 and word[0].isupper():
                    addedSpace = ''.join([(' ' + x) if x.isupper() else x for x in word])[1:]
                    capitalized_words.append(addedSpace.lower())
                    checkHashtag = False
                elif len(word) > 0 and (word[0].isupper() or word == '-' or word == ','):
                    temp += " " + word
                elif len(word) > 0 and word == ',':
                    continue
                elif temp != "":
                    capitalized_words.append(temp.lower()[1:])
                    if temp.lower()[1:] in directors:
                        sentiments[temp.lower()[1:]] = sentiments.get(temp.lower()[1:], 0) + sentence.polarity * \
                                           sentence.subjectivity
                    temp = ""
                if word == '#':
                    checkHashtag = True

            if temp != "":
                capitalized_words.append(temp.lower()[1:])
        capitalized_words = list(dict.fromkeys(capitalized_words))

        awards = {}
        award_phrases = []
        for noun in capitalized_words:
            if noun.lower() in real_awards:
                if noun.lower() not in names.keys():
                    names[noun.lower()] = dict()
                award_phrases.append(noun.lower())
                awards[noun.lower()] = 100

        if len(awards.keys()) == 0:
            for noun in capitalized_words:
                if 'best' not in noun:
                    continue
                temp = noun
                if 'actor' in noun or 'actress' in noun:
                    noun = 'performance ' + noun
                if 'supporting' in noun:
                    noun = noun.replace('supporting', 'in a supporting role')
                # possible_awards = [(x,lev.setratio(x.split(' '), noun.lower().split(' ')) * 10) for x in OFFICIAL_AWARDS_1315 if lev.setratio(x.split(' '), noun.lower().split(' ')) > 0.7]
                possible_awards = [(x, fuzz.token_sort_ratio(noun.lower(), x)) for x in real_awards if fuzz.token_sort_ratio(noun.lower(), x) > 60]
                for award in possible_awards:
                    award_phrases.append(temp)
                    awards[award[0]] = awards.get(award[0], 0) + award[1]

        for award in awards.keys():
            if award.lower() not in names.keys():
                names[award.lower()] = dict()

        if len(awards.keys()) != 0:
            for noun in capitalized_words:
                for award in awards.keys():
                    temp = names[award]
                    if 'actor' in award:
                        if noun in actors:
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        # elif noun not in all_stopwords and noun not in award_phrases and noun not in directors and noun.isalpha():
                        #     temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                        #     names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp
                    elif 'actress' in award:
                        if noun in actresses:
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        # elif noun not in all_stopwords and noun not in award_phrases and noun not in directors and noun.isalpha():
                        #     temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                        #     names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp
                    elif 'director' in award:
                        if noun in directors:
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        # elif noun not in all_stopwords and noun not in award_phrases and noun not in directors and noun.isalpha():
                        #     temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                        #     names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp
                    elif 'film' in award or 'motion picture' in award or 'series' in award:
                        if noun in titles:
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + 2 * awards[award]
                            names[award] = temp
                        elif noun not in all_stopwords and noun not in award_phrases and noun not in directors and noun.isalpha():
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp
                    elif award == 'cecil b. demille award':
                        if noun in directors and noun != 'cecil b demille':
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                    else:
                        if noun in directors or (noun not in all_stopwords and noun not in award_phrases):
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp
    for award in names.keys():
        nominees[award] = sorted(names[award].items(), key=lambda key : key[1])[-5:]
        nominees[award] = [x[0] for x in nominees[award]]

    for award in real_awards:
        if award not in nominees.keys():
            nominees[award] = dict()
    #print(nominees)
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    try:
        with open(year + '_titles.txt', 'r', encoding='UTF-8') as f:
            titles = f.read().splitlines()
            titles = set(titles)
        with open('actors.txt', 'r', encoding='UTF-8') as f:
            actors = f.read().splitlines()
            actors = set(actors)
        with open('actresses.txt', 'r', encoding='UTF-8') as f:
            actresses = f.read().splitlines()
            actresses = set(actresses)
        with open('directors.txt', 'r', encoding='UTF-8') as f:
            directors = f.read().splitlines()
            directors = set(directors)
        with open('gg' + str(year) + ".json") as f:
            data = json.load(f)
    except IOError or FileNotFoundError:
        print("File not found. Run Preceremony individually")
        sys.exit()
    sensitive_words = ['supporting', 'actor','actress','of']
    names = {}
    winners = {}
    real_awards = []
    if year == '2013' or year == '2015':
        real_awards = OFFICIAL_AWARDS_1315
    else:
        real_awards = OFFICIAL_AWARDS_1819
    processed_data = [x for x in data if 'hop' not in x['text'].lower() and 'wish' not in x['text'] and 'should\'ve' not in x['text'] and ('best' in x['text'].lower() or 'award' in x['text'].lower()) and
                      ('goes to' in x['text'] or 'wins' in x['text'].split() or 'won' in x['text'].split() or 'awarded' in x['text'].split() or 'receives' in x['text'].lower())]
    counter = 0
    for tweet in processed_data:
        # counter += 1
        # print((counter / len(processed_data)) * 100)
        words = tweet['text'].split()
        words = ' '.join([x.capitalize() if x.lower() in sensitive_words else x for x in words if '@' not in x and not x == 'RT' and '#GoldenGlobe' not in x and '#goldenglobe' not in x and x != 'or'])
        words = re.compile(re.escape('movie'),re.IGNORECASE).sub('Motion Picture', words)
        words = re.compile(re.escape('tv'),re.IGNORECASE).sub('Television', words)
        words = re.compile(re.escape('in a')).sub('In A', words)
        words = re.compile(re.escape('miniseries'),re.IGNORECASE).sub('Mini-Series', words)

        textb = TextBlob(words)
        capitalized_words = []
        for sentence in textb.sentences:
            # split_sentence = re.sub(r'[^A-Za-z0-9#: \-]+', ' ', sentence.raw).split()
            split_sentence = sentence.tokens
            # split_sentence = words.split()
            temp = ""
            checkHashtag = False
            for word in split_sentence:
                if checkHashtag and len(word) > 0 and word[0].isupper():
                    addedSpace = ''.join([(' ' + x) if x.isupper() else x for x in word])[1:]
                    capitalized_words.append(addedSpace.lower())

                    checkHashtag = False
                elif len(word) > 0 and (word[0].isupper() or word == '-' or word == ','):
                    temp += " " + word
                elif len(word) > 0 and word == ',':
                    continue
                elif temp != "":
                    capitalized_words.append(temp.lower()[1:])
                    if temp.lower()[1:] in directors:
                        sentiments[temp.lower()[1:]] = sentiments.get(temp.lower()[1:], 0) + sentence.polarity * \
                                           sentence.subjectivity
                    temp = ""
                if word == '#':
                    checkHashtag = True

            if temp != "":
                capitalized_words.append(temp.lower()[1:])
        capitalized_words = list(dict.fromkeys(capitalized_words))

        awards = {}

        # text = tweet['text'].split(' ')
        # sentence_sentiment = TextBlob(' '.join(re.findall('[a-zA-Z0-9]+', tweet['text'])))
        for noun in capitalized_words:
            if noun.lower() in real_awards:

                if noun.lower() not in names.keys():
                    names[noun.lower()] = dict()
                awards[noun.lower()] = 500


        if len(awards.keys()) == 0:
            for noun in capitalized_words:
                if 'best' not in noun:
                    continue
                if 'actor' in noun or 'actress' in noun:
                    noun = 'performance ' + noun
                if 'supporting' in noun:
                    noun = noun.replace('supporting', 'in a supporting role')
                # possible_awards = [(x,lev.setratio(x.split(' '), noun.lower().split(' ')) * 10) for x in OFFICIAL_AWARDS_1315 if lev.setratio(x.split(' '), noun.lower().split(' ')) > 0.7]

                possible_awards = [(x, fuzz.token_sort_ratio(noun.lower(), x)) for x in real_awards if fuzz.token_sort_ratio(noun.lower(), x) > 80]
                #if 'maggie smith' in capitalized_words:
                    #print()
                for award in possible_awards:
                    awards[award[0]] = awards.get(award[0], 0) + award[1]

        # for award in awards.keys():
        #     if award.lower() not in names.keys():
        #         names[award.lower()] = dict()

        if len(awards.keys()) != 0:
            for noun in capitalized_words:
                for award in awards.keys():
                    temp = names.get(award.lower(), dict())
                    if 'actor' in award:
                        if noun in actors:
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp
                    elif 'actress' in award:
                        if noun in actresses:
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp
                    elif 'director' in award:
                        if noun in directors:
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp
                    elif 'film' in award or 'motion picture' in award or 'series' in award:
                        if noun in titles:
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp
                    else:
                        if noun in directors or noun in titles:
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp

    for award in names.keys():
        winners[award] = max(names[award].items(), key=lambda key : key[1])[0]

    for award in real_awards:
        if award not in winners.keys():
            winners[award] = dict()
        # text = TextBlob(x['text'].lower())
        # tokens = text.tokens
        # if 'wins' in tokens or 'won' in tokens or 'goes to' in tokens or 'awarded' in tokens:
        #     processed_data.append(x)
    return winners

# def sentiment_analysis(year, data, actors, awards, titles):
#     sentiments = {}
#     counter = 0
#     for tweet in data:
#         print(counter/len(data) * 100)
#         tweettext = tweet['text'].replace('Best', '')
#         words = tweettext.split()
#         words = ' '.join([x for x in words if not x.startswith('@') and not x.startswith('#') and not x == 'RT'])
#         text = TextBlob(words)
#
#         # split_sentence = ' '.join(re.findall('[a-zA-Z0-9]+', words))
#
#         split_sentence = re.sub(r'[^A-Za-z0-9 \-]+', '', words)
#         text2 = TextBlob(split_sentence)
#         sentences = text.sentences
#         for sentence in text2.sentences:
#             if sentence.polarity == 0 or sentence.subjectivity == 0:
#                 continue
#
#             split = sentence.split(' ')
#             capitalized_words = []
#             temp = ""
#             for word in split:
#                 if len(word) > 0 and (word[0].isupper() or word == '-'):
#                     temp += " " + word
#                 elif temp != "":
#                     capitalized_words.append(temp.lower()[1:])
#                     temp = ""
#             if temp != "":
#                 capitalized_words.append(temp.lower()[1:])
#             for noun in capitalized_words:
#                 if noun in sentiments.keys() or noun in actors or noun in titles:
#                     sentiments[noun] = sentiments.get(noun, 0) + sentence.polarity * sentence.subjectivity
#         counter += 1
#
#     print(sentiments)
#
#     return []


def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    actual_award_names = []
    if year == '2013' or year == '2015':
        actual_award_names = OFFICIAL_AWARDS_1315
    else:
        actual_award_names = OFFICIAL_AWARDS_1819
    # Your code here
    try:
        with open('directors.txt', 'r', encoding='UTF-8') as f:
            directors = f.read().splitlines()
            directors = set(directors)
        with open('gg' + str(year) + ".json") as f:
            data = json.load(f)
    except IOError or FileNotFoundError:
        print("File not found. Run Preceremony individually")
        sys.exit()
    def find_award(tokens, awards):
        match, max_common = [], 0
        for award in awards:
            common = list(set(tokens) & set(award))
            if len(common) > 2 and max_common < len(common):
                max_common = len(common)
                match = award
        return None if len(match) == 0 else match
    
    def find_ppl(tokens, directors, no_words):
        common_celeb_nicknames = {'jlo':'jennifer lopez', 'schwarzenegger':'arnold schwarzenegger', 'stallone':'sylvester stallone'}
        ppl, i, n = [], 0, len(tokens)-1
        while i < n:
            if (tokens[i] in no_words and tokens[i]!='will') or (i > 1 and tokens[i-2]!='thanks' and (tokens[i-1]=='to' or tokens[i-1]=='a')):
               i+=1
               continue
            elif tokens[i] in common_celeb_nicknames:
               ppl.append(common_celeb_nicknames[tokens[i]])
            else:
                if i < n-1:
                    pp = tokens[i]+' '+tokens[i+1]
                    if pp in directors:
                        ppl.append(pp)
                        i+=2
                        continue
                if i < n-2:
                    ppp = pp + ' ' + tokens[i+2]
                    if ppp in directors:
                        ppl.append(ppp)
                        i+=3
                        continue
                if i > 1 and tokens[i-1] == 'to':
                    for d in directors:
                        if lev.distance(tokens[i], d) <= 1:
                            ppl.append(d)
                            break
                if tokens[i] in directors:
                    ppl.append(tokens[i])
            i+=1
        return ppl

    presenters, proc_data, award_names, proc_awards = {}, [], {}, []
    keywords = ['presenter','present','presents','presenters','presented']
    award_words = ['best', ' ', 'performance', '', 'award']
    nlp = spacy.load("en_core_web_sm")
    all_stopwords = nlp.Defaults.stop_words
    # look for keywords, remove punctuation, make lowercase
    for tweet_obj in data:
        tweet = re.sub(r'[^\w\s]','', tweet_obj['text']).lower()
        if any(word in tweet for word in keywords):
            if not 'not present' in tweet and not 'represent' in tweet:
                proc_data.append(tweet)
    # process award names to make easier to match
    for award in actual_award_names:
        og_award = award
        award = re.sub(r'[^\w\s]','', award).lower()
        award_tokens = award.split(' ')
        award_tokens = [word for word in award_tokens if not word in award_words and not word in all_stopwords]
        if 'television' in award_tokens:
            award_tokens.append('tv')
        if 'picture' in award_tokens:
            award_tokens.append('film')
            award_tokens.append('movie')
        award_names.update({str(award_tokens): og_award}) # maps to real award name used later for formatting
        proc_awards.append(award_tokens)
        presenters.update({og_award: []})
    no_words = ['rt']
    no_words.extend(all_stopwords)
    no_words.extend(award_words)
    no_words.extend(keywords)
    for lst in proc_awards:
        no_words.extend(lst)
    # find award and ppl in processed tweets
    for tweet in proc_data:

        tweet_tokens = [word for word in tweet.split(' ') if not word in ['', ' ']]  
        correct_award = find_award(tweet_tokens, proc_awards)
        if correct_award is not None:
            sentence = TextBlob(tweet).sentences[0]
            ppl = find_ppl(tweet_tokens, directors, no_words)
            for p in ppl:
                sentiments[p] = sentiments.get(p, 0) + sentence.polarity * \
                                               sentence.subjectivity
            real_name = award_names[str(correct_award)]
            presenters[real_name].extend(ppl)
    for award in actual_award_names:
        count = Counter(presenters[award])
        num_pres = 1 if award == 'cecil b. demille award' else 2
        pre = sorted(count.items(), key=lambda x:x[1], reverse=True)[:num_pres]
        ar = [person[0] for person in pre] 
        presenters.update({award: ar})
    return presenters


def pre_ceremony(year):
    download_corpora.main()
    actors_download = request.urlopen("https://datasets.imdbws.com/name.basics.tsv.gz")
    titles_download = request.urlopen("https://datasets.imdbws.com/title.basics.tsv.gz")
    if path.exists('actors.txt') and path.exists('actresses.txt') and path.exists('directors.txt'):
        print('Actor files already exist. Skipping download')
    else:
        actors_zipped = gzip.GzipFile(fileobj=actors_download)
        actors_zipped.readline()
        try:
            actors_file = open('actors.txt', 'w', encoding='UTF-8')
            actresses_file = open('actresses.txt', 'w', encoding='UTF-8')
            directors_file = open('directors.txt', 'w', encoding='UTF-8')
            for line in actors_zipped:
                actor_info = line.decode('UTF-8').split('\t')
                if actor_info[2] == '\\N':
                    continue
                name = re.sub(r'[^\w\s]', '', actor_info[1].lower())
                if 'actor' in actor_info[4]:
                    actors_file.write('%s\n' % name)
                if 'actress' in actor_info[4]:
                    actresses_file.write('%s\n' % name)
                directors_file.write('%s\n' % name)
        except IOError or FileNotFoundError:
            print("Cannot open file")
        finally:
            actors_file.close()
            actresses_file.close()
            directors_file.close()


    if path.exists(year + '_titles.txt'):
        print('titles file already exist. Skipping download')
        print("Pre-ceremony processing complete.")
        return
    year = int(year)
    titles_zipped = gzip.GzipFile(fileobj=titles_download)
    schema = titles_zipped.readline().decode('UTF-8').split('\t')
    schema[len(schema) - 1] = schema[len(schema) - 1][:-1]
    try:
        titles_file = open(str(year) + '_titles.txt', 'w', encoding='UTF-8')
        for line in titles_zipped:
            title_info = line.decode('UTF-8').split('\t')
            title_info[len(title_info) - 1] = title_info[len(title_info) - 1][:-1]

            try:
                if title_info[5] == '\\N' or \
                        (title_info[6] == '\\N' and (int(title_info[5]) < year - 2 or int(title_info[5]) > year)) or \
                        (title_info[6] != '\\N' and int(title_info[6]) < year - 2 or int(title_info[5]) > year) or \
                        (title_info[1] == 'tvEpisode') or 'Reality-TV' in title_info[8] or title_info[4] == 1 or \
                        title_info[2] == 'tvSpecial' or title_info[2] == 'video' or title_info[2] == 'videoGame' or \
                        title_info[2] == 'tvShort' or title_info[2] == 'short' or '\\N' in title_info[8] or 'Talk-Show' in title_info[8]:
                    continue
            except ValueError:
                continue
            titles_file.write('%s\n' % title_info[2].lower())
    except IOError or FileNotFoundError:
        print("Cannot open file")
            # title = {}
            # for i in range(len(schema)):
            #     title_info[i] = title_info[i].lower()
            #     title[schema[i]] = title_info[i]
            # titles[title['primaryTitle']] = title


        # json.dump(titles, titles_file)
    print("Pre-ceremony processing complete.")
    return
def data_exploration(year):
    titles_download = request.urlopen("https://datasets.imdbws.com/title.basics.tsv.gz")
    year = int(year)
    titles_zipped = gzip.GzipFile(fileobj=titles_download)
    schema = titles_zipped.readline().decode('UTF-8').split('\t')
    schema[len(schema) - 1] = schema[len(schema) - 1][:-1]
    titleTypes = []
    for line in titles_zipped:
        title_info = line.decode('UTF-8').split('\t')
        title_info[len(title_info) - 1] = title_info[len(title_info) - 1][:-1]
        try:
            if title_info[5] == '\\N' or \
                    (title_info[6] == '\\N' and (int(title_info[5]) < year - 2 or int(title_info[5]) > year)) or \
                    (title_info[6] != '\\N' and int(title_info[6]) < year - 2 or int(title_info[5]) > year) or \
                    (title_info[1] == 'tvEpisode') or 'Reality-TV' in title_info[8] or title_info[4] == 1 or \
                    title_info[2] == 'tvSpecial' or title_info[2] == 'video' or title_info[2] == 'videoGame' or \
                    title_info[2] == 'tvShort' or title_info[2] == 'short' or '\\N' in title_info[8] or 'Talk-Show' in title_info[8]:
                continue
        except ValueError:
            continue
        titleTypes.extend(title_info[8].split(','))
    titleTypes = list(set(titleTypes))
    print(titleTypes)

def main(year):
    #pre_ceremony(year)
    # data_exploration(year)
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    global actual_award_names
    output = {}
    
    if year == '2013' or year == '2015':
        actual_award_names = OFFICIAL_AWARDS_1315
    else:
        actual_award_names = OFFICIAL_AWARDS_1819
    hosts = get_hosts(year)
    #award_data = answer["award_data"]
    awards = get_awards(year)
    nominees = get_nominees(year)
    presenters = get_presenters(year)
    winners = get_winner(year)
    sentiments_sorted_descend = sorted(sentiments.items(), key=lambda x: x[1], reverse=True)
    sentiments_sorted_ascend = sorted(sentiments.items(), key=lambda x: x[1])
    dresses_sorted_descend = sorted(dresses.items(), key=lambda x: x[1], reverse=True)
    dresses_sorted_ascend = sorted(dresses.items(), key=lambda x: x[1])
    #print(sentiments_sorted_descend)
    #print(sentiments_sorted_ascend)
    print("Host:", ', '.join([x.title() for x in hosts]))
    output['Hosts'] = [x.title() for x in hosts]
    for award in actual_award_names:
        print("Award:", award.title())
        temp = {}
        print("Our Award Name:", max(awards, key= lambda k : fuzz.token_sort_ratio(award, k)).title())
        print("Presenters:", ', '.join([x.title() for x in presenters[award]]))
        temp['Presenters'] = [x.title() for x in presenters[award]]
        if 'performance' or 'director' in award or 'best' not in award:
            print("Nominees:", ', '.join([x.title() for x in nominees[award]]))
        else:
            print("Nominees:", ', '.join(['"' + x.title() + '"' for x in nominees[award]]))
        temp['Nominees'] = [x.title() for x in nominees[award]]
        #print("Winner:", winners[award].title())
        if 'performance' or 'director' in award or 'best' not in award:
            print("Winner:", winners[award].title())
        else:
            print("Winner:", '"' + winners[award].title() + '"')

        temp['Winner'] = winners[award].title()
        output[award.title()] = temp
        print()

    ## need to replace this with real sentiments
    print('Most Loved Person:', sentiments_sorted_descend[0][0].title())
    print('Most Hated Person:', sentiments_sorted_ascend[0][0].title())
    print('Best Dressed Person:', dresses_sorted_descend[0][0].title())
    print('Worst Dressed Person:', dresses_sorted_ascend[0][0].title())
    with open('output.json', 'w', encoding='UTF-8') as output_file:
        json.dump(output, output_file)
    return


if __name__ == '__main__':
    if sys.argv[1] == 'pre_ceremony':
        try:
            year = sys.argv[2]
            pre_ceremony(year)
        except:
            print('Please input a year after pre_ceremony')
    else:
        year = sys.argv[1]
        main(year)