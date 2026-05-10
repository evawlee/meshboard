from flask import Blueprint, request, jsonify, g
from meshboard.api.auth import require_auth, require_role, tenant_in_scope
from meshboard.store import SitesStore, AuditStore

bp = Blueprint("sites", __name__, url_prefix="/api/sites")
_sites = SitesStore()
_audit = AuditStore()


@bp.route("", methods=["GET"])
@require_auth
def list_sites():
    ident = g.identity
    if "*" in ident["tenants"]:
        return jsonify(_sites.all())
    out = []
    for t in ident["tenants"]:
        out.extend(_sites.list_for_tenant(t))
    return jsonify(out)


@bp.route("", methods=["POST"])
@require_role("operator", "netadmin")
def create_site():
    ident = g.identity
    body = request.get_json(silent=True) or {}
    site_id = body.get("site_id")
    tenant_id = body.get("tenant_id")
    if not site_id or not tenant_id:
        return jsonify({"error": "site_id and tenant_id required"}), 400
    if not tenant_in_scope(ident, tenant_id):
        return jsonify({"error": "tenant not in scope"}), 403
    _sites.put(site_id, {"site_id": site_id, "tenant_id": tenant_id, "name": body.get("name", "")})
    _audit.append({"action": "create_site", "user": ident["user"], "site_id": site_id})
    return jsonify({"ok": True, "site_id": site_id}), 201


@bp.route("/<site_id>", methods=["GET"])
@require_auth
def get_site(site_id):
    ident = g.identity
    site = _sites.get(site_id)
    if site is None:
        return jsonify({"error": "not found"}), 404
    if not tenant_in_scope(ident, site["tenant_id"]):
        return jsonify({"error": "tenant not in scope"}), 403
    return jsonify(site)


@bp.route("/<site_id>", methods=["DELETE"])
@require_role("operator", "netadmin")
def delete_site(site_id):
    ident = g.identity
    site = _sites.get(site_id)
    if site is None:
        return jsonify({"error": "not found"}), 404
    if not tenant_in_scope(ident, site["tenant_id"]):
        return jsonify({"error": "tenant not in scope"}), 403
    _sites.delete(site_id)
    _audit.append({"action": "delete_site", "user": ident["user"], "site_id": site_id})
    return jsonify({"ok": True})
