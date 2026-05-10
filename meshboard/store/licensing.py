class LicensingStore:
    _data = {}
    _manifest_index = {}

    def record_upload(self, manifest_id, payload):
        self._data[manifest_id] = payload
        self._manifest_index[manifest_id] = payload.get("uploaded_at") if isinstance(payload, dict) else None

    def get(self, manifest_id):
        return self._data.get(manifest_id)

    def index_for(self, manifest_id):
        return self._manifest_index.get(manifest_id)

    def all(self):
        return list(self._data.values())
