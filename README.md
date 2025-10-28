# neonblue-takehome

## Environment Configuration

Before running the application, create a `.env` file in the root directory with the following configuration:

```env
# MySQL Configuration
MYSQL_ROOT_PASSWORD=<your_mysql_root_password>
MYSQL_DATABASE=experiments_db
MYSQL_USER=app_user
MYSQL_PASSWORD=<your_mysql_password>
MYSQL_HOST=mysql
MYSQL_PORT=3306

# Database URL
DATABASE_URL=mysql+pymysql://app_user:<your_mysql_password>@mysql:3306/experiments_db

# Authentication Tokens (comma-separated)
VALID_TOKENS=test-token-123,demo-token-456

# Token to Client ID Mapping (format: token:client_id, separated by commas)
TOKEN_CLIENT_ID_MAP=test-token-123:1,demo-token-456:2
```

## Running the Docker Containers

```bash
docker compose up
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
- `.env` file configured with required environment variables

### Accessing the Application

Once the containers are running:

- **FastAPI Application**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs
- **MySQL Database**: localhost:3306

## Documentation

For detailed API endpoint documentation and usage examples, see [API_USAGE.md](API_USAGE.md).
### Stopping the Containers

To stop the running containers:

```bash
docker compose down
```

To stop and remove all data (including the database):

```bash
docker compose down -v
```

# Design Considerations and Improvements

## Code Organization

All of the code for the endpoints is in the routers directory. For a production system, I would have a src directory that would contain the bulk of the code, with the routers calling methods in the src directory.

---

## The Database Schema

Improvements I might make:
- Some table IDs are UUIDs and some are auto-incrementing integers. Database generated integer IDs should not be exposed via the API to the clients/users, but are probably better for performance. The only way to know for sure would be to compare the performance of the two options, but the results of that comparison might change as the database evolves, so we might just include both UUIDs and auto-incrementing integers from the start so that we don't have to make major updates later. 
---

## The Endpoints
I would remove the integer IDs from the return object in the models because they are not needed by the clients. 

The results endpoint returns a summary of the experiment, including:
- the number of users assigned to each variant, 
- the number of users who triggered each event type, and 
- the conversion rate for each variant per event type.

This is pretty rudimentary data, and given more time to generate realistic data, I would add additional metrics and make the endpoint more configurable.