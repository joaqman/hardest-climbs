import os
import json
import git

from flask import render_template
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from src.update import update
from src.tunnel import create_tunnel
from src.config import settings
from src.models import db, Climbers, Climbs, Repeats, Videos, Grades


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

app = Flask("Hardest Climbs", template_folder=THIS_FOLDER + "/templates")


# Database
if settings.local:
    tunnel = create_tunnel()
    tunnel.start()

    db_uri = "mysql://{user}:{pwd}@127.0.0.1:{port}/{user}${schema}".format(
        user=settings.db_username,
        pwd=settings.db_password,
        port=tunnel.local_bind_port,
        schema=settings.db_schema,
    )
else:
    db_uri = "mysql://{user}:{pwd}@127.0.0.1/{user}${schema}".format(
        user=settings.db_username,
        pwd=settings.db_password,
        schema=settings.db_schema,
    )


app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)

grade_map = {
    "9c": "5.15d",
    "9b/c": "5.15c/d",
    "9b+": "5.15c",
    "9b/+": "5.15b/c",
    "9b": "5.15b",
    "9a+": "5.15a",
    # Bouldering ---
    "9A": "V17",
    "8C+/9A": "V16/V17",
    "8C+": "V16",
    "8C/+": "V15/16",
    "8C": "V15",
}


with open(os.path.join(THIS_FOLDER, 'data/lead.json'), "r", encoding='utf-8') as f:
    lead_data = json.load(f)

with open(os.path.join(THIS_FOLDER, 'data/boulder.json'), "r", encoding='utf-8') as f:
    boulder_data = json.load(f)


def climber_ascents(climber, data):
    # TODO More elegant solution would require better data system than JSON/dict
    fa_data = [x for x in data if climber in x["fa"].lower()]
    repeat_data = [x for x in data if any(climber in y.lower() for y in x["repeat"])]
    return fa_data + repeat_data


@app.route('/')
def index():
    select = db.select(Climbs, Grades, Climbers).join(Grades).join(Climbers).where(Grades.rank >= 4)
    climbs = db.session.execute(select)

    return render_template('index.html', climbs=climbs)


@app.route('/sport')
def sport():
    return render_template('generic.html', title="Sport Climbing", category="sport", climbs=lead_data)


@app.route("/bouldering")
def bouldering():
    return render_template('generic.html', title="Bouldering", category="bouldering", climbs=boulder_data)


@app.route("/sport/<climber>")
def sport_climber(climber):
    return render_template('generic.html', title=f"Sport Climbing: {climber.capitalize()}", category="sport", climbs=climber_ascents(climber, lead_data))


@app.route("/bouldering/<climber>")
def bouldering_climber(climber):
    return render_template('generic.html', title=f"Bouldering: {climber.capitalize()}", category="bouldering", climbs=climber_ascents(climber, boulder_data))


@app.route("/update", methods=["POST"])
def webhook():
    if request.method == "POST":
        repo = git.Repo("~/mysite")
        origin = repo.remotes.origin
        origin.pull()
        
        update()
        
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400


# helper template filters

@app.template_filter('map_grade')
def map_grade(grade):
    return grade_map.get(grade)


@app.template_filter('bg_alternate')
def bg_alternate(index):
    return "secondary" if index % 2 == 0 else "dark"


@app.template_filter('climber_first_name')
def climber_first_name(name):
    return " ".join(name.split(" ")[0:-1])


@app.template_filter('climber_last_name')
def climber_last_name(name):
    return name.split(" ")[-1]
