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
from fuzzywuzzy import fuzz
from collections import Counter
import nltk

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
fluff = ["a", "about", "above", "after", "again", "against", "ain", "all", "am", "an", "and", "any", "are", "aren",
         "aren't", "as", "at", "be", "because",
         "been", "before", "being", "below", "between", "both", "but", "by", "can", "couldn", "couldn't", "d", "did",
         "didn", "didn't", "do", "does", "doesn",
         "doesn't", "doing", "don", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn",
         "hadn't", "has", "hasn", "hasn't", "have",
         "haven", "haven't", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i",
         "if", "in", "into", "is", "isn", "isn't", "it",
         "it's", "its", "itself", "just", "ll", "m", "ma", "me", "mightn", "mightn't", "more", "most", "mustn",
         "mustn't", "my", "myself", "needn", "needn't", "no",
         "nor", "not", "now", "o", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out",
         "over", "own", "re", "s", "same", "shan",
         "shan't", "she", "she's", "should", "should've", "shouldn", "shouldn't", "so", "some", "such", "t", "than",
         "that", "that'll", "the", "their", "theirs",
         "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too", "under",
         "until", "up", "ve", "very", "was", "wasn",
         "wasn't", "we", "were", "weren", "weren't", "what", "when", "where", "which", "while", "who", "whom", "why",
         "will", "with", "won", "won't", "wouldn",
         "wouldn't", "y", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
         "could", "he'd", "he'll", "he's", "here's",
         "how's", "i'd", "i'll", "i'm", "i've", "let's", "ought", "she'd", "she'll", "that's", "there's", "they'd",
         "they'll", "they're", "they've", "we'd", "we'll",
         "we're", "we've", "what's", "when's", "where's", "who's", "why's", "would", "able", "abst", "accordance",
         "according", "accordingly", "across", "act",
         "actually", "added", "adj", "affected", "affecting", "affects", "afterwards", "ah", "almost", "alone", "along",
         "already", "also", "although", "always",
         "among", "amongst", "announce", "another", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway",
         "anyways", "anywhere", "apparently",
         "approximately", "arent", "arise", "around", "aside", "ask", "asking", "auth", "available", "away", "awfully",
         "b", "back", "became", "become", "becomes",
         "becoming", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "believe", "beside",
         "besides", "beyond", "biol", "brief", "briefly", "c",
         "ca", "came", "cannot", "can't", "cause", "causes", "certain", "certainly", "co", "com", "come", "comes",
         "contain", "containing", "contains", "couldnt",
         "date", "different", "done", "downwards", "due", "e", "ed", "edu", "effect", "eg", "eight", "eighty", "either",
         "else", "elsewhere", "end", "ending",
         "enough", "especially", "et", "etc", "even", "ever", "every", "everybody", "everyone", "everything",
         "everywhere", "ex", "except", "f", "far", "ff", "fifth",
         "first", "five", "fix", "followed", "following", "follows", "former", "formerly", "forth", "found", "four",
         "furthermore", "g", "gave", "get", "gets",
         "getting", "give", "given", "gives", "giving", "go", "gone", "got", "gotten", "h", "happens", "hardly", "hed",
         "hence", "hereafter", "hereby", "herein",
         "heres", "hereupon", "hes", "hi", "hid", "hither", "home", "howbeit", "however", "hundred", "id", "ie", "im",
         "immediate", "immediately", "importance",
         "important", "inc", "indeed", "index", "information", "instead", "invention", "inward", "itd", "it'll", "j",
         "k", "keep", "keeps", "kept", "kg", "km",
         "know", "known", "knows", "l", "largely", "last", "lately", "later", "latter", "latterly", "least", "less",
         "lest", "let", "lets", "like", "liked", "likely",
         "line", "little", "'ll", "look", "looking", "looks", "ltd", "made", "mainly", "make", "makes", "many", "may",
         "maybe", "mean", "means", "meantime",
         "meanwhile", "merely", "mg", "might", "million", "miss", "ml", "moreover", "mostly", "mr", "mrs", "much",
         "mug", "must", "n", "na", "name", "namely", "nay",
         "nd", "near", "nearly", "necessarily", "necessary", "need", "needs", "neither", "never", "nevertheless", "new",
         "next", "nine", "ninety", "nobody", "non",
         "none", "nonetheless", "noone", "normally", "nos", "noted", "nothing", "nowhere", "obtain", "obtained",
         "obviously", "often", "oh", "ok", "okay", "old",
         "omitted", "one", "ones", "onto", "ord", "others", "otherwise", "outside", "overall", "owing", "p", "page",
         "pages", "part", "particular", "particularly",
         "past", "per", "perhaps", "placed", "please", "plus", "poorly", "possible", "possibly", "potentially", "pp",
         "predominantly", "present", "previously",
         "primarily", "probably", "promptly", "proud", "provides", "put", "q", "que", "quickly", "quite", "qv", "r",
         "ran", "rather", "rd", "readily", "really",
         "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research",
         "respectively", "resulted", "resulting",
         "results", "right", "run", "said", "saw", "say", "saying", "says", "sec", "section", "see", "seeing", "seem",
         "seemed", "seeming", "seems", "seen", "self",
         "selves", "sent", "seven", "several", "shall", "shed", "shes", "show", "showed", "shown", "showns", "shows",
         "significant", "significantly", "similar",
         "similarly", "since", "six", "slightly", "somebody", "somehow", "someone", "somethan", "something", "sometime",
         "sometimes", "somewhat", "somewhere", "soon",
         "sorry", "specifically", "specified", "specify", "specifying", "still", "stop", "strongly", "sub",
         "substantially", "successfully", "sufficiently", "suggest",
         "sup", "sure", "take", "taken", "taking", "tell", "tends", "th", "thank", "thanks", "thanx", "thats",
         "that've", "thence", "thereafter", "thereby", "thered",
         "therefore", "therein", "there'll", "thereof", "therere", "theres", "thereto", "thereupon", "there've",
         "theyd", "theyre", "think", "thou", "though",
         "thoughh", "thousand", "throug", "throughout", "thru", "thus", "til", "tip", "together", "took", "toward",
         "towards", "tried", "tries", "truly", "try",
         "trying", "ts", "twice", "two", "u", "un", "unfortunately", "unless", "unlike", "unlikely", "unto", "upon",
         "ups", "us", "use", "used", "useful", "usefully",
         "usefulness", "uses", "using", "usually", "v", "value", "various", "'ve", "via", "viz", "vol", "vols", "vs",
         "w", "want", "wants", "wasnt", "way", "wed",
         "welcome", "went", "werent", "whatever", "what'll", "whats", "whence", "whenever", "whereafter", "whereas",
         "whereby", "wherein", "wheres", "whereupon",
         "wherever", "whether", "whim", "whither", "whod", "whoever", "whole", "who'll", "whomever", "whos", "whose",
         "widely", "willing", "wish", "within", "without",
         "wont", "words", "world", "wouldnt", "www", "x", "yes", "yet", "youd", "youre", "z", "zero", "a's", "ain't",
         "allow", "allows", "apart", "appear", "appreciate",
         "appropriate", "associated", "better", "c'mon", "c's", "cant", "changes", "clearly", "concerning",
         "consequently", "consider", "considering",
         "corresponding", "course", "currently", "definitely", "described", "despite", "entirely", "exactly", "example",
         "going", "greetings", "hello", "help",
         "hopefully", "ignored", "inasmuch", "indicate", "indicated", "indicates", "inner", "insofar", "it'd", "keep",
         "keeps", "novel", "presumably", "reasonably",
         "second", "secondly", "sensible", "serious", "seriously", "sure", "t's", "third", "thorough", "thoroughly",
         "three", "well", "wonder", "a", "about", "above",
         "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already",
         "also", "although", "always", "am", "among",
         "amongst", "amoungst", "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway",
         "anywhere", "are", "around", "as", "at", "back",
         "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
         "below", "beside", "besides", "between",
         "beyond", "bill", "both", "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con", "could",
         "couldnt", "cry", "de", "describe", "detail", "do",
         "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "empty",
         "enough", "etc", "even", "ever", "every", "everyone",
         "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for",
         "former", "formerly", "forty", "found", "four",
         "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her",
         "here", "hereafter", "hereby", "herein",
         "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc",
         "indeed", "interest", "into", "is", "it", "its",
         "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me",
         "meanwhile", "might", "mill", "mine", "more", "moreover",
         "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless",
         "next", "nine", "no", "nobody", "none",
         "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto",
         "or", "other", "others", "otherwise", "our",
         "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps", "please", "put", "rather", "re", "same",
         "see", "seem", "seemed", "seeming", "seems",
         "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some",
         "somehow", "someone", "something", "sometime",
         "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them",
         "themselves", "then", "thence", "there",
         "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third",
         "this", "those", "though", "three", "through",
         "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two",
         "un", "under", "until", "up", "upon", "us",
         "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where",
         "whereafter", "whereas", "whereby", "wherein",
         "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose",
         "why", "will", "with", "within", "without",
         "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the", "a", "c", "d", "e", "f", "g", "h",
         "i", "j", "k", "l", "m", "n", "o", "p", "q",
         "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
         "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W",
         "X", "Y", "Z", "co", "op", "research-articl", "pagecount", "cit", "ibid", "les", "le", "au", "que", "est",
         "pas", "vol", "el", "los", "pp", "u201d", "well-b",
         "http", "volumtype", "par", "0o", "0s", "3a", "3b", "3d", "6b", "6o", "a1", "a2", "a3", "a4", "ab", "ac", "ad",
         "ae", "af", "ag", "aj", "al", "an", "ao", "ap",
         "ar", "av", "aw", "ax", "ay", "az", "b1", "b2", "b3", "ba", "bc", "bd", "be", "bi", "bj", "bk", "bl", "bn",
         "bp", "br", "bs", "bt", "bu", "bx", "c1", "c2",
         "c3", "cc", "cd", "ce", "cf", "cg", "ch", "ci", "cj", "cl", "cm", "cn", "cp", "cq", "cr", "cs", "ct", "cu",
         "cv", "cx", "cy", "cz", "d2", "da", "dc", "dd",
         "de", "df", "di", "dj", "dk", "dl", "do", "dp", "dr", "ds", "dt", "du", "dx", "dy", "e2", "e3", "ea", "ec",
         "ed", "ee", "ef", "ei", "ej", "el", "em", "en",
         "eo", "ep", "eq", "er", "es", "et", "eu", "ev", "ex", "ey", "f2", "fa", "fc", "ff", "fi", "fj", "fl", "fn",
         "fo", "fr", "fs", "ft", "fu", "fy", "ga", "ge",
         "gi", "gj", "gl", "go", "gr", "gs", "gy", "h2", "h3", "hh", "hi", "hj", "ho", "hr", "hs", "hu", "hy", "i",
         "i2", "i3", "i4", "i6", "i7", "i8", "ia", "ib",
         "ic", "ie", "ig", "ih", "ii", "ij", "il", "in", "io", "ip", "iq", "ir", "iv", "ix", "iy", "iz", "jj", "jr",
         "js", "jt", "ju", "ke", "kg", "kj", "km", "ko",
         "l2", "la", "lb", "lc", "lf", "lj", "ln", "lo", "lr", "ls", "lt", "m2", "ml", "mn", "mo", "ms", "mt", "mu",
         "n2", "nc", "nd", "ne", "ng", "ni", "nj", "nl",
         "nn", "nr", "ns", "nt", "ny", "oa", "ob", "oc", "od", "of", "og", "oi", "oj", "ol", "om", "on", "oo", "oq",
         "or", "os", "ot", "ou", "ow", "ox", "oz", "p1",
         "p2", "p3", "pc", "pd", "pe", "pf", "ph", "pi", "pj", "pk", "pl", "pm", "pn", "po", "pq", "pr", "ps", "pt",
         "pu", "py", "qj", "qu", "r2", "ra", "rc", "rd",
         "rf", "rh", "ri", "rj", "rl", "rm", "rn", "ro", "rq", "rr", "rs", "rt", "ru", "rv", "ry", "s2", "sa", "sc",
         "sd", "se", "sf", "si", "sj", "sl", "sm", "sn",
         "sp", "sq", "sr", "ss", "st", "sy", "sz", "t1", "t2", "t3", "tb", "tc", "td", "te", "tf", "th", "ti", "tj",
         "tl", "tm", "tn", "tp", "tq", "tr", "ts", "tt",
         "tx", "ue", "ui", "uj", "uk", "um", "un", "uo", "ur", "ut", "va", "wa", "vd", "wi", "vj", "vo", "wo", "vq",
         "vt", "vu", "x1", "x2", "x3", "xf", "xi",
         "xj", "xk", "xl", "xn", "xo", "xs", "xt", "xv", "xx", "y2", "yj", "yl", "yr", "ys", "yt", "zi", "zz",
         "goldenglobes", "goldenglobe", "golden", "globes", "globe"]

