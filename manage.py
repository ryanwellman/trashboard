#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line
    if sys.argv[1] == 'shell':
        sys.argv[1] = 'shell_plus'
    execute_from_command_line(sys.argv)
