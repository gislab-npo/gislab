"""
Django settings for webgis project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '{{ secret_key }}'

TEMPLATE_DEBUG = False

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Bratislava'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': '',
		'USER': '',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')



WEBGIS_OWS_URL = 'http://server.gis.lab/cgi-bin/qgis_mapserv.fcgi'

WEBGIS_SCALES = (10000000,5000000,2500000,1000000,500000,250000,100000,50000,25000,10000,5000,2500,1000,500)

# Dictionary of <MIME Type>: <File extension> pairs
FILE_EXTENSIONS_TABLE = {
	"application/json": "json",
	"application/geojson": "geojson",
}



ALLOWED_HOSTS = ['web.gis.lab']

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
)

# Application definition

INSTALLED_APPS = (
	'django.contrib.staticfiles',
	'webgis.viewer',
	'webgis.storage',
)

ROOT_URLCONF = '{{ project_name }}.urls'

WSGI_APPLICATION = '{{ project_name }}.wsgi.application'
