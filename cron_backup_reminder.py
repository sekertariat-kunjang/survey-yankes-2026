"""
Script pengingat backup mingguan (Weekly Backup Reminder Cronjob).
Dapat dijalankan secara berkala (misal via Windows Task Scheduler atau Linux Crontab setiap pekan).
"""
import os
import sys
from datetime import datetime

DATABASE_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'survey.db')
BACKUP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'backups')


def check_backup_status():
    if not os.path.exists(DATABASE_FILE):
        print("[INFO] Database survey.db belum ada.")
        return 0

    if not os.path.exists(BACKUP_DIR):
        print("[PERINGATAN INTERVENSI] Belum pernah dilakukan backup database. Segera lakukan backup!")
        return 1

    backups = [
        f for f in os.listdir(BACKUP_DIR)
        if f.startswith('survey_backup_') and f.endswith('.db')
    ]

    if not backups:
        print("[PERINGATAN INTERVENSI] Belum ada file cadangan database di direktori backups/. Segera lakukan backup!")
        return 1

    latest_file = max(
        backups,
        key=lambda f: os.path.getmtime(os.path.join(BACKUP_DIR, f))
    )
    latest_path = os.path.join(BACKUP_DIR, latest_file)
    mtime = datetime.fromtimestamp(os.path.getmtime(latest_path))
    days_since = (datetime.now() - mtime).days

    if days_since >= 7:
        print(f"[PERINGATAN INTERVENSI] Sudah {days_since} hari sejak backup terakhir ({mtime.strftime('%Y-%m-%d %H:%M')}). Segera unduh backup database baru!")
        return 1
    else:
        print(f"[AMAN] Backup database masih dalam batas aman ({days_since} hari lalu, {mtime.strftime('%Y-%m-%d %H:%M')}).")
        return 0


if __name__ == '__main__':
    exit_code = check_backup_status()
    sys.exit(exit_code)
