# Question 2

### Background:

**Throughout these questions we are only dealing with bookings so don't worry about engineering a solution that involves cancellations also.**

A booking curve for a specific reserved night date is the graph which shows our
customers the cumulative sum of occupancy or revenue over time.

(example [purple line is the booking curve]: https://drive.google.com/file/d/10NYdhUqd0aBM4oqYij35kTntT0qDH5zO)

### Task 

Finish the booking curve endpoint, located in the `app.py` file at the bottom, to return two booking curves for a specific
hotel room and reserved_night_date. The first booking curve should be an occupancy curve (expressed as a percentage) 
and the second should be a revenue booking curve showing the cumulative sum of revenue over time.

We want the curve to go back in time 90 days and any booking prior to 90 days should be considered also (by including them with the results of the bookings at 90 days ago)

# Advice
This whole task can be done in SQL but its 50+ lines of SQL if you do. We strongly advise if you are getting stuck you just fetch the data you need and create for loops in python. There is no extra points for doing this in python vs doing this in SQL so please pick which ever you are comfortable using.

# Hint
booking curves are for ONE  reserved night date and they show how bookings flow in over time (booking_datetime is the time the booking was made).

We advise you start by calculating the occupancy curve then adding the revenue curve if you have time later as most of the code should be the same.

