# CTV

## Authors
- Elizabeth Gasañol
- Federico Martinez
- Pablo Pissi

## Installation

### Install mysql dependencies
```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config
```

### Install project dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # use requirements-dev.txt for development
```

## Run the project

### Run the services
```bash
docker compose up -d
```

### Run the server
```bash
python manage.py runserver
```

## Create migrations
```bash
python manage.py makemigrations
```

## Run migrations
```bash
python manage.py migrate
```
