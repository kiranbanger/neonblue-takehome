# Design Considerations and Improvements

## Code Organization

All of the code for the endpoints is in the routers directory. For a production system, I would have a src directory that would contain the bulk of the code, with the routers calling methods in the src directory.

---

## The Database Schema

Improvements I might make:
- Some table IDs are UUIDs and some are auto-incrementing integers. Database generated integer IDs should not be exposed via the API to the clients/users, but are probably better for performance. The only way to know for sure would be to compare the performance of the two options, but the results of that comparison might change as the database evolves, so we might just include both UUIDs and auto-incrementing integers from the start so that we don't have to make major updates later. 
---

## The Endpoints
I would remove the integer IDs from the return object in the models becuase they are not needed by the clients. 

The results endpoint returns a summary of the experiment, including:
- the number of users assigned to each variant, 
- the number of users who triggered each event type, and 
- the conversion rate for each variant per event type.

This is pretty rudimentary data, and given more time to generate realistic data, I would add more metrics and make the endpoint more configurable.