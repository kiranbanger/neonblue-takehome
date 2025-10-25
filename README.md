# neonblue-takehome

## Running the Docker Containers

To create and run the Docker containers, use the following command:

```bash
docker-compose up --build
```

This will:
- Build the FastAPI image
- Create and start both the MySQL and FastAPI containers
- Link them together automatically
- Start the FastAPI application on port 5000
- Start the MySQL database on port 3306

### Prerequisites

- Docker installed and running
- Docker Compose installed

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