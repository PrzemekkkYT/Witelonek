from datetime import datetime
import json
from typing import Optional, Any
import logging
from colored import fg, attr

# discord import
import discord
from discord.app_commands import locale_str, TranslationContextTypes, Translator
from discord.app_commands.translator import OtherTranslationContext
from discord.enums import Locale

logger = logging.getLogger(__name__)


class JSONTranslator(Translator):
    def __init__(self):
        self.translations_path = "./langs.json"
        self.translations = None

    async def load(self) -> None:
        with open(self.translations_path, "r", encoding="utf-8") as f:
            self.translations = json.load(f)
        print("translations loaded")

    async def unload(self) -> None:
        self.translations = None

    async def translate(
        self,
        string: locale_str,
        locale: Locale = Locale.polish,
        context: Optional[TranslationContextTypes] = OtherTranslationContext,
    ) -> Optional[str]:
        return self.translate_sync(string, locale, context)

    def translate_sync(
        self,
        string: locale_str,
        locale: Locale = Locale.polish,
        context: Optional[TranslationContextTypes] = OtherTranslationContext,
    ):
        if self.translations is None:
            return str(string)

        if str(locale) not in self.translations:
            locale = Locale.polish

        if str(string) not in self.translations[str(locale)]:
            return str(string)

        ret_string = self.translations[str(locale)][str(string)]
        for arg, val in string.extras.items():
            ret_string = ret_string.replace(f"{{{arg}}}", str(val))

        return ret_string


def pretty_traceback(error: BaseException, comment=""):
    file = error.__traceback__.tb_frame.f_code.co_filename
    line = error.__traceback__.tb_lineno
    # tb = "".join(traceback.format_exception_only(error))
    tb = str(error.__class__).replace("<class '", "").replace("'>", "")
    output = (
        f"{fg('red_1')}Error in {fg('red')}{file}{fg('red_1')} on line "
        f"{fg('red')}{line}{fg('red_1')}:\n  {tb}: {fg('red')}{error}{attr('reset')}"
    )
    if comment != "":
        output = (
            output
            + f"\n{fg('blue_1')}Additional comment: {fg('blue')}{comment}{attr('reset')}"
        )
    return output


def small_traceback(error: BaseException, comment=""):
    file = error.__traceback__.tb_frame.f_code.co_filename
    line = error.__traceback__.tb_lineno
    # tb = "".join(traceback.format_exception_only(error))
    tb = str(error.__class__).replace("<class '", "").replace("'>", "")
    output = f"Error in {file} on line {line}:\n" f"{tb}: {error}"
    if comment != "":
        output = output + f"\nAdditional comment: {comment}"
    return output


def keys_exists(element: dict, keys: tuple, returntype: str = ""):
    """
    Check if *keys (nested) exists in `element` (dict).

    returntype:
        `result`: returns items of last key
        `element`: return full element
        anything else: returns if key exists [True/False]
    """
    try:
        if not isinstance(element, dict):
            raise AttributeError("keys_exists() expects dict as first argument.")
        if not isinstance(keys, tuple):
            raise AttributeError("keys_exists() expects tuple as second argument.")

        _element = element
        for key in keys:
            try:
                _element = _element[key]
                # print(_element)
            except (KeyError, IndexError, TypeError):
                # print(pretty_traceback(error))
                # print(f"key: {key}")
                match returntype:
                    case "result":
                        return None
                    case "element":
                        return []
                    case _:
                        return False
        match returntype:
            case "result":
                return _element
            case "element":
                return element
            case _:
                return True

    except Exception as error:
        logger.error(small_traceback(error))
        # print(error)
        # traceback.print_stack()
        # print("=========")


def catch_err(func, *args, handle=lambda e: e, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return handle(e)
