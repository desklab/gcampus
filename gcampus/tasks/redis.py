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

__all__ = ("connection_pool_wrapper", "get_redis_instance")
from typing import Optional

from django.conf import settings
from redis import ConnectionPool, Redis


class ConnectionPoolWrapper:
    def __init__(self, url: str):
        self._url: str = url
        self._pool: Optional[ConnectionPool] = None

    @property
    def connection_pool(self) -> ConnectionPool:
        if self._pool is not None:
            return self._pool
        else:
            self._pool = _pool = ConnectionPool.from_url(self._url)
            return _pool

    pool = connection_pool


connection_pool_wrapper = ConnectionPoolWrapper(getattr(settings, "REDIS_URL"))


def get_redis_instance() -> Redis:
    return Redis(connection_pool=connection_pool_wrapper.pool)
