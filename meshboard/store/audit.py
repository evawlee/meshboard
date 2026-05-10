class AuditStore:
    _data = []
    _seen_ids = set()

    def append(self, event):
        eid = event.get("id") if isinstance(event, dict) else None
        if eid is not None and eid in self._seen_ids:
            return False
        self._data.append(event)
        if eid is not None:
            self._seen_ids.add(eid)
        return True

    def all(self):
        return list(self._data)
