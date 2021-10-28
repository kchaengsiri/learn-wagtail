clear:
	clear

makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

run: clear
	python manage.py runserver 0.0.0.0:9999

update: clear makemigrations migrate

reload: update run
