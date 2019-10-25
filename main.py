from dialog_bot_sdk.bot import DialogBot
from models import Job, User, Guide
from handlers import admin, regular, utils
import grpc
import os
import time
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN") or ""
ENDPOINT = os.environ.get("ENDPOINT") or "hackathon-mob.transmit.im"


def on_click(*params):
    try:
        if params[0].id == "initial_reg":
            regular.new_user_type_handler(bot, params)

        elif params[0].id == "default_admin":
            admin.default_admin_handler(bot, params)

        elif params[0].id == "default_user":
            regular.default_user_handler(bot, params)

        elif params[0].id == "get_guide":
            regular.guide_getter_by_id(bot, params)

        elif params[0].id == "new_guide_essential":
            admin.guide_creation_handler(bot, params)

        elif params[0].id == "default_schedule":
            admin.default_schedule_handler(bot, params)

        elif params[0].id == "scheduled_job_list":
            admin.scheduled_job_delete_handler(bot, params)

        else:
            regular.unknown_message_handler(bot, params)
    except:
        regular.error_handler(bot, params)


def on_msg(*params):
    try:
        if not User.select().where(User.uid == params[0].sender_uid).exists():
            regular.new_user_handler(bot, params)
            return

        state = User.select().where(User.uid == params[0].sender_uid).get().state

        if params[0].message.textMessage.text == "/cancel" or params[0].message.textMessage.text == "/menu":
            utils.cancel_handler(bot, params)

        elif state == "GUIDE_DELETION":
            admin.guide_deletion_handler(bot, params)

        elif state == "GET_GUIDE_BY_NAME":
            regular.guide_getter_by_name_handler(bot, params)

        elif state == "NEW_GUIDE_NAME" or state == "NEW_GUIDE_TEXT":
            admin.guide_creation_handler(bot, params)

        elif state == "GUIDE_EDIT":
            admin.guide_edit_handler(bot, params)

        elif state == "GUIDE_SCHEDULE_ADD":
            admin.default_schedule_add_handler(bot, params)

        else:
            regular.unknown_message_handler(bot, params)

    except:
        regular.error_handler(bot, params)


if __name__ == '__main__':
    bot = DialogBot.get_secure_bot(
        ENDPOINT,  # bot endpoint from environment
        grpc.ssl_channel_credentials(),  # SSL credentials (empty by default!)
        BOT_TOKEN  # bot token from environment
    )

    bot.messaging.on_message_async(on_msg, on_click)

    while (True):
        time.sleep(59)

        now = datetime.now()

        for job in Job.select():
            if (job.publication_time - now).seconds <= 60:
                guide = Guide.select().where(Guide.id == job.guide_id).get()
                for user in User.select():
                    if not user.is_admin:
                        bot.messaging.send_message(
                            bot.users.get_user_peer_by_id(user.uid),
                            f"Отложенная отправка гайда '{guide.name}':"
                        )

                        bot.messaging.send_message(
                            bot.users.get_user_peer_by_id(user.uid),
                            guide.text
                        )
                    else:
                        bot.messaging.send_message(
                            bot.users.get_user_peer_by_id(user.uid),
                            f"Пользователям был успешно отправлен гайд '{guide.name}':"
                        )
                job.delete_instance()
