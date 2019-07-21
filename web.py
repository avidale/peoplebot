
import tables

from autolink import linkify
from flask import Flask, render_template


app = Flask(__name__)


@app.template_filter('linkify_filter')
def linkify_filter(s):
    return linkify(s)


@app.route('/')
def home():
    return "На этой страничке пока ничего нету. Идите в t.me/gaggle_bot!"


@app.route('/community/<chat_id>')
def peoplebook_for_event(chat_id):
    try:
        chat_id = int(chat_id)
    except ValueError:
        pass
    the_chat = tables.chats.find_one({'chat_id': chat_id})
    if the_chat is None:
        return 'Такого сообщества ({}) не найдено!'.format(chat_id)
    profiles = list(tables.peoplebook.find({'chat_id': chat_id}))
    if len(profiles) == 0:
        return 'В сообществе "{}" пока никто не заполнил анкеты'.format(the_chat.get('title') or chat_id)
    return render_template(
        'peoplebook.html',
        title=the_chat.get('title', 'Пиплбук встречи'),
        profiles=profiles
    )


@app.route('/community/<chat_id>/person/<user_id>')
def peoplebook_for_person(chat_id, user_id):
    the_profile = tables.peoplebook.find_one({'user_id': user_id, 'chat_id': chat_id})
    if the_profile is None:
        return 'Такого профиля не найдено!'
    return render_template('single_person.html', profile=the_profile)
