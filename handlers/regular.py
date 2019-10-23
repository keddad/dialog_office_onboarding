from dialog_bot_sdk.bot import DialogBot
from dialog_bot_sdk import interactive_media, internal
from models import Guide, User
from handlers import utils


def unknown_message_handler(bot: DialogBot, params):
    try:
        peer = bot.users.get_user_peer_by_id(params[0].uid)
    except AttributeError:
        peer = params[0].peer

    bot.messaging.send_message(
        peer,
        "Я не понимаю, что ты хочешь сделать. Можешь написать /menu для возврата в главное меню"
    )


def error_handler(bot: DialogBot, params):
    try:
        peer = bot.users.get_user_peer_by_id(params[0].uid)
    except AttributeError:
        peer = params[0].peer

    bot.messaging.send_message(
        peer,
        "Кажется, что то сломалось. Возвращаемся в главное меню"
    )

    utils.cancel_handler(bot, params)


def new_user_handler(bot: DialogBot, params):
    """
    Обработчик для новых пользователей, возвращающий приветственное сообщение
    """
    if not User.select().where(User.uid == params[0].sender_uid).exists():
        bot.messaging.send_message(
            params[0].peer,
            "Привет. Кажется, ты еще не зарегестрирован. Ты пишешь гайды или читаешь?"
        )

        bot.messaging.send_message(
            params[0].peer,
            "Укажите роль",
            [interactive_media.InteractiveMediaGroup(
                [
                    interactive_media.InteractiveMedia(
                        "initial_reg",
                        interactive_media.InteractiveMediaButton("user_normal", "Я читаю")
                    ),
                    interactive_media.InteractiveMedia(
                        "initial_reg",
                        interactive_media.InteractiveMediaButton("user_admin", "Я пишу")
                    ),
                ]
            )]
        )


def new_user_type_handler(bot: DialogBot, params):
    """
    Обработчик клика на кнопку выбора роли при регистрации
    """
    new_user = User.create(
        uid=params[0].uid,
        is_admin=True if params[0].value == "user_admin" else False
    )

    new_user.save()

    bot.messaging.delete(
        params[0]
    )

    user_peer = bot.users.get_user_peer_by_id(params[0].uid)

    bot.messaging.send_message(
        user_peer,
        "Ура, регистрация прошла успешно"
    )

    bot.messaging.send_message(
        user_peer,
        "Давайте что нибудь сделаем. Вы в любой момент можете написать /menu и вернуться сюда.",
        utils.get_default_layout(
            User.select().where(User.uid == params[0].uid).get()
        )
    )


def guide_getter_by_name_handler(bot: DialogBot, params):
    """
    Обработчик статуса GET_GUIDE_BY_NAME
    """
    guide_name = params[0].message.textMessage.text
    if not Guide.select().where(Guide.name == guide_name).exists():
        bot.messaging.send_message(
            params[0].peer,
            "Гайда с таким названием не существует"
        )

    else:
        utils.send_guide_by_name(bot, params, guide_name)
        utils.cancel_handler(bot, params)


def default_user_handler(bot: DialogBot, params):
    """
    Обработчик главного меню для обычного пользователя, "default_user"
    """
    if params[0].value == "list_guides":
        guides = [guide for guide in Guide.select().where(Guide.essential == True)]
        bot.messaging.send_message(
            bot.users.get_user_peer_by_id(params[0].uid),
            "Выбери гайд",
            utils.get_guides_layout(guides)
        )

    elif params[0].value == "read_guide_by_name":
        bot.messaging.send_message(
            bot.users.get_user_peer_by_id(params[0].uid),
            "Скажи мне название гайда, который ты хочешь прочесть"
        )

        utils.set_state_by_uid(params[0].uid, "GET_GUIDE_BY_NAME")


def guide_getter_by_id(bot: DialogBot, params):
    """
    Обработчик события "get_guide"
    """
    id = int(params[0].value)
    if not Guide.select().where(Guide.id == id).exists():
        bot.messaging.send_message(
            bot.users.get_user_peer_by_id(params[0].uid),
            "Этот гайд был удален или перемещен"
        )
        return

    utils.send_guide_by_id(bot, params, id)
