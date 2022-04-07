
from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram import Update, User
import os
import psycopg2
import requests
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

updater = Updater(token=os.environ.get("TELEGRAM_TOKEN"))

def register(update: Update, context: CallbackContext):
    user: User = update.message.from_user
    if user.id != update.effective_chat.id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please contact me in DM only so we dont spam this chat! Go to @anetabtcairdroprecorderbot")
        return
    if context.args.__len__() < 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please supply an Ergo address as the first argument to the command. (Like this: /register 9myergoadressjjjsz")
        return
    address = context.args[0]
    r = requests.get(f'{os.environ.get("ERGO_NODE")}/utils/address/{address}')
    res = r.json()
    if res['isValid']:
        with psycopg2.connect(host=os.environ.get("POSTGRES_HOST"),port=os.environ.get("POSTGRES_PORT"),database=os.environ.get('POSTGRES_DB'),user=os.environ.get('POSTGRES_USER'),password=os.environ.get('POSTGRES_PASSWORD')) as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO telegram_wallets 
                (user_id,user_name,wallet_address) 
                VALUES 
                ('%s',%s,%s)
                ON CONFLICT ON CONSTRAINT "telegram_wallets_USER_ID"
                DO UPDATE SET
                (user_name, wallet_address, wallet_update_ts)
                = (EXCLUDED.user_name, EXCLUDED.wallet_address, CURRENT_TIMESTAMP)""",(user.id,user.full_name,address))
                conn.commit()
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"CONGRATULATIONS! 🎊 You successfully registered your Ergo Wallet address.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="ERROR! Please re-enter a valid Ergo wallet address.")

register_handler = CommandHandler('register', register)
updater.dispatcher.add_handler(register_handler)
updater.start_polling()
updater.idle()
