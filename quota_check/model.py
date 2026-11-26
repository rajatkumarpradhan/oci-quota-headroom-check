"""Load and validate a synthetic OCI service-limit usage export."""
import json
import os

REQUIRED_LIMIT = ("service", "name", "scope", "limit", "used")
SCOPES = ("region", "tenancy")


class LoadError(Exception):
    pass


def load(path):
    if not os.path.exists(path):
        raise LoadError("missing file: %s" % path)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except json.JSONDecodeError as exc:
        raise LoadError("bad JSON in %s: %s" % (path, exc))
    if not isinstance(doc, dict) or not isinstance(doc.get("limits"), list):
        raise LoadError("export must be an object with a 'limits' list")
    for i, item in enumerate(doc["limits"]):
        if not isinstance(item, dict):
            raise LoadError("limits[%d] is not an object" % i)
        for field in REQUIRED_LIMIT:
            if field not in item:
                raise LoadError("limits[%d] missing field %r" % (i, field))
        if item["scope"] not in SCOPES:
            raise LoadError("limits[%d] has unknown scope %r" % (i, item["scope"]))
        for num in ("limit", "used"):
            if not isinstance(item[num], (int, float)) or item[num] < 0:
                raise LoadError("limits[%d].%s must be a non-negative number" % (i, num))
    return doc["limits"]


def utilization(item):
    """used/limit as a fraction; None when the limit is zero."""
    if item["limit"] == 0:
        return None
    return item["used"] / item["limit"]
