import json


def _post(client, path, body, headers=None):
    return client.post(path, data=json.dumps(body), content_type="application/json", headers=headers or {})


def _put(client, path, body, headers=None):
    return client.put(path, data=json.dumps(body), content_type="application/json", headers=headers or {})




def test_unauth_request_to_sites_is_rejected(client):
    r = client.get("/api/sites")
    assert r.status_code == 401


def test_viewer_token_reaches_sites(client, viewer):
    r = client.get("/api/sites", headers=viewer)
    assert r.status_code == 200


def test_operator_token_reaches_sites(client, operator):
    r = client.get("/api/sites", headers=operator)
    assert r.status_code == 200


def test_netadmin_token_reaches_sites(client, netadmin):
    r = client.get("/api/sites", headers=netadmin)
    assert r.status_code == 200


def test_bearer_prefix_accepted_and_bare_token_too(client):
    r1 = client.get("/api/sites", headers={"Authorization": "Bearer viewer-tok-001"})
    r2 = client.get("/api/sites", headers={"Authorization": "viewer-tok-001"})
    assert r1.status_code == 200 and r2.status_code == 200




def test_operator_creates_site_in_assigned_tenant(client, operator):
    r = _post(client, "/api/sites", {"site_id": "s1", "tenant_id": "t-acme", "name": "branch-1"}, operator)
    assert r.status_code == 201
    assert r.get_json()["site_id"] == "s1"


def test_operator_cannot_create_site_in_unassigned_tenant(client, operator):
    r = _post(client, "/api/sites", {"site_id": "s2", "tenant_id": "t-globex", "name": "x"}, operator)
    assert r.status_code == 403


def test_viewer_cannot_create_site(client, viewer):
    r = _post(client, "/api/sites", {"site_id": "s3", "tenant_id": "t-acme", "name": "x"}, viewer)
    assert r.status_code == 403


def test_viewer_lists_only_assigned_tenant_sites(client, viewer, operator, viewer_other_tenant):
    _post(client, "/api/sites", {"site_id": "s-acme", "tenant_id": "t-acme", "name": "a"}, operator)
    listed = client.get("/api/sites", headers=viewer).get_json()
    assert any(s["site_id"] == "s-acme" for s in listed)
    other = client.get("/api/sites", headers=viewer_other_tenant).get_json()
    assert not any(s["site_id"] == "s-acme" for s in other)


def test_get_site_in_scope_returns_payload(client, operator):
    _post(client, "/api/sites", {"site_id": "s-get", "tenant_id": "t-acme", "name": "g"}, operator)
    r = client.get("/api/sites/s-get", headers=operator)
    assert r.status_code == 200 and r.get_json()["site_id"] == "s-get"


def test_delete_site_removes_it(client, operator):
    _post(client, "/api/sites", {"site_id": "s-del", "tenant_id": "t-acme", "name": "d"}, operator)
    assert client.delete("/api/sites/s-del", headers=operator).status_code == 200
    assert client.get("/api/sites/s-del", headers=operator).status_code == 404




def test_reports_root_lists_files(client, viewer):
    r = client.get("/reports/", headers=viewer)
    assert r.status_code == 200
    names = {e["name"] for e in r.get_json()}
    assert "summary.txt" in names and "audit.txt" in names


def test_reports_get_file_returns_content(client, viewer):
    r = client.get("/reports/summary.txt", headers=viewer)
    assert r.status_code == 200 and b"daily summary" in r.data


def test_reports_get_audit_returns_content(client, viewer):
    r = client.get("/reports/audit.txt", headers=viewer)
    assert r.status_code == 200 and b"audit baseline" in r.data


def test_reports_get_missing_returns_404(client, viewer):
    r = client.get("/reports/does-not-exist.txt", headers=viewer)
    assert r.status_code == 404




def test_operator_uploads_manifest_with_safe_filename(client, operator):
    r = _post(client, "/dataservice/smartLicensing/uploadAck",
              {"filename": "ack-2026-q1.json", "payload": "{}"}, operator)
    assert r.status_code == 201
    assert r.get_json()["ok"] is True


def test_uploaded_manifest_appears_in_listing(client, operator):
    _post(client, "/dataservice/smartLicensing/uploadAck",
          {"filename": "ack-list.json", "payload": "{}"}, operator)
    r = client.get("/dataservice/smartLicensing/manifests", headers=operator)
    assert r.status_code == 200
    assert any(m["filename"] == "ack-list.json" for m in r.get_json())


def test_upload_missing_filename_rejected(client, operator):
    r = _post(client, "/dataservice/smartLicensing/uploadAck", {"payload": "{}"}, operator)
    assert r.status_code == 400


def test_netadmin_can_upload(client, netadmin):
    r = _post(client, "/dataservice/smartLicensing/uploadAck",
              {"filename": "ack-admin.json", "payload": "{}"}, netadmin)
    assert r.status_code == 201




def test_netadmin_lists_users(client, netadmin):
    r = client.get("/admin/users", headers=netadmin)
    assert r.status_code == 200 and "alice" in r.get_json()


def test_viewer_cannot_list_users(client, viewer):
    r = client.get("/admin/users", headers=viewer)
    assert r.status_code == 403


def test_unauth_cannot_list_users(client):
    r = client.get("/admin/users")
    assert r.status_code == 401




def test_sites_store_put_get_roundtrip():
    from meshboard.store import SitesStore
    s = SitesStore()
    s.put("x1", {"site_id": "x1", "tenant_id": "t-acme"})
    assert s.get("x1")["tenant_id"] == "t-acme"


def test_configs_store_put_delete():
    from meshboard.store import ConfigsStore
    s = ConfigsStore()
    s.put("c1", {"config_id": "c1"})
    s.delete("c1")
    assert s.get("c1") is None


def test_licensing_store_records_uploads():
    from meshboard.store import LicensingStore
    s = LicensingStore()
    s.record_upload("m1", {"manifest_id": "m1"})
    assert s.get("m1")["manifest_id"] == "m1"


def test_reports_store_holds_data():
    from meshboard.store import ReportsStore
    s = ReportsStore()
    s.put("r1", {"report_id": "r1"})
    assert s.get("r1")["report_id"] == "r1"


def test_audit_store_appends_events():
    from meshboard.store import AuditStore
    s = AuditStore()
    s.append({"e": 1})
    s.append({"e": 2})
    assert len(s.all()) == 2
