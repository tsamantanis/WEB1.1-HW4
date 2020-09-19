from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from fruits import fruits
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
def fruits_list():
    """Display the fruits list page."""
    fruits_data = database.fruits.find()
    context = {
        'fruits': fruits_data,
    }
    return render_template('fruits_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the fruit creation page & process data from the creation form."""
    if request.method == 'POST':
        print(request.form["fruit"])
        photo_url, color = get_fruit_details(request.form["fruit"])
        new_fruit_info = {
            'name': request.form["fruit"],
            'variety': request.form["variety"],
            'photo_url': photo_url,
            'color': color,
            'date_planted': request.form["date_planted"]
        }
        new_fruit = database.fruits.insert_one(new_fruit_info)
        return redirect(url_for('detail', fruit_id = new_fruit.inserted_id))

    else:
        return render_template('create.html', fruits = fruits)

@app.route('/fruit/<fruit_id>')
def detail(fruit_id):
    """Display the fruit detail page & process data from the harvest form."""
    fruit_to_show = database.fruits.find_one_or_404({"_id": ObjectId(fruit_id)})
    harvests = database.harvests.find({"fruit_id": ObjectId(fruit_id)})
    context = {
        'fruit' : fruit_to_show,
        'harvests': harvests,
        'harvest_count': harvests.count()
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<fruit_id>', methods=['POST'])
def harvest(fruit_id):
    """Accepts a POST request with data for 1 harvest and inserts into database."""
    new_harvest = {
        'quantity': request.form["quantity"],
        'date_harvested': request.form["date_harvested"],
        'fruit_id': ObjectId(fruit_id)
    }
    database.harvests.insert_one(new_harvest)
    return redirect(url_for('detail', fruit_id = fruit_id))

@app.route('/edit/<fruit_id>', methods=['GET', 'POST'])
def edit(fruit_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        updated_fruit_info = { "$set": {
            'fruit_name': request.form["fruit_name"],
            'variety': request.form["variety"],
            'photo_url': request.form["photo_url"],
            'date_planted': request.form["date_planted"]
        }}
        database.fruits.update_one({"_id": ObjectId(fruit_id)}, updated_fruit_info)
        return redirect(url_for('detail', fruit_id = fruit_id))
    else:
        fruit_to_show = database.fruits.find_one_or_404({"_id": ObjectId(fruit_id)})
        context = {
            'fruit': fruit_to_show
        }

        return render_template('edit.html', **context)

@app.route('/delete/<fruit_id>', methods=['POST'])
def delete(fruit_id):
    """Delete's specified fruit and all of its harvest data"""
    database.fruits.delete_one({"_id": ObjectId(fruit_id)})
    database.harvests.delete_many({"fruit_id": ObjectId(fruit_id)})
    return redirect(url_for('fruits_list'))

# Error Handling

@app.errorhandler(404)
def show_404(error):
    """Display a 404 error page"""
    return render_template('error_page.html', message = "Oops! Looks like you are using an invalid URL.", button = "Back to Home"), 404

# Helpers

def get_fruit_details(fruit):
    """Returns image url for specified fruit"""
    index = 0
    for fruit_preset in fruits:
        for key in fruit_preset:
            if fruit == str(key):
                return fruits[index][str(key)]['url'], fruits[index][str(key)]['color']
        index += 1

if __name__ == '__main__':
    app.run(debug=True)
