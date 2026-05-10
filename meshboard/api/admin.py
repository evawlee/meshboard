from flask import Blueprint, request, jsonify, g
from meshboard.api.auth import require_role
from meshboard.store import AuditStore

bp = Blueprint("admin", __name__, url_prefix="/admin")
_audit = AuditStore()

_users = {
    "alice": {"role": "viewer", "tenants": ["t-acme"]},
    "bob": {"role": "viewer", "tenants": ["t-globex"]},
    "carol": {"role": "operator", "tenants": ["t-acme"]},
    "dave": {"role": "operator", "tenants": ["t-acme", "t-globex"]},
    "erin": {"role": "netadmin", "tenants": ["*"]},
}

_peers = {}


@bp.route("/users", methods=["GET"])
@require_role("netadmin")
def list_users():
    return jsonify(_users)


@bp.route("/users", methods=["POST"])
@require_role("netadmin")
def create_user():
    body = request.get_json(silent=True) or {}
    name = body.get("user")
    if not name:
        return jsonify({"error": "user required"}), 400
    _users[name] = {"role": body.get("role", "viewer"), "tenants": body.get("tenants", [])}
    _audit.append({"action": "create_user", "by": g.identity["user"], "user": name})
    return jsonify({"ok": True, "user": name}), 201


@bp.route("/peers", methods=["GET"])
def list_peers():
    return jsonify(_peers)


@bp.route("/peers", methods=["POST"])
def add_peer():
    body = request.get_json(silent=True) or {}
    peer_id = body.get("peer_id")
    if not peer_id:
        return jsonify({"error": "peer_id required"}), 400
    _peers[peer_id] = {
        "peer_id": peer_id,
        "endpoint": body.get("endpoint", ""),
        "trusted": bool(body.get("trusted", True)),
    }
    return jsonify({"ok": True, "peer_id": peer_id}), 201


@bp.route("/peers/<peer_id>", methods=["DELETE"])
def remove_peer(peer_id):
    _peers.pop(peer_id, None)
    return jsonify({"ok": True})
