#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect Static Files
python manage.py collectstatic --no-input

# Run Migrations
python manage.py migrate

# YE WALI LINE SABSE NEECHE ADD KAREIN:
python manage.py loaddata db_backup.json