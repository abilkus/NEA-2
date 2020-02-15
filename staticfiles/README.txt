In development - static files are served from catalog
In production - this directory is created with the needed static files for all of django, and can be used to serve directly by apache

python manage.py collectstatic will do this