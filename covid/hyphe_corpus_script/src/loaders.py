#coding:utf-8
import csv, os, logging, re, json
from collections import defaultdict
from re import Pattern
from typing import Any, cast, Dict, Optional, Mapping, NamedTuple, Sequence , Union
from urllib.parse import urlparse, urlunparse, ParseResult, parse_qs
from pathlib import Path
from datetime import date, datetime
from .config import config
from .structures import Url, PlatformRule, EntityStatus, EntitySemilight, EntityPage, BCWebScope

logger = logging.getLogger(f"corpus_builder.{__name__}")
    
   
EMPTY_REENCODING_RULES:Mapping[str,str] = {}

def validate_entity_status(status_string:str) -> Optional[EntityStatus]:
    if status_string == "IN":
        return "IN"
    elif status_string == "UNDECIDED":
        return "UNDECIDED"
    elif status_string == "OUT":
        return "OUT"
    elif status_string == "DISCOVERED":
        return "DISCOVERED"
    return None

def strip_path(path:str) -> str:
    path = path.strip()
    return "" if path == "/" else path
    
def parse_url(url_string:str, reencoding_rules:Optional[Mapping[str,str]] = None,
        decode_percent:bool = False) -> Url:
    if reencoding_rules is None:
        reencoding_rules = EMPTY_REENCODING_RULES
    parts = urlparse(url_string.strip())
    if parts.scheme == "ttps":
        new_url = urlunparse(parts._replace(scheme="https"))
        return parse_url(new_url, reencoding_rules, decode_percent)
    elif parts.query == "og=1":
        new_url = urlunparse(parts._replace(query=""))
        return parse_url(new_url, reencoding_rules, decode_percent)
    domain_parts = parts.netloc.split(".")
    domain_name = parts.netloc if domain_parts[0] != "www" else ".".join(domain_parts[1:])
    qs = parse_qs(parts.query)
    if len(qs) == 1 and "fbclid" in qs:
        new_url = urlunparse(parts._replace(query=""))
        return parse_url(new_url, reencoding_rules, decode_percent)
    elif decode_percent and domain_name == "tumblr.com" and parts.path == "/privacy/consent" and (redirect_url := qs.get("redirect", None)) is not None:
        return parse_url(redirect_url[0], reencoding_rules=reencoding_rules, decode_percent=decode_percent)
    elif decode_percent and domain_name == "blogger.com" and parts.path == "/blogin.g" and (redirect_url := qs.get("blogspotURL", None)) is not None:
        return parse_url(redirect_url[0], reencoding_rules=reencoding_rules, decode_percent=decode_percent)
    if domain_name in reencoding_rules:
        new_domain = reencoding_rules[domain_name]
        new_url = url_string.replace(domain_name, new_domain)
        logger.info(f"{domain_name} will be reencoded to {new_domain}")
        return parse_url(new_url, reencoding_rules, decode_percent)
    elif url_string in reencoding_rules:
        new_url = reencoding_rules[url_string]
        return parse_url(new_url, reencoding_rules, decode_percent)
    key_path = strip_path(parts.path)
    key_url = urlunparse(parts._replace(scheme="", path=key_path, netloc=domain_name))[2:]
    parts = parts._replace(path=key_path)
    new_url_string = urlunparse(parts)
    return Url(new_url_string, domain_name, key_url, parts)

def _determine_url_segment(url:Url, rule:PlatformRule) -> str:
    if rule.segment == "Domain+Path":
        return url.key_url
    elif rule.segment == "Domain":
        return url.domain_name
    raise ValueError(f"Unexpected segment {rule.segment} for rule or filter: {rule}")

def _match_url_using_rule(url:Url, rule:PlatformRule) -> Optional[tuple[str, str, bool]]:
    """Attempts to match a <url> against a single platform <rule>.
    Returns None if the <url> doesn't match.
    Returns the <platform><sitename><path_platform> if it matches."""
    segment = _determine_url_segment(url, rule)
    match = rule.regex.search(segment)
    if match is None:
        return None
    platform, sitename = rule.name, match.group(0)
    path_platform = (rule.segment == "Domain+Path")
    return (platform, sitename, path_platform)


