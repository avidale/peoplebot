# -*- coding: utf-8 -*-
import argparse
import json
import os
import telebot

import tables

from flask import request
from web import app as server

TOKEN = os.environ['TOKEN']
bot = telebot.TeleBot(TOKEN)

CLICKED_BY = []


TELEBOT_URL = 'telebot_webhook/'
BASE_URL = 'https://piplbot.herokuapp.com/'


@server.route("/" + TELEBOT_URL)
def web_hook():
    bot.remove_webhook()
    bot.set_webhook(url=BASE_URL + TELEBOT_URL + TOKEN)
    return "!", 200


@bot.message_handler(
    func=lambda message: message.chat.type != "private",
    content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker' 'new_chat_members']
)
def register_user_in_public_chat(msg):
    cid = msg.chat.id
    mid = msg.message_id
    uid = msg.from_user.id
    if msg.chat.type != "private":
        the_chat = tables.chats.find_one({'chat_id': cid})
        if the_chat is None:
            tables.chats.insert_one({'chat_id': cid, 'title': msg.chat.title or 'Chat {}'.format(cid)})
        user_in_chat = tables.membership.find_one({'user_id': uid, 'chat_id': cid})
        if user_in_chat is None:
            tables.membership.insert_one({'user_id': uid, 'chat_id': cid})
            # do not reply if not called explicitly
            # bot.reply_to(msg, "О, теперь я добавляю юзера {} в чат {}".format(uid, cid))
        else:
            # do not reply if not called explicitly
            # bot.reply_to(msg, "О, юзер {}, я вас уже видел в чате {}".format(uid, cid))
            pass


@bot.message_handler(commands=['choose_event'])
@bot.message_handler(regexp='.*(выбрать|выбери|покажи|список) (событи|встреч|чат|сообществ).*')
def command_choose_chat(msg):
    cid = msg.chat.id
    mid = msg.message_id
    uid = msg.from_user.id
    if msg.chat.type == "private":
        chat_ids = [c['chat_id'] for c in tables.membership.find({'user_id': uid})]
        if len(chat_ids) > 0:
            click_kb = telebot.types.InlineKeyboardMarkup()
            for chat_id in chat_ids:
                cb_data = {"chat_id": chat_id, "event": "choose_chat"}
                chat_data = tables.chats.find_one({'chat_id': chat_id})
                click_button = telebot.types.InlineKeyboardButton(chat_data['title'], callback_data=json.dumps(cb_data))
                click_kb.row(click_button)
            bot.send_message(cid, "Вот чаты, где я вас видел. Выбирайте!", reply_markup=click_kb)
        else:
            bot.send_message(cid, "Я пока не заметил вас ни в одном общем чате, где я админ. Правда.")


@bot.callback_query_handler(func=lambda call: 'choose_chat' in call.data)
def callback_choose_chat(call):
    cid = call.message.chat.id
    cb_data = json.loads(call.data)
    bot.send_message(cid, 'Отлично, вы выбрали комнату {}!'.format(cb_data['chat_id']))
    # todo: put it into user state


@bot.message_handler(func=lambda message: message.chat.type != "private", content_types=[
    'audio', 'video', 'document', 'text', 'location', 'contact', 'sticker' 'new_chat_members'
])
def bullshit(msg):
    uid = msg.from_user.id
    chat_ids = [c['chat_id'] for c in tables.membership.find({'user_id': uid})]
    bot.reply_to(msg, "Я вас вижу, юзер {}. Вы состоите в чатах {}.".format(uid, chat_ids))


@server.route('/' + TELEBOT_URL + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


parser = argparse.ArgumentParser(description='Run the bot')
parser.add_argument('--poll', action='store_true')


def main():
    args = parser.parse_args()
    if args.poll:
        bot.remove_webhook()
        bot.polling()
    else:
        web_hook()
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


if __name__ == '__main__':
    main()
