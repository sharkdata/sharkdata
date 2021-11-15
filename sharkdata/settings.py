"""
Django settings for sharkdata_proj project.

"""

import os
import pathlib
import logging

DEFAULT_APP_NAME = "sharkdata"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# Environment variables.
env_debug = os.environ.get("ENV_DJANGO_DEBUG", "True")
env_secret_key = os.environ.get("ENV_DJANGO_SECRET_KEY", "")
env_allowed_hosts = os.environ.get("ENV_DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
env_timezone = os.environ.get("ENV_DJANGO_TIMEZONE", "Europe/Stockholm")
env_base_dir = os.environ.get("ENV_BASE_DIR", "")
env_data_dir = os.environ.get("ENV_DATA_DIR")

env_use_postgresql = os.environ.get("ENV_DJANGO_USE_POSTGRESQL", "False")
env_psql_db_name = os.environ.get("ENV_DJANGO_PSQL_DB_NAME", "sharkdata")
env_psql_db_user = os.environ.get("ENV_DJANGO_PSQL_DB_USER", "sharkdata")
env_psql_db_pass = os.environ.get("ENV_DJANGO_PSQL_DB_PASSWORD", None)
env_psql_db_host = os.environ.get("ENV_DJANGO_PSQL_DB_HOST", "127.0.0.1")
env_psql_db_port = os.environ.get("ENV_DJANGO_PSQL_DB_PORT", None)

env_enable_syslog = os.environ.get("ENV_DJANGO_ENABLE_SYSLOG", "False")

env_app_name = os.environ.get("ENV_DJANGO_APP_NAME", DEFAULT_APP_NAME)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
if env_debug.lower() in ["true", "t", "yes", "y"]:
    DEBUG = True

USE_POSTGRESQL = False
if env_use_postgresql.lower() in ["true", "t", "yes", "y"]:
    USE_POSTGRESQL = True

ENABLE_SYSLOG = False
if env_enable_syslog.lower() in ["true", "t", "yes", "y"]:
    ENABLE_SYSLOG = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = pathlib.Path(BASE_DIR).parent.parent
if env_base_dir:
    root_dir = pathlib.Path(env_base_dir)

if DEBUG:
    print("DEBUG: root_dir: ", root_dir)

DATASETS_FOLDER_NAME = "datasets"
RESOURCES_FOLDER_NAME = "resources"
EXPORTFORMATS_FOLDER_NAME = "exportformats"

FILENAME_PATTERN_ID_FORMAT = "FORMAT"
FILENAME_PATTERN_ID_DATATYPE = "DATATYPE"
FILENAME_PATTERN_ID_YEAR = "YEAR"
FILENAME_PATTERN_ID_GENERATED = "GENERATED"
FILENAME_PATTERN_ID_FILETYPE = "FILETYPE"
FILENAME_PATTERN_VAR_START_SIGN = "<"
FILENAME_PATTERN_VAR_STOP_SIGN = ">"
EXPORTFORMATS_FILENAME_PATTERN = "<FORMAT>_<INSTITUTE>_<DATATYPE>_<YEAR>_version_<GENERATED>.<FILETYPE>"
EXPORTFORMATS_LOG_FILENAME_ENDING = "_LOG.txt"

LOGGER = logging.getLogger("SHARKdata")
SHARKDATA_DB = pathlib.Path(root_dir, "db")
SHARKDATA_LOG = pathlib.Path(root_dir, "log")
SHARKDATA_STATIC = pathlib.Path(root_dir, "static")
SHARKDATA_DATA_IN = pathlib.Path(root_dir, "data_in")
SHARKDATA_DATA_IN_DATASETS = pathlib.Path(SHARKDATA_DATA_IN, DATASETS_FOLDER_NAME)
SHARKDATA_DATA_IN_RESOURCES = pathlib.Path(SHARKDATA_DATA_IN, RESOURCES_FOLDER_NAME)
SHARKDATA_DATA_IN_EXPORTFORMATS = pathlib.Path(SHARKDATA_DATA_IN, EXPORTFORMATS_FOLDER_NAME)
SHARKDATA_DATA = pathlib.Path(root_dir, "data")
SHARKDATA_DATA_DIR = pathlib.Path(env_data_dir) if env_data_dir != None else None

# Create missing directories.
if not SHARKDATA_DB.exists():
    SHARKDATA_DB.mkdir(parents=True)
if not SHARKDATA_LOG.exists():
    SHARKDATA_LOG.mkdir(parents=True)
if not SHARKDATA_STATIC.exists():
    SHARKDATA_STATIC.mkdir(parents=True)
if not SHARKDATA_DATA.exists():
    SHARKDATA_DATA.mkdir(parents=True)
if not SHARKDATA_DATA_IN.exists():
    SHARKDATA_DATA_IN.mkdir(parents=True)


def setup_data_link_to_target(base_source_dir, folder_name, target_dir):
    source_dir = pathlib.Path(base_source_dir, folder_name)
    if not source_dir.exists():
        raise Exception("No %s folder exists at %s!" % (folder_name, env_data_dir))
    if target_dir.exists():
        if pathlib.Path(target_dir).is_symlink():
            os.unlink(target_dir)
        else:
            raise Exception(
                "%s folder exists at %s. If you want to replace it with data from %s, manually remove folder first."
                % (folder_name, base_source_dir, target_dir)
            )
    os.symlink(source_dir, target_dir, target_is_directory=True)


if SHARKDATA_DATA_DIR and SHARKDATA_DATA_DIR != SHARKDATA_DATA_IN:
    if not SHARKDATA_DATA_DIR.exists():
        raise Exception(
            "Data directory %s does not exist or is not accessible!"
            % (SHARKDATA_DATA_DIR)
        )
    setup_data_link_to_target(
        SHARKDATA_DATA_DIR, DATASETS_FOLDER_NAME, SHARKDATA_DATA_IN_DATASETS
    )
    setup_data_link_to_target(
        SHARKDATA_DATA_DIR, RESOURCES_FOLDER_NAME, SHARKDATA_DATA_IN_RESOURCES
    )
else:
    if not SHARKDATA_DATA_IN_DATASETS.exists():
        SHARKDATA_DATA_IN_DATASETS.mkdir(parents=True)
    if not SHARKDATA_DATA_IN_RESOURCES.exists():
        SHARKDATA_DATA_IN_RESOURCES.mkdir(parents=True)

if env_secret_key:
    SECRET_KEY = env_secret_key
else:
    raise Exception(
        "Secret key must be provided by setting environment variable ENV_DJANGO_SECRET_KEY'!"
    )

ALLOWED_HOSTS = ["localhost"]
if env_allowed_hosts:
    host_list = []
    for host in env_allowed_hosts.split(","):
        host_list.append(host)
    ALLOWED_HOSTS = host_list

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # For SHARKdata.
    "app_sharkdata_base",
    "app_datasets",
    "app_ctdprofiles",
    "app_resources",
    "app_exportformats",
    "filehandler",
]


