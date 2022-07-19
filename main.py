import threading
import time

import pytz
import re
from string import Template

import schedule
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import config as conf
import text_templs
import telebot
from typing import List
# from decouple import config

from config import REPEAT_PERIOD
from datetime import timedelta, datetime
from storage import UsersDB, RSSFeed
from rssparser import RSSParser

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
BOT_TOKEN = conf.api_token

bot = telebot.TeleBot(BOT_TOKEN)
users_db = UsersDB()


keyboard_user = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_user.row(text_templs.btn_start_1)
keyboard_user.row(text_templs.btn_start_2, text_templs.btn_start_3,
                  text_templs.btn_start_4)
keyboard_user.one_time_keyboard = True

keyboard_rss = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
keyboard_rss.add(text_templs.btn_rsslist_1, text_templs.btn_rsslist_2, text_templs.btn_rsslist_3, text_templs.btn_back)
keyboard_rss.one_time_keyboard = True

keyboard_setting = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
keyboard_setting.add(text_templs.btn_setting_1, text_templs.btn_setting_2, text_templs.btn_back)
keyboard_setting.one_time_keyboard = True


def look_for_jobs_cb(*args):
    user_obj = users_db.get_user(args[0])
    rss_list: List[RSSFeed] = users_db.get_user_rss(args[0])
    show_summary = user_obj["settings"].get("show_summary", "no")
    show_summary = False if show_summary == "no" else True
    chat_id = user_obj["settings"].get("chat_id", args[0])
    now = datetime.utcnow()
    date_start = now - timedelta(minutes=args[1])
    for rss in rss_list:
        posts = RSSParser(rss['url'], user_obj).parse_rss()
        posts = posts[::-1]
        for post in posts:
            if post.published > date_start.replace(tzinfo=pytz.utc):

                inline_btn = InlineKeyboardButton('LINK', url=post.url)
                inline_kb1 = InlineKeyboardMarkup().add(inline_btn)

                message = f"#{rss['name']}\n{post.to_str(show_summary)}"
                bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML", reply_markup=inline_kb1)


def add_job_to_queue(user_id, interval, first):
    job_name = f"job_{user_id}"
    schedule.every(interval).minutes.do(look_for_jobs_cb, user_id, first).tag(job_name)
    schedule.run_pending()
    # all_jobs = schedule.get_jobs()
    # print(all_jobs)

def check_for_update():
    while True:
        schedule.run_pending()
        all_jobs = schedule.get_jobs()
        # print(all_jobs)
        # print('watching..')
        time.sleep(1)


def del_job_schedule(user_id):
    job_name = f"job_{user_id}"
    schedule.clear(job_name)


@bot.message_handler(commands=['start'])
def start_message(message):
    if message.from_user.id == message.chat.id:
        users_db.get_user(message.chat.id)
        state = users_db.get_user_state(message.chat.id)
        state = "✅" if state == 1 else "❌"
        bot.send_message(
            message.chat.id,
            text_templs.templ_start,
            parse_mode="Markdown"
        )
        bot.send_message(
            message.chat.id,
            Template(text_templs.templ_main).substitute(working=state),
            reply_markup=keyboard_user
        )


