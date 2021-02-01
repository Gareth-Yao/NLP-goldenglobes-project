'''Version 0.35'''
import json
import sys
import textblob.download_corpora as download_corpora
from textblob import TextBlob
import heapq
OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

# optimize with heap
# needs IMDB Data to filter out names/movies (may need database for this). Knowledge Base
# "X won Y" needs to find a binding list where X is a movie and Y is an award
# Needs to find a way to combine first name entries and full name entries

def get_hosts(year, data):
    names = {}
    processed_data = [x for x in data if 'Host' in x['text'] or 'host' in x['text']]
    for tweet in processed_data:
        text = TextBlob(tweet['text'])
        for noun in text.noun_phrases:
            names[noun] = names.get(noun, 0) + 1

    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    names_sorted = sorted(names.items(), key=lambda x: x[1], reverse=True)
    hosts = heapq.nlargest(5, names, key=names.get)
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    awards = []

    return awards

def get_nominees(year, data):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    nominees = []
    names = {}
    processed_data = [x for x in data if 'best motion picture - drama' in x['text'] or 'Best Motion Picture - Drama' in x['text'] or 'Best Drama' in x['text']]
    for tweet in processed_data:
        text = TextBlob(tweet['text'])

        for noun in text.noun_phrases:
            names[noun] = names.get(noun, 0) + 1

    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    names_sorted = sorted(names.items(), key=lambda x: x[1], reverse=True)
    hosts = heapq.nlargest(5, names, key=names.get)
    return nominees

def get_winner(year, data):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    winners = []
    processed_data = []
    for x in data:
        text = TextBlob(x['text'].lower())
        tokens = text.tokens
        if 'wins' in tokens or 'won' in tokens or 'goes to' in tokens or 'awarded' in tokens:
            processed_data.append(x)


    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    presenters = []
    return presenters

def pre_ceremony():

    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

def main():
    with open(sys.argv[1]) as f:
        data = json.load(f)
    # May be unnecessary
    preprocessed_data = [x for x in data if '#GoldenGlobes' in x['text'] or '#goldenglobes' in x['text']]
    download_corpora.main()
    # get_hosts(2013, data)
    # get_winner(2013, data)
    get_nominees(2013, data)
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    return

if __name__ == '__main__':
    main()
