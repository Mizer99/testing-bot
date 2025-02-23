import logging
import pandas as pd
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# Set your bot token here
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Define storage file
data_file = "work_records.xlsx"

# Language selection
LANGUAGE = "EN"
languages = {
    "EN": {
        "work_on": "Work In",
        "off": "Off Work",
        "wc": "Washroom Break",
        "food_break": "Food Break",
        "smoke": "Smoke Break",
        "other": "Other",
        "back": "Back to Work",
        "daily_record": "Daily Record",
        "change_lang": "Change Language",
    },
    "CN": {
        "work_on": "上班",
        "off": "下班",
        "wc": "洗手间休息",
        "food_break": "吃饭休息",
        "smoke": "抽烟",
        "other": "其他",
        "back": "回去工作",
        "daily_record": "每日记录",
        "change_lang": "更改语言",
    },
}

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton(languages[LANGUAGE]["work_on"], callback_data="work_on")],
                [InlineKeyboardButton(languages[LANGUAGE]["off"], callback_data="off")],
                [InlineKeyboardButton(languages[LANGUAGE]["wc"], callback_data="wc")],
                [InlineKeyboardButton(languages[LANGUAGE]["food_break"], callback_data="food_break")],
                [InlineKeyboardButton(languages[LANGUAGE]["smoke"], callback_data="smoke")],
                [InlineKeyboardButton(languages[LANGUAGE]["other"], callback_data="other")],
                [InlineKeyboardButton(languages[LANGUAGE]["back"], callback_data="back")],
                [InlineKeyboardButton(languages[LANGUAGE]["daily_record"], callback_data="daily_record")],
                [InlineKeyboardButton(languages[LANGUAGE]["change_lang"], callback_data="change_lang")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select an option:", reply_markup=reply_markup)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    action = query.data
    user = query.from_user.username or query.from_user.first_name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if action == "change_lang":
        global LANGUAGE
        LANGUAGE = "CN" if LANGUAGE == "EN" else "EN"
        query.edit_message_text(f"Language changed to {LANGUAGE}")
        return
    
    log_data(user, action, timestamp)
    query.edit_message_text(f"{languages[LANGUAGE][action]} recorded at {timestamp}\nPurpose: {languages[LANGUAGE][action]}")

def log_data(user, action, timestamp):
    if not os.path.exists(data_file):
        df = pd.DataFrame(columns=["Username", "Action", "Timestamp"])
    else:
        df = pd.read_excel(data_file)
    
    new_data = pd.DataFrame([[user, action, timestamp]], columns=["Username", "Action", "Timestamp"])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel(data_file, index=False)

def send_daily_report(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if os.path.exists(data_file):
        context.bot.send_document(chat_id=chat_id, document=open(data_file, "rb"))
    else:
        update.message.reply_text("No records found!")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(CommandHandler("daily_record", send_daily_report))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