########### TEST. ###########
REST_FRAMEWORK = {"DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema"}


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sharkdata.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sharkdata.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
if USE_POSTGRESQL:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env_psql_db_name,
            "USER": env_psql_db_user,
            "HOST": env_psql_db_host,
        }
    }
    if env_psql_db_port != None:
        DATABASES["default"]["PORT"] = env_psql_db_port
    if env_psql_db_pass != None:
        DATABASES["default"]["PASSWORD"] = env_psql_db_pass
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(pathlib.Path(SHARKDATA_DB, "db.sqlite3")),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

# TIME_ZONE = 'UTC'
TIME_ZONE = env_timezone

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# Static files will be collected and put here by running the
# command: python manage.py collectstatic
STATIC_ROOT = str(SHARKDATA_STATIC)
STATICFILES_DIRS = (str(pathlib.Path(BASE_DIR, "app_sharkdata_base", "static")),)

STATIC_URL = "/static/"

# Logging.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {
            "format": "python[" + env_app_name + "]: %(message)s",
            "datefmt": "%d%b%YT%H:%M:%S",
        }
    },
    "handlers": {
        "file_error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(SHARKDATA_LOG, "sharkdata_errors.log"),
            "maxBytes": 1024 * 1024,
            "backupCount": 10,
        },
        "file_debug": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(SHARKDATA_LOG, "sharkdata_debug.log"),
            "maxBytes": 1024 * 1024,
            "backupCount": 10,
        },
        "syslog": {
            "level": "INFO",
            "class": "logging.handlers.SysLogHandler",
            "formatter": "standard",
            "facility": "local3",
            "address": "/dev/log",
        },
    },
    "loggers": {
        "": {
            "handlers": ["file_error", "file_debug"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

if ENABLE_SYSLOG:
    LOGGING["loggers"][""]["handlers"].append("syslog")
