#coding:utf-8
from typing import Any, Mapping, Optional, Sequence, Tuple, Union
from urllib.parse import urlunparse, urlparse
from .structures import PlatformRule, Url
import logging, re


logger = logging.getLogger(f"corpus_builder.{__name__}")
LRU_BLOGSPOT_HANDLER = re.compile(r"^s:([a-zA-Z]+)\|h:([^\|]+)\|h:blogspot\|(.+)")

def ensure_lru_handle_blogspot(lru:str) -> str:
    return LRU_BLOGSPOT_HANDLER.sub(r"s:\1|h:blogspot.\2|\3", lru, count=1)

def get_lru_from_sitename(sitename:str, https:bool = True, www:bool = False) -> str:
    parsed = urlparse(f"//{sitename}")
    lru = "s:https|" if https else "s:http|"
    lru += "".join(f"h:{domain}|" for domain in reversed(parsed.netloc.split(".")))
    if www:
        lru += "h:www|"
    lru += "".join(f"p:{folder}|" if folder else "" for folder in parsed.path.split("/") if parsed.path.strip())
    lru += f"q:{parsed.query}|" if parsed.query else ""
    lru += f"f:{parsed.fragment}|" if parsed.fragment else ""
    return ensure_lru_handle_blogspot(lru)