# optimize with heap
# needs IMDB Data to filter out names/movies (may need database for this). Knowledge Base
# "X won Y" needs to find a binding list where X is a movie and Y is an award
# Needs to find a way to combine first name entries and full name entries
sentiments = {}
def get_hosts(year, data, actors):
    names = {}
    processed_data = [x for x in data if 'Host' in x['text'] or 'host' in x['text']]
    re_search = {}
    counter = 0
    for tweet in processed_data:
        print((counter / len(processed_data)) * 100)
        # text = TextBlob(tweet['text'])
        text = re.findall('[a-zA-Z0-9]+', tweet['text'])
        # text = tweet['text'].split(' ')
        split_sentence = TextBlob(' '.join(text))
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
            if noun in names.keys() or noun in actors:
                names[noun] = names.get(noun, 0) + 1
                sentiments[noun] = sentiments.get(noun, 0) + split_sentence.sentences[0].polarity * split_sentence.sentences[0].subjectivity

            n = list(names.keys())
            for name in n[:10]:
                if name.startswith(noun) and name != noun:
                    if noun in names.keys():
                        sentiments[noun] = sentiments.get(noun, 0) - split_sentence.sentences[0].polarity * \
                                           split_sentence.sentences[0].subjectivity
                    names[name] = names[name] + 1
            # if noun not in re_search.keys():
            #     re_search[noun] = heapq.nlargest(10, names, key=names.get)
            # n = re_search[noun]
        counter += 1


    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here



    # names_sorted = sorted(names.items(), key=lambda x: x[1], reverse=True)
    # sentiments_sorted_descend = sorted(sentiments.items(), key=lambda x: x[1], reverse=True)
    # sentiments_sorted_ascend = sorted(sentiments.items(), key=lambda x: x[1])
    hosts = heapq.nlargest(5, names, key=names.get)
    return hosts


