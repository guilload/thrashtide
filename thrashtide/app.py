import flask
import schema

from .query import validate_request
from .station import Station


THRASHTIDE = flask.Flask(__name__)


@THRASHTIDE.route("/", methods=["GET"])
def root():
    try:
        query = validate_request(flask.request.args.copy())
    except schema.SchemaError:
        flask.abort(400)

    station = Station.get(query["latitude"], query["longitude"])
    extrema = station.tide.extrema(*[query[key] for key in ("start", "stop", "timezone", "unit")])

    return flask.jsonify(
        extrema=extrema,
        station=station.description,
        ), 200
