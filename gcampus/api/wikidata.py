#  Copyright (C) 2022 desklab gUG (haftungsbeschränkt)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

__ALL__ = ["get_wikipedia_urls", "get_wikipedia_url"]

from functools import lru_cache
from typing import Optional, Dict

import httpx
from django.conf import settings
from django.utils.translation import get_language
from django.core.cache import cache

from gcampus.core.models.util import EMPTY


def _get_cache_key(wikidata_id: str, language: Optional[str] = None) -> str:
    if language is None:
        language = "all"
    return f"gcampus_cache_wikidata_{wikidata_id!s}_{language}"


@lru_cache(maxsize=128)  # Additional (faster) local cache
def get_wikipedia_urls(
    wikidata_id: str,
    client: Optional[httpx.Client] = None,
    timeout: Optional[int] = None,
) -> Dict[str, str]:
    """Get all Wikipedia URLs related to a given Wikidata ID. Returns
    a dictionary where the keys relate to the language (e.g. 'en', 'de')
    and the values denote the URL.

    :param wikidata_id: Wikidata ID for which to retrieve the related
        Wikipedia articles.
    :param client: Optional httpx client.
    :param timeout: Optional request timeout. Defaults to the
        ``REQUEST_TIMEOUT`` setting.
    :returns: Dictionary of languages and their associated URL.
    """
    sentinel = object()
    cache_key = _get_cache_key(wikidata_id)
    cached_val = cache.get(cache_key, sentinel)
    if cached_val is not sentinel:
        if isinstance(cached_val, dict) and cached_val != {}:
            return cached_val
    if timeout is None:
        timeout = getattr(settings, "REQUEST_TIMEOUT", 5)
    user_agent = getattr(
        settings, "REQUEST_USER_AGENT", f"GewaesserCampus ({settings.GCAMPUS_HOMEPAGE})"
    )
    if client is None:
        _client = httpx.Client()
    else:
        _client = client
    try:
        response: httpx.Response = _client.get(
            f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id!s}.json",
            headers={"User-Agent": user_agent},
            timeout=timeout,
        )
    except httpx.TimeoutException:
        return {}
    finally:
        if client is None:
            # Close '_client' manually. Otherwise, the client has to be
            # closed by the caller of this function.
            _client.close()
    if response.is_success:
        sitelinks: Optional[dict] = (
            response.json()
            .get("entities", {})
            .get(wikidata_id, {})
            .get("sitelinks", {})
        )
        if sitelinks in EMPTY:
            return {}
        urls = {}
        for key, val in sitelinks.items():
            if isinstance(key, str) and isinstance(val, dict) and key.endswith("wiki"):
                language_code = key[:-4]
                url = val.get("url", None)
                if url is not None:
                    urls[language_code] = url
        if urls != {}:
            cache.set(cache_key, urls)
        return urls
    else:
        return {}


@lru_cache(maxsize=512)  # Additional (faster) local cache
def get_wikipedia_url(
    wikidata_id: str,
    language: Optional[str] = None,
    client: Optional[httpx.Client] = None,
    timeout: Optional[int] = None,
) -> Optional[str]:
    """Get Wikipedia URL for a Wikidata entry and a specific language"""
    if language is None:
        language = get_language()
    sentinel = object()
    cache_key = _get_cache_key(wikidata_id, language)
    cached_val = cache.get(cache_key, sentinel)
    if cached_val is not sentinel and isinstance(cached_val, str) and cached_val != "":
        return cached_val
    urls = get_wikipedia_urls(wikidata_id, client=client, timeout=timeout)
    url = urls.get(language, None)
    if url is not None:
        cache.set(cache_key, url)
    return url
