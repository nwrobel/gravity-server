# script to restart the server and reload all code
sudo service gunicorn stop;
sudo service nginx stop;
sudo service gunicorn start;
sudo service nginx start;


