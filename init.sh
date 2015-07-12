# development/localhost
export APP_SETTINGS="config.DevelopmentConfig"
export DATABASE_URL="sqlite:///catalog.db"

# Export google's key and secret
export GOOGLE_ID=305336525443-1u951dk3fvf103m7la9pc27sgs13put8.apps.googleusercontent.com
export GOOGLE_SECRET=vobF9Wteqy5Ofc6EvAvj104i

# Initialize models
python models.py

# Initialize application and listen on port: 8000
python application.py
