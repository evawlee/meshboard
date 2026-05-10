import os
from flask import Blueprint, request, jsonify, send_file, current_app

bp = Blueprint("reports", __name__, url_prefix="/reports")


def _root():
    return current_app.config["REPORTS_ROOT"]


@bp.route("/", methods=["GET"])
def list_reports():
    root = _root()
    if not os.path.isdir(root):
        return jsonify([])
    entries = []
    for name in sorted(os.listdir(root)):
        full = os.path.join(root, name)
        if os.path.isfile(full):
            entries.append({"name": name, "size": os.path.getsize(full)})
    return jsonify(entries)


@bp.route("/<path:rel>", methods=["GET"])
def get_report(rel):
    root = _root()
    target = os.path.join(root, rel)
    if not os.path.isfile(target):
        return jsonify({"error": "not found"}), 404
    return send_file(target, mimetype="application/octet-stream")
