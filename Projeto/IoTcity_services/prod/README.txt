Step-by-step guide to deploy the web server

On this section, we are going to explain how to do the deployment for production on a Linux Debian Operative System.

If the platform does not run locally, you may want first to assure that the minimum requirements are met ("../README_SERVER").


0) Download server files and put them on /srv.

1) To deploy gunicorn:

run "$ sudo pip install gunicorn"
Copy the "gunicorn.service" file (on "/prod") to the directory "/etc/systemd/system/"

run "$ sudo systemctl start gunicorn" 
run "$ sudo systemctl enable gunicorn"

To check if the service is working, you can verify the status with the command "$ sudo systemctl status gunicorn".

2) Now let's install Nginx:

"$ sudo apt-get install nginx"
To allow Nginx to communicate with HTTP, run the command "$ sudo ufw allow 'Nginx Full' "

Copy the file "prod/server", to "/etc/nginx/sites-available"

We now need to link the configuration file to the enabled websites. For that, run "$ sudo ln -s /etc/nginx/sites-available/server /etc/nginx/sites-enabled"

To verify if the configuration is done correctly, you can run "$ sudo nginx -t"

Finally, let's run the daemon with the command "$ sudo service nginx start"
To verify if the service is working correctly, you can run "$ sudo systemctl status nginx".


3) Message Broker (Rabbitmq):
sudo service rabbitmq-server start

4) Celery workers

Run "$ sudo apt-get install supervisor"

Copy the local configuration file, "prod/supervisord.conf", to "/server"

Execute the command "$ supervisord -c supervisord.conf" on the same folder.

To kill the process, run "$ pkill -f "supervisord" ".


5) We need to change some configuration settings in Django files.

Copy the "SECRET_KEY" in "server/settings.py" and paste it on new file in "/etc/iotcity/django_secret.txt". 

Copy the file "prod/settings.py" to "server/settings.py" and override the existent one.

Finally, on the folder "server", run "$ python manage.py collectstatic".

6) Let's change the database of the project.

Create a postgresql database:

Run:
"$ sudo su - postgres"
"$ psql"
"> CREATE DATABASE db"
"> CREATE USER admin WITH PASSWORD 'rootroot';"

"> ALTER ROLE myprojectuser SET client_encoding TO 'utf8';"
"> ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';"
"> ALTER ROLE myprojectuser SET timezone TO 'UTC';"

"> GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;"

After the user and the database are created, execute "$ python manage.py makemigrations".
Then, run "$ python manage.py migrate" to apply the changes on the new database.

Create a new super user in django, and go to the admin page.
From there, you can add as sensors and subscriptions as you want.

And that's it! The IoTCity is now fully deployed.
