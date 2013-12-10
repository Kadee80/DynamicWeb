# mongoengine database module
from mongoengine import *
from datetime import datetime
import logging

	
class Theft(Document):
	#if you leave the max_lnegth off it is a text area, turn it on and you have an input
	
	formatAddress = StringField()
	zipcode = StringField()
	point = GeoPointField()

	when = StringField()

	# Category is a list of Strings
	parts = ListField(StringField(max_length=50))
	lockMethods = ListField(StringField(max_length=50))
	# Rides associated with this user

	# Timestamp 
	timestamp = DateTimeField(default=datetime.now())
	
