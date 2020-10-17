# Trade

## About the project
Project Trade is an online resource for online commerce.
It is currently under development.
The service is integrated with API distributers of various products, ranging between computers and furniture.
API needs to regularly renew the catalogs, items, characteristics, availability, prices, etc. It also include web interface for delivering the catalog to a potential customer with options to select and purchase the product.

## Run the project
Create a folder where you plan to save the project files.
And then make some commands:
```
git clone https://github.com/ivngithub/trade.git
cd trade
```

You must have Docker installed.

```
docker-compose build
docker-compose up
```

For the correct work of the project, file .env should be completed correctly.

## Run tests
If you want to see html report of tests coverage.

```
docker exec -it <container_name> bash
pytest -v --cov=app --cov-report html
```

If you want to run tests for project.

```
docker exec -it <container_name> bash
pytest -v --cov=app
```