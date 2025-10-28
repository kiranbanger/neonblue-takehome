# Design Considerations and Improvements

## Code Organization

All of the code for the endpoints is in the routers directory. For a production system, I would have a src directory that would contain the bulk of the code, with the routers calling methods in the src directory.

---

## The Database Schema

One thing I would update are the IDs. Some IDs are UUIDs and some are auto-incrementing integers. Database generageted integer IDs should not be exposed via the API to the clients/users, but are probably better for performance, so we might want to have both UUIDs and auto-incrementing integers, and remove the integer IDs from the return in the models.

---

## The Endpoints

The results endpoint returns a summary of the experiment, including:
- the number of users assigned to each variant, 
- the number of users who triggered each event type, and 
- the conversion rate for each variant per event type. 
This is pretty rudimentary data, and given more time to generate realistic data, I would add more metrics and make the endpoint more configurable.