# neonblue-takehome

## Running the Docker Containers

```bash
docker compose up
```
or if you're running an older version of Docker:
```bash
docker-compose up --build
```
This will:
- Build/rebuild the FastAPI image with your latest code changes
- Create and start both the MySQL and FastAPI containers
- Link them together automatically
- Start the FastAPI application on port 5000
- Start the MySQL database on port 3306

### Prerequisites

- Docker installed and running
- Docker Compose installed (depending on your Docker version)

### Accessing the Application

Once the containers are running:

- **FastAPI Application**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs
- **MySQL Database**: localhost:3306
  - Username: `app_user`
  - Password: `app_password`
  - Database: `experiments_db`

### Stopping the Containers

To stop the running containers:

```bash
docker-compose down
```

To stop and remove all data (including the database):

```bash
docker-compose down -v
```