def get_awards(year, data):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    awards = []
    #fluff = ["a", "an", "at", "the", "for", "if", "and", "in", "rt", "goldenglobes", "golden", "globes", "globe", "goldenglobe", "but", "i", "not", "no", "or", "then", "than", "should", "could", "would", "are", "is", "be", "am", "you", "he", "she", "they", "had", "to", "so", "can", "this", "that", "with", "on", "was", "will", "it", "did", "do", "of", "by", "his", "her", "my", "their", "there", "them", "him", "hers", "who", "what", "when", "where", "why", "how", "come", "does", "me", "mine", "go", "off", "all", "some", "many", "only", "just", "we", "us", "going", "as", "have", "same", "too", "also", "well", "like", "more", "less", "been", "want", "m", "ve", "re", "t", "co", "http", "s", "because", "again", "amp"]
    candidate_ans = {}
    processed_data = [x for x in data if "won " in x["text"] or "wins " in x["text"] or "goes to " in x["text"]]
    for tweet in processed_data:
        text = re.findall('[a-zA-Z0-9]+', tweet['text'].lower())
        try:
            f_ind = text.index("won")
            candidate = ""
            for w in text[f_ind+1:]:
                if w in fluff:
                    continue
                if len(candidate) == 0:
                    candidate = w
                else:
                    candidate = candidate + " " + w
                if "best" in candidate or "award" in candidate:
                    candidate_ans[candidate] = candidate_ans.get(candidate, 0) + 3
                else:
                    candidate_ans[candidate] = candidate_ans.get(candidate, 0) + 1
        except Exception:
            try:
                f_ind = text.index("wins")
                candidate = ""
                for w in text[f_ind+1:]:
                    if w in fluff:
                        continue
                    if len(candidate) == 0:
                        candidate = w
                    else:
                        candidate = candidate + " " + w
                    if "best" in candidate or "award" in candidate:
                        candidate_ans[candidate] = candidate_ans.get(candidate, 0) + 3
                    else:
                        candidate_ans[candidate] = candidate_ans.get(candidate, 0) + 1
            except Exception:
                try:
                    f_ind = text.index("goes")
                    candidate = ""
                    f_ind -= 1
                    while f_ind >= 0:
                        if text[f_ind] in fluff:
                            f_ind -= 1
                            continue
                        if len(candidate) == 0:
                            candidate = text[f_ind]
                        else:
                            candidate = text[f_ind] + " " + candidate
                        if "best" in candidate or "award" in candidate:
                            candidate_ans[candidate] = candidate_ans.get(candidate, 0) + 3
                        else:
                            candidate_ans[candidate] = candidate_ans.get(candidate, 0) + 1
                        f_ind -= 1
                except Exception:
                    continue

    def from_back(root, s_):
        tmp = s_[:s_.rfind(" ")]
        if tmp not in candidate_ans:
            pass
        elif candidate_ans[tmp] == candidate_ans[root]:
            del candidate_ans[tmp]
            from_back(root, tmp)

    def from_front(root, s_):
        tmp = s_[s_.find(" ")+1:]
        if tmp not in candidate_ans:
            pass
        elif candidate_ans[tmp] == candidate_ans[root]:
            del candidate_ans[tmp]
            from_front(root, tmp)

    for can in sorted(list(candidate_ans.keys()), key=len, reverse=True):
        if can not in candidate_ans:
            continue
        elif len(can.split()) > 1 and can[:can.rfind(" ")] in candidate_ans and candidate_ans[can[:can.rfind(" ")]] == candidate_ans[can]:
            del candidate_ans[can[:can.rfind(" ")]]
            from_back(can, can[:can.rfind(" ")])
            continue
        elif len(can.split()) > 1 and can[can.find(" ")+1:] in candidate_ans and candidate_ans[can[can.find(" ")+1:]] == candidate_ans[can]:
            del candidate_ans[can[can.find(" ")+1:]]
            from_front(can, can[can.find(" ")+1:])
            continue

    for k in list(candidate_ans.keys()):
        if len(k.split()) >= 8:
            del candidate_ans[k]

    cands = sorted(candidate_ans, key=candidate_ans.get, reverse=True)

    sim_score = {}
    val = 0
    for ans in cands:
        for word in ans.split():
            sim_score[word] = sim_score.get(word, 0) + (len(cands)-val)/len(cands)
        val += 1

    sim_score2 = sorted(sim_score, key=sim_score.get, reverse=True)

    for k in list(sim_score.keys()):
        if sim_score[k] < 20:
            del sim_score[k]

    def get_sim_score(c_s):
        s_ = 0
        for word in c_s:
            s_ += (1/len(c_s)) * (sim_score.get(word, 0)/len(candidate_ans))
        return s_

    def sort_help(c_):
        c_s = c_.split()
        if len(c_s) > 10 or len(c_s) <=2:
            return -1
        else:
            return candidate_ans.get(c_) + get_sim_score(c_s)

    def fuck(shmeeg):
        return len(shmeeg.split())

    heyyo = sorted(candidate_ans, key=fuck, reverse=True)

    top_n = 200

    awards = heapq.nlargest(top_n, candidate_ans, key=sort_help)

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