def _find_platform_of_url_using_rules(url:Url, rules:Sequence[PlatformRule],
        include_social_media:bool = True, include_contextual:bool = True) -> Optional[tuple[str, str, bool]]:
    """Finds the <platform><sitename><path_platform> of a <url> exclusively using our platform <rules>.
    If no platform is found, returns None."""
    for rule in rules:
        if not include_social_media and rule.name in config.hyphe.social_media_platforms:
            continue
        elif not include_contextual and rule.name in config.hyphe.contextual_platforms:
            continue
        result = _match_url_using_rule(url, rule)
        if result is None:
            continue
        return result
    return None

def find_platform_of_url(url:Url, rules:Sequence[PlatformRule],
        bcweb_scope:Optional[BCWebScope] = None,
        include_social_media:bool = True,
        include_contextual:bool = True) -> tuple[str, str, bool]:
    """Returns a tuple with the <platform><sitename><path_platform>...
    ... of a given <url> using our platform <rules> and a bit of manual logic.
    If the <url> originates from BCweb, <bcweb_scope> must contain its BCweb scope.

    If we find a platfom within our platform rules, that platform is returned.
    To do so, we iterate over our platform rules (a regex per platform), and...
       * If the platform's rule is path-based (path-significant platform like sites.google.com), we apply the regex on the key URL (full URL with the path segment but without "www" or the protocol or any trailing slash)
       * If the platform's rule is domain-based (like Blogspot), we apply the regex on the domain name only
    If none is found, we return the default platform for sites with distinct/individual DNS records ("Nom de domaine distinct").

    The <sitename> is important since it defines the site's boundary, and may not be so obvious:
    E.g a site named lemonde.fr/livres/ will be much smaller than just lemonde.fr.
    Our platform rules already handle complex path URLs for Lifranum seeds, but there are too many BCweb entries
    to manually find rules for each of them, so a lot of path URLs will be unhandled.
    How to determine the <sitename>/<path_platform> then?
    (1) If we find a platform according to our rules, we always rely on it:
        It always yields a good sitename exactly matching the editorial entity
        It may be path-significant or not, but the rule should be fairly accurate!
    (2) We take the key <url> as sitename if 3 conditions are met:
        (*) the <url> comes from BCweb
        (*) the BCweb entry has a path scope ('chemin' or 'page + 2 clics')
        (*) the <url> has a path segment (e.g lemonde.fr/livres/)
    (3) In all other cases, we take the host (full domain name) as a <sitename>
    Beware:
    (a) The reason why in (2) we don't use a wider domain scope (lemonde.fr) on Urls with a path segment (lemonde.fr/livres/):
        Because we risk matching a large site that contains many unrelated sections (e.g lemonde.fr is a press site)
        What we want is the editorial entity not the whole site, so we use a narrow scope (path) only for narrow URLs
        The counterpart is that sometimes, a path scope is too narrow:
        In some sites in page+2, the pages distant by 1 click have a different Url structure that we won't match:
        cipag.ulg.ac.be/interintro.php is a revue homepage; subpages are at ulg.ac.be/cipa/intervalles1/
        ...So matching with a domain scope would be safer, and we may miss some urls when doing matching later
    (b) Sometimes, we may find a domain platform, and yet have a path segment or a path scope in BCweb
        This will fall into case (1) and means either that:
        * there's a path homepage/prefix (kev.worpress.com/blog/)
        * only a smaller part of the editorial entity is collected by the BnF (kev.wordpress.com/reviews-section/)
    (c) Sometimes, a <url> from BCweb with a path segment may have a domain scope
        Usually, this indicates a 'path homepage', like myblog.com/wordpress:
        The path isn't really significant, we ignore it, and rely on the platform/domain scope anyway
        But we should be aware of it, because perhaps there was an error on the entry...
        ... in which case we would match a large site when we only want a page"""
    path_segment = strip_path(url.parts.path) if bcweb_scope is not None else ""
    bcweb_path_significant = path_segment and bcweb_scope in config.bcweb.PATH_SCOPES
    bcweb_str = "" if bcweb_scope is None else f", which comes from BCweb (scope {bcweb_scope})"
    logger.debug(f"Searching the platform & sitename of Url <{url.key_url}>{bcweb_str}")
    found = _find_platform_of_url_using_rules(url, rules, include_social_media=include_social_media, include_contextual=include_contextual)
    if found is not None:
        platform, sitename, path_platform = found
        logger.debug(f"[Case (1)] Found platform {platform} with sitename {sitename} using our custom platform rules!")
        if not path_platform and (path_segment or bcweb_scope in config.bcweb.PATH_SCOPES):
            logger.debug(f"[caveat (b)] This platform is domain-significant, and yet got a path segment or a path scope ({url.key_url} & {bcweb_scope}): the BnF collects only a tiny portion of the entity, or this is a path homepage")
        return (platform, sitename, path_platform)
    platform = config.various.DEFAULT_PLATFORM
    logger.debug(f"Found no platform using our platform rules, thus platform is, by default, {platform}")
    if bcweb_path_significant:
        sitename, path_platform = url.key_url, True
        logger.debug(f"[Case (2)] By default, sitename is {sitename} because of the path scope on Bcweb ({bcweb_scope}).")
        logger.debug(f"[caveat (a)] This will prevent casting too wide a net; but beware of the path scope being too narrow")
        return (platform, sitename, path_platform)
    sitename, path_platform = url.domain_name, False
    logger.debug(f"[Case (3)] By default, sitename is {sitename} (domain scope)")
    if bcweb_scope is None:
        logger.debug(f"This wasn't a BCweb entry, so the domain scope was applied without any issue")
    elif path_segment:
        logger.debug(f"[caveat (c)] In BCweb, got a non-path scope ({bcweb_scope}) even if the Url had a path segment ({url.key_url}): this may indicate a path homepage")
    return (platform, sitename, path_platform)

