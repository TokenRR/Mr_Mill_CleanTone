import telebot
from telebot import types
from tg_bot_config import TOKEN, WHITE_LIST, TRANSLATIONS

# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# Store user language preferences (default to Ukrainian)
user_languages = {}

# Helper function to get the correct translation for a user
def translate(user_id, key):
    lang = user_languages.get(user_id, 'uk')  # Default to Ukrainian if no language is set
    return TRANSLATIONS[lang].get(key, key)

# Main menu keyboard generation
def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Buttons for video/audio processing in a row with emojis
    enhance_audio_video_btn = types.KeyboardButton(translate(user_id, 'enhance_audio_video'))
    enhance_audio_btn = types.KeyboardButton(translate(user_id, 'enhance_audio'))
    get_audio_from_video_btn = types.KeyboardButton(translate(user_id, 'get_audio_from_video'))

    # Account button at the bottom with an emoji
    my_account_btn = types.KeyboardButton(translate(user_id, 'my_account') + " 🧑‍💼")

    # Arrange buttons in a row for the top row, and "My account" button below
    markup.row(enhance_audio_video_btn, enhance_audio_btn, get_audio_from_video_btn)
    markup.add(my_account_btn)

    return markup

# Account submenu keyboard
def account_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    language_btn = types.KeyboardButton(translate(user_id, 'language') + " 🌐")
    telegram_id_btn = types.KeyboardButton(translate(user_id, 'get_telegram_id') + " 🆔")
    back_btn = types.KeyboardButton(translate(user_id, 'back_to_main_menu') + " ⬅️")

    # Add buttons to the markup
    markup.add(language_btn, telegram_id_btn)
    markup.add(back_btn)
    return markup

# Language selection keyboard with emojis
def language_selection_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    english_btn = types.KeyboardButton("🇬🇧 English")
    ukrainian_btn = types.KeyboardButton("🇺🇦 Українська")
    back_btn = types.KeyboardButton(translate(user_id, 'back_to_main_menu') + " ⬅️")

    # Add language buttons with emojis and back button
    markup.add(english_btn, ukrainian_btn)
    markup.add(back_btn)
    return markup

# Decorator to check if the user is in the white list
def whitelist_only(func):
    def wrapper(message):
        user_id = message.from_user.id
        if user_id in WHITE_LIST:
            return func(message)
        else:
            bot.send_message(message.chat.id, translate(user_id, 'not_authorized'))
    return wrapper

# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_languages[user_id] = 'uk'  # Default to Ukrainian
    bot.send_message(message.chat.id, translate(user_id, 'welcome_message'), reply_markup=main_menu(user_id))

# Handle all menu options, including language switching
@bot.message_handler(func=lambda message: True)
def main_menu_handler(message):
    user_id = message.from_user.id
    text = message.text

    # Handle "My Account" and related options
    if text == translate(user_id, 'my_account') + " 🧑‍💼":
        bot.send_message(message.chat.id, translate(user_id, 'select_option'), reply_markup=account_menu(user_id))
    elif text == translate(user_id, 'enhance_audio_video'):
        enchance_audio_on_video(message)
    elif text == translate(user_id, 'enhance_audio'):
        enchance_audio(message)
    elif text == translate(user_id, 'get_audio_from_video'):
        get_audio_from_video(message)
    elif text == translate(user_id, 'back_to_main_menu') + " ⬅️":
        bot.send_message(message.chat.id, translate(user_id, 'select_option'), reply_markup=main_menu(user_id))
    elif text == translate(user_id, 'language') + " 🌐":
        bot.send_message(message.chat.id, translate(user_id, 'choose_language'), reply_markup=language_selection_menu(user_id))
    elif text == translate(user_id, 'get_telegram_id') + " 🆔":
        # Escape special characters for MarkdownV2 format
        telegram_id = message.from_user.id
        formatted_id = f"`{telegram_id}`"
        bot.send_message(message.chat.id, translate(user_id, 'your_telegram_id').format(formatted_id), parse_mode="MarkdownV2")

    # Handle language switching in the same handler
    elif text == '🇬🇧 English':
        user_languages[user_id] = 'en'  # Switch to English
        bot.send_message(message.chat.id, translate(user_id, 'language_switched_english'), reply_markup=main_menu(user_id))
    elif text == '🇺🇦 Українська':
        user_languages[user_id] = 'uk'  # Switch to Ukrainian
        bot.send_message(message.chat.id, translate(user_id, 'language_switched_ukrainian'), reply_markup=main_menu(user_id))

# Handlers that require the user to be whitelisted
@whitelist_only
def enchance_audio_on_video(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, translate(user_id, 'success'))

@whitelist_only
def enchance_audio(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, translate(user_id, 'success'))

@whitelist_only
def get_audio_from_video(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, translate(user_id, 'success'))

# Run the bot
if __name__ == '__main__':
    bot.polling(none_stop=True)