def get_winner(year, data, actors, actresses, directors, titles):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    sensitive_words = ['supporting', 'actor','actress','of']
    sensitive_words.append('of')
    names = {}
    winners = {}
    processed_data = [x for x in data if 'hop' not in x['text'].lower() and 'wish' not in x['text'] and 'should\'ve' not in x['text'] and
                      ('goes to' in x['text'] or 'wins' in x['text'].split() or 'won' in x['text'].split() or 'awarded' in x['text'].split() or 'receives' in x['text'].lower())]
    for tweet in processed_data:
        if 'cecil b. demille' in tweet['text'].lower():
            print('xxx')
        words = tweet['text'].split()
        words = ' '.join([x.capitalize() if x.lower() in sensitive_words else x for x in words if '@' not in x and not x == 'RT' and '#GoldenGlobe' not in x and '#goldenglobe' not in x and x != 'or'])
        words = re.compile(re.escape('movie'),re.IGNORECASE).sub('Motion Picture', words)
        words = re.compile(re.escape('tv'),re.IGNORECASE).sub('Television', words)
        words = re.compile(re.escape('in a')).sub('In A', words)

        words = re.compile(re.escape('miniseries'),re.IGNORECASE).sub('Mini-Series', words)
        # words = words.replace('supporting', 'Supporting')
        # words = words.replace('actor', 'Actor')
        # words = words.replace('actress', 'Actress')
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
                    temp = ""
                if word == '#':
                    checkHashtag = True

            if temp != "":
                capitalized_words.append(temp.lower()[1:])
            capitalized_words = list(dict.fromkeys(capitalized_words))

        awards = {}
        for noun in capitalized_words:
            if noun.lower() in OFFICIAL_AWARDS_1315:
                if 'best original score' in noun.lower():
                    print()
                if noun.lower() not in names.keys():
                    names[noun.lower()] = dict()
                awards[noun.lower()] = 500

        if len(awards.keys()) == 0:
            for noun in capitalized_words:
                if 'actor' in noun or 'actress' in noun:
                    noun = 'performance ' + noun
                if 'supporting' in noun:
                    noun = noun.replace('supporting', 'in a supporting role')


                # possible_awards = [(x,lev.setratio(x.split(' '), noun.lower().split(' ')) * 10) for x in OFFICIAL_AWARDS_1315 if lev.setratio(x.split(' '), noun.lower().split(' ')) > 0.7]
                possible_awards = [(x, fuzz.token_sort_ratio(noun.lower(), x)) for x in OFFICIAL_AWARDS_1315 if fuzz.token_sort_ratio(noun.lower(), x) > 80]

                for award in possible_awards:
                    awards[award[0]] = awards.get(award[0], 0) + award[1]

        for award in awards.keys():
            if award.lower() not in names.keys():
                names[award.lower()] = dict()

        if len(awards.keys()) != 0:
            for noun in capitalized_words:
                if 'life of pi' in noun:
                    print()
                for award in awards.keys():
                    temp = names[award]
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
                        if noun in titles.keys():
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp
                    else:
                        if noun in directors or noun in titles.keys():
                            temp[noun.lower()] = temp.get(noun.lower(), 0) + awards[award]
                            names[award] = temp
                        else:
                            for tempkey in temp.keys():
                                if noun.lower() in tempkey:
                                    temp[tempkey] = temp.get(tempkey, 0) + awards[award]
                                    names[award] = temp




    for award in names.keys():
        winners[award] = max(names[award].items(), key=lambda key : key[1])[0]
        # text = TextBlob(x['text'].lower())
        # tokens = text.tokens
        # if 'wins' in tokens or 'won' in tokens or 'goes to' in tokens or 'awarded' in tokens:
        #     processed_data.append(x)
    print(winners)
    return winners

