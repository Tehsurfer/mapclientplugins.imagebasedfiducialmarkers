
from mapclientplugins.imagebasedfiducialmarkersstep.handlers.datapointhandlerbase import DataPointHandlerBase


class DataPointRemover(DataPointHandlerBase):

    def mouse_press_event(self, event):
        super(DataPointRemover, self).mouse_press_event(event)
        if self._processing_mouse_events:
            x = event.x()
            y = event.y()
            node = self._scene_viewer.get_nearest_node(x, y)
            if node and node.isValid():
                self._model.select_node(node.getIdentifier())
                self._active_node = node

    def mouse_release_event(self, event):
        super(DataPointRemover, self).mouse_release_event(event)
        if self._processing_mouse_events and self._active_node:
            x = event.x()
            y = event.y()
            node = self._scene_viewer.get_nearest_node(x, y)
            node_identifier = self._active_node.getIdentifier()
            if self._model.is_selected(node_identifier) and node_identifier == node.getIdentifier():
                self._model.remove_node(node_identifier)
                self._active_node = None
