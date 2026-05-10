import os
import time
from flask import Blueprint, request, jsonify, current_app, g
from meshboard.api.auth import require_auth
from meshboard.store import LicensingStore

bp = Blueprint("licensing", __name__)
_store = LicensingStore()


def _root():
    return current_app.config["LICENSING_DIR"]


@bp.route("/dataservice/smartLicensing/uploadAck", methods=["POST"])
@require_auth
def upload_ack():
    ident = g.identity
    body = request.get_json(silent=True) or {}
    filename = body.get("filename")
    payload = body.get("payload", "")
    if not filename:
        return jsonify({"error": "filename required"}), 400

    target = os.path.join(_root(), filename)
    parent = os.path.dirname(target)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(target, "w") as f:
        f.write(payload)

    manifest_id = f"manifest-{int(time.time() * 1000)}"
    _store.record_upload(manifest_id, {
        "manifest_id": manifest_id,
        "filename": filename,
        "by": ident["user"],
    })
    return jsonify({"ok": True, "manifest_id": manifest_id, "stored": target}), 201


@bp.route("/dataservice/smartLicensing/manifests", methods=["GET"])
@require_auth
def list_manifests():
    return jsonify(_store.all())
