#coding:utf-8
from collections import defaultdict
from typing import cast, Generic, Mapping, Pattern, Sequence, Tuple, Optional, TypeVar, Iterator, ClassVar, Literal, Union
from typing_extensions import TypedDict
from urllib.parse import urlparse, urlunparse, ParseResult
import dataclasses, logging

logger = logging.getLogger(f"corpus_builder.{__name__}")

ScopeDomain = Literal["domaine"]
ScopeHost = Literal["hôte"]
Scope2Clicks = Literal["page + 2 clics"]
Scope1ClickActu = Literal["page + 1 actu"]
ScopePath = Literal["chemin"]
ScopeVideo = Literal["vidéo"]
ScopeSocial = Literal["websocial"]
ScopeEmpty = Literal[""]
BCWebScope = Union[ScopeDomain, ScopeHost, Scope2Clicks, Scope1ClickActu, ScopeVideo, ScopeSocial, ScopeEmpty]


@dataclasses.dataclass
class Url:
    string: str
    domain_name: str #Domain name (without "www")
    key_url: str #URL without the protocol ("http://" or "https://") and without "www"
    parts: ParseResult

    def __hash__(self) -> int:
        return hash((self.string, self.domain_name, self.key_url, self.parts))


@dataclasses.dataclass
class PlatformRule:
    segment:str
    name:str
    regex_string:str
    regex:Pattern[str]

    def is_path_significant(self) -> bool:
        return self.segment == "Domain+Path"


EntityStatus = Union[Literal["IN"], Literal["OUT"], Literal["UNDECIDED"], Literal["DISCOVERED"]]
CrawlingStatus = Union[Literal["CRAWLED"], Literal["UNCRAWLED"], Literal["RUNNING"]]


class TagsDict(TypedDict, total=False):
    USER: Mapping[str, Sequence[str]]


class EntityLight(TypedDict):
    status: EntityStatus
    prefixes:Sequence[str]
    undirected_degree:int
    indegree:int
    outdegree:int
    _id:int
    name:str

class EntitySemilight(EntityLight):
    pages_total:int
    crawling_status: CrawlingStatus
    tags: TagsDict
    creation_date:int
    crawled:bool
    last_modification_date: int
    pages_crawled:int
    homepage: str

class EntityFull(EntitySemilight):
    startpages:Sequence[str]

Entity = Union[EntityLight, EntitySemilight, EntityFull]
E = TypeVar("E", EntityLight, EntitySemilight, EntityFull)


class HypheJob(TypedDict):
    nb_links: int
    _id: str
    crawled_at: int
    crawling_status: CrawlingStatus
    finished_at: int
    created_at: int
    indexing_status: str
    webentity_id: int
    scheduled_at: int
    nb_crawled_pages:int

class EntityPage(TypedDict):
    url:str
    crawled:bool
    lru: str

PageLink = tuple[str, str, int]

class EntitiesListPage(TypedDict):
    count:int
    total_results:int
    webentities: list[Entity]
    token:str
    page:int
    last_page:int
    previous_page:Optional[int]
    next_page:Optional[int]
