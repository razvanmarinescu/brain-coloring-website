all:
	FLASK_APP=main.py FLASK_ENV=development FLASK_DEBUG=1 flask run

# use this to ensure everything runs ok
test_on_prod:
	/home/ubuntu/miniconda3/envs/razenv/bin/gunicorn main.py

	# then restart gunicorn server
	sudo systemctl restart gunicorn

	# optional?
	sudo systemctl enable gunicorn
	
