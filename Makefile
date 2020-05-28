install:
	# clone repo of BrainPainter code
	git clone https://github.com/mrazvan22/brain-coloring.git
	mv brain-coloring brainPainterRepo

	# create folder under static to generate images, as only unders tatic one can display images on the website in Flask/Gunicorn 
	mkdir -p static/generated

	# create symlink also in main folder, as FLASK app 'generated' needs to be in main folder
	ln -s static/generated generated

all:
	FLASK_APP=main.py FLASK_ENV=development FLASK_DEBUG=1 flask run

# use this to ensure everything runs ok
test_on_prod:
	/home/ubuntu/miniconda3/envs/razenv/bin/gunicorn wsgi

	# then restart gunicorn server
	sudo systemctl restart gunicorn

	# see error log
	journalctl -u gunicorn
	

# gunicorn setup here: sudo vim /etc/systemd/system/gunicorn.service
# 

docker:
	docker run --mount src=/Users/razvan/research/brain-coloring-website/static/generated/,target=/home/brain-coloring/generated/,type=bind mrazvan22/brain-coloring:dev /bin/bash -c 'cd /home/brain-coloring; configFile=generated/A0A6A376286EF21C/cortical-outer_config.py blender --background --python blendCreateSnapshot.py' > log.txt
	
movie:
	cd brainPainterRepo; python3 genTemplateMovie.py

	docker run  --mount src=/Users/razvan/research/brain-coloring-website/static/generated/,target=/home/brain-coloring/generated/,type=bind mrazvan22/brain-coloring:dev /bin/bash -c 'cd /home/brain-coloring; configFile=generated/DK_movie/cortical-outer_config.py blender --background --python blendCreateSnapshot.py'
	docker run  --mount src=/Users/razvan/research/brain-coloring-website/static/generated/,target=/home/brain-coloring/generated/,type=bind mrazvan22/brain-coloring:dev /bin/bash -c 'cd /home/brain-coloring; configFile=generated/DK_movie/cortical-inner_config.py blender --background --python blendCreateSnapshot.py'
	docker run  --mount src=/Users/razvan/research/brain-coloring-website/static/generated/,target=/home/brain-coloring/generated/,type=bind mrazvan22/brain-coloring:dev /bin/bash -c 'cd /home/brain-coloring; configFile=generated/DK_movie/subcortical_config.py blender --background --python blendCreateSnapshot.py'

	convert -delay 20 -loop 0 *.jpg myimage.gif
