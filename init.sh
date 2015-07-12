# development/localhost
export APP_SETTINGS="config.DevelopmentConfig"
export DATABASE_URL="sqlite:///catalog.db"

export GOOGLE_ID=305336525443-1u951dk3fvf103m7la9pc27sgs13put8.apps.googleusercontent.com
export GOOGLE_SECRET=vobF9Wteqy5Ofc6EvAvj104i

python models.py

python application.py
