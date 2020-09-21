# BrainPainter website - Brain Visualisation and Image Generation from the browser

![Front page](static/frontPage.png)

For any issues, please email me: razvan (at) csail-mit-edu (replace dash with dot). The website template is open-source 
and adapted from the grayscale template: https://startbootstrap.com/themes/grayscale/. It is published under the free, MIT license. 

## Features

* Ideal starting template for serving results from research models
* Central hosting on a server means users don't have to install the software (BrainPainter)
* Interfaces with docker application 
* Launches parallel processes for computational speed-up
* Simple, customizable template served with Flask


## Prerequisites

* Flask
* Docker
* Flask-Mikasa
* Pandas=0.24.2

## Installation

1. Install Flask and Flask-Misaka: 

```pip install -U Flask Flask-Misaka pandas==0.24.2```

2. Install BrainPainter using docker (needs docker already installed): 

`sudo docker run -it mrazvan22/brain-coloring`. 

Once docker container finishes installation, it should automatically connect to the shell. Once inside docker, pull the latest changes if any:

``` 
cd /home/brain-coloring/

git pull origin master
```


3. Log out of docker and clone this repo (website code only) using:

``` 
git clone https://github.com/mrazvan22/brain-coloring-website.git ; cd brain-coloring-website
```

Install the BrainPainter code using:

``` 
make install 
```

This command will clone the BrainPainter code repo, create folder static/generated as well as a symlink to it in main folder. These are required because images have to be under the static folder for displaying them on the webpage. Have a look at the Makefile for more details

4. Run the website using flask:

```
 FLASK_APP=main.py FLASK_ENV=development FLASK_DEBUG=1 flask run
```

If everything works, you should see the following:

```
FLASK_APP=main.py FLASK_ENV=development FLASK_DEBUG=1 flask run
 * Serving Flask app "main.py" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 175-529-670
```

5. Generate the  Flask secret key: 

```
>>> import os
>>> os.urandom(12).hex()
'f3cfe9ed8fae309f02079dbf'

```

Copy the secret key in a file `~/.flaskToken` (no extra newlines or space characters)

```
echo 'f3cfe9ed8fae309f02079dbf' > ~/.flaskToken
```

At this point, the website should be able to load, but not necessarily successfully process the images.  

6. Set docker to work without sudo (more info [here](https://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo) ):

```
sudo groupadd docker

sudo gpasswd -a $USER docker
```
Then log out or restart docker using:

```
newgrp docker 

```

If it worked, it should be able to run `docker run hello-world` without sudo. 

7. Test to see if you can upload a template file and run BrainPainter through the flask app. If it works, you should see the progress bar and the generated images after 30 seconds.

If docker did not update changes try committing to the image:
https://phoenixnap.com/kb/how-to-commit-changes-to-docker-image

## Development notes

The website will serve requests for drawing brain images to the BrainPainter version installed within the docker container `mrazvan22/brain-coloring`. The website server will also do the image creation in parallel by spawning multiple processes for each request. See function main:processFile()

Note: There exists a docker API to interface with python, but I couldn't get it to work properly, so I'm running docker through unix processes instead.


## Customisation

Main files to modify are:
* main.py
* templates/index.html


## Deployment

For deployment, one should use Gunicorn. Flask should not be used for deployment as it is a slow web-engine only designed for development. Check out this tutorial for how to do it: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04

Main steps (extracted from the above tutorial) are as follows:
1. create wsgi.py entry point (already done)
2. test with gunicorn: `gunicorn --bind 0.0.0.0:5000 wsgi:app`
3. create systemd service unit file: `sudo nano /etc/systemd/system/myproject.service`. Content should be similar to this:

```
[Unit]
Description=Gunicorn instance to serve myproject
After=network.target

[Service]
User=sammy
Group=www-data
WorkingDirectory=/home/sammy/myproject
Environment="PATH=/home/sammy/myproject/myprojectenv/bin"
ExecStart=/home/sammy/myproject/myprojectenv/bin/gunicorn --workers 3 --bind unix:myproject.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

4. configure nginx to proxy requests: `sudo nano /etc/nginx/sites-available/myproject`. Cotent should be similar to:

```
server {
    listen 80;
    server_name your_domain www.your_domain;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/sammy/myproject/myproject.sock;
    }
}
```

5. Enable nginx server block configuration: `sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled`, then restart nginx: `sudo systemctl restart nginx`


6. Configure firewall to allow nginx full access: 

```
sudo ufw delete allow 5000
sudo ufw allow 'Nginx Full'
```


