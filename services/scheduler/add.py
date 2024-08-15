
from aiogram.types import TelegramObject
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.variables import TEST_STARTED, TEST_ENDING, TEST_FAILED, get_task, exam_times
from database.database import ORM
from services.telegram.handlers.admin.notify import notify_admins
from services.telegram.misc.actions import TgActions
from services.telegram.misc.enums import TestStatus
from services.telegram.misc.keyboards import Keyboards


# Основная функция для обработки тестирования
async def process_testing(tg_object: TelegramObject, user_id: int, orm: ORM):
    user = await orm.user_repo.find_user_by_user_id(user_id)
    tga = TgActions(tg_object, user.user_id)

    if user.test_status is TestStatus.waiting:
        task = get_task(max_tasks=3)
        await orm.user_repo.upsert_user(user_id, test_status=TestStatus.started, task=task)
        await tga.send_message(TEST_STARTED.format(task), reply_markup=Keyboards.on_task())
        await notify_admins(tg_object.bot, f"Началось тестирование для @{user.username} 👨‍💻")
    elif user.test_status is TestStatus.started:
        await tga.send_message(TEST_ENDING)
        await orm.user_repo.upsert_user(user_id, test_status=TestStatus.test_ending)
    elif user.test_status is TestStatus.test_ending:
        await tga.send_message(TEST_FAILED)
        await notify_admins(tg_object.bot, f"@{user.username} не прошел тестирование ❌")
        await orm.user_repo.upsert_user(user_id, test_status=TestStatus.failed)


async def add_testing_jobs(scheduler: AsyncIOScheduler, tg_object: TelegramObject, user_id: int, orm: ORM):
    user = await orm.user_repo.find_user_by_user_id(user_id)
    kwargs = {"tg_object": tg_object, "user_id": user_id, "orm": orm}
    scheduler.add_job(process_testing, trigger='date', run_date=user.testing_at, kwargs=kwargs)
    scheduler.add_job(process_testing, trigger='date', run_date=str(user.testing_at + exam_times["send_notification"]), kwargs=kwargs)
    scheduler.add_job(process_testing, trigger='date', run_date=str(user.testing_at + exam_times["duration"]), kwargs=kwargs)


# async def start_test(tg_object: TelegramObject, user: User, scheduler: AsyncIOScheduler):
#     ids = random.sample(range(len(tasks)), 3)
#     tasks_text = "\n".join([f'{i + 1}) ' + tasks[ids[i]] for i in range(len(ids))])
#
#     tga = TgActions(tg_object, user.user_id)
#     await tga.send_message(TEST_STARTED.format(tasks_text), reply_markup=Keyboards.on_task())
#     await notify_admins(tg_object.bot, f"Началось тестирование для @{user.username} 👨‍💻")
#
#     scheduler.add_job(test_ending, trigger='date',
#                       run_date=str(user.testing_at + exam_times["send_notification"]),
#                       kwargs={"tg_object": tg_object, "user": user, "scheduler": scheduler})
#
#
# async def test_ending(tg_object: TelegramObject, user: User, scheduler: AsyncIOScheduler):
#     tga = TgActions(tg_object, user.user_id)
#
#     await tga.send_message(TEST_ENDING)
#     scheduler.add_job(process_testing, trigger='date',
#                       run_date=str(user.testing_at + exam_times["duration"]),
#                       kwargs={"tg_object": tg_object, "user": user})
#
#
# async def test_failed(tg_object: TelegramObject, user: User, scheduler: AsyncIOScheduler):
#     tga = TgActions(tg_object, user.user_id)
#
#     await tga.send_message(TEST_ENDING)
#     scheduler.add_job(process_testing, trigger='date',
#                       run_date=str(user.testing_at + exam_times["duration"]),
#                       kwargs={"tg_object": tg_object, "user": user})