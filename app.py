from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)
database = mongo.db
############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""
    plants_data = database.plants.find()
    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        new_plant_info = {
            'plant_name': request.form["plant_name"],
            'variety': request.form["variety"],
            'photo_url': request.form["photo_url"],
            'date_planted': request.form["date_planted"]
        }
        new_plant = database.plants.insert_one(new_plant_info)
        return redirect(url_for('detail', plant_id = new_plant.inserted_id))

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    plant_to_show = database.plants.find_one_or_404({"_id": ObjectId(plant_id)})

    # TODO: Use the `find` database operation to find all harvests for the
    # plant's id.
    # HINT: This query should be on the `harvests` collection, not the `plants`
    # collection.
    harvests = database.harvests.find()

    context = {
        'plant' : plant_to_show,
        'harvests': harvests
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """Accepts a POST request with data for 1 harvest and inserts into database."""
    new_harvest = {
        'quantity': request.form["quantity"],
        'date_harvested': request.form["date_harvested"],
        'plant_id': plant_id
    }
    database.harvests.insert_one(new_harvest)
    return redirect(url_for('detail', plant_id = plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        # TODO: Make an `update_one` database call to update the plant with the
        # given id. Make sure to put the updated fields in the `$set` object.


        return redirect(url_for('detail', plant_id=plant_id))
    else:
        # TODO: Make a `find_one` database call to get the plant object with the
        # passed-in _id.
        plant_to_show = ''

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    """Delete's specified plant and all of its harvest data"""
    database.plants.delete_one({"_id": ObjectId(plant_id)})
    database.harvests.delete_many({"plant_id": ObjectId(plant_id)})
    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)
