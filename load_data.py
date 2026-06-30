import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.core.management import call_command

print("Starting data restoration...")
try:
    call_command('loaddata', 'db_backup.json')
    print("Data loaded successfully!")
except Exception as e:
    print(f"Error loading data: {e}")