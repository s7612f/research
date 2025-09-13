import urllib.request
import urllib.error

WAYBACK_SAVE = "https://web.archive.org/save/"

def snapshot(url: str) -> str:
    """Archive a URL using the Wayback Machine."""
    try:
        req = urllib.request.Request(WAYBACK_SAVE + url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            loc = resp.headers.get('Content-Location')
            if loc:
                return 'https://web.archive.org' + loc
    except Exception:
        pass
    return f"https://web.archive.org/web/0/{url}"
