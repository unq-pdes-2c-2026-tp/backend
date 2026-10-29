# CTV

## Authors
- Elizabeth Gasañol
- Federico Martinez
- Pablo Pissi

## ERM
Ver acá: [link](ERM.md)

### Update ERM

You can update the ERM by running the following command:

```bash
./update_erm.sh
```

## Run the project

### Run the services
```bash
docker compose up -d
```

## Create migrations
```bash
python manage.py makemigrations
```

## Run migrations
```bash
python manage.py migrate
```
