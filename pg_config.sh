apt-get -qqy update
apt-get -qqy install postgresql python-psycopg2
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip
apt-get -qqy install sqlite
pip install bleach
pip install --user --upgrade flask-wtf
pip install Flask-OAuthlib
pip install ipython
#su postgres -c 'createuser -dRS vagrant'
#su vagrant -c 'createdb'
#su vagrant -c 'createdb catalog'

