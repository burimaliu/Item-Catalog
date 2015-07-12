###Item Catalog

###About:

This is a Python-Flask project using Sqlite database to fulfill a music catalog needs.
It provides a list of items(music list) with categories and registration/authentication system using (Google Oauth) to allow users add/edit/delete their own items.


###Requirements to run this application:

1. alembic==0.7.4
2. Flask==0.10.1
3. Flask-Migrate==1.3.0
4. Flask-Script==2.0.5
5. Flask-SQLAlchemy==2.0
6. Flask-OAuthlib=0.9.1
7. Flask-flask-wtf
8. gunicorn==19.2.1
9. itsdangerous==0.24
10. Jinja2==2.7.3
11. Mako==1.0.1
12. MarkupSafe==0.23
13. requests==2.5.1
14. SQLAlchemy==0.9.8
15. Werkzeug==0.10.1

Or use "pg_config.sh" to have them installed into your environment.

###How to run this application:

1. Clone this repository to your working directory
2. Make sure none of requirements above is missing
3. From your working directory run "sh init.sh"

That's it, you should see on your console something like: Running on http://0.0.0.0:8000/

Open your browser and navigate to: http://0.0.0.0:8000/
