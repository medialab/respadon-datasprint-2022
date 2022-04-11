#coding:utf-8
from pathlib import Path
from typing import Literal, Union, Sequence

class PathsConfig:
    ######
    # All paths are relative to the current directory, e.g the corpus builder root
    START_DIRECTORY = Path(".") 
    # The data directory contains starting CSV files
    DATA_DIRECTORY = START_DIRECTORY / "data"
    # The data directory contains resulting files
    RESULTS_DIRECTORY = START_DIRECTORY / "results"

    ######
    # Logs are displayed both to stdout and to a log file
    LOG_FILEPATH = START_DIRECTORY / "script.log" 
    # Raw LIFRANUM start URLs
    # Rules to gather URLs by platform
    PLATFORM_RULES_FILEPATH = DATA_DIRECTORY / "platform_rules.csv" 

    DATASPRINT_SOURCE = DATA_DIRECTORY / "datasprint_urls.csv"
    DATASPRINT_SOURCE_OTHER = DATA_DIRECTORY / "datasprint_other_urls.csv"

    PROBLEMATIC_URLS_FILEPATH = RESULTS_DIRECTORY / "problematic_urls.txt"


class BCWebConfig:
    PATH_SCOPES = ("chemin", "page + 2 clics", "page + 1 actu", "vidéo", "websocial")
    DOMAIN_SCOPES = ("domaine", "hôte")
    SCOPES = PATH_SCOPES + DOMAIN_SCOPES + ("",)

class VariousConfig:
    DEFAULT_PLATFORM = "Nom de domaine distinct"

class HypheConfig:
    contextual_platforms = ("Amazon", "Babelio", "Wikipedia", "Ebooks publie.net", "Wikisource")
    social_media_platforms = ("Instagram", "Twitter", "YouTube", "Dailymotion", "LinkedIn", "Facebook", "Gravatar")
    inactivity_delay = 30
    request_delay = 1.0
    gateway_timeout_max_retries = 3
    use_proxy = False
    use_nemo = False
    proxy_settings = {"http":"http://example.com"}
    api_url_nemo = "http://example.com/hyphe-api/"
    api_url_scpo = "http://archivesinternetrecherche.bnf.fr/hyphe-api/"
    api_url_archives = "http://archivesinternetrecherche.bnf.fr/hyphe-api/"
    api_url_live = "https://hyphe.medialab.sciences-po.fr/respadon-sprint/api/"


class Config:
    
    def __init__(self) -> None:
        self.paths = PathsConfig
        self.bcweb = BCWebConfig
        self.various = VariousConfig
        self.hyphe = HypheConfig

config = Config()
