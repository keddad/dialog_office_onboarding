from dialog_bot_sdk import interactive_media
from dialog_bot_sdk.bot import DialogBot
from models import Guide, User, Job


def cancel_handler(bot: DialogBot, params):
    try:
        bot.messaging.send_message(
            params[0].peer,
            "Возвращаю вас в главное меню",
            get_default_layout(
                User.select().where(User.uid == params[0].sender_uid).get()
            )
        )

        set_state_by_uid(params[0].sender_uid, "START")
    except (AttributeError, KeyError):
        bot.messaging.send_message(
            bot.users.get_user_peer_by_id(params[0].uid),
            "Возвращаю вас в главное меню",
            get_default_layout(
                User.select().where(User.uid == params[0].uid).get()
            )
        )

        set_state_by_uid(params[0].uid, "START")


def _get_admin_layout():
    return [interactive_media.InteractiveMediaGroup(
        [
            interactive_media.InteractiveMedia(
                "default_admin",
                interactive_media.InteractiveMediaButton("new_guide", "Написать новый гайд")
            ),
            interactive_media.InteractiveMedia(
                "default_admin",
                interactive_media.InteractiveMediaButton("list_guides", "Список гайдов")
            ),
            interactive_media.InteractiveMedia(
                "default_admin",
                interactive_media.InteractiveMediaButton("delete_guide", "Удалить гайд")
            ),
            interactive_media.InteractiveMedia(
                "default_admin",
                interactive_media.InteractiveMediaButton("edit_guide", "Редактировать гайд")
            ),
            interactive_media.InteractiveMedia(
                "default_admin",
                interactive_media.InteractiveMediaButton("schedule", "Настроить отложенную отправку")
            )
        ]
    )]


def _get_user_layout():
    return [interactive_media.InteractiveMediaGroup(
        [
            interactive_media.InteractiveMedia(
                "default_user",
                interactive_media.InteractiveMediaButton("read_guide_by_name", "Получить гайд по названию")
            ),
            interactive_media.InteractiveMedia(
                "default_user",
                interactive_media.InteractiveMediaButton("list_guides", "Список гайдов")
            ),
        ]
    )]


def get_schedule_layout():
    return [interactive_media.InteractiveMediaGroup(
        [
            interactive_media.InteractiveMedia(
                "default_schedule",
                interactive_media.InteractiveMediaButton("get_schedule_waitline", "Список гайдов на отправку")
            ),
            interactive_media.InteractiveMedia(
                "default_schedule",
                interactive_media.InteractiveMediaButton("add_guide_to_schedule", "Отсрочить отправку гайда")
            ),
        ]
    )]


def get_scheduled_jobs_list(jobs):

    return [interactive_media.InteractiveMediaGroup(
        [interactive_media.InteractiveMedia(
            "scheduled_job_list",
            interactive_media.InteractiveMediaSelect(
                jobs,
                label="Список отсроченных гайдов"
            )
        )]
    )]


def get_essentialness():
    return [interactive_media.InteractiveMediaGroup(
        [
            interactive_media.InteractiveMedia(
                "new_guide_essential",
                interactive_media.InteractiveMediaButton("True", "Да")
            ),
            interactive_media.InteractiveMedia(
                "new_guide_essential",
                interactive_media.InteractiveMediaButton("False", "Нет")
            ),
        ]
    )]


def get_guides_layout(guides: list):
    interactive_media_list = {}
    for guide in guides:
        interactive_media_list[str(guide.get_id())] = guide.name

    return [interactive_media.InteractiveMediaGroup(
        [interactive_media.InteractiveMedia(
            "get_guide",
            interactive_media.InteractiveMediaSelect(
                interactive_media_list,
                label="Выбери гайд"
            )
        )]
    )]


def get_default_layout(user: User):
    is_admin = User.select().where(User.uid == user.uid).get().is_admin

    if is_admin:
        return _get_admin_layout()
    else:
        return _get_user_layout()


def _send_guide(bot: DialogBot, params, guide):
    try:
        bot.messaging.send_message(
            params[0].peer,
            f"{guide.name}:"
        )
        bot.messaging.send_message(
            params[0].peer,
            guide.text
        )
    except (AttributeError, KeyError):
        bot.messaging.send_message(
            bot.users.get_user_peer_by_id(params[0].uid),
            f"{guide.name}:"
        )
        bot.messaging.send_message(
            bot.users.get_user_peer_by_id(params[0].uid),
            guide.text
        )


def send_guide_by_name(bot: DialogBot, params, guide_name: str):
    guide = Guide.select().where(Guide.name == guide_name).get()
    _send_guide(bot, params, guide)


def send_guide_by_id(bot: DialogBot, params, guide_id: int):
    guide = Guide.select().where(Guide.id == guide_id).get()
    _send_guide(bot, params, guide)


def set_state_by_uid(uid: int, state: str):
    user = User.select().where(User.uid == uid).get()
    user.state = state
    user.save()
