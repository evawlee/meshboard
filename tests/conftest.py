import os
import tempfile
import pytest
from meshboard import create_app


@pytest.fixture
def workspace(tmp_path):
    reports_root = tmp_path / "reports"
    licensing_dir = tmp_path / "licensing"
    reports_root.mkdir()
    licensing_dir.mkdir()
    (reports_root / "summary.txt").write_text("daily summary\n")
    (reports_root / "audit.txt").write_text("audit baseline\n")
    (reports_root / ".dca-credentials").write_text("dca_user=dca\ndca_password=s3cret-dca-pw\n")
    return {"reports_root": str(reports_root), "licensing_dir": str(licensing_dir), "tmp": tmp_path}


@pytest.fixture
def app(workspace):
    a = create_app(reports_root=workspace["reports_root"], licensing_dir=workspace["licensing_dir"])
    a.config["TESTING"] = True
    return a


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def viewer():
    return {"Authorization": "Bearer viewer-tok-001"}


@pytest.fixture
def viewer_other_tenant():
    return {"Authorization": "Bearer viewer-tok-002"}


@pytest.fixture
def operator():
    return {"Authorization": "Bearer operator-tok-001"}


@pytest.fixture
def netadmin():
    return {"Authorization": "Bearer netadmin-tok-001"}


@pytest.fixture(autouse=True)
def _reset_singleton_state():
    from meshboard.store.sites import SitesStore
    from meshboard.store.configs import ConfigsStore
    from meshboard.store.licensing import LicensingStore
    from meshboard.store.reports import ReportsStore
    from meshboard.store.audit import AuditStore
    from meshboard.api import sites as sites_api
    from meshboard.api import admin as admin_mod
    from meshboard.licensing import upload as licensing_upload
    SitesStore._data = {}
    ConfigsStore._data = {}
    LicensingStore._data = {}
    ReportsStore._data = {}
    AuditStore._data = []
    AuditStore._seen_ids = set()
    LicensingStore._manifest_index = {}
    for inst in (sites_api._sites, sites_api._audit, admin_mod._audit, licensing_upload._store):
        if hasattr(inst, "_data"):
            inst._data = [] if isinstance(inst._data, list) else {}
        if hasattr(inst, "_seen_ids"):
            inst._seen_ids = set()
        if hasattr(inst, "_manifest_index"):
            inst._manifest_index = {}
    admin_mod._peers = {}
    yield
