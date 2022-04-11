# Hyphe corpus script

Script based on prior work at the BnF on [project Lifranum](https://www.univ-lyon3.fr/projet-lifranum).

It requires [Python 3.9](https://www.python.org/downloads/).  
To install dependencies, I recommend using [Poetry](https://python-poetry.org), although you may rely on [pip](https://pip.pypa.io/en/stable/) alone too.

If you rely on Poetry, activate the virtual environment using the `poetry shell` command, then install all dependencies with `poetry install`.

If you rely on pip alone, create a virtual environment in a folder named `venv` with `python -m venv venv`.  
Activate it by running `venv/bin/activate` on Linux or `venv/Scripts/activate.bat` on Windows.  
Then install all dependencies with `pip install -r requirements.txt`.

The script can be launched by running `python main.py`.  
Three Python functions were written in `src/hyphe.py`. You can choose which function to launch by editing the `task` function at the bottom of `src/hyphe.py`:

* `datasprint_populate_corpus` to import sites in our 3 Hyphe corpora
* `datasprint_correct_undecided` to attempt to fix Entity status errors
* `datasprint_recrawl` to automatically launch new crawls for entities for which no pages were found
