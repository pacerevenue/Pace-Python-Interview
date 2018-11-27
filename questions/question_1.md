# Question 1

### Background:

This app is a simplified version of our API servers we use in production today.

In the current implementation of this application we have a concept of hotels, hotel rooms and bookings.

Each hotel has associated hotel rooms and each hotel room has  associated bookings. The models for these can be
found in `models.py`.

Hotel rooms have a concept of `capacity` which is the total number of rooms the hotel has of that type of room. E.g. if a hotel has a room called `Double Suite` and has 20 physical rooms of this type in their hotel then the capacity for this room is equal to 20. Similary if they have another room type called `Single Queen` with 30 physical rooms then the capacity for this room type is equal to 30. The total capacity for the hotel is equal to all the room type capacities summed e.g. 20 + 30 = 50 in the previous example.

Occupancy Percentage for any particular hotel room and reserved night date 

    Total Sales For Reserved Night Date * 100  / Capacity of Room

It is possible to calculate an occupancy percentage for multiple reserved night dates aggregated. E.g. if you want the occupancy currently for the next 7 days you would perform the followig calculation:

    (Total Sales Over Next 7 days * 100) / (Capacity of Room * 7)


Note: Currently we have a `static` capacity for each hotel room. e.g. on the hotel rooms table each room type has a capacity figure and we use this when calculating occupancy.


**Throughout these questions we are only dealing with bookings so don't worry about engineering a solution that involves cancellations also.**


When hotels decide that a room needs to be taken `offline` they can mark these rooms as `blocked` in their Property Management System **(PMS)**. This notifies us that they cant currently sell that room
between a start date and end date. They can mark multiple rooms and different room types as `offline` for various reasons including
refurbishment work and cleaning required.

Currently because we calculate occupancy by  using the capacity figure on the hotel rooms table, we are showing incorrect occupancies for reserved night dates where
the hotel has decided to block rooms. 



### Task 

The first task in this question is to create a database model in the `models.py` which allows us to store this extracted blocked room information that the hotels PMS send us.

Next this table should be used to update the exisiting `/occupancy` endpoint in `app.py` to return the actual real occupancy with the blocked rooms took into consideration.


#### Hint

Blocking rooms happens on the reserved night level meaning that a hotel can decide the start date and end date of the block and can add multiple blocks in the future if needed.

#### Example:
Setup
- hotel room: Queen Suite
- sales for tonight: 6
- capacity: 10
- blocked rooms: 4

Answer
- Current occupancy in Pace: 6 / 10 = 60%
- After your changes to the endpoint: 6 / (10 - 4) = 6 / 6 = 100%




