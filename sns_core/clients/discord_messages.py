import json
import os
from typing import Any

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
DOMAIN_MNET_PLUS = "artist.mnetplus.world"

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
        "https://i.postimg.cc/Hk2WNNMT/X-icon-2-svg.png",
    ),
    DOMAIN_X: (
        "X",
        "https://i.postimg.cc/Hk2WNNMT/X-icon-2-svg.png",
    ),
    DOMAIN_INSTAGRAM: (
        "Instagram",
        "https://i.postimg.cc/4x5400cs/Instagram-icon.png",
    ),
    DOMAIN_WEVERSE: (
        "Weverse",
        "https://i.postimg.cc/8zHkYYv8/icon.webp",
    ),
    DOMAIN_THREADS: (
        "Threads",
        "https://i.postimg.cc/RZRCYYHk/free-threads-logo-icon-svg-download-png-8461527.png",
    ),
    DOMAIN_BERRIZ: (
        "Berriz",
        "https://i.postimg.cc/wjVxrrNp/unnamed.png",
    ),
    DOMAIN_MNET_PLUS: (
        "Plus Chat",
        "https://i.postimg.cc/2SwjttWf/unnamed.jpg"
    )
}

_BSTAGE_SOURCE: tuple[str, str] = ("b.stage", "https://i.postimg.cc/B6tvHCXJ/bstage.png")


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
        content: str = "",
        embeds: list[Embed] | None = None,
        file_paths: list[str] | None = None,
        show_all: bool = False,
) -> requests.Response:
    """
    發送 Discord 訊息到指定 channel

    Args:
        channel_id: Discord channel id
        content: 純文字內容
        embeds: discord.Embed 清單
        file_paths: 要上傳的本地檔案路徑清單
        show_all: 是否印出送出的 payload

    Returns:
        requests.Response
    """
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f'Bot {os.environ["BOT_TOKEN"]}',
    }

    embeds = embeds or []
    file_paths = file_paths or []

    embed_payloads = [embed.to_dict() for embed in embeds]

    # Discord 至少要有一種內容
    if not content and not embed_payloads and not file_paths:
        raise ValueError("content、embeds、file_paths 不能全部為空")

    if file_paths:
        payload: dict[str, Any] = {"content": content}
        if embed_payloads:
            payload["embeds"] = embed_payloads

        if show_all:
            print("payload_json =", json.dumps(payload, ensure_ascii=False, indent=2))
            print("files =", file_paths)

        files_dict = {
            f"files[{i}]": open(path, "rb")
            for i, path in enumerate(file_paths)
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                data={"payload_json": json.dumps(payload, ensure_ascii=False)},
                files=files_dict,
                timeout=60,
            )
        finally:
            for file_obj in files_dict.values():
                file_obj.close()
    else:
        payload: dict[str, Any] = {"content": content}
        if embed_payloads:
            payload["embeds"] = embed_payloads

        if show_all:
            print("json payload =", json.dumps(payload, ensure_ascii=False, indent=2))

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60,
        )

    print("status_code =", response.status_code)
    print("response_text =", response.text)
    response.raise_for_status()
    return response
