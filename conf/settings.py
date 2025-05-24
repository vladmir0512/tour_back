from pathlib import Path
import os
import pyrebase

AUTH_USER_MODEL = 'users.CustomUser'
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-lp5=()m1te#cj*2zr!uf4gy_x%ulj3fi(&4p2(t+tvtj64t*uh'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'route',
    'api',
    'rest_framework',
    'corsheaders'
]
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware'
]
ROOT_URLCONF = 'conf.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'conf.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'charset': 'utf8mb4',
    }
}
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "route/static",
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_ALLOW_ALL = True
config = {
    'apiKey': "AIzaSyAI_Ws21kfg3FirZWUNIse-AsUwrwuDDro",
    'authDomain': "alexeyroutes.firebaseapp.com",
    'projectId': "alexeyroutes",
    'storageBucket': "alexeyroutes.firebasestorage.app",
    'messagingSenderId': "766026330256",
    'appId': "1:766026330256:web:01b1cdeaf63377a5346815",
    'measurementId': "G-RLG27RXYC9",
    'databaseURL': 'https://alexeyroutes-default-rtdb.europe-west1.firebasedatabase.app/'
}
FIREBASE= pyrebase.initialize_app(config)
FIREBASE_AUTH=FIREBASE.auth()
TIME_ZONE = 'Europe/Moscow'
CORS_ALLOWED_ORIGINS = ["http://10.0.2.2:8000", "http://127.0.0.1:8000", "http://localhost:8000", "http://89.104.66.155"]
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024