import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital.settings")

from django.core.management import execute_from_command_line

if len(sys.argv) == 1:
    sys.argv.extend(["runserver", "8000"])

execute_from_command_line(sys.argv)
