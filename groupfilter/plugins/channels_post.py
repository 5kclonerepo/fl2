import re
from imdb import Cinemagoer
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from groupfilter import (
    LOGGER,
    ADMINS,
    POST_CHANNELS,
    MAX_LIST_ELM,
    LONG_IMDB_DESCRIPTION,
)

LANGUAGES = {
    "mal": "Malayalam",
    "tam": "Tamil",
    "kan": "Kannada",
    "hin": "Hindi",
    "eng": "English",
    "tel": "Telugu",
    "kor": "Korean",
    "chi": "Chinese",
    "jap": "Japanese",
    "multi": "Multi-Language",
}
FONT = ["ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘᴏ̨ʀsᴛᴜᴠᴡxʏᴢ𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"]

def textchanger(text):
    if not text:
        return text
    regular_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    font_chars = "".join(FONT)
    translation_table = str.maketrans(regular_chars, font_chars)
    converted_text = text.translate(translation_table)
    return converted_text

temp = {}
imdb = Cinemagoer()


@Client.on_message(filters.command("channelpost") & filters.user(ADMINS))
async def channelpost(bot, message):
    if not POST_CHANNELS:
        return await message.reply_text("No channels found to post to.")
    try:
        query = message.text.split(" ", 1)
        if len(query) < 2:
            return await message.reply_text(
                "<b>Usage:</b> /channelpost movie_name\n\nExample: /channelpost Money Heist"
            )
        file_name = query[1].strip()
        movie_details = await get_poster(file_name)
        if not movie_details:
            return await message.reply_text(
                f"No results found for {file_name} on IMDB."
            )
        language_buttons = []
        for code, lang in LANGUAGES.items():
            language_buttons.append(
                [InlineKeyboardButton(lang, callback_data=f"lang_{code}_{file_name}")]
            )
        language_markup = InlineKeyboardMarkup(language_buttons)
        temp["current_movie"] = {"details": movie_details, "name": file_name}
        await message.reply_text(
            "Select the languages for this movie:", reply_markup=language_markup
        )
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
        LOGGER.error(f"Error in channelpost: {str(e)}")


