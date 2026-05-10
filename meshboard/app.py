import os
import tempfile
from flask import Flask

from meshboard.api import sites as sites_api
from meshboard.api import admin as admin_api
from meshboard.reports import data_api as reports_api
from meshboard.licensing import upload as licensing_upload


def create_app(reports_root=None, licensing_dir=None):
    app = Flask(__name__)
    if reports_root is None:
        reports_root = os.environ.get("MESHBOARD_REPORTS_ROOT") or tempfile.mkdtemp(prefix="meshboard-reports-")
    if licensing_dir is None:
        licensing_dir = os.environ.get("MESHBOARD_LICENSING_DIR") or tempfile.mkdtemp(prefix="meshboard-licensing-")
    app.config["REPORTS_ROOT"] = reports_root
    app.config["LICENSING_DIR"] = licensing_dir

    app.register_blueprint(sites_api.bp)
    app.register_blueprint(admin_api.bp)
    app.register_blueprint(reports_api.bp)
    app.register_blueprint(licensing_upload.bp)
    return app
