from datetime import datetime, timedelta, time
from typing import Literal, Optional, List
from peewee import fn

# discord import
import discord
from discord import app_commands
from discord.app_commands import locale_str
from discord.ext import commands

# local import
from utils.utils import JSONTranslator, pretty_traceback
from utils.discord_extension import ExtEmbedGenerator, ExtView
from orms.calendar import Event


class PastDateError(Exception): ...


class FarDateError(Exception): ...


class InvalidDateError(Exception): ...


class Calendar(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.embedGenerator = ExtEmbedGenerator(
            translator=client.tree.translator, locale=discord.Locale.polish
        )

    calendar_group = app_commands.Group(
        name=locale_str("calendar_group"),
        description=locale_str("calendar_group_description"),
    )
    show_subgroup = app_commands.Group(
        name=locale_str("calendar_show_group"),
        description=locale_str("calendar_show_group_description"),
    )
    calendar_group.add_command(show_subgroup)

    @calendar_group.command(
        name=locale_str("calendar_add"),
        description=locale_str("calendar_add_description"),
    )
    @app_commands.rename(
        title=locale_str("calendar_add_title"),
        event_type=locale_str("calendar_add_eventtype"),
        message=locale_str("calendar_add_message"),
        role=locale_str("calendar_add_role"),
        date=locale_str("calendar_add_date"),
        time=locale_str("calendar_add_time"),
    )
    @app_commands.describe(
        title=locale_str("calendar_add_title_description"),
        event_type=locale_str("calendar_add_eventtype_description"),
        message=locale_str("calendar_add_message_description"),
        role=locale_str("calendar_add_role_description"),
        date=locale_str("calendar_add_date_description"),
        time=locale_str("calendar_add_time_description"),
    )
    @app_commands.default_permissions(manage_events=True)
    async def add(
        self,
        interaction: discord.Interaction,
        title: str,
        date: str,
        event_type: Optional[
            Literal[
                "calendar_add_type_test",
                "calendar_add_type_exam",
                "calendar_add_type_deadline",
            ]
        ] = None,
        message: Optional[str] = None,
        role: Optional[discord.Role] = None,
        time: Optional[str] = None,
    ):
        date = date.replace("-", ".").replace("/", ".")
        formatted_date = datetime(1970, 1, 1)
        formatted_time = None

        error_desc = None
        try:
            try:
                formatted_date = datetime.strptime(date, "%d.%m.%Y")
                if formatted_date < datetime.now():
                    raise PastDateError
                if formatted_date > datetime.now() + timedelta(days=365):
                    raise FarDateError
            except ValueError:
                error_desc = locale_str("calendar_add_failure_invaliddate")
            except PastDateError:
                error_desc = locale_str("calendar_add_failure_pastdate")
            except FarDateError:
                error_desc = locale_str("calendar_add_failure_fardate")
            try:
                if time:
                    formatted_time = datetime.strptime(time, "%H:%M")
            except ValueError:
                if not error_desc:
                    error_desc = locale_str("calendar_add_failure_invalidtime")

            if not error_desc and len(title) > 100:
                error_desc = locale_str("calendar_add_failure_toolongtitle")

            if error_desc:
                raise ValueError(error_desc)

            created_event: Event = Event.create(
                title=title,
                date=formatted_date,
                message=message,
                event_type=event_type.split("_")[-1] if event_type else "other",
                role_id=role.id if role else None,
                time=formatted_time,
                guild_id=interaction.guild_id,
            )

            await interaction.response.send_message(
                embed=self.embedGenerator.embed(
                    title=locale_str("calendar_add_success_title"),
                    description=await self.client.tree.translator.translate(
                        locale_str(
                            "calendar_add_success_message",
                            title=created_event.title,
                            event_id=str(created_event.id),
                        )
                    ),
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )
        except Exception as e:
            embed = self.embedGenerator.embed(
                title=locale_str("calendar_add_failure_title"),
                color=discord.Color.red(),
            )
            embed.description = await self.client.tree.translator.translate(
                string=(
                    error_desc
                    if error_desc
                    else locale_str(
                        "calendar_add_failure_message", error_name=type(e).__name__
                    )
                ),
                locale=discord.Locale.polish,
            )
            print(pretty_traceback(e))

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )

    @calendar_group.command(
        name=locale_str("calendar_remove"),
        description=locale_str("calendar_remove_description"),
    )
    @app_commands.rename(
        query=locale_str("calendar_remove_query"),
        event_id=locale_str("calendar_remove_eventid"),
    )
    @app_commands.describe(
        query=locale_str("calendar_remove_query_description"),
        event_id=locale_str("calendar_remove_eventid_description"),
    )
    @app_commands.default_permissions(manage_events=True)
    async def remove(
        self,
        interaction: discord.Interaction,
        query: Optional[str],
        event_id: Optional[int] = None,
    ):
        async def remove_event(interaction: discord.Interaction):
            if not interaction.user.guild_permissions.manage_events:
                await interaction.followup.send(
                    await self.client.tree.translator.translate(
                        locale_str("missing_permissions"), discord.Locale.polish
                    ),
                    ephemeral=True,
                )
                return
            await interaction.message.delete()
            event = Event.get_or_none(
                (Event.id == interaction.data["custom_id"].split("_")[-1])
                & (Event.guild_id == interaction.guild_id)
            )
            deleted = 0
            if event and event.guild_id == interaction.guild_id:
                deleted = event.delete_instance()
            embed = self.embedGenerator.embed(
                title=(
                    locale_str("calendar_remove_success_title")
                    if deleted
                    else locale_str("calendar_remove_failure_title")
                ),
                description=(
                    locale_str("calendar_remove_success_message")
                    if deleted
                    else locale_str("calendar_remove_failure_notfound")
                ),
                color=discord.Color.green() if deleted else discord.Color.red(),
            )
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True,
                )

        event: Event = None
        try:
            if not query and not event_id:
                raise ValueError(
                    locale_str("calendar_remove_failure_neitherquerynorid")
                )
            if query and event_id:
                raise ValueError(
                    locale_str("calendar_remove_failure_bothqueryandeventid")
                )
            if query and not event_id:
                events = None
                try:
                    tempDate = datetime.strptime(query, "%d.%m.%Y")
                    events = Event.select().where(
                        (Event.date == tempDate)
                        & (Event.guild_id == interaction.guild_id)
                    )
                except:
                    events = Event.select().where(
                        (
                            (fn.Lower(Event.title).contains(query.lower()))
                            | (fn.Lower(Event.message).contains(query.lower()))
                        )
                        & (Event.guild_id == interaction.guild_id)
                    )
                # test
                for event in events:
                    print(event.title)
                # /test
                if not events:
                    raise ValueError(locale_str("calendar_remove_failure_notfound"))
                if len(events) > 5:
                    raise ValueError(locale_str("calendar_remove_failure_toomany"))
                if len(events) == 1:
                    view = ExtView(
                        translator=self.client.tree.translator,
                        locale=discord.Locale.polish,
                    )
                    view.add_item(
                        view.new_button(
                            style=discord.ButtonStyle.green,
                            label=locale_str("calendar_remove_approve"),
                            custom_id=f"calendar_remove_event_{events[0].id}",
                            callback=remove_event,
                        )
                    )

                    async def cancel_remove(interaction: discord.Interaction):
                        if interaction.user.guild_permissions.manage_events:
                            await interaction.message.delete()
                        else:
                            await interaction.followup.send(
                                await self.client.tree.translator.translate(
                                    locale_str("missing_permissions"),
                                    discord.Locale.polish,
                                )
                            )

                    view.add_item(
                        view.new_button(
                            style=discord.ButtonStyle.danger,
                            label=locale_str("calendar_remove_cancel"),
                            custom_id="calendar_remove_cancel",
                            callback=cancel_remove,
                        )
                    )

                    tempField = EventField(
                        translator=self.client.tree.translator,
                        locale=discord.Locale.polish,
                    )
                    await tempField._init(events[0])

                    embed = self.embedGenerator.embed(
                        title=locale_str("calendar_remove_approve_title"),
                        description=locale_str("calendar_remove_approve_description"),
                        color=discord.Color.orange(),
                        fields=[tempField],
                    )

                    await interaction.response.send_message(
                        embed=embed,
                        view=view,
                    )

                    return
                else:
                    view = ExtView(
                        translator=self.client.tree.translator,
                        locale=discord.Locale.polish,
                    )
                    embed = self.embedGenerator.embed(
                        title=locale_str("calendar_remove_choose_title"),
                        description=locale_str("calendar_remove_choose_description"),
                        color=discord.Color.blurple(),
                    )

                    for i, event in enumerate(events, start=1):
                        print(event.date, event.time)
                        embed.add_field(
                            name=str(i) + ". " + event.title,
                            value=(
                                f" <t:{int(datetime.timestamp(datetime.combine(event.date, event.time)))}:f>\n"
                                if event.time
                                else f" <t:{int(datetime.timestamp(datetime.combine(event.date, time(hour=12))))}:D>\n"
                            ),
                        )
                        view.add_item(
                            view.new_button(
                                style=discord.ButtonStyle.primary,
                                label=str(i)
                                + ". "
                                + (
                                    f"{event.title[:10]}..."
                                    if len(event.title) > 10
                                    else event.title
                                ),
                                custom_id=f"calendar_remove_event_{event.id}",
                                callback=remove_event,
                            )
                        )

                    await interaction.response.send_message(
                        embed=embed,
                        view=view,
                    )

                    return

            if event_id:
                event = Event.get_or_none(
                    (Event.id == event_id) & (Event.guild_id == interaction.guild_id)
                )
                if not event:
                    raise ValueError(locale_str("calendar_remove_failure_notfound"))
        except ValueError as e:
            await interaction.response.send_message(
                embed=self.embedGenerator.embed(
                    title=locale_str("calendar_remove_failure_title"),
                    description=e.args[0],
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        try:
            deleted = 0
            if event and event.guild_id == interaction.guild_id:
                deleted = event.delete_instance()
            embed = self.embedGenerator.embed(
                title=(
                    locale_str("calendar_remove_success_title")
                    if deleted
                    else locale_str("calendar_remove_failure_title")
                ),
                description=(
                    locale_str("calendar_remove_success_message")
                    if deleted
                    else locale_str("calendar_remove_failure_notfound")
                ),
                color=discord.Color.green() if deleted else discord.Color.red(),
            )
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True,
                )
        except Exception as e:
            embed = self.embedGenerator.embed(
                title=locale_str("calendar_remove_failure_title"),
                description=locale_str(
                    "calendar_remove_failure_message", error_name=type(e).__name__
                ),
                color=discord.Color.red(),
            )
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True,
                )

    @show_subgroup.command(
        name=locale_str("calendar_show_day"),
        description=locale_str("calendar_show_day_description"),
    )
    @app_commands.rename(
        date=locale_str("calendar_show_day_date"),
        two_rows=locale_str("calendar_show_day_tworows"),
    )
    @app_commands.describe(
        date=locale_str("calendar_show_day_date_description"),
        two_rows=locale_str("calendar_show_day_tworows_description"),
    )
    async def show_day(
        self,
        interaction: discord.Interaction,
        date: str,
        two_rows: Optional[bool] = False,
    ):
        date = date.replace("-", ".").replace("/", ".")
        try:
            formatted_date = datetime.strptime(date, "%d.%m.%Y")
            events = []

            for i, event in enumerate(
                Event.select()
                .where(
                    (Event.date == formatted_date)
                    & (Event.guild_id == interaction.guild_id)
                )
                .order_by(Event.time)
            ):
                tempEvent = EventField(
                    self.client.tree.translator, discord.Locale.polish
                )
                await tempEvent._init(event)
                events.append(tempEvent)
                if two_rows and i % 2 == 0:
                    events.append(
                        ExtEmbedGenerator.Field(
                            name="\u200b", value="\u200b", inline=False
                        )
                    )

            if two_rows and len(events) > 6:
                for event in events:
                    event.inline = True

            if len(events) > 0:
                embed = self.embedGenerator.embed(
                    title=await self.client.tree.translator.translate(
                        locale_str("calendar_show_day_title", date=date)
                    ),
                    fields=events,
                    color=discord.Color.blurple(),
                    thumbnail=self.client.user.avatar.url,
                    footer=await self.client.tree.translator.translate(
                        locale_str("calendar_show_week_footer"), discord.Locale.polish
                    ),
                )
            else:
                embed = self.embedGenerator.embed(
                    title=await self.client.tree.translator.translate(
                        locale_str("calendar_show_day_title", date=date)
                    ),
                    description=locale_str("calendar_show_day_noevents"),
                    color=discord.Color.blurple(),
                    thumbnail=self.client.user.avatar.url,
                )

            await interaction.response.send_message(
                embed=embed,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except ValueError:
            await interaction.response.send_message(
                embed=self.embedGenerator.embed(
                    title=locale_str("calendar_show_day_failure_title"),
                    description=locale_str("calendar_show_day_failure_invaliddate"),
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )

    @show_subgroup.command(
        name=locale_str("calendar_show_week"),
        description=locale_str("calendar_show_week_description"),
    )
    @app_commands.rename(
        date=locale_str("calendar_show_week_date"),
        week=locale_str("calendar_show_week_week"),
    )
    @app_commands.describe(
        date=locale_str("calendar_show_week_date_description"),
        week=locale_str("calendar_show_week_week_description"),
    )
    async def show_week(
        self,
        interaction: discord.Interaction,
        date: Optional[str] = None,
        week: Optional[int] = None,
    ):
        start_of_week: datetime = None
        try:
            if not date and week is None:
                start_of_week = datetime.combine(
                    datetime.now().date(), time(hour=0, minute=0, second=0)
                )
            if date and week:
                raise InvalidDateError(
                    locale_str("calendar_show_week_failure_bothdateandweek")
                )
            if date and not week:  # wybrano datę
                try:
                    start_of_week = datetime.strptime(date, "%d.%m.%Y")
                except:
                    raise InvalidDateError(
                        locale_str("calendar_show_week_failure_invaliddate")
                    )
            if not date and week is not None:  # wybrano numer tygodnia
                try:
                    start_of_week = datetime.fromisocalendar(
                        datetime.now().year, week, 1
                    )
                except:
                    raise InvalidDateError(
                        locale_str("calendar_show_week_failure_invalidweek")
                    )
        except InvalidDateError as e:
            await interaction.response.send_message(
                embed=self.embedGenerator.embed(
                    title=locale_str("calendar_show_week_failure_title"),
                    description=e.args[0],
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return
        end_of_week = start_of_week + timedelta(days=7)
        events = (
            Event.select()
            .where(
                (Event.date >= start_of_week)
                & (Event.date <= end_of_week)
                & (Event.guild_id == interaction.guild.id)
            )
            .order_by(Event.date, Event.time)
        )
        weekDays = []

        for event in events.group_by(Event.date):
            weekDay = DayField(self.client.tree.translator, discord.Locale.polish)
            await weekDay._init(
                event.date, events.where(Event.date == event.date), True
            )
            weekDays.append(weekDay)

        embed = self.embedGenerator.embed(
            title=await self.client.tree.translator.translate(
                locale_str(
                    "calendar_show_week_title",
                    date=await datetime_to_words(
                        self.client.tree.translator,
                        discord.Locale.polish,
                        start_of_week,
                    ),
                )
            ),
            color=discord.Color.blurple(),
            thumbnail=self.client.user.avatar.url,
        )

        if weekDays:
            for weekday in weekDays:
                embed.add_field(
                    name=weekday.name, value=weekday.value, inline=weekday.inline
                )
        else:
            embed.description = await self.client.tree.translator.translate(
                locale_str("calendar_show_week_noevents"), discord.Locale.polish
            )

        await interaction.response.send_message(
            embed=embed,
            allowed_mentions=discord.AllowedMentions.none(),
        )


async def setup(client: commands.Bot):
    await client.add_cog(Calendar(client))


class EventField(ExtEmbedGenerator.Field):
    def __init__(
        self,
        translator: JSONTranslator,
        locale: discord.Locale,
    ):
        self.translator = translator
        self.locale = locale

    async def _init(self, event: Event):
        self.field_title = f"◻️   {event.title}"
        self.field_desc = ""
        self.field_desc += (
            f" <t:{int(datetime.timestamp(datetime.combine(event.date, event.time)))}:f>\n"
            if event.time
            else f" <t:{int(datetime.timestamp(datetime.combine(event.date, time(hour=12))))}:D>\n"
        )
        self.field_desc += (
            "   📄 "
            + await self.translator.translate(
                locale_str(f"calendar_add_type_{event.event_type}"),
                self.locale,
            )
            + "\n"
        )
        self.field_desc += "   💬 " + event.message + "\n" if event.message else ""
        self.field_desc += (
            "   👥 "
            + await self.translator.translate(
                locale_str(
                    "calendar_show_week_weekday_appliesto", role_id=str(event.role_id)
                ),
                self.locale,
            )
            if event.role_id
            else " "
        )

        super().__init__(name=self.field_title, value=self.field_desc, inline=False)


class DayField(ExtEmbedGenerator.Field):
    def __init__(
        self,
        translator: JSONTranslator,
        locale: discord.Locale,
    ):
        self.translator = translator
        self.locale = locale

    async def _init(
        self, date: datetime, events: list[Event], inline: Optional[bool] = False
    ):
        self.name = (
            await datetime_to_words(
                translator=self.translator,
                locale=discord.Locale.polish,
                date=date,
            )
            + " ("
            + await self.translator.translate(
                locale_str(f"weekday_{date.weekday()}"), self.locale
            )
            + ")"
        )
        self.value = "\n".join(
            [
                (
                    f"• {event.title} o <t:{int(datetime.timestamp(datetime.combine(event.date, event.time)))}:t>"
                    if event.time
                    else f"• {event.title}"
                )
                for event in events
            ]
        )
        self.inline = inline
        super().__init__(name=self.name, value=self.value, inline=False)


async def datetime_to_words(
    translator: JSONTranslator, locale: discord.Locale, date: datetime
) -> str:
    return f"{date.day} {await translator.translate(string=locale_str(f'month_{date.month}'), locale=locale)} {date.year}"
