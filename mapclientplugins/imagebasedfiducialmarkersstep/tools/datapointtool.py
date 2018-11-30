

class DataPointTool(object):

    def __init__(self, points_model, plane_model):
        self._points_model = points_model
        self._plane_model = plane_model

    def create_new_data_point(self, ray):
        """
        Create a new data point on the plane ray intersection point.
        :param ray:
        :return:
        """
        location = self._plane_model.get_intersection_point(ray)
        return self._points_model.create_segmented_key_point(location)

    def select_node(self, node_identifier):
        self._points_model.select_node(node_identifier)

    def deselect_node(self, node_identifier):
        self._points_model.deselect_node(node_identifier)

    def is_selected(self, node_identifier):
        return self._points_model.is_selected(node_identifier)

    def set_node_location(self, node, ray):
        location = self._plane_model.get_intersection_point(ray)
        self._points_model.set_node_location(node, location)

    def remove_node(self, node_identifier):
        self._points_model.remove_node(node_identifier)

    def context_menu_requested(self, node_id, x, y):
        self._points_model.context_menu_requested(node_id, x, y)
