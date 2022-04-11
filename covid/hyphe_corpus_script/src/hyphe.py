#coding:utf-8
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, cast, ClassVar, Dict, Generic, Literal, Mapping, Optional, Sequence, TypeVar, Union, NamedTuple
from .config import config
from .loaders import get_platform_rules_as_both, find_platform_of_url, get_datasprint_urls, get_datasprint_other_urls
from .structures import Url, Entity, EntityLight, EntitySemilight, EntityFull, EntityStatus, HypheJob, TagsDict , EntitiesListPage
from .lru_converter import get_lru_from_sitename
import json, logging, requests, time, math
logger = logging.getLogger(f"corpus_builder.{__name__}")
API_URL = config.hyphe.api_url_nemo if config.hyphe.use_nemo else config.hyphe.api_url_scpo
CrawlRoutine = Union[Literal["wp"], Literal["full_corpus"]]

F = TypeVar("F", bound=Callable[..., Any])

def rate_limited(delay:float) -> Callable[[F], F]:

    def decorate(function:F) -> F:
        time_last:list[float] = [0.0]

        def wrapper(corpus_name:str, method_name:str, allowed_errors:Optional[Mapping[str,str]] = None, as_bool:bool = False, raise_on_fail:bool = False, api_url:str = API_URL, **kwargs:Any) -> Any:
            time_current = time.time()
            time_elapsed = time_current - time_last[0]
            if time_elapsed < delay:
                time_remaining = delay - time_elapsed
                logger.debug(f"Only {time_elapsed:.2f}s have passed, waiting for {time_remaining:.2f}s...")
                time.sleep(time_remaining)
            logger.debug("Enough time has passed, launching the request")
            time_last[0] = time.time()
            value = function(corpus_name=corpus_name, method_name=method_name, allowed_errors=allowed_errors, as_bool=as_bool, raise_on_fail=raise_on_fail, api_url=api_url, **kwargs)
            return value
        return cast(F, wrapper)
    return decorate

class GatewayTimeoutError(ValueError):
    pass

class ResponseFail(ValueError):
    pass

def any_attempts_left(attempts_count:int, wait_duration:float = 3.0) -> bool:
    if attempts_count >= config.hyphe.gateway_timeout_max_retries:
        return False
    logger.warning(f"There are still attempts left, sleeping for a bit before retrying")
    time.sleep(wait_duration)
    return True

def retry_on_gateway_timeout(function:F) -> F:
    def wrapper(corpus_name:str, method_name:str, allowed_errors:Optional[Mapping[str,str]] = None, as_bool:bool = False, raise_on_fail:bool = False, api_url:str = API_URL, **kwargs:Any) -> Any:
        attempts_count = 0
        while attempts_count < config.hyphe.gateway_timeout_max_retries:
            try:
                value = function(corpus_name=corpus_name, method_name=method_name, allowed_errors=allowed_errors, as_bool=as_bool, raise_on_fail=raise_on_fail, api_url=api_url, **kwargs)
            except GatewayTimeoutError as error:
                logger.warning(f"Got a gateway timeout error at attempt no {attempts_count}")
                attempts_count += 1
                if any_attempts_left(attempts_count):
                    continue
                logger.error(f"No attempts left to retry after getting this error")
                raise error from error
            except requests.exceptions.ProxyError as proxy_error:
                logger.warning(f"Got a proxy error at attempt no {attempts_count}")
                attempts_count += 1
                if any_attempts_left(attempts_count, wait_duration=5.0):
                    continue
                logger.error(f"No attempts left to retry after getting this error")
                raise proxy_error from proxy_error
            else:
                return value
    return cast(F, wrapper)

@retry_on_gateway_timeout
@rate_limited(config.hyphe.request_delay)
def request_api(corpus_name:str, method_name:str, allowed_errors:Optional[Mapping[str,str]] = None, as_bool:bool = False, raise_on_fail:bool = False, api_url:str = API_URL, **kwargs:Any) -> Any:
    if allowed_errors is None:
        allowed_errors = {}
    corpus_name_param_name = "name" if method_name == "create_corpus" else "corpus"
    req:Dict[str, Any] = {}
    req["method"] = method_name
    req["params"] = dict(kwargs) | {corpus_name_param_name:corpus_name}
    proxies:Optional[Mapping] = None
    if config.hyphe.use_proxy:
        proxies = config.hyphe.proxy_settings
    response_raw = requests.post(api_url, json=req, proxies=proxies)
    if response_raw.status_code in (504,502) and response_raw.reason.lower() in ("gateway time-out", "bad gateway"):
        raise GatewayTimeoutError(f"With req {req}, got a {response_raw.status_code} {response_raw.reason}: {response_raw.text}")
    try:
        response_maybe = response_raw.json()
    except json.JSONDecodeError as error:
        logger.exception(f"JSON decode error for req {req} with response {response_raw} (code {response_raw.status_code}, text {response_raw.text}: {error}")
        breakpoint()
    else:
        if isinstance(response_maybe, Mapping) and "fault" in response_maybe:
            logger.info(response_maybe)
            raise ValueError(f"Error in the response: {response_maybe}, from request {req}")
        response:Mapping = response_maybe[0]
        if (code := response.get("code", None)) is None:
            raise ValueError(f"Unexpected response from Hyphe: {response}, from request {req}")
        elif code == "fail" and isinstance(response["message"], Mapping) and response["message"]["message"] == "Corpus is not started" and response["message"].get("corpus_id", "") == corpus_name:
            logger.error(f"Corpus {corpus_name} wasn't started; starting it again before launching another request")
            start_corpus(corpus_name)
            return request_api(corpus_name, method_name, allowed_errors=allowed_errors, as_bool=as_bool, **kwargs)
        elif code == "fail":
            for error_msg in allowed_errors:
                if error_msg in response["message"]:
                    if as_bool:
                        return (False, allowed_errors[error_msg], response["message"])
                    else:
                        return response["message"]
            error_msg = f"Request {req} failed with {response['message']}"
            logger.error(error_msg)
            if raise_on_fail:
                raise ResponseFail(error_msg)
            else:
                breakpoint()
        elif code == "success":
            if as_bool:
                return (True, None, response["result"])
            else:
                return response["result"]


