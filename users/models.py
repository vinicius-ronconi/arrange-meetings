import mongoengine
import mongoengine.fields as fields


mongoengine.connect('users')


class UserPreferences(mongoengine.Document):
    user_id = fields.IntField(required=True)

    home_location = fields.GeoPointField(required=True)
    radius_in_meters = fields.IntField(required=True)

    min_price = fields.IntField(required=True)
    max_price = fields.IntField(required=True)

    restaurant_types = fields.ListField(field=fields.StringField(), required=True)


if UserPreferences.objects.all().count() == 0:
    UserPreferences(
        user_id=1,  # Bob
        home_location=(40.758899,-73.987325),  # Times Square
        radius_in_meters=8000,
        min_price=0,
        max_price=4,
        restaurant_types=['japanese', 'italian', 'brazilian', 'BBQ', 'hamburger', 'mexican', 'fast food'],
    ).save()
    UserPreferences(
        user_id=2,  # Alice
        home_location=(40.7794406,-73.965438),  # The Met
        radius_in_meters=16000,
        min_price=0,
        max_price=4,
        restaurant_types=['brazilian', 'BBQ', 'hamburger', 'mexican', 'fast food'],
    ).save()
    UserPreferences(
        user_id=3,  # John
        home_location=(40.7505085,-73.9956327),  # Madison Square Garden
        radius_in_meters=32000,
        min_price=3,
        max_price=4,
        restaurant_types=['vegan'],
    ).save()
    UserPreferences(
        user_id=4,  # Mary
        home_location=(40.7570917,-73.8480153),  # City Field
        radius_in_meters=3200,
        min_price=4,
        max_price=4,
        restaurant_types=['japanese', 'italian', 'indian'],
    ).save()
