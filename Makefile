all:
	FLASK_APP=main.py FLASK_ENV=development FLASK_DEBUG=1 flask run

# use this to ensure everything runs ok
test_on_prod:
	/home/ubuntu/miniconda3/envs/razenv/bin/gunicorn main.py

	# then restart gunicorn server
	sudo systemctl restart gunicorn

	# see error log
	journalctl -u gunicorn
	

docker:
	docker run --mount src=/Users/razvan/research/brain-coloring-website/static/generated/,target=/home/brain-coloring/generated/,type=bind mrazvan22/brain-coloring:dev /bin/bash -c 'cd /home/brain-coloring; configFile=generated/A0A6A376286EF21C/cortical-outer_config.py blender --background --python blendCreateSnapshot.py' > log.txt
	
