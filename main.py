import signal
import setting, words
import sys
import asyncio
import random
import telepot
import telepot.async
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent

from snuMenu import *

"""
skeleton from https://github.com/nickoala/telepot/blob/master/examples/skeletona_route.py

An example that demonstrates the use of custom keyboard and inline keyboard, and their various buttons.

Before running this example, remember to `/setinline` and `/setinlinefeedback` to enable inline mode for your bot.

The bot works like this:

- First, you send it one of these 4 characters - `c`, `i`, `h`, `f` - and it replies accordingly:
    - `c` - a custom keyboard with various buttons
    - `i` - an inline keyboard with various buttons
    - `h` - hide custom keyboard
    - `f` - force reply
- Press various buttons to see their effects
- Within inline mode, what you get back depends on the **last character** of the query:
    - `a` - a list of articles
    - `p` - a list of photos
    - `b` - to see a button above the inline results to switch back to a private chat with the bot
- Play around with the bot for an afternoon ...
"""

message_with_inline_keyboard = None

async def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat:', content_type, chat_type, chat_id)

    if content_type != 'text':
        return
    command = msg['text']
    print(command)
    

    if command == "/도움":
        await bot.sendMessage(chat_id, words.help)
    if command[:3] == "/식단":
        result = snuMenu(command[3:])
        await bot.sendMessage(chat_id, result.getMenu())

    elif command == "/날씨":
        # 날씨 출력
        await bot.sendMessage(chat_id, "날씨를 출력합니다.")

    #elif command == "/놀자":
        # 놀기
        

    elif command == '/c':
        markup = ReplyKeyboardMarkup(keyboard=[
                     ['Plain text', KeyboardButton(text='Text only')],
                     [dict(text='Phone', request_contact=True), KeyboardButton(text='Location', request_location=True)],
                 ])
        await bot.sendMessage(chat_id, 'Custom keyboard with various buttons', reply_markup=markup)
    elif command == '/i':
        markup = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text='Telegram URL', url='https://core.telegram.org/')],
                     [InlineKeyboardButton(text='Callback - show notification', callback_data='notification')],
                     [dict(text='Callback - show alert', callback_data='alert')],
                     [InlineKeyboardButton(text='Callback - edit message', callback_data='edit')],
                     [dict(text='Switch to using bot inline', switch_inline_query='initial query')],
                 ])

        global message_with_inline_keyboard
        message_with_inline_keyboard = await bot.sendMessage(chat_id, 'Inline keyboard with various buttons', reply_markup=markup)
    elif command == '/h':
        markup = ReplyKeyboardHide()
        await bot.sendMessage(chat_id, 'Hide custom keyboard', reply_markup=markup)
    elif command == '/f':
        markup = ForceReply()
        await bot.sendMessage(chat_id, 'Force reply', reply_markup=markup)

async def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, data)

    if data == 'notification':
        await bot.answerCallbackQuery(query_id, text='Notification at top of screen')
    elif data == 'alert':
        await bot.answerCallbackQuery(query_id, text='Alert!', show_alert=True)
    elif data == 'edit':
        global message_with_inline_keyboard

        if message_with_inline_keyboard:
            msg_idf = telepot.message_identifier(message_with_inline_keyboard)
            await bot.editMessageText(msg_idf, 'NEW MESSAGE HERE!!!!!')
        else:
            await bot.answerCallbackQuery(query_id, text='No previous message to edit')

def on_inline_query(msg):
    def compute():
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        print('Computing for: %s' % query_string)

        articles = [InlineQueryResultArticle(
                        id='abcde', title='Telegram', input_message_content=InputTextMessageContent(message_text='Telegram is a messaging app')),
                    dict(type='article',
                        id='fghij', title='Google', input_message_content=dict(message_text='Google is a search engine'))]

        photo1_url = 'https://core.telegram.org/file/811140934/1/tbDSLHSaijc/fdcc7b6d5fb3354adf'
        photo2_url = 'https://www.telegram.org/img/t_logo.png'
        photos = [InlineQueryResultPhoto(
                      id='12345', photo_url=photo1_url, thumb_url=photo1_url),
                  dict(type='photo',
                      id='67890', photo_url=photo2_url, thumb_url=photo2_url)]

        result_type = query_string[-1:].lower()

        if result_type == 'a':
            return articles
        elif result_type == 'p':
            return photos
        else:
            results = articles if random.randint(0,1) else photos
            if result_type == 'b':
                return dict(results=results, switch_pm_text='Back to Bot', switch_pm_parameter='Optional start parameter')
            else:
                return dict(results=results)

    answerer.answer(msg, compute)

def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print('Chosen Inline Result:', result_id, from_id, query_string)


TOKEN = setting.token  # get token from command-line

bot = telepot.async.Bot(TOKEN)
answerer = telepot.async.helper.Answerer(bot)

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop({'chat': on_chat_message,
                                   'callback_query': on_callback_query,
                                   'inline_query': on_inline_query,
                                   'chosen_inline_result': on_chosen_inline_result}))

# Handle ^C gracefully
def signal_handler(signal, frame):
    print('Bye!')
    exit(0)
signal.signal(signal.SIGINT, signal_handler)


print('SNUBot is on its way!')
loop.run_forever()