def sentiment_analysis(year, data, actors, awards, titles):
    sentiments = {}
    counter = 0
    for tweet in data:
        print(counter/len(data) * 100)
        tweettext = tweet['text'].replace('Best', '')
        words = tweettext.split()
        words = ' '.join([x for x in words if not x.startswith('@') and not x.startswith('#') and not x == 'RT'])
        text = TextBlob(words)

        # split_sentence = ' '.join(re.findall('[a-zA-Z0-9]+', words))

        split_sentence = re.sub(r'[^A-Za-z0-9 \-]+', '', words)
        text2 = TextBlob(split_sentence)
        sentences = text.sentences
        for sentence in text2.sentences:
            if sentence.polarity == 0 or sentence.subjectivity == 0:
                continue

            split = sentence.split(' ')
            capitalized_words = []
            temp = ""
            for word in split:
                if len(word) > 0 and (word[0].isupper() or word == '-'):
                    temp += " " + word
                elif temp != "":
                    capitalized_words.append(temp.lower()[1:])
                    temp = ""
            if temp != "":
                capitalized_words.append(temp.lower()[1:])
            for noun in capitalized_words:
                if noun in sentiments.keys() or noun in actors or noun in titles:
                    sentiments[noun] = sentiments.get(noun, 0) + sentence.polarity * sentence.subjectivity
        counter += 1

    print(sentiments)

    return []


