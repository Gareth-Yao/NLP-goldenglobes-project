To install requirements on OS/Linux:
- run: pip install -r mac_requirements.txt
To install requirements on Windows' Anaconda virtual environment:
- run: pip install -r windows_requirements.txt
- run: conda install -c conda-forge python-levenshtein

To run gg_api.py and get the human readable results as well as json results:
    Pre_ceremony downloads the actors, actresses and director list as well as movie titles list for that year.
    Have to run pre_ceremony if you run it for a new year since we have to download the movie titles for each year.
    - run preceremony: python gg_api.py pre_ceremony year
    - run main: python gg_api.py year

Please make sure the tweet json file with the year you are trying to run is in the directory. For example, put gg2018.json in this directory if you are running 2018.



Github Repo:
https://github.com/Gareth-Yao/NLP-goldenglobes-project