#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
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
import logging
import typing as t
from functools import lru_cache, wraps
from threading import Lock as ThreadLock

from django.conf import settings
from redis.client import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.lock import Lock as RedisLock

logger = logging.getLogger("gcampus.tasks.lock")


@lru_cache
def _get_named_thread_lock(name: str) -> ThreadLock:
    # The parameter 'name' only ensures that the LRU cache saves
    # different locks for each name
    return ThreadLock()


def weak_lock(name: str, timeout: int = 120) -> t.Union[ThreadLock, RedisLock]:
    r = Redis(host=getattr(settings, "REDIS_HOST"))
    try:
        r.ping()
    except RedisConnectionError:
        logger.warning("Fall back to thread lock")
        return _get_named_thread_lock(name)
    return r.lock(name, timeout=timeout)


def weak_lock_task(name: t.Union[str, callable], timeout: int = 120):
    if callable(name):
        lock_name = name.__name__
    else:
        lock_name = name

    def decorator(task):
        @wraps(task)
        def wrapper(*args, **kwargs):
            with weak_lock(lock_name, timeout=timeout):
                return task(*args, **kwargs)

        return wrapper

    if callable(name):
        return decorator(name)
    else:
        return decorator
