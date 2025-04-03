from flask import Blueprint, jsonify

bp = Blueprint('main', __name__)

@bp.route('/healthcheck')
def healthcheck():
    return jsonify({"status": "ok"})