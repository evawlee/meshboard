class SitesStore:
    _data = {}

    def put(self, site_id, payload):
        self._data[site_id] = payload

    def get(self, site_id):
        return self._data.get(site_id)

    def delete(self, site_id):
        self._data.pop(site_id, None)

    def list_for_tenant(self, tenant_id):
        return [s for s in self._data.values() if s.get("tenant_id") == tenant_id]

    def all(self):
        return list(self._data.values())
