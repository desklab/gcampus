import os
import sys
import mimetypes
from weasyprint import default_url_fetcher, HTML
from weasyprint.urls import URLFetchingError

FOLDER = os.path.join(os.path.dirname(__file__), "resources")


def url_fetcher(url: str, **kwargs):
    if url.startswith("gcampus:"):
        resource = url[8:]
        res_path = os.path.join(FOLDER, resource)
        mime_type, __ = mimetypes.guess_type(res_path, strict=True)
        if mime_type is None:
            mime_type = "image/*"
        if not os.path.isfile(res_path):
            raise URLFetchingError()
        return {"mime_type": mime_type, "file_obj": open(res_path, "rb")}
    else:
        return default_url_fetcher(url, **kwargs)


if __name__ == "__main__":
    filename = sys.argv[1]
    file_pdf = filename.split(".")[0] + ".pdf"
    HTML(filename=filename, url_fetcher=url_fetcher).write_pdf(file_pdf)
