from apscheduler.schedulers.asyncio import AsyncIOScheduler


def resume_jobs():  # TODO DODODODODODOODODODODODODODODOODODODODOODODODODODO
    cursor = con.cursor()
    cursor.execute("SELECT * FROM users_data")
    results = cursor.fetchall()
    now = datetime.datetime.now()
    print(results)
    for row in results:
        date = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        time = datetime.datetime.strptime(row[4], "%H:%M")
        run_at = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=time.hour, minute=time.minute)
        print(run_at, now)
        print(time)
        if run_at >= now:
            scheduler = AsyncIOScheduler(timezone="Asia/Almaty")
            started_at = datetime.datetime.strptime(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d "
                                                                                            "%H:%M")
            cursor.execute("UPDATE users_data SET run_date=%s WHERE user_id=%s",
                           (started_at, row[0]))
            con.commit()
            scheduler.add_job(send_testing_bot, trigger='date', run_date=run_at,
                              kwargs={"bot": bot, "user_id": row[0], "username": row[5],
                                      "run_date": started_at, "test_status": 2})
            scheduler.add_job(send_testing_bot, trigger='date',
                              run_date=str(run_at + config.exam_times["send_notification"]),
                              kwargs={"bot": bot, "user_id": row[0], "username": row[5],
                                      "run_date": started_at, "test_status": 3})
            scheduler.add_job(send_testing_bot, trigger='date',
                              run_date=str(run_at + config.exam_times["duration"]),
                              kwargs={"bot": bot, "user_id": row[0], "username": row[5],
                                      "run_date": started_at, "test_status": 5})
            scheduler.start()