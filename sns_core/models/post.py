from dataclasses import dataclass
from datetime import datetime


@dataclass
class PostAuthor:
    name: str
    url: str


@dataclass(kw_only=True)
class SocialPost:
    post_link: str
    author: PostAuthor
    text: str
    title: str | None = None
    images: list[str] | None = None
    videos: list[str] | None = None
    links: list[str] | None = None
    created_at: datetime | None = None


__all__ = ["PostAuthor", "SocialPost"]