def get_presenters(year, data, directors, awards):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
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
    for award in awards:
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
            ppl = find_ppl(tweet_tokens, directors, no_words)
            real_name = award_names[str(correct_award)]
            presenters[real_name].extend(ppl)
    for award in awards:
        count = Counter(presenters[award])
        num_pres = 1 if award == 'cecil b. demille award' else 2
        pre = sorted(count.items(), key=lambda x:x[1], reverse=True)[:num_pres]
        ar = [person[0] for person in pre] 
        presenters.update({award: ar})
    return presenters


def pre_ceremony(year):
    actors_download = request.urlopen("https://datasets.imdbws.com/name.basics.tsv.gz")
    titles_download = request.urlopen("https://datasets.imdbws.com/title.basics.tsv.gz")
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''

    actors = []
    actresses = []
    directors = []
    actors_zipped = gzip.GzipFile(fileobj=actors_download)
    actors_zipped.readline()
    for line in actors_zipped:
        actor_info = line.decode('UTF-8').split('\t')
        if actor_info[1] == 'Ben Affleck':
            print(actor_info)
        if actor_info[2] == '\\N':
            continue
        if 'actor' in actor_info[4]:
            actors.append(actor_info[1].lower())
        if 'actress' in actor_info[4]:
            actresses.append(actor_info[1].lower())
        directors.append(actor_info[1].lower())

    with open('actors.txt', 'w', encoding='UTF-8') as actors_file:
        for actor in actors:
            actor = re.sub(r'[^\w\s]','', actor)
            actors_file.write('%s\n' % actor)
    with open('actresses.txt', 'w', encoding='UTF-8') as actors_file:
        for actress in actresses:
            actress = re.sub(r'[^\w\s]','', actress)
            actors_file.write('%s\n' % actress)
    with open('directors.txt', 'w', encoding='UTF-8') as actors_file:
        for director in directors:
            director = re.sub(r'[^\w\s]','', director)
            actors_file.write('%s\n' % director)

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
    with open('actresses.txt', 'r', encoding='UTF-8') as f:
        actresses = f.read().splitlines()
    with open('directors.txt', 'r', encoding='UTF-8') as f:
        directors = f.read().splitlines()
    # May be unnecessary
    # preprocessed_data = [x for x in data if '#GoldenGlobes' in x['text'] or '#goldenglobes' in x['text']]
    download_corpora.main()
    get_presenters(2014, data, directors, OFFICIAL_AWARDS_1315);
    # awards = get_awards(2013, data)
    #get_winner(2013, data, actors, actresses, directors, titles)

    #hosts = get_hosts(2013, data, actors)

    #print(hosts)
    #     # get_presenters(2013, data, actors, OFFICIAL_AWARDS_1315)
    #     # get_winner(2013, data)
    #     # get_nominees(2013, data)
    #     # sentiment_analysis(2013, data, actors, OFFICIAL_AWARDS_1315, titles)
    #sentiments_sorted_descend = sorted(sentiments.items(), key=lambda x: x[1], reverse=True)
    #sentiments_sorted_ascend = sorted(sentiments.items(), key=lambda x: x[1])
    #print(sentiments_sorted_descend)
    #print(sentiments_sorted_ascend)
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    return


if __name__ == '__main__':
    main()
