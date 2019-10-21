from dialog_bot_sdk.bot import DialogBot
from models import Guide, User
import utils
import handlers
import grpc
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ENDPOINT = os.environ.get("ENDPOINT") or "hackathon-mob.transmit.im"


def on_click(*params):
    if params[0].id == "initial_reg":
        handlers.new_user_type_handler(bot, params)

        user_peer = bot.users.get_user_peer_by_id(params[0].uid)

        bot.messaging.send_message(
            user_peer,
            "Ура, регистрация прошла успешно"
        )

        bot.messaging.send_message(
            user_peer,
            "Давайте что нибудь сделаем",
            utils.get_default_layout(
                User.select().where(User.uid == params[0].uid).get()
            )
        )

    elif params[0].id == "default_admin":
        handlers.default_admin_handler(bot, params)

    elif params[0].id == "default_user":
        handlers.default_user_handler(bot, params)

    elif params[0].id == "get_guide":
        handlers.guide_getter_by_id(bot, params)

    elif params[0].id == "new_guide_essential":
        handlers.guide_creation_handler(bot, params)


def on_msg(*params):
    if not User.select().where(User.uid == params[0].sender_uid).exists():
        handlers.new_user_handler(bot, params)
        return

    state = User.select().where(User.uid == params[0].sender_uid).get().state

    if params[0].message.textMessage.text == "/cancel":
        handlers.cancel_handler(bot, params)

    elif state == "GUIDE_DELETION":
        handlers.guide_deletion_handler(bot, params)

    elif state == "GET_GUIDE_BY_NAME":
        handlers.guide_getter_by_name_handler(bot, params)

    elif state == "NEW_GUIDE_NAME" or state == "NEW_GUIDE_TEXT":
        handlers.guide_creation_handler(bot, params)


if __name__ == '__main__':
    bot = DialogBot.get_secure_bot(
        ENDPOINT,  # bot endpoint from environment
        grpc.ssl_channel_credentials(),  # SSL credentials (empty by default!)
        BOT_TOKEN  # bot token from environment
    )

    bot.messaging.on_message(on_msg, on_click)
