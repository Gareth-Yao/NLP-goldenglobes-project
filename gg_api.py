'''Version 0.35'''
import json
import sys
import textblob.download_corpora as download_corpora
from textblob import TextBlob
import heapq
from urllib import request
import gzip
import re


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

def get_hosts(year, data, actors):
    names = {}
    processed_data = [x for x in data if 'Host' in x['text'] or 'host' in x['text']]
    re_search = {}
    for tweet in processed_data:
        # text = TextBlob(tweet['text'])
        text = tweet['text'].split(' ')
        capitalized_words = []
        temp = ""
        for word in text:
            if len(word) > 0 and word[0].isupper():
                temp += " " + word
            elif  temp != "":
                capitalized_words.append(temp.lower()[1:])
                temp = ""
        if temp != "":
            capitalized_words.append(temp.lower()[1:])
        for noun in capitalized_words:
            # if noun not in re_search.keys():
            #     # p = re.compile('^' + noun + '.*')
            #     # filtered_actors = list(filter(p.match, actors))
            #     filtered_actors = [x for x in actors if x.startswith(noun)]
            #     re_search[noun] = filtered_actors
            # filtered_actors = re_search[noun]
            # for name in filtered_actors:
            #     names[name] = names.get(name, 0) + 1
            if noun in actors:
                names[noun] = names.get(noun, 0) + 1
            # if noun not in re_search.keys():
            #     re_search[noun] = heapq.nlargest(10, names, key=names.get)
            # n = re_search[noun]
            n = list(names.keys())
            for name in n[:10]:
                if name.startswith(noun):
                    names[name] = names[name] + 1

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
    # processed_data = [x for x in data if 'best motion picture - drama' in x['text'] or 'Best Motion Picture - Drama' in x['text']]
    processed_data = data
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


def pre_ceremony(year):
    actors_download = request.urlopen("https://datasets.imdbws.com/name.basics.tsv.gz")
    titles_download = request.urlopen("https://datasets.imdbws.com/title.basics.tsv.gz")
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''

    actors = []
    actors_zipped = gzip.GzipFile(fileobj=actors_download)
    actors_zipped.readline()
    for line in actors_zipped:
        actor_info = line.decode('UTF-8').split('\t')
        if(actor_info[1] == 'Tina Fey'):
            print(actor_info)
        if actor_info[2] == '\\N':
            continue
        actors.append(actor_info[1].lower())
    with open('actors.txt', 'w', encoding='UTF-8') as actors_file:
        for actor in actors:
            actors_file.write('%s\n' % actor)

    # titles = {}
    # titles_zipped = gzip.GzipFile(fileobj=titles_download)
    # schema = titles_zipped.readline().decode('UTF-8').split('\t')
    # schema[len(schema) - 1] = schema[len(schema) - 1][:-1]
    # trial = ["zero dark thirty", "lincoln", "silver linings playbook", "argo", "the best exotic marigold hotel",
    #          "moonrise kingdom", "salmon fishing in the yemen", "silver linings playbook", "the girl",
    #          "hatfields & mccoys", "the hour", "political animals"]
    # for line in titles_zipped:
    #     title_info = line.decode('UTF-8').split('\t')
    #     title_info[len(title_info) - 1] = title_info[len(title_info) - 1][:-1]
    #
    #     try:
    #         if title_info[5] == '\\N' or \
    #                 (title_info[6] == '\\N' and (int(title_info[5]) < year - 2 or int(title_info[5]) > year)) or \
    #                 (title_info[6] != '\\N' and int(title_info[6]) < year - 2 or int(title_info[5]) > year) or \
    #                 (title_info[1] == 'tvEpisode'):
    #             continue
    #     except ValueError:
    #         continue
    #
    #     title = {}
    #     for i in range(len(schema)):
    #         title_info[i] = title_info[i].lower()
    #         title[schema[i]] = title_info[i]
    #     titles[title['primaryTitle']] = title
    #
    #
    # for entry in trial:
    #     if entry not in titles.keys():
    #         print(entry)
    #
    # with open('titles.json', 'w', encoding='UTF-8') as titles_file:
    #     json.dump(titles, titles_file)
    print("Pre-ceremony processing complete.")
    return


def main():
    with open(sys.argv[1]) as f:
        data = json.load(f)
    # pre_ceremony(2013)
    with open('titles.json', encoding='UTF-8') as f:
        titles = json.load(f)
    with open('actors.txt', 'r', encoding='UTF-8') as f:
        actors = f.read().splitlines()
    # May be unnecessary
    # preprocessed_data = [x for x in data if '#GoldenGlobes' in x['text'] or '#goldenglobes' in x['text']]
    download_corpora.main()
    hosts = get_hosts(2013, data, actors)
    print(hosts)
    # get_winner(2013, data)
    # get_nominees(2013, data)
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    return


if __name__ == '__main__':
    main()
