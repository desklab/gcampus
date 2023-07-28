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

__all__ = ["MarkerSize", "get_cluster_marker", "MAX_COUNT"]

import enum
from os.path import exists, isfile

from PIL import Image, ImageDraw, ImageFont
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage


class MarkerSize(enum.Enum):
    """Size and font size variations of the markers

    There are three different sizes of markers: ``LARGE``, ``MEDIUM``,
    ``SMALL``, and ``TINY``. The value of the enum returns a tuple of
    the size (i.e. width and height), and the font size of the given
    marker size.
    """

    LARGE = (210, 48)
    MEDIUM = (180, 48)
    SMALL = (120, 32)
    TINY = (90, 32)


ColorType = tuple[int, int, int, int]
TRANSPARENT: ColorType = (255, 255, 255, 0)
TEXT_COLOR: ColorType = (240, 242, 245, 255)  # Gray 100
FILL_COLOR: ColorType = (152, 156, 158, 255)  # Gray 500
LINE_COLOR: ColorType = (230, 234, 237, 255)  # Gray 200
LINE_WIDTH: int = 6
MAX_COUNT: int = 999


def get_cluster_marker(
    count: int,
    size: MarkerSize,
    font: str = "gcampusauth/fonts/JetBrainsMono-Medium.ttf",
    max_count: int = MAX_COUNT,
) -> Image.Image:
    """Generate a marker image for a given text.

    :param count: Number that is displayed on the cluster marker.
    :param size: Instance of :class:`.MarkerSize`.
    :param font: Optional font, path to a static file.
    :param max_count: Maximum number displayed on the marker. If the
        number is larger than that, the string ``>[max_count]`` is
        used.
    """
    marker_size: int
    font_size: int
    marker_size, font_size = size.value
    # Because 'ImageDraw' does not support antialiasing or pixel
    # sub-sampling, the circles will appear pixelated. To mitigate this,
    # the image will be drawn at 4 times the resolution and later
    # sampled down using 'Image.resize'.
    subsampling_factor = 2
    bg_size = marker_size * subsampling_factor
    bg = Image.new("RGBA", (bg_size, bg_size), color=TRANSPARENT)
    bg_draw = ImageDraw.Draw(bg)
    bg_draw.ellipse(
        [
            (subsampling_factor - 1, subsampling_factor - 1),
            (bg_size - subsampling_factor, bg_size - subsampling_factor),
        ],
        fill=FILL_COLOR,
        outline=LINE_COLOR,
        width=LINE_WIDTH * subsampling_factor,
    )
    # Down-sample the image, causing pixel sub-sampling.
    marker = bg.resize((marker_size, marker_size), resample=Image.LANCZOS)
    text_draw = ImageDraw.Draw(marker)
    if count > max_count:
        text = f">{max_count:d}"
    else:
        text = str(count)
    with _open_static(font) as font_file:
        # Draw the marker text using the font loaded from a static file.
        text_draw.text(
            (marker_size // 2, marker_size // 2),
            text,
            font=ImageFont.truetype(font_file, size=font_size),
            anchor="mm",
            fill=TEXT_COLOR,
        )
    return marker


def _open_static(path: str):
    """Open static file

    Opens a static file using either the static file finders or the
    static files storage class itself. Both methods are used as during
    development, the static files storage class delivers an outdated
    result if ``collectstatic`` has not been run recently. Instead, the
    static file finders are used.

    In production, the static files may be stripped (when using Docker)
    from the project after running ``collectstatic`` to save on space.
    Thus, only ``staticfiles_storage`` will deliver a file.

    :param path: Path to a static file.
    """
    absolute_path = finders.find(path)
    try:
        if not absolute_path:
            raise FileNotFoundError()
        if not isfile(absolute_path) or not exists(absolute_path):
            raise FileNotFoundError()
        return open(absolute_path, "rb")
    except FileNotFoundError:
        return staticfiles_storage.open(path, mode="rb")
