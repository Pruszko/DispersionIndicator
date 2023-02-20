from aih_constants import GUN_MARKER_TYPE

# Helper fields for new gun marker types
FOCUS_MARKER_TYPE_OFFSET = 2
GUN_MARKER_TYPE_CLIENT_FOCUS = GUN_MARKER_TYPE.CLIENT + FOCUS_MARKER_TYPE_OFFSET
GUN_MARKER_TYPE_SERVER_FOCUS = GUN_MARKER_TYPE.SERVER + FOCUS_MARKER_TYPE_OFFSET

LATENCY_MARKER_TYPE_OFFSET = 4
GUN_MARKER_TYPE_CLIENT_LATENCY = GUN_MARKER_TYPE.CLIENT + LATENCY_MARKER_TYPE_OFFSET
