# ...existing code from scheduler.py...
# scheduler.py

from flask_apscheduler import APScheduler
from datetime import datetime

scheduler = APScheduler()


def init_scheduler(app, backup_system):
    scheduler.init_app(app)

    # Configura os backups automáticos
    @scheduler.task('cron', id='daily_backup', hour=0)
    def daily_backup():
        backup_system.create_backup('daily')

    @scheduler.task('cron', id='weekly_backup', day_of_week=0, hour=1)
    def weekly_backup():
        backup_system.create_backup('weekly')

    @scheduler.task('cron', id='monthly_backup', day=1, hour=2)
    def monthly_backup():
        backup_system.create_backup('monthly')

    scheduler.start()