@bot.message_handler(content_types='text')
def answer_message(message):
    if message.text == text_templs.btn_start_1:
        state = users_db.get_user_state(message.chat.id)
        if state == 1:
            del_job_schedule(message.chat.id)
            state = 0
        else:
            add_job_to_queue(
                message.chat.id,
                REPEAT_PERIOD,
                REPEAT_PERIOD
            )
            state = 1
        users_db.set_user_state(message.chat.id, state)
        state = "✅" if state == 1 else "❌"
        bot.send_message(
            message.chat.id,
            Template(text_templs.templ_main).substitute(working=state),
            reply_markup=keyboard_user
        )
    elif message.text == text_templs.btn_start_2:
        # add rss links for user
        rss_links = users_db.get_user_rss(message.chat.id)
        text_links = ''
        if len(rss_links) > 0:
            for rss in rss_links:
                text_links += Template(text_templs.templ_list_rss_link).substitute(
                    link_title=rss['name'], link=rss['url']
                )
                # print(text_links)
        else:
            text_links += text_templs.templ_list_rss_no
        str1 = ", "
        filters = users_db.get_user_filters(message.chat.id)
        text_filters = Template(text_templs.templ_filters).substitute(
                    add_skills=str1.join(filters['add_skills']), exclude_countries=str1.join(filters['exclude_countries']))
        # print(text_templs.templ_menu + text_templs.templ_list_rss + text_links + text_filters)

        bot.send_message(
            message.chat.id,
            text_templs.templ_menu + text_templs.templ_list_rss + text_links + text_filters,
            reply_markup=keyboard_rss, parse_mode="Markdown"
        )
    elif message.text == text_templs.btn_start_3:
        setting = users_db.get_user_settings(message.chat.id)
        if setting["show_summary"] == 'yes':
            text = '✅'
        else:
            text = '❌'
        bot.send_message(
            message.chat.id,
            Template(text_templs.templ_setting).substitute(
                show_summary=text, chat_id=setting["chat"]
            ),
            reply_markup=keyboard_setting
        )
    elif message.text == text_templs.btn_start_4:
        # nothing to get
        bot.send_message(
            message.chat.id,
            text_templs.templ_help,
            reply_markup=keyboard_user,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    elif message.text == text_templs.btn_rsslist_1:
        # nothing to get
        bot.send_message(
            message.chat.id,
            text_templs.templ_list_rssadd,
            reply_markup=None
        )
    elif message.text == text_templs.btn_rsslist_2:
        # nothing to get
        bot.send_message(
            message.chat.id,
            text_templs.templ_list_rss_edit,
            reply_markup=None
        )
    elif message.text == text_templs.btn_rsslist_3:
        # nothing to get
        bot.send_message(
            message.chat.id,
            text_templs.templ_list_rssdelete,
            reply_markup=None
        )
    elif message.text == text_templs.btn_setting_1:
        # set setting
        setting = users_db.get_user_settings(message.chat.id)
        if setting["show_summary"] == 'yes':
            show_summary = 'no'
            text = '❌'
        else:
            show_summary = 'yes'
            text = '✅'
        users_db.set_user_settings(message.chat.id, "show_summary", show_summary)
        bot.send_message(
            message.chat.id,
            Template(text_templs.templ_setting).substitute(
                show_summary=text, chat_id=setting["chat"]
            ),
            reply_markup=keyboard_setting
        )
    elif message.text == text_templs.btn_setting_2:
        # nothing to get
        bot.send_message(
            message.chat.id,
            text_templs.templ_send_chat,
            reply_markup=None
        )
    elif message.text == text_templs.btn_back:
        # as start msg
        users_db.get_user(message.chat.id)
        state = users_db.get_user_state(message.chat.id)
        state = "✅" if state == 1 else "❌"
        bot.send_message(
            message.chat.id,
            Template(text_templs.templ_main).substitute(working=state),
            reply_markup=keyboard_user
        )
    elif (message.text.split()[0]).lower() == text_templs.text_command_1:
        regex_url = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        info = message.text.split(' ')
        if len(info) == 3:
            rss_url = info[2]
            if re.match(regex_url, rss_url) is not None:
                rss_name = info[1]
                rss_feed = RSSFeed(rss_name, rss_url)
                users_db.add_user_rss(message.chat.id, rss_feed)
                bot.send_message(
                    message.chat.id,
                    text_templs.templ_list_rssadd_good
                )
            else:
                bot.send_message(
                    message.chat.id,
                    text_templs.templ_list_rssadd_bad_link
                )
        else:
            bot.send_message(
                message.chat.id,
                text_templs.templ_list_rssadd_bad_command
            )
    elif (message.text.split()[0]).lower() == text_templs.text_command_2:
        info = message.text.split(' ')
        if len(info) == 2:
            users_db.delete_user_rss(message.chat.id, info[1])
            bot.send_message(
                message.chat.id,
                text_templs.templ_list_rssdelete_good
            )
        else:
            bot.send_message(
                message.chat.id,
                text_templs.templ_list_rssdelete_bad
            )
    elif (message.text.split()[0]).lower() == text_templs.text_command_3:
        info = message.text.split(' ')
        if len(info) == 3:
            str1 = " "
            if info[1] == 'exclude_countries':
                value = info[2].split(',')
                users_db.clear_user_filter(message.chat.id, info[1])
                users_db.set_user_filter(message.chat.id, info[1], value)
                bot.send_message(
                    message.chat.id,
                    Template(text_templs.templ_add_filter).substitute(keyword=info[1], value=str1.join(value))
                )
            elif info[1] == 'add_skills':
                value = info[2].split(',')
                users_db.clear_user_filter(message.chat.id, info[1])
                users_db.set_user_filter(message.chat.id, info[1], value)
                bot.send_message(
                    message.chat.id,
                    Template(text_templs.templ_add_filter).substitute(keyword=info[1], value=str1.join(value)))
            else:
                bot.send_message(
                    message.chat.id,
                    text_templs.error_bad_filter
                )
        else:
            bot.send_message(
                message.chat.id,
                text_templs.error_notype
            )
    elif message.text.split()[0].lower() == text_templs.text_command_4:
        if len(message.text.split()) == 2:
            users_db.set_user_settings(message.chat.id, "chat", message.text.split(' ')[1])
            bot.send_message(
                message.chat.id,
                text_templs.templ_send_chat_good
            )
        else:
            bot.send_message(
                message.chat.id,
                text_templs.error_notype
            )
    else:
        print(message.text.split())
        users_db.get_user(message.chat.id)
        state = users_db.get_user_state(message.chat.id)
        state = "✅" if state == 1 else "❌"
        bot.send_message(
            message.chat.id,
            text_templs.error_notype
        )
        bot.send_message(
            message.chat.id,
            Template(text_templs.templ_main).substitute(working=state),
            reply_markup=keyboard_user
        )


if __name__ == "__main__":
    # Init jobs
    for user in users_db.get_all_users():
        if user["id"] == 1:
            continue
        job_name = f"job_{user['id']}"
        state = users_db.get_user_state(user["id"])
        if state == 1:
            add_job_to_queue(
                user["id"],
                REPEAT_PERIOD,
                REPEAT_PERIOD
            )
    schedule.run_all()
    x = threading.Thread(target=check_for_update)
    x.start()
    bot.infinity_polling()
