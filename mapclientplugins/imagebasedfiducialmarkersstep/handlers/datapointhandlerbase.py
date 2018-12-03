from opencmiss.zinchandlers.keyactivatedhandler import KeyActivatedHandler


class DataPointHandlerBase(KeyActivatedHandler):

    def __init__(self, key_code):
        super(DataPointHandlerBase, self).__init__(key_code)
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
