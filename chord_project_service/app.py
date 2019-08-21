import os
import sqlite3

import chord_project_service

from flask import Flask, g, json, jsonify, request, Response
from uuid import uuid4, UUID


application = Flask(__name__)
application.config.from_mapping(
    DATABASE=os.environ.get("DATABASE", "chord_project_service.db")
)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(application.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(_e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with application.open_resource("schema.sql") as sf:
        db.executescript(sf.read().decode("utf-8"))

    db.commit()


def update_db():
    db = get_db()
    c = db.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='peers'")
    if c.fetchone() is None:
        init_db()
        return

    # TODO


application.teardown_appcontext(close_db)

with application.app_context():
    if not os.path.exists(os.path.join(os.getcwd(), application.config["DATABASE"])):
        init_db()
    else:
        update_db()


def validate_project(project):
    if "name" not in project or "description" not in project or "data_use" not in project:
        return False

    if (not isinstance(project["name"], str) or not isinstance("description", str)
            or not isinstance("data_use", dict)):
        # Also checks None
        return False

    # TODO: validate data_use

    return True


def preprocess_project(project):
    project["name"] = project["name"].strip()
    project["description"] = project["description"].strip()


def validate_dataset(dataset):
    if "dataset_id" not in dataset or "service_id" not in dataset or "data_type_id" not in dataset:
        return False

    if not isinstance(dataset["data_type_id"], str):
        return False

    try:
        UUID(dataset["dataset_id"])
        UUID(dataset["service_id"])
        return True

    except ValueError:
        return False


def preprocess_dataset(dataset):
    # Standardize UUID formats
    dataset["dataset_id"] = str(UUID(dataset["dataset_id"]))
    dataset["service_id"] = str(UUID(dataset["service_id"]))

    # Trim whitespace
    dataset["data_type_id"] = dataset["data_type_id"].strip()


# TODO: Authentication
@application.route("/projects", methods=["GET", "POST"])
def project_list():
    db = get_db()
    c = db.cursor()

    if request.method == "POST":
        project = request.json

        # Validate posted project
        # TODO: Better errors

        if not validate_project(project):
            return Response(status=400)

        preprocess_project(project)

        c.execute("SELECT name FROM projects WHERE name = ?", (project["name"],))
        if c.fetchone() is not None:
            # Already exists
            return Response(status=400)

        c.execute("INSERT INTO projects (id, name, description, data_use) VALUES (?, ?, ?, ?)",
                  (str(uuid4()), project["name"], project["description"], json.dumps(project["data_use"])))

        db.commit()

        return Response(status=201)

    c.execute("SELECT * FROM projects")
    db.commit()

    projects = [dict(p) for p in c.fetchall()]
    for project in projects:
        project["data_use"] = json.loads(project["data_use"])

    return jsonify(projects)


# TODO: Authentication
@application.route("/projects/<uuid:project_id>", methods=["GET", "POST", "DELETE"])
def project_detail(project_id):
    db = get_db()
    c = db.cursor()

    c.execute("SELECT * FROM projects WHERE id = ?", (project_id,))

    project = c.fetchone()

    if project is None:
        # TODO: Nicer errors
        return Response(status=400)

    if request.method == "POST":
        new_project = request.json
        if not validate_project(new_project):
            return Response(status=400)

        preprocess_project(new_project)

        c.execute("UPDATE projects SET name = ?, description = ?, data_use = ? WHERE id = ?",
                  (new_project["name"], new_project["description"], json.dumps(new_project["data_use"]), project["id"]))

        db.commit()

        return Response(status=204)

    elif request.method == "DELETE":
        c.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return Response(status=204)

    project = dict(project)
    project["data_use"] = json.loads(project["data_use"])

    return jsonify(project)


# TODO: Authentication
@application.route("/projects/<uuid:project_id>/datasets", methods=["GET", "POST"])
def project_datasets(project_id):
    db = get_db()
    c = db.cursor()

    c.execute("SELECT * FROM projects WHERE id = ?", (project_id,))

    project = c.fetchone()

    if project is None:
        # TODO: Nicer errors
        return Response(status=400)

    if request.method == "POST":
        new_dataset = request.json
        if not validate_dataset(new_dataset):
            return Response(status=400)

        preprocess_dataset(new_dataset)

        c.execute("INSERT INTO project_datasets (dataset_id, service_id, data_type_id, project_id) VALUES (?, ?, ?, ?)",
                  (new_dataset["dataset_id"], new_dataset["service_id"], new_dataset["data_type_id"], project["id"]))

    c.execute("SELECT * FROM project_datasets WHERE project_id = ?", (project_id,))

    return jsonify([dict(r) for r in c.fetchall()])


@application.route("/service-info", methods=["GET"])
def service_info():
    # Spec: https://github.com/ga4gh-discovery/ga4gh-service-info

    return jsonify({
        "id": "ca.distributedgenomics.chord_project_service",  # TODO: Should be globally unique
        "name": "CHORD Project Service",                       # TODO: Should be globally unique
        "type": "urn:chord:project_service",                   # TODO
        "description": "Project service for a CHORD application.",
        "organization": {
            "name": "GenAP",
            "url": "https://genap.ca/"
        },
        "contactUrl": "mailto:david.lougheed@mail.mcgill.ca",
        "version": chord_project_service.__version__,
        "extension": {}
    })
