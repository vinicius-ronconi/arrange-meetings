# arrange-meetings
This project uses Google Places API to suggest restaurants to go based on users preferences

This version considers that we will have an existing MongoDB collection with user preferences that we will just need to read it. This structure will contain things like: a list of their favorite cuisines, a range of prices they want to spend (from 0 to 4, according to the Google Places API), their home location & radius they want to commute. 

We're not considering any authentication feature in this scope. For now, the front-end will let you select two users from a list (organizer and invitee). The organizer will be able to override the default preferences (price range, cuisines and location).

The web service will find the places matching both user preferences and rank them first, but it will also show some invitee results that don't match the organizer preferences, so he or she will be able to suggest some place according to the invitee's preferences.

# local settings
Add a new file ArrangeMeetings/local_settings.py with the following content:
```python
GOOGLE_PLACES_API_KEY = 'YOUR_API_KEY'
USE_FAKE_DATA = True  # To use Fake Dao & API or False to use real data on Mongo & Google Places API```
