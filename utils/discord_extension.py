from typing import Optional, Union, List, Any
from datetime import datetime

import discord
from discord.app_commands import Translator, locale_str
from discord.types.embed import EmbedType
from discord import ButtonStyle, Emoji, PartialEmoji
from discord.enums import Locale

from utils.utils import JSONTranslator


class EmbedError(Exception): ...


class ExtEmbedGenerator:
    """
    author: dict("name", Optional["icon_url"], Optional["url"])
    fields: list(BatterEmbed.Field)
    """

    class Field:
        def __init__(self, name: str, value: str, inline: bool = False) -> None:
            self.name: str = name
            self.value: str = value
            self.inline: bool = inline

    def __init__(
        self,
        *,
        translator: Translator,
        locale: Optional[Union[str, Locale]] = Locale.polish,
    ):
        if not translator or not getattr(translator, "translations", None):
            raise EmbedError
        self.translator: Translator = translator
        self.locale = str(locale)

    def embed(
        self,
        colour: Optional[Union[int, discord.Colour]] = None,
        color: Optional[Union[int, discord.Colour]] = None,
        title: Optional[Any] = "",
        embed_type: EmbedType = "rich",
        url: Optional[Any] = None,
        description: Optional[Any] = "",
        timestamp: Optional[datetime] = None,
        fields: Optional[List[Field]] = None,
        thumbnail: Optional[Any] = None,
        footer: Optional[Any] = None,
        author: Optional[dict] = None,
        image: Optional[Any] = None,
    ):
        embed = discord.Embed(
            colour=colour,
            color=color,
            title=self.translator.translate_sync(title),
            type=embed_type,
            url=url,
            description=self.translator.translate_sync(description),
            timestamp=timestamp,
        )
        if fields:
            for field in fields:
                _name = self.translator.translate_sync(field.name)
                _value = self.translator.translate_sync(field.value)

                embed.add_field(name=_name, value=_value, inline=field.inline)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if footer:
            embed.set_footer(text=self.translator.translate_sync(footer))
        if author and "name" in author:
            embed.set_author(
                name=self.translator.translate_sync(author["name"]),
                icon_url=(author["icon_url"] if "icon_url" in author else None),
                url=(author["url"] if "url" in author else None),
            )
        if image:
            embed.set_image(url=image)

        return embed


class ExtView(discord.ui.View):
    def __init__(
        self,
        translator: Translator,
        locale: Optional[Union[str, Locale]] = Locale.american_english,
        timeout: float | None = 180,
    ):
        self.translator = translator
        self.locale = locale

        super().__init__(timeout=timeout)

    def new_button(
        self,
        label: Optional[Union[str, locale_str]] = None,
        custom_id: Optional[str] = None,
        disabled: bool = False,
        style: ButtonStyle = ButtonStyle.secondary,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        row: Optional[int] = None,
        callback: Optional[Any] = None,
    ):
        return ExtButton(
            translator=self.translator,
            locale=self.locale,
            label=label,
            custom_id=custom_id,
            disabled=disabled,
            style=style,
            emoji=emoji,
            row=row,
            callback=callback,
        )


class ExtButton(discord.ui.Button):
    def __init__(
        self,
        translator: JSONTranslator,
        locale: Optional[Union[str, Locale]] = Locale.american_english,
        label: Optional[Union[str, locale_str]] = None,
        custom_id: Optional[str] = None,
        disabled: bool = False,
        style: ButtonStyle = ButtonStyle.secondary,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        row: Optional[int] = None,
        callback: Optional[Any] = None,
    ):
        if not translator or not getattr(translator, "translations", None):
            raise EmbedError
        self.translator = translator
        self.locale = locale
        if callback:
            self.callback = callback

        super().__init__(
            label=(
                self.translator.translate_sync(label, locale=self.locale)
                if type(label) == locale_str
                else label
            ),
            custom_id=custom_id,
            disabled=disabled,
            style=style,
            emoji=emoji,
            row=row,
        )
