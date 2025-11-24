import flask

import functions_framework

from app import get_index_context, init_connection_pool, migrate_db, save_vote

############ TABS vs. SPACES App for Cloud Functions ############

# lazy global initialization
# db connection must be established within request context
db = None

app = Flask(__name__)

@functions_framework.http
def votes(request: flask.Request) -> flask.Response:
    """Handles HTTP requests to our application.

    Args:
        request: a Flask request object.

    Returns:
        Flask HTTP Response to the client.
    """
    global db
    # initialize db within request context
    if not db:
        # initiate a connection pool to a Cloud SQL database
        db = init_connection_pool()
        # creates required 'votes' table in database (if it does not exist)
        migrate_db(db)
    if request.method == "GET":
        context = get_index_context(db)
        return flask.render_template("index.html", **context)

    if request.method == "POST":
        team = request.form["team"]
        return save_vote(db, team)

    return flask.Response(
        response="Invalid http request. Method not allowed, must be 'GET' or 'POST'",
        status=400,
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)


# init_db lazily instantiates a database connection pool. Users of Cloud Run or
# App Engine may wish to skip this lazy instantiation and connect as soon
# as the function is loaded. This is primarily to help testing.
@app.before_request
def init_db() -> sqlalchemy.engine.base.Engine:
    """Initiates connection to database and its' structure."""
    logger.info("init db")
    global db
    if db is None:
        db = init_connection_pool()
        migrate_db(db)


@app.route("/", methods=["GET"])
def render_index() -> str:
    """Serves the index page of the app."""
    context = get_index_context(db)
    return render_template("index.html", **context)


@app.route("/votes", methods=["POST"])
def cast_vote() -> Response:
    """Processes a single vote from user."""
    team = request.form["team"]
    return save_vote(db, team)