import unittest

from sns_core.clients.discord_messages import build_text_embed, escape_discord_description
from sns_core.models import PostAuthor, SocialPost


class DiscordDescriptionEscapingTest(unittest.TestCase):
    def test_escapes_markdown_and_mentions(self) -> None:
        # Arrange
        value = "차차 ~~안녕~~ @everyone"

        # Act
        escaped = escape_discord_description(value)

        # Assert
        self.assertEqual("차차 \\~\\~안녕\\~\\~ @\u200beveryone", escaped)

    def test_build_text_embed_uses_escaped_and_limited_description(self) -> None:
        # Arrange
        post = SocialPost(
            post_link="https://example.com/post",
            author=PostAuthor(name="Artist", url="https://example.com/avatar.jpg"),
            text="~" * 4096,
        )

        # Act
        embed = build_text_embed(post)[0]

        # Assert
        self.assertLessEqual(len(embed.description), 4096)
        self.assertTrue(embed.description.startswith("\\~"))


if __name__ == "__main__":
    unittest.main()