from functools import wraps
from flask import request, jsonify, g

TOKENS = {
    "viewer-tok-001": {"user": "alice", "role": "viewer", "tenants": ["t-acme"]},
    "viewer-tok-002": {"user": "bob", "role": "viewer", "tenants": ["t-globex"]},
    "operator-tok-001": {"user": "carol", "role": "operator", "tenants": ["t-acme"]},
    "operator-tok-002": {"user": "dave", "role": "operator", "tenants": ["t-acme", "t-globex"]},
    "netadmin-tok-001": {"user": "erin", "role": "netadmin", "tenants": ["*"]},
}


def resolve_token(raw):
    if not raw:
        return None
    if raw.lower().startswith("bearer "):
        raw = raw[7:].strip()
    return TOKENS.get(raw)


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ident = resolve_token(request.headers.get("Authorization"))
        if ident is None:
            return jsonify({"error": "unauthenticated"}), 401
        g.identity = ident
        return fn(*args, **kwargs)
    return wrapper


def require_role(*allowed):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ident = resolve_token(request.headers.get("Authorization"))
            if ident is None:
                return jsonify({"error": "unauthenticated"}), 401
            if ident["role"] not in allowed:
                return jsonify({"error": "forbidden"}), 403
            g.identity = ident
            return fn(*args, **kwargs)
        return wrapper
    return deco


def tenant_in_scope(ident, tenant_id):
    if "*" in ident.get("tenants", []):
        return True
    return tenant_id in ident.get("tenants", [])
