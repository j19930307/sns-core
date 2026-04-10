import json
import os

import requests
from discord import Embed

from sns_core.models import SocialPost
from sns_core.utils import get_domain_from_url

DOMAIN_TWITTER = "twitter.com"
DOMAIN_X = "x.com"
DOMAIN_INSTAGRAM = "instagram.com"
DOMAIN_WEVERSE = "weverse.io"
DOMAIN_THREADS = "threads.com"
DOMAIN_BERRIZ = "berriz.in"

DOMAIN_H1KEY = "h1key-official.com"
DOMAIN_H1KEY_BSTAGE = "h1key.bstage.in"
DOMAIN_YEEUN_BSTAGE = "yeeun.bstage.in"
DOMAIN_PURPLE_KISS = "purplekiss.co.kr"
DOMAIN_KISS_OF_LIFE = "kissoflife-official.com"
DOMAIN_KISS_OF_LIFE_BSTAGE = "kissoflife.bstage.in"

DOMAINS_BSTAGE = {
    DOMAIN_H1KEY,
    DOMAIN_H1KEY_BSTAGE,
    DOMAIN_YEEUN_BSTAGE,
    DOMAIN_PURPLE_KISS,
    DOMAIN_KISS_OF_LIFE,
    DOMAIN_KISS_OF_LIFE_BSTAGE,
}

_SOURCE_MAP: dict[str, tuple[str, str]] = {
    DOMAIN_TWITTER: (
        "X",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/X_icon_2.svg/2048px-X_icon_2.svg.png",
    ),
    DOMAIN_X: (
        "X",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/X_icon_2.svg/2048px-X_icon_2.svg.png",
    ),
    DOMAIN_INSTAGRAM: (
        "Instagram",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/600px-Instagram_icon.png",
    ),
    DOMAIN_WEVERSE: (
        "Weverse",
        "https://image.winudf.com/v2/image1/Y28uYmVueC53ZXZlcnNlX2ljb25fMTY5NjQwNDE0MF8wMTM/icon.webp?w=140&fakeurl=1&type=.webp",
    ),
    DOMAIN_THREADS: (
        "Threads",
        "https://cdn.iconscout.com/icon/free/png-256/free-threads-logo-icon-svg-download-png-8461527.png",
    ),
    DOMAIN_BERRIZ: (
        "Berriz",
        "https://play-lh.googleusercontent.com/vr-o5CiOCByufCykA7PWFFQSppaEpSQAjXvm5ehthw2IiHQ8L0umnOQdqUmZAEUjkgeJ",
    ),
}

_BSTAGE_SOURCE: tuple[str, str] = ("b.stage", "https://i.imgur.com/xekJ8pd.png")


def resolve_source(domain: str) -> tuple[str, str] | None:
    if domain in DOMAINS_BSTAGE:
        return _BSTAGE_SOURCE
    return _SOURCE_MAP.get(domain)


def _base_embed(
    *,
    social_post: SocialPost,
    description: str,
    source: tuple[str, str] | None,
) -> Embed:
    embed = Embed(
        title=social_post.title,
        description=description,
        url=social_post.post_link,
        timestamp=social_post.created_at,
    ).set_author(
        name=social_post.author.name,
        icon_url=social_post.author.url,
    )

    if source:
        embed.set_footer(text=source[0], icon_url=source[1])

    return embed


def _resolve_source_from_post(social_post: SocialPost) -> tuple[str, str] | None:
    return resolve_source(get_domain_from_url(social_post.post_link) or "")


def build_embeds(social_post: SocialPost) -> list[Embed]:
    source = _resolve_source_from_post(social_post)
    description = (social_post.text or "")[:4096]
    images = social_post.images

    def base() -> Embed:
        return _base_embed(social_post=social_post, description=description, source=source)

    if not images:
        return [base()]

    embeds = [base().set_image(url=images[0])]
    for image_url in images[1:4]:
        embeds.append(Embed(url=social_post.post_link).set_image(url=image_url))

    return embeds


def build_text_embed(social_post: SocialPost) -> list[Embed]:
    source = _resolve_source_from_post(social_post)
    description = (social_post.text or "")[:4096]
    return [_base_embed(social_post=social_post, description=description, source=source)]


def is_bot_mentioned(message, bot_id: int) -> bool:
    if bot_id in message.raw_mentions:
        return True
    return any(
        member.id == bot_id
        for role in message.role_mentions
        for member in role.members
    )


def post_message(
    channel_id: str,
    content: str,
    embeds: list[Embed] | None = None,
    files: list[str] | None = None,
) -> requests.Response:
    url = f"https://discord.com/api/channels/{channel_id}/messages"
    headers = {"Authorization": f'Bot {os.environ["BOT_TOKEN"]}'}
    embeds = embeds or []

    if files:
        data = {"content": content}
        if embeds:
            data["embeds"] = json.dumps([embed.to_dict() for embed in embeds])

        files_dict = {f"files[{i}]": open(path, "rb") for i, path in enumerate(files)}
        try:
            response = requests.post(url, headers=headers, data=data, files=files_dict)
        finally:
            for file_obj in files_dict.values():
                file_obj.close()
    else:
        headers["Content-Type"] = "application/json"
        data: dict[str, object] = {"content": content}
        if embeds:
            data["embeds"] = [embed.to_dict() for embed in embeds]
        response = requests.post(url, headers=headers, data=json.dumps(data))

    response.raise_for_status()
    return response
