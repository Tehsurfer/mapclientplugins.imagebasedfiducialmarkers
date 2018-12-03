
from PySide import QtCore

from mapclientplugins.imagebasedfiducialmarkersstep.handlers.datapointhandlerbase import DataPointHandlerBase


class DataPointEditor(DataPointHandlerBase):

    def mouse_press_event(self, event):
        super(DataPointEditor, self).mouse_press_event(event)
        self._active_node = None
        if self._processing_mouse_events:
            x = event.x()
            y = event.y()
            node = self._scene_viewer.get_nearest_node(x, y)
            if node and node.isValid():
                self._model.select_node(node.getIdentifier())
                self._active_node = node

                if event.buttons() & QtCore.Qt.RightButton:
                    self._model.context_menu_requested(node.getIdentifier(), x, y)

    def mouse_move_event(self, event):
        super(DataPointEditor, self).mouse_move_event(event)
        if self._processing_mouse_events and self._active_node and event.buttons() & QtCore.Qt.LeftButton:
            x = event.x()
            y = event.y()
            ray = self._get_ray(x, y)
            self._model.set_node_location(self._active_node, ray)

    def mouse_release_event(self, event):
        super(DataPointEditor, self).mouse_release_event(event)
        if self._processing_mouse_events and self._active_node:
            self._model.deselect_node(self._active_node.getIdentifier())
            self._active_node = None
