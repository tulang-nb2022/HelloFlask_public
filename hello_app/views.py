# NOTE contains the routings and the view function
import re 
from datetime import datetime
from flask import Flask
from flask import render_template 

from . import app

from . import kmeans 
import json 

@app.route("/")
def home():
    return render_template("home.html")




# Serving other flext templates
# New functions
@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/movies/")
def movies_there():
    return render_template(
        "index.html",
        date=datetime.now()
    )

# Serving static templates
@app.route("/api/data")
def get_data():
    return app.send_static_file("data.json")