@Client.on_callback_query(filters.regex(r"^lang_"))
async def language_selection(bot, query):
    await query.answer()
    _, lang_code, file_name = query.data.split("_")
    if "selected_languages" not in temp:
        temp["selected_languages"] = []
    if lang_code == "multi":
        temp["selected_languages"] = ["Multi-Language"]
    elif lang_code in LANGUAGES:
        if LANGUAGES[lang_code] in temp["selected_languages"]:
            temp["selected_languages"].remove(LANGUAGES[lang_code])
        else:
            if "Multi-Language" in temp["selected_languages"]:
                temp["selected_languages"].remove("Multi-Language")
            temp["selected_languages"].append(LANGUAGES[lang_code])
    language_buttons = []
    for code, lang in LANGUAGES.items():
        button_text = f"✅ {lang}" if lang in temp["selected_languages"] else lang
        language_buttons.append(
            [
                InlineKeyboardButton(
                    button_text, callback_data=f"lang_{code}_{file_name}"
                )
            ]
        )
    language_buttons.append(
        [InlineKeyboardButton("Proceed ➡️", callback_data=f"proceed_{file_name}")]
    )
    language_markup = InlineKeyboardMarkup(language_buttons)
    await query.message.edit_text(
        "Select the languages for this movie:", reply_markup=language_markup
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^proceed_"))
async def preview_movie_details(bot, query):
    await query.answer("Please confirm...")
    movie_details = temp["current_movie"]["details"]
    file_name = temp["current_movie"]["name"]
    selected_languages = (
        ", ".join(temp["selected_languages"]) if "selected_languages" in temp else "N/A"
    )
    movie_title = movie_details.get("title", "N/A")
    rating = movie_details.get("rating", "N/A")
    genres = movie_details.get("genres", "N/A")
    year = movie_details.get("year", "N/A")
    preview_text = (
        f"✅ {textchanger(movie_title)} {textchanger(str(year))}\n\n"
        f"🎙 {textchanger(selected_languages)}\n\n"
        f"📽 Genre: {textchanger(genres)}"
    )
    confirm_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Yes, Post", callback_data=f"post_yes_{file_name}")],
            [InlineKeyboardButton("❌ No, Cancel", callback_data=f"post_no_{file_name}")],
        ]
    )
    await query.message.edit_text(
        preview_text, reply_markup=confirm_markup, parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^post_(yes|no)_"))
async def post_to_channels(bot, query):
    action, file_name = query.data.split("_")[1], query.data.split("_")[2]
    if action == "yes":
        await query.answer("♻️ Pᴏsᴛɪɴɢ Iɴ Tʜᴇ Cʜᴀɴɴᴇʟ...")
        movie_details = await get_poster(file_name)
        if not movie_details:
            return await query.message.reply_text(
                f"No results found for {file_name} on IMDB."
            )
        movie_title = movie_details.get("title", "N/A")
        rating = movie_details.get("rating", "N/A")
        genres = movie_details.get("genres", "N/A")
        year = movie_details.get("year", "N/A")
        selected_languages = (
            ", ".join(temp["selected_languages"])
            if "selected_languages" in temp
            else "N/A"
        )
        custom_link = f"https://t.me/{bot.me.username}?start=search_{file_name.replace(' ', '_').lower()}"
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Get the File 🔎", url=custom_link)]]
        )
        caption = (
            f"<b>✅ {textchanger(movie_title)} ({textchanger(str(year))})</b>\n\n"
            f"<b>🎙️ Audio: {textchanger(selected_languages)}</b>\n\n"
            f"<b>📽️ Genres: {textchanger(genres)}</b>"
        )
      if rating:
         caption += f"\n\n<b>⭐ Rating:</b> {textchanger(rating)}"
      
        for channel_id in POST_CHANNELS:
            try:
                await bot.send_message(
                    chat_id=channel_id,
                    text=caption,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML,
                )
            except Exception as e:
                await query.message.reply_text(
                    f"Error posting to channel {channel_id}: {str(e)}"
                )
                LOGGER.error(f"Error posting to channel {channel_id}: {str(e)}")
        await query.message.edit_text("✅ Mᴏᴠɪᴇ Dᴇᴛᴀɪʟs Sᴜᴄᴄᴇssғᴜʟʟʏ Pᴏsᴛᴇᴅ Iɴ Tʜᴇ Cʜᴀɴɴᴇʟ....")
    elif action == "no":
        await query.answer("Cancelling...")
        await query.message.edit_text("❌ Mᴏᴠɪᴇ Dᴇᴛᴀɪʟs Cᴀɴɴᴏᴛ Bᴇ Pᴏsᴛᴇᴅ Iɴ Tʜᴇ Cʜᴀɴɴᴇʟ....")


async def get_poster(query, bulk=False, id=False, file=None):
    if not id:
        query = (query.strip()).lower()
        title = query
        year = re.findall(r"[1-2]\d{3}$", query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r"[1-2]\d{3}", file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])
        else:
            year = None
        movieid = imdb.search_movie(title.lower(), results=10)
        if not movieid:
            return None
        if year:
            filtered = list(filter(lambda k: str(k.get("year")) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid
        movieid = list(
            filter(lambda k: k.get("kind") in ["movie", "tv series"], filtered)
        )
        if not movieid:
            movieid = filtered
        if bulk:
            return movieid
        movieid = movieid[0].movieID
    else:
        movieid = query
    movie = imdb.get_movie(movieid)
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get("plot")
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get("plot outline")
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."

    return {
        "title": movie.get("title"),
        "votes": movie.get("votes"),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get("box office"),
        "localized_title": movie.get("localized title"),
        "kind": movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer": list_to_str(movie.get("writer")),
        "producer": list_to_str(movie.get("producer")),
        "composer": list_to_str(movie.get("composer")),
        "cinematographer": list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        "release_date": date,Add commentMore actions
        "year": movie.get("year"),
        "genres": list_to_str(movie.get("genres")),
        "poster": movie.get("full-size cover url"),
        "plot": plot,Add commentMore actions
        "rating": str(movie.get("rating")),
        "url": f"https://www.imdb.com/title/tt{movieid}",
    }


def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[: int(MAX_LIST_ELM)]
        return " ".join(f"{elem}, " for elem in k)
    else:
        return " ".join(f"{elem}, " for elem in k)
