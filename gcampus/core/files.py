#  Copyright (C) 2023 desklab gUG (haftungsbeschränkt)
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

from django.core.files import File
from django.core.files.storage import default_storage, Storage


def file_exists(file: File | None, storage: Storage = default_storage) -> bool:
    """Check if a :class:`django.core.files.File` exists.

    Sometimes files may get deleted from the actual storage. In that
    case, the database will fall out of sync with the storage system.
    This function checks the storage system whether the file exsits.

    :param file: A :class:`django.core.files.File` instance. E.g. the
        file field of a model instance.
    :param storage: Optional storage instance. Defaults to
         :attr:`django.core.files.storage.default_storage`.
    """
    return bool(file and storage.exists(file.name))
