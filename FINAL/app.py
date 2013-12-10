import os, datetime
import re
import random
import requests
from flask import Flask, request, render_template, redirect, abort, jsonify
from unidecode import unidecode


# mongoengine database module
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)   # create our flask app
app.config['CSRF_ENABLED'] = False

# --------- Database Connection ---------
# MongoDB connection to MongoLab's database
app.config['MONGODB_SETTINGS'] = {'HOST':os.environ.get('MONGOLAB_URI'),'DB': 'BikeStat'}

#this prints shit to terminal
app.logger.debug("Connecting to MongoLabs")
db = MongoEngine(app) # connect MongoEngine with Flask App

# import data models
import models

# hardcoded [parts] for the checkboxes on the form
parts = ['the_whole_damn_thing', 'front_wheel','back_wheel', 'seat', 'handlebars', 'lights', 'pedals', 'brakes', 'shifting_set',  'saddle_pack', 'bike_computer', 'accessories' ]
# how was bike secured
lockMethods = ['U-lock_frame', 'U-lock_front wheel', 'U-lock_back wheel', 'cable_through wheels', 'cable_lock frame', 'cable_lock wheels']


# --------- Routes ----------
# main page, theft reporter

@app.route("/report", methods=['GET','POST'])
def index():

	# if form was submitted and it is valid...
	if request.method == "POST":

		# get form data - create new user
		theft = models.Theft()
		
		theft.formatAddress = request.form.get('formatAddress')
		theft.zipcode = request.form.get('zip')
		theft.point = [float(request.form.get('lon')), float(request.form.get('lat'))]
		theft.when = request.form.get('when')
		theft.parts = request.form.getlist('parts') # getlist will pull multiple items into a list
		theft.lockMethods= request.form.getlist('lockMethods') # getlist will pull multiple items into a list
		theft.save() # save it

		# redirect to the solition page
		return redirect('/allthefts')
		#return redirect('/user/')

	else:

		# render the template
		templateData = {
		'thefts' : models.Theft.objects(),
		'parts' : parts,
		'lockMethods' : lockMethods
		}
		return render_template("newtheft.html", **templateData)

@app.route("/")
def test():
	return render_template('vis.html')

@app.route("/allthefts")
def allusers():

	templateData = {
		'thefts' : models.Theft.objects()
		}
	return render_template('allthefts.html', **templateData)
####################################

@app.route("/theft/<theft_id>")
def solution_display(theft_id):

	# get solution by solution_slug
	try:
		theft = models.Theft.objects.get(id=theft_id)
	except:
		abort(404)

	# prepare template data
	templateData = {
		'theft' : theft,
		'parts' : parts,
		'lockMethods' : lockMethods
		}

	# render and return the template
	return render_template('theft_entry.html', **templateData)

####################################

# Display all solutions for a specific category
@app.route("/part/<part_name>")
def by_category(part_name):

	# try and get solutions where cat_name is inside the categories list
	try:
		thefts = models.Theft.objects(parts=part_name)
		

	# not found, abort w/ 404 page
	except:
		abort(404)

	# prepare data for template
	templateData = {
		'current_part' : {
			'slug' : part_name,
			'name' : part_name.replace('_',' ')
	
		},
		'thefts' : thefts,
		'parts' : parts
	}

	# render and return template
	return render_template('category_listing.html', **templateData)




####################################
@app.route('/data/thefts')
def data_thefts():
 
	# query for the users - return oldest first, limit 10
	thefts = models.Theft.objects().order_by('-timestamp')
 
	if thefts:
 
		# list to hold users
		public_thefts = []
 
		#prep data for json
		for t in thefts:
			
			tmpTheft= {
				'type':'feature',
				'properties' :{
				'formatAddress' : t.formatAddress,
				'zipcode' : t.zipcode,
				
				'when':t.when,
				'parts':t.parts,
				'lockMethods':t.lockMethods,
				'reported' : str( t.timestamp )
				},
				'geometry':{
				'type': 'point',
				'coordinates' : t.point
				}
				
				
			}
 
 
			# insert user dictionary into public_users list
			public_thefts.append( tmpTheft )
 
		# prepare dictionary for JSON return
		data = {
			
			'thefts' : public_thefts
		}
 
		# jsonify (imported from Flask above)
		# will convert 'data' dictionary and set mime type to 'application/json'
		return jsonify(data)
 
	else:
		error = {
			'status' : 'error',
			'msg' : 'unable to retrieve users'
		}
		return jsonify(error)


####################################


 
 
##################################





@app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404


# slugify the title 
# via http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
	"""Generates an ASCII-only slug."""
	result = []
	for word in _punct_re.split(text.lower()):
		result.extend(unidecode(word).split())
		return unicode(delim.join(result))






# --------- Server On ----------
# start the webserver
if __name__ == "__main__":
	app.debug = True
	
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)



	