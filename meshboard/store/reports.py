class ReportsStore:
    _data = {}

    def put(self, report_id, payload):
        self._data[report_id] = payload

    def get(self, report_id):
        return self._data.get(report_id)

    def all(self):
        return list(self._data.values())
