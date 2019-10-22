from dialog_bot_sdk.bot import DialogBot
from dialog_bot_sdk import interactive_media, internal
from models import Guide, User
from handlers import utils

GUIDE_CACHE = {}
DELETE_CACHE = {}


def guide_deletion_handler(bot: DialogBot, params):
    """
    Обработчик статуса GUIDE_DELETION
    """
    guide_name = params[0].message.textMessage.text
    if not Guide.select().where(Guide.name == guide_name).exists():
        bot.messaging.send_message(
            params[0].peer,
            "Гайда с таким названием не существует"
        )

    else:
        guide = Guide.select().where(Guide.name == guide_name).get()
        guide.delete_instance()  # TODO: Замутить подтверждение удаления, когда баг пофиксят
        bot.messaging.send_message(
            params[0].peer,
            "Гайд успешно удален"
        )
        utils.cancel_handler(bot, params)


def default_admin_handler(bot: DialogBot, params):
    """
    Обработчик главного меню для администратора бота, "default_admin"
    """
    if params[0].value == "list_guides":
        guides = [guide for guide in Guide.select()]
        bot.messaging.send_message(
            bot.users.get_user_peer_by_id(params[0].uid),
            "Выбери гайд",
            utils.get_guides_layout(guides)
        )

    elif params[0].value == "delete_guide":
        bot.messaging.send_message(
            bot.users.get_user_peer_by_id(params[0].uid),
            "Для удаления гайда напиши, пожалуйста, его название. Для отмены операции напиши /cancel"
        )

        utils.set_state_by_uid(params[0].uid, "GUIDE_DELETION")

    elif params[0].value == "new_guide":
        bot.messaging.send_message(
            bot.users.get_user_peer_by_id(params[0].uid),
            "Отправь название нового гайда, одним сообщением"
        )

        utils.set_state_by_uid(params[0].uid, "NEW_GUIDE_NAME")

    elif params[0].value == "edit_guide":
        bot.messaging.send_message(
            bot.users.get_user_peer_by_id(params[0].uid),
            "Какой гайд требуется редактировать?"
        )

        utils.set_state_by_uid(params[0].uid, "GUIDE_EDIT")


def guide_creation_handler(bot: DialogBot, params):
    """
    Обработчик создания гайда, "NEW_GUIDE_*", "new_guide_essential"
    """
    try:
        state = User.select().where(User.uid == params[0].sender_uid).get().state
    except (AttributeError, KeyError):
        state = User.select().where(User.uid == params[0].uid).get().state

    if state == "NEW_GUIDE_NAME":
        name = params[0].message.textMessage.text

        if Guide.select().where(Guide.name == name).exists():
            bot.messaging.send_message(
                params[0].peer,
                "Гайд с таким именем уже есть. Придумай другое."
            )
            return

        GUIDE_CACHE[params[0].sender_uid] = {
            "name": name,
            "text": "",
            "essential": False
        }

        bot.messaging.send_message(
            params[0].peer,
            "Теперь напиши гайд, одним сообщением"
        )

        utils.set_state_by_uid(params[0].sender_uid, "NEW_GUIDE_TEXT")

    elif state == "NEW_GUIDE_TEXT":
        text = params[0].message.textMessage.text

        try:
            GUIDE_CACHE[params[0].sender_uid]["text"] = text
        except (AttributeError, KeyError):
            bot.messaging.send_message(
                params[0].peer,
                "Кажется, бот перезагрузился и у него исчез кеш. Вам придется написать гайд еще раз :("
            )
            utils.cancel_handler(bot, params)
            return

        bot.messaging.send_message(
            params[0].peer,
            "Мне следует показывать этот гайдов в списке гайдов по умолчанию для каждого пользователя? ",
            utils.get_essentialness()
        )

        utils.set_state_by_uid(params[0].sender_uid, "NEW_GUIDE_ESSENTIAL")


    elif state == "NEW_GUIDE_ESSENTIAL":
        try:
            if params[0].value == "True":
                GUIDE_CACHE[params[0].uid]["essential"] = True
            else:
                GUIDE_CACHE[params[0].uid]["essential"] = False
        except (AttributeError, KeyError):
            bot.messaging.send_message(
                bot.users.get_user_peer_by_id(params[0].uid),
                "Кажется, бот перезагрузился и у него исчез кеш. Вам придется написать гайд еще раз :("
            )
            utils.cancel_handler(bot, params)
            return

        guide = Guide.create(**GUIDE_CACHE[params[0].uid])
        guide.save()

        del GUIDE_CACHE[params[0].uid]

        bot.messaging.send_message(
            bot.users.get_user_peer_by_id(params[0].uid),
            "Гайд успешно создан!"
        )

        utils.set_state_by_uid(params[0].uid, "START")
        utils.cancel_handler(bot, params)


def guide_edit_handler(bot: DialogBot, params):
    """
    Обработчик изменения гайда, "GUIDE_EDIT"
    """
    if params[0].sender_uid not in DELETE_CACHE:
        guide_name = params[0].message.textMessage.text
        if not Guide.select().where(Guide.name == guide_name).exists():
            bot.messaging.send_message(
                params[0].peer,
                "Такого гайда не существует. Попробуйте другое название или напишите /cancel для возврата в главное меню"
            )
            return

        utils.send_guide_by_name(bot, params, guide_name)
        bot.messaging.send_message(
            params[0].peer,
            "Напишите, на что мне заменить текущий текст:"
        )

        DELETE_CACHE[params[0].sender_uid] = guide_name
    else:
        new_text = params[0].message.textMessage.text

        guide = Guide.select().where(Guide.name == DELETE_CACHE[params[0].sender_uid]).get()
        guide.text = new_text
        guide.save()

        bot.messaging.send_message(
            params[0].peer,
            "Текст успешно обновлен"
        )

        del DELETE_CACHE[params[0].sender_uid]
        utils.cancel_handler(bot, params)
