#===============================================================================
# Jokr Backend production server settings file
#
# Nick Wrobel
# Created: 1/8/15
# Modified: 2/25/16
#===============================================================================

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jqe#b&(f797rq7^4019drdopnj5b&acu^pqm7oek%rvdxfb0yz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['gravitybackend.ddns.net']

#------------------------------------------------------------------------------ 
# Settings customized to Gravity

# FEATURES
HTTP_RESPONSE_MESSAGES = True # enables a more detailed server response
PRUNE_OLD_LOCALPOSTS = False # delete old localposts after time limit
PRUNE_OLD_MESSAGES = False # delete old messages after time limit
PRUNE_OLD_USERS = False # delete unused user accounts after time limit
PRUNE_STATIC_CONTENT = False # remove old static content from the 3rd party static content hoster
RATE_LIMIT_LOCAL = False # limit the rate a user posts to local
RATE_LIMIT_LIVE = False # limit the rate a user posts to live (replies)
OP_THREAD_LIMIT = False # limits the OP to X threads at a time
LIMIT_IMAGE_REPLIES = False # sets a limit on the max number of image replies in a thread
HIDE_OWN_LOCALPOSTS = False # determines if a user can see his own posts on local
EMAIL_NOTIFICATIONS = True # send email notifications from server

# CONTENT SETTINGS
BOARD_THREAD_LIMIT = 10
LOCALPOST_MAX_AGE_HOURS = 6
MESSAGE_MAX_AGE_HOURS = 24
USER_MAX_AGE_DAYS = 1

# MODERATION SETTINGS
LOCAL_MAX_POSTS_WITHIN_TIMEFRAME = 10
LOCAL_MAX_POSTS_TIMEFRAME_MINUTES = 10
LIVE_MAX_POSTS_WITHIN_TIMEFRAME = 10
LIVE_MAX_POSTS_TIMEFRAME_MINUTES = 10
REPLY_MAX_POSTS_WITHIN_TIMEFRAME = 10
REPLY_MAX_POSTS_TIMEFRAME_MINUTES = 10
MODERATION_CACHE_DIR = '/var/webserver/JokrBackend/ExternalScripts/cache/'

# AWS
AWS_REGION_NAME = 'us-east-1'
AWS_BUCKET_NAME = 'launch-zone'
AWS_ARHCIVE_BUCKET_NAME = 'gravity-content-archive'
AWS_COGNITO_IDENTITY_POOL_ID = 'us-east-1:7e122fe9-aee8-4536-b675-f2f4e882b724'
AWS_COGNITO_DEVELOPER_PROVIDER_NAME = 'gravity.johnquinn.com'
AWS_COGNITO_TOKEN_DURATION = 86400 # seconds

# EMAIL CONFIG
MAX_TIME_BETWEEN_EMAILS_SEC = 60
SENDER_EMAIL = 'server@gravwith.us'
EMAIL_USE_TLS = True
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'AKIAJ64MG6J3CZVN2B6A'
EMAIL_HOST_PASSWORD = 'AsmceYIFSjFPScaCyR7QhvbN4Wdb5Ju49PAPvUJWmWHd'
EMAIL_RECIPIENTS = ['nickwrobel2@gmail.com',
                    'nicholaswrobel@gravwith.us']



# Application definition
# Include 'JokrBackned' here to tell django about our app
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'JokrBackend'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'JokrBackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'JokrBackend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Gravity_db',
        'USER': 'grav',
        'PASSWORD': 'Win32.64.128.exe!',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = False

APPEND_SLASH = False # Makes URLs without the trailing '/' 404


LOG_LOCATION = '/var/log/JokrBackend/' # location of the log files


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    # Formatters - control how the log is textually written to the text file
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
           
    # Handlers - controls what to do with the log message.
    'handlers': {
                 
        # catchall loggers - catch all exceptions in python/django that
        # are not caught explicitly
        'django_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': LOG_LOCATION + 'django.log',
            'formatter': 'verbose'
        },
        'django_db': {
            'level': 'ERROR',
            'class': 'JokrBackend.DataCollection.DataCollector.DjangoMiddlewareErrorLogger',
            'formatter': 'verbose'
        },

        # null handler
        'null': {
            'level': 'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
    },
           
    # Loggers - sends the log message to the right handler.
    #    django - all messages from djangos internals will use django file
    #                logging and our database logging
    'loggers': {
        # catchall loggers
        'django': {
            'handlers':['django_file', 'django_db'],
            'propagate': True,
            'level':'DEBUG',
        },
 
        # to stifle mysql logging, set the DB package to use the null handler
        'django.db.backends': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level':'DEBUG',
        },
    }
}



