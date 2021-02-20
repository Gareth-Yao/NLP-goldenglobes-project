To install requirements on OS/Linux:
- run: pip install -r mac_requirements.txt
To install requirements on Windows' Anaconda virtual environment:
- run: pip install -r windows_requirements.txt
- run: conda install -c conda-forge python-levenshtein

Running gg_api.py. Have to run pre_ceremony every time you change the year since we have to download the movie titles.
- run preceremony: python gg_api.py pre_ceremony year
- run main: python gg_api.py year

Please make sure the tweet json file with the year you are trying to run is in the directory. For example, put gg2018.json in this directory if you are running 2018.

You only have to run precermony if you have not run the year yet.

Github Repo:
https://github.com/Gareth-Yao/NLP-goldenglobes-project