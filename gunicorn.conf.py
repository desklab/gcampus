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

from gunicorn.workers.base import Worker
from gevent import monkey
from psycogreen.gevent import patch_psycopg


def post_fork_patch(server, worker: Worker):
    monkey.patch_all()
    patch_psycopg()
    worker.log.info("Patched 'psycopg'")


wsgi_app = "gcampus.wsgi"
errorlog = "-"  # log to stderr
loglevel = "info"
# capture_output = True
bind = "0.0.0.0:8000"
workers = 4
worker_class = "gevent"
post_fork = post_fork_patch
max_requests = 2000
max_requests_jitter = 20
