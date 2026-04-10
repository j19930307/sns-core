import re
from urllib.parse import urlparse, urlunparse

import requests


def get_domain_from_url(url: str) -> str | None:
    """Return the domain portion of an HTTPS URL."""
    match = re.search(r"https://(www\.)?([^/]+)", url)
    if match:
        return match.group(2)
    return None


def to_alternative_instagram_url(url: str) -> str:
    """Rewrite Instagram URLs to the alternate host used by downstream clients."""
    if not url.startswith("https://www.instagram.com"):
        return url

    parsed_url = urlparse(url)
    modified_netloc = parsed_url.netloc.replace("instagram.com", "zzinstagram.com")
    return urlunparse(
        (
            parsed_url.scheme,
            modified_netloc,
            parsed_url.path,
            parsed_url.params,
            "",
            parsed_url.fragment,
        )
    )


def shorten_url(original_url: str) -> str:
    """Shorten a URL and fall back to the original value if all providers fail."""
    get_providers = [
        "https://is.gd/create.php",
        "https://v.gd/create.php",
    ]

    for endpoint in get_providers:
        try:
            response = requests.get(
                endpoint,
                params={
                    "format": "simple",
                    "url": original_url,
                },
                timeout=5,
            )
            if response.ok and response.text.startswith("http"):
                return response.text.strip()
        except Exception:
            continue

    try:
        response = requests.post(
            "https://cleanuri.com/api/v1/shorten",
            data={"url": original_url},
            timeout=5,
        )
        if response.ok:
            data = response.json()
            short_url = data.get("result_url")
            if short_url:
                return short_url
    except Exception:
        pass

    return original_url

__all__ = [
    "get_domain_from_url",
    "to_alternative_instagram_url",
    "shorten_url",
]
