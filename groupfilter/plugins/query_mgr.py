from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from pyrogram.errors import QueryIdInvalid
from groupfilter import PM_SUPPORT, GROUP_SUPPORT, LOGGER


# @Client.on_callback_query(group=1)
# async def query_hndlr(bot, query):
#     if not query.message:
#         LOGGER.warning("Query handler received a message without a message object.")
#         return
#     LOGGER.info(
#         f"Query received from {query.message.chat.id} | {query.message.chat.title} | {query.from_user.first_name} | {query.from_user.id} | {query.data}"
#     )

if not PM_SUPPORT:

    @Client.on_callback_query(filters.regex(r"^pmfile#(.+)$"))
    async def get_pm_files_qry_hndlr(bot, query):
        if not query.message:
            return
        if isinstance(query, CallbackQuery):
            try:
                await query.answer("PM mode is disabled", cache_time=10)
            except QueryIdInvalid:
                return

    @Client.on_callback_query(filters.regex(r"^(nxt_pgg|prev_pgg) \d+ \d+ .+$"))
    async def pages_pm_qry_hndlr(bot, query):
        if not query.message:
            return
        if isinstance(query, CallbackQuery):
            try:
                await query.answer("PM mode is disabled", cache_time=10)
            except QueryIdInvalid:
                return


if not GROUP_SUPPORT:

    @Client.on_callback_query(filters.regex(r"^file#(.+)#(\d+)$"))
    async def get_files_qry_hndlr(bot, query):
        if not query.message:
            return
        if isinstance(query, CallbackQuery):
            try:
                await query.answer("Group mode is disabled", cache_time=10)
            except QueryIdInvalid:
                return

    @Client.on_callback_query(filters.regex(r"^(nxt_pg|prev_pg) \d+ \d+ .+$"))
    async def pages_qry_hndlr(bot, query):
        if not query.message:
            return
        if isinstance(query, CallbackQuery):
            try:
                await query.answer("Group mode is disabled", cache_time=10)
            except QueryIdInvalid:
                return
