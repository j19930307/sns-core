from datetime import datetime
from typing import Any

from google.cloud import firestore
from google.oauth2 import service_account

from sns_core.platform_types import SocialPlatform


class FirestoreSubscriptionStore:
    def __init__(self, creds_dict: dict[str, Any]):
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        self._db = firestore.AsyncClient(
            project=creds_dict.get("project_id"),
            credentials=credentials,
        )

    def _doc_ref(self, platform: SocialPlatform, account_id: str):
        return self._db.collection(platform.value).document(account_id)

    async def add_account(
        self,
        platform: SocialPlatform,
        account_id: str,
        username: str,
        discord_channel_id: str,
        updated_at: datetime,
    ) -> None:
        await self._doc_ref(platform, account_id).set(
            {
                "username": username,
                "discord_channel_id": discord_channel_id,
                "updated_at": updated_at,
            }
        )

    async def delete_account(self, platform: SocialPlatform, account_id: str) -> None:
        await self._doc_ref(platform, account_id).delete()

    async def is_account_exists(self, platform: SocialPlatform, account_id: str) -> bool:
        doc = await self._doc_ref(platform, account_id).get()
        return doc.exists

    async def get_documents(self, platform: SocialPlatform) -> list:
        return [doc async for doc in self._db.collection(platform.value).stream()]

    async def get_updated_at(
        self, platform: SocialPlatform, account_id: str
    ) -> datetime:
        doc = await self._doc_ref(platform, account_id).get()
        if doc.exists:
            return doc.to_dict()["updated_at"]
        return datetime.now()

    async def set_updated_at(
        self, platform: SocialPlatform, account_id: str, updated_at: datetime
    ) -> None:
        await self._doc_ref(platform, account_id).update({"updated_at": updated_at})

    async def get_subscribed_list(self, platform: SocialPlatform) -> list:
        return [doc async for doc in self._db.collection(platform.value).stream()]

    async def get_subscribed_list_from_discord_id(
        self, platform: SocialPlatform, discord_id: str
    ) -> list[tuple[str, str]]:
        docs = await self.get_documents(platform)
        return [
            (doc.get("username"), doc.id)
            for doc in docs
            if doc.get("discord_channel_id") == discord_id
        ]

    async def add_youtube_account(
        self,
        handle: str,
        channel_name: str,
        discord_channel_id: str,
        latest_video_id: str,
        latest_video_published_at: datetime,
        latest_short_id: str,
        latest_short_published_at: datetime,
        latest_stream_id: str,
        latest_stream_published_at: datetime,
    ) -> None:
        await self._db.collection(SocialPlatform.YOUTUBE.value).document(handle).set(
            {
                "channel_name": channel_name,
                "discord_channel_id": discord_channel_id,
                "latest_video": {
                    "id": latest_video_id,
                    "published_at": latest_video_published_at,
                },
                "latest_short": {
                    "id": latest_short_id,
                    "published_at": latest_short_published_at,
                },
                "latest_stream": {
                    "id": latest_stream_id,
                    "published_at": latest_stream_published_at,
                },
            }
        )

    async def get_youtube_subscribed_list_from_discord_id(
        self, discord_id: str
    ) -> list[str]:
        docs = [
            doc async for doc in self._db.collection(SocialPlatform.YOUTUBE.value).stream()
        ]
        return [doc.id for doc in docs if doc.get("discord_channel_id") == discord_id]

    async def add_berriz_account(
        self,
        username: str,
        community_id: str,
        board_id: str,
        discord_channel_id: str,
        updated_at: datetime,
    ) -> None:
        await self._db.collection(SocialPlatform.BERRIZ.value).document(username).set(
            {
                "community_id": community_id,
                "board_id": board_id,
                "discord_channel_id": discord_channel_id,
                "updated_at": updated_at,
            }
        )

    async def get_berriz_subscribed_list(self, discord_id: str) -> list[str]:
        docs = [
            doc async for doc in self._db.collection(SocialPlatform.BERRIZ.value).stream()
        ]
        return [doc.id for doc in docs if doc.get("discord_channel_id") == discord_id]


__all__ = ["FirestoreSubscriptionStore"]
