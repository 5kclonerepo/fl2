from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from groupfilter.db.settings_sql import get_search_settings, change_search_settings
from groupfilter.utils.constants import SET_MSG
from groupfilter.utils.util_support import is_admin
from groupfilter import ADMINS


@Client.on_message(filters.command(["settings"]) & filters.user(ADMINS))
async def user_settings(bot, message):
    group_id = message.chat.id
    set_kb = await find_search_settings(group_id)
    await message.reply(
        text=SET_MSG,
        reply_markup=set_kb,
    )


@Client.on_callback_query(filters.regex(r"^prec (.+)$"))
async def set_precise_mode(bot, query):
    await query.answer("Disabled permanently")
    return
    user_id = query.from_user.id
    if not is_admin(user_id):
        query.answer(text="You are not allowed to use this command.", show_alert=True)
        return
    group_id = query.chat.id
    prsc_mode = query.data.split()[1]
    if prsc_mode == "on":
        await change_search_settings(group_id, precise_mode=True)
    if prsc_mode == "off":
        await change_search_settings(group_id, precise_mode=False)
    if prsc_mode == "md":
        await query.answer(text="Toggle Precise Search ON/OFF", show_alert=False)
        return

    set_kb = await find_search_settings(group_id)

    await query.message.edit(
        text=SET_MSG,
        reply_markup=set_kb,
    )


@Client.on_callback_query(filters.regex(r"^res (.+)$"))
async def set_list_mode(bot, query):
    user_id = query.from_user.id
    if not is_admin(user_id):
        query.answer(text="You are not allowed to use this command.", show_alert=True)
        return
    group_id = query.message.chat.id
    result_mode = query.data.split()[1]
    if result_mode == "btnn":
        await change_search_settings(
            group_id, button_mode=True, link_mode=False, list_mode=False
        )
    if result_mode == "link":
        await change_search_settings(
            group_id, button_mode=False, link_mode=True, list_mode=False
        )
    if result_mode == "list":
        await change_search_settings(
            group_id, button_mode=False, link_mode=False, list_mode=True
        )
    if result_mode == "mode":
        await query.answer(text="Toggle Button/Link/List Mode", show_alert=False)
        return

    set_kb = await find_search_settings(group_id)

    await query.message.edit(
        text=SET_MSG,
        reply_markup=set_kb,
    )


async def find_search_settings(group_id):
    search_settings = await get_search_settings(group_id)

    kb = [
        InlineKeyboardButton("[Precise Mode]:", callback_data="prec md"),
    ]

    on_kb = InlineKeyboardButton("❌ Disabled", callback_data="prec on")
    off_kb = InlineKeyboardButton("✅ Enabled", callback_data="prec off")

    if search_settings:
        precise_mode = search_settings.precise_mode
        if precise_mode:
            precise_mode = "Enabled"
            kb.append(off_kb)
        else:
            precise_mode = "Disabled"
            kb.append(on_kb)
    else:
        await change_search_settings(group_id)
        precise_mode = "Disabled"
        kb.append(on_kb)

    bkb = [
        InlineKeyboardButton("[Result Mode]:", callback_data="res mode"),
    ]

    btn_kb = InlineKeyboardButton("📃 List", callback_data="res btnn")
    link_kb = InlineKeyboardButton("🔳 Button", callback_data="res link")
    list_kb = InlineKeyboardButton("🔗 HyperLink", callback_data="res list")

    if search_settings:
        button_mode = search_settings.button_mode
        link_mode = search_settings.link_mode
        list_mode = search_settings.list_mode
        if button_mode:
            bkb.append(link_kb)
        elif link_mode:
            bkb.append(list_kb)
        elif list_mode:
            bkb.append(btn_kb)
        else:
            await change_search_settings(group_id, button_mode=True)
            bkb.append(list_kb)
    else:
        await change_search_settings(group_id, button_mode=True)
        bkb.append(btn_kb)

    set_kb = InlineKeyboardMarkup([kb, bkb])

    return set_kb