def declare_webentity_by_lru(corpus_name:str, lru_prefix:str, status:EntityStatus, name:Optional[str] = None, startpages:Optional[Sequence[str]] = None,
        lru_variations:bool = True, tags:Optional[TagsDict] = None,
        api_url:str = API_URL) -> Optional[int]:
    params:dict[str,Any] = {"lru_prefix":lru_prefix, "status":status, "lruVariations":lru_variations}
    if name is not None:
        params["name"] = name
    if startpages is not None:
        params["startpages"] = startpages
    if tags is not None:
        params["tags"] = tags
    ok, details, response = request_api(corpus_name, "store.declare_webentity_by_lru", allowed_errors={"prefixes were already set":"prefixes"}, as_bool=True, api_url=api_url, **params)
    if not ok and details == "prefixes":
        logger.error(f"Prefixes were already set for {name}")
        return None
    elif not ok:
        raise ValueError(f"Unexpected exit while trying to add site of LRU prefix {lru_prefix} with {details}")
    _id:int = response["id"]
    return _id

def crawl_webentity(corpus_name:str, entity_id:int, depth:int) -> str:
    response = request_api(corpus_name, "crawl_webentity", webentity_id=entity_id, depth=depth)
    crawl_id = cast(str, response)
    logger.info(f"Crawl no {crawl_id} launched for {entity_id}!")
    return crawl_id

def get_webentity(corpus_name:str, webentity_id:int) -> EntityFull:
    response = request_api(corpus_name, "store.get_webentity", webentity_id=webentity_id)
    entity = cast(EntityFull, response[0])
    return entity

def get_webentities(corpus_name:str, light:bool = False, semilight:bool = False, sort:Optional[Sequence[str]] = None, paginate:bool = False) -> Sequence[Entity]:
    logger.debug(f"Requesting webentities with sort {sort}")
    if not paginate:
        response = request_api(corpus_name, "store.get_webentities", light=light, semilight=semilight, sort=sort, count=-1)
        entities = cast(list[Entity], response)
        return entities
    response = request_api(corpus_name, "store.get_webentities", light=light, semilight=semilight, sort=sort, count=5000)
    page = cast(EntitiesListPage, response)
    entities, cur_page, next_page, last_page, token = page["webentities"], page["page"], page["next_page"], page["last_page"], page["token"]
    while cur_page < last_page:
        response = request_api(corpus_name, "store.get_webentities_page", pagination_token=token, n_page=next_page)
        page = cast(EntitiesListPage, response)
        entities += page["webentities"]
        cur_page, next_page, last_page, token = page["page"], page["next_page"], page["last_page"], page["token"]
        logger.info(f"Got page {cur_page}; next page is {next_page}, to get with token {token} (last page {last_page})")
    return entities
    

def get_webentities_light(corpus_name:str, sort:Optional[Sequence[str]] = None, paginate:bool = False) -> Sequence[EntityLight]:
    response = get_webentities(corpus_name, light=True, sort=sort, paginate=paginate)
    return cast(Sequence[EntityLight], response)

def get_webentities_semilight(corpus_name:str, sort:Optional[Sequence[str]] = None, paginate:bool = False) -> Sequence[EntitySemilight]:
    response = get_webentities(corpus_name, semilight=True, sort=sort, paginate=paginate)
    return cast(Sequence[EntitySemilight], response)
def set_webentity_status(corpus_name:str, webentity_id:int, status:EntityStatus) -> None:
    logger.info(f"Setting status of entity no {webentity_id} to {status}")
    response = request_api(corpus_name, "store.set_webentity_status", webentity_id=webentity_id, status=status)
    logger.info(f"Was the status changed? '{response}'")

def list_jobs(corpus_name:str) -> Sequence[HypheJob]:
    jobs = request_api(corpus_name, "listjobs")
    return cast(Sequence[HypheJob], jobs)

