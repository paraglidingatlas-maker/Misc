"""Pick a reader by the link's domain. Each reader module has read(link, opts) -> RAW TASK (see taskpkg.py)."""
from urllib.parse import urlparse

READERS = [
    ("airtribune.com", "airtribune"),
    ("airscore.cc", "airscore"),
    ("pwca.org", "pwca"), ("pwca.events", "pwca"),
    ("livetrack24.com", "livetrack24"),
    ("flymaster.net", "flymaster"),
]


def pick(link):
    if "://" not in link:
        return "files"
    host = urlparse(link).hostname or ""
    for dom, mod in READERS:
        if host == dom or host.endswith("." + dom):
            return mod
    return None