def parse_bool(value:Any) -> bool:
    if value == "True":
        return True
    elif value == "False":
        return False
    raise ValueError(f"Unexpected non-boolean value: {value}")
    
def get_platform_rules(path:Path) -> Sequence[PlatformRule]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        rules = []
        for i,row in enumerate(reader):
            if (columns_count := len(row)) != 3:
                raise ValueError(f"Row no {i} has {columns_count} columns instead of 3: {row}")
            segment, name, regex_string  = row[0], row[1], r"{}".format(row[2])
            try:
                regex = re.compile(regex_string)
            except Exception as error:
                raise ValueError(f"Row no {i} has an invalid regex: {regex_string}") from error
            else:
                rules.append(PlatformRule(segment, name, regex_string, regex))
        return tuple(rules)

def get_platform_rules_as_mapping(path:Path) -> Mapping[str, PlatformRule]:
    rules = get_platform_rules(path)
    return {rule.name:rule for rule in rules}

def get_platform_rules_as_both(path:Path) -> tuple[Mapping[str, PlatformRule], Sequence[PlatformRule]]:
    platform_rules = get_platform_rules_as_mapping(config.paths.PLATFORM_RULES_FILEPATH)
    platform_rules_sequence = tuple(platform_rules[name] for name in platform_rules)
    return (platform_rules, platform_rules_sequence)
    
def validate_bool(i:int, value:Any) -> bool:
    if value == "TRUE":
        return True
    elif value == "FALSE":
        return False
    raise ValueError(f"Erreur sur la ligne n°{i}: {value} n'est pas un booléen valide")

def get_datasprint_urls() -> Sequence[tuple[Url,bool,bool,bool,set[str]]]:
    with config.paths.DATASPRINT_SOURCE.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        data =  []
        for i,row in enumerate(reader):
            url_string, main_tags, sante_tags, exists_in_2020_r, exists_in_2021_r, *foo = row
            tags = set()
            exists_in_2020 = validate_bool(i, exists_in_2020_r)
            exists_in_2021 = validate_bool(i, exists_in_2021_r)
            for iterable in (main_tags, sante_tags):
                for tag in iterable.split(","):
                    tag = tag.strip()
                    if tag:
                        tag = tag[0].upper() + tag[1:]
                        tags.add(tag)
            is_path = False
            if "Chemin" in tags:
                tags.remove("Chemin")
                is_path = True
            url = parse_url(url_string)
            data.append((url,is_path,exists_in_2020, exists_in_2021,tags))
        return data


def get_datasprint_other_urls() -> Sequence[tuple[str,EntityStatus]]:
    with config.paths.DATASPRINT_SOURCE_OTHER.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        data =  []
        for i,row in enumerate(reader):
            url_string, prefixes, status = row
            data.append((url_string, cast(EntityStatus, status)))
        return data
