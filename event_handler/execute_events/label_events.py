"""
Events for the node-labelling pipeline: selected in VR (paint/lasso) -> analysed
and labelled through the backend. See enrichment_module.suggest_labels_for_nodes
for the analysis step.

Currently implements only the read-only "suggest a label" step. Placing the
resulting label (persisting it + anchoring it at the selection's centroid in the
3D view) is a separate, not-yet-built step.
"""
from flask_socketio import emit

import enrichment_module
import GlobalData as GD


def get_active_node_selection():
    """
    The node set label suggestions are computed over: the union of whatever is
    currently painted/lasso-selected in VR (GD.paintedNodes) and whatever is
    currently in the GUI clipboard (GD.pdata["cbnode"]). Mirrors the "vr"/"jupyter"
    union pattern used by SessionManager.selections in dataXplorer.py - VR and GUI
    are just two entry points into the same working set here.
    """
    clipboard_ids = {int(n["id"]) for n in GD.pdata.get("cbnode", [])}
    return list(set(GD.paintedNodes) | clipboard_ids)


def suggest_label_event(message, room):
    """
    Suggests label candidates for the current node selection (VR paint/lasso and/or
    GUI clipboard, combined - see get_active_node_selection), based on which
    annotation attributes are statistically overrepresented in that set compared to
    the whole project. Read-only - does not persist anything or modify the selection.
    """
    candidates, reason = enrichment_module.suggest_labels_for_nodes(get_active_node_selection())

    response = {
        "usr": message["usr"],
        "id": message["id"],
        "fn": "labelSuggestions",
        "val": candidates,
        "reason": reason,
    }
    emit("ex", response, room=room)
