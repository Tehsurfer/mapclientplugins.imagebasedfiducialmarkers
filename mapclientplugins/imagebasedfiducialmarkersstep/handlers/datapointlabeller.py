
from PySide import QtCore

from opencmiss.zinchandlers.keyactivatedhandler import KeyActivatedHandler


class DataPointLabeler(KeyActivatedHandler):

    def __init__(self, key_code):
        super(DataPointLabeler, self).__init__(key_code)
        self._model = None
        self._active_node = None

    def set_model(self, model):
        self._model = model

    def enter(self):
        pass

    def leave(self):
        pass

    def _get_ray(self, x, y):
        near_plane_point = self._scene_viewer.unproject(x, -y, 1.0)
        far_plane_point = self._scene_viewer.unproject(x, -y, -1.0)
        return [near_plane_point, far_plane_point]

    def mouse_press_event(self, event):
        super(DataPointLabeler, self).mouse_press_event(event)
        self._active_node = None
        if self._processing_mouse_events and event.buttons() & QtCore.Qt.RightButton:
            x = event.x()
            y = event.y()
            node = self._scene_viewer.get_nearest_node(x, y)
            if node and node.isValid():
                self._model.select_node(node.getIdentifier())
                self._model.context_menu_requested(node.getIdentifier(), x, y)

                self._active_node = node

    def mouse_move_event(self, event):
        super(DataPointLabeler, self).mouse_move_event(event)

    def mouse_release_event(self, event):
        super(DataPointLabeler, self).mouse_release_event(event)
        if self._processing_mouse_events and self._active_node and event.buttons() & QtCore.Qt.RightButton:
            self._model.deselect_node(self._active_node.getIdentifier())
            self._active_node = None
