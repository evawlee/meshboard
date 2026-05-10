class ConfigsStore:
    _data = {}

    def put(self, config_id, payload):
        self._data[config_id] = payload

    def get(self, config_id):
        return self._data.get(config_id)

    def delete(self, config_id):
        self._data.pop(config_id, None)

    def all(self):
        return list(self._data.values())
