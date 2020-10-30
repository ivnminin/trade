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

If you launch first time you need to create a database.
```
docker exec -it $(docker inspect --format="{{.Id}}" trade_container) bash
flask create_db
```

Use localhost:8001 in browser.

## User Story

The application currently doesn’t have an interface. There are two options. First one is for the user. Second one for the administrator.

Route ```localhost:8001```
Currently, a user can only see and complete the form with a feedback. In that form, the user can provide a name, question, and contact information. After that, the administrator will get an email with that information. 

Route ```localhost:8001/backend```
Interface for the administrator has navigation.

Route ```localhost:8001/backend/category```
Display of all categories. You can see a parent for a particular category and you can see category is included or excluded.

Route ```localhost:8001/backend/task/category```
Display of all tasks for categories. Task’s completion time, success of the task, and result of the task. The task can by manually activated.

Route ```localhost:8001/backend/position```
Display of all items. You can see item’s name, vendor code, and item is included or excluded.

Route ```localhost:8001/backend/task/position```
Display of all tasks for items.  Task’s completion time, success of the task, and result of the task. The task can by manually activated.