def start_corpus(corpus_name:str, logging_level:int = logging.INFO) -> None:
    logger.log(logging_level, f"Starting corpus {corpus_name}")
    response = request_api(corpus_name, "start_corpus")

def set_corpus_options(corpus_name:str, options:Mapping) -> Mapping:
    response = request_api(corpus_name, "set_corpus_options", options=options)
    logger.info(f"Set the following options for corpus {corpus_name}: {options}")
    return response #type:ignore


def datasprint_get_corpus_name(year:int) -> tuple[str,str]:
    corpus_name = f"covid_{year}"
    api_url = config.hyphe.api_url_archives if year < 2022 else config.hyphe.api_url_live
    return (corpus_name, api_url)

def get_webentity_by_lruprefix(corpus_name:str, lru_prefix:str) -> EntitySemilight:
    return request_api(corpus_name, "store.get_webentity_by_lruprefix", lru_prefix=lru_prefix, raise_on_fail=True) #type:ignore

def datasprint_populate_corpus() -> None:
    platform_rules, platform_rules_sequence = get_platform_rules_as_both(config.paths.PLATFORM_RULES_FILEPATH)
    site_tags:defaultdict[str,set[str]] =  defaultdict(set)
    site_urls:defaultdict[str,set[Url]] =  defaultdict(set)
    site_is_path:defaultdict[str,set[bool]] = defaultdict(set)
    site_exists_2020:dict[str,bool] =  {}
    site_exists_2021:dict[str,bool] =  {}
    for (url,is_path,exists_in_2020, exists_in_2021, tags_set) in get_datasprint_urls():
        platform, sitename, path_platform = find_platform_of_url(url, platform_rules_sequence, bcweb_scope=None, include_social_media=True, include_contextual=True)
        if is_path and platform == config.various.DEFAULT_PLATFORM:
            raise ValueError(f"On aurait dû trouver une plateforme de blogs pour {url.string}")
        for tag in tags_set:
            site_tags[sitename].add(tag)
        site_urls[sitename].add(url)
        site_is_path[sitename].add(is_path)
        site_exists_2020[sitename] = exists_in_2020
        site_exists_2021[sitename] = exists_in_2021
    for sitename in site_tags:
        tags_list = sorted(site_tags[sitename])
        tags_list_str = ", ".join(tags_list)
        tags:TagsDict =  {"USER":{"Acteur":[tags_list_str]}}
        urls = sorted([url.string for url in site_urls[sitename]])
        lru_prefix = get_lru_from_sitename(sitename)
        if len(site_is_path[sitename]) > 1:
            raise ValueError(f"Plusieurs valeurs pour {sitename}:  {site_is_path[sitename]}")
        logger.info(f"{sitename} a le préfixe LRU {lru_prefix} et ces tags:  {tags['USER']['Acteur']}")
        for year in (2020,2021,2022):
            if year == 2020 and not site_exists_2020[sitename]:
                continue
            elif year == 2021 and not site_exists_2021[sitename]:
                continue
            corpus_name, api_url = datasprint_get_corpus_name(year)
            response = declare_webentity_by_lru(corpus_name, api_url=api_url, lru_prefix=lru_prefix, status="IN", name=sitename, startpages=urls, lru_variations=True, tags=tags)
    for (sitename, status) in get_datasprint_other_urls():
        lru_prefix = get_lru_from_sitename(sitename)
        for year in (2020, 2021, 2022):
            corpus_name, api_url = datasprint_get_corpus_name(year)
            response = declare_webentity_by_lru(corpus_name, api_url=api_url, lru_prefix=lru_prefix, status=status, name=sitename, lru_variations=True)


def datasprint_correct_undecided() -> None:
    corpus_name, api_url = datasprint_get_corpus_name(2020)
    for (sitename,status) in get_datasprint_other_urls():
        if status != "UNDECIDED":
            continue
        ok = False
        lru_prefix = get_lru_from_sitename(sitename)
        try:
            entity = get_webentity_by_lruprefix(corpus_name, lru_prefix)
        except:
            logger.info(f"{sitename}: failed to get entity")
            config.paths.PROBLEMATIC_URLS_FILEPATH.open("a", encoding="utf-8").write(f"{sitename}\n")
            continue
        if entity["status"] != "IN":
            logger.info(f"{sitename} is OK")
        else:
            logger.info(f"{sitename} is not OK:!!!!!!!!!!!!!")
            set_webentity_status(corpus_name, entity["_id"], status)

def datasprint_recrawl() -> None:
    for year in (2021,2022):
        jobs = defaultdict(set)
        corpus_name, api_url = datasprint_get_corpus_name(year)
        for job in list_jobs(corpus_name):
            jobs[job["webentity_id"]].add(job["nb_crawled_pages"] > 1)
        for entity in get_webentities(corpus_name,light=True):
            _id = entity["_id"]
            if entity["status"] == "IN" and True not in jobs[_id]:
                crawl_webentity(corpus_name, _id, 1)

def task(corpus_name:Optional[str]) -> None:
    datasprint_recrawl()
    breakpoint()

def run_task(corpus_name:Optional[str] = None) -> None:
    task(corpus_name)

    breakpoint()
    return
