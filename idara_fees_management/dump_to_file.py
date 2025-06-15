# dump_to_file.py
from django.core.management import call_command
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idara_fees_management.settings")
django.setup()

with open("db_backup.json", "w", encoding="utf-8") as f:
    call_command("dumpdata", indent=2, stdout=f)

