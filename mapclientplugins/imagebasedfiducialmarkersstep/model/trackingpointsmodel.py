
from opencmiss.zinc.status import OK as CMISS_OK
from opencmiss.utils.zinc import create_finite_element_field, create_node, AbstractNodeDataObject


class NodeCreator(AbstractNodeDataObject):

    def __init__(self, coordinates):
        super(NodeCreator, self).__init__(['coordinates'])
        self._coordinates = coordinates
        self._label = None

    def coordinates(self):
        return self._coordinates

    def set_label(self, label):
        self._label = label

    def label(self):
        return self._label


FIDUCIAL_MARKER_LABELS = [
    'lv_apex',
    'rv_apex',
    'lv1',
    'lv2',
    'sept1',
    'sept2',
    'rv1',
    'rv2',
    'rb1',
    'rb2',
    'lb1',
    'lb2',
]


class KeyPoint(object):

    def __init__(self, node, time):
        self._node = node
        self._creation_time = time
        self._label = '%s' % self._node.getIdentifier()

    def get_creation_time(self):
        return self._creation_time

    def get_node(self):
        return self._node

    def has_node(self, node):
        return node.getIdentifier() == self._node.getIdentifier()

    def get_label(self):
        return self._label


class ElectrodeKeyPoint(KeyPoint):
    pass


class SegmentedKeyPoint(KeyPoint):

    def __init__(self, node, time, label):
        super(SegmentedKeyPoint, self).__init__(node, time)
        self._label = label


class TrackingPointsModel(object):

    def __init__(self, master_model):
        self._master_model = master_model
        self._region = None
        self._coordinate_field = None
        self._label_field = None
        self._selection_group = None
        self._selection_group_field = None
        self._key_points = []
        self._used_labels = []
        self._unused_labels = FIDUCIAL_MARKER_LABELS
        self._context_menu_callback = None

    def get_region(self):
        return self._region

    def get_coordinate_field(self):
        return self._coordinate_field

    def count(self):
        return len(self._key_points)

    def select_node(self, identifier):
        node = self._get_node(identifier)
        self._selection_group.removeAllNodes()
        self._selection_group.addNode(node)

    def deselect_node(self, identifier):
        node = self._get_node(identifier)
        self._selection_group.removeNode(node)

    def is_selected(self, identifier):
        node = self._get_node(identifier)
        return self._selection_group.containsNode(node)

    def _create_node(self, location, time, label=None):
        field_module = self._coordinate_field.getFieldmodule()
        node_creator = NodeCreator(location)
        node_creator.set_time_sequence(self._master_model.get_time_sequence())
        node_creator.set_time_sequence_field_names(['coordinates'])
        if label is not None:
            node_creator.set_field_names(['coordinates', 'label'])
            node_creator.set_label(label)
            node_creator.set_time_sequence_field_names(['coordinates', 'label'])
        identifier = create_node(field_module, node_creator,
                                 node_set_name='datapoints', time=time)

        return self._get_node(identifier)

    def set_context_menu_callback(self, callback):
        self._context_menu_callback = callback

    def set_node_location(self, node, location):
        time = self._master_model.get_timekeeper_time()
        field_module = self._coordinate_field.getFieldmodule()
        field_module.beginChange()
        field_cache = field_module.createFieldcache()
        field_cache.setTime(time)
        field_cache.setNode(node)
        self._coordinate_field.assignReal(field_cache, location)
        field_module.endChange()

    def get_key_points_description(self):
        description = {}

        time_array = self._master_model.get_time_sequence()
        description['time_array'] = time_array

        field_module = self._coordinate_field.getFieldmodule()
        field_module.beginChange()
        field_cache = field_module.createFieldcache()
        for key_point in self._key_points:
            node = key_point.get_node()
            field_cache.setNode(node)
            node_locations = []
            for time in time_array:
                field_cache.setTime(time)
                _, coordinates = self._coordinate_field.evaluateReal(field_cache, 3)

                node_locations.append(coordinates)

            description[key_point.get_label()] = node_locations

        return description

    def remove_node(self, identifier):
        node = self._get_node(identifier)
        key_points = [point for point in self._key_points if point.has_node(node)]
        key_point_index = self._key_points.index(key_points[0])
        self._key_points.pop(key_point_index)
        node_set = node.getNodeset()
        node_set.destroyNode(node)

    def _get_node(self, identifier):
        node_set = self._selection_group.getMasterNodeset()
        return node_set.findNodeByIdentifier(identifier)

    def get_selection_field(self):
        return self._selection_group_field

    def get_label_field(self):
        return self._label_field

    def _get_next_label(self):
        if len(self._unused_labels) > 0:
            label = self._unused_labels.pop(0)
        else:
            label = self._used_labels.pop(0)

        self._used_labels.append(label)

        return label

    def create_segmented_key_point(self, location):
        time = self._master_model.get_timekeeper_time()
        label = self._get_next_label()
        node = self._create_node(location, time, label=label)
        self.select_node(node.getIdentifier())
        self._key_points.append(SegmentedKeyPoint(node, time, label))

        return node

    def create_electrode_key_points(self, key_points):
        time = self._master_model.get_timekeeper_time()
        field_module = self._coordinate_field.getFieldmodule()
        field_module.beginChange()
        for key_point in key_points:
            node = self._create_node([float(key_point[0]), float(key_point[1]), 0.0], time)
            self._key_points.append(ElectrodeKeyPoint(node, time))
        field_module.endChange()

    def set_key_points_at_time(self, key_points, time):
        assert len(key_points) == len(self._key_points)
        field_module = self._coordinate_field.getFieldmodule()
        field_module.beginChange()
        field_cache = field_module.createFieldcache()
        field_cache.setTime(time)
        for index, key_point in enumerate(self._key_points):
            node = key_point.get_node()
            coordinates = [key_points[index][0], key_points[index][1], 0.0]
            field_cache.setNode(node)
            self._coordinate_field.assignReal(field_cache, coordinates)

        field_module.endChange()

    def get_key_points(self):
        key_points = []
        field_module = self._coordinate_field.getFieldmodule()
        field_cache = field_module.createFieldcache()
        for key_point in self._key_points:
            node = key_point.get_node()
            field_cache.setNode(node)
            time = key_point.get_creation_time()
            field_cache.setTime(time)
            result, coordinates = self._coordinate_field.evaluateReal(field_cache, 3)
            if result == CMISS_OK:
                key_points.append(coordinates)

        return key_points

    def create_model(self):
        self.clear()
        default_region = self._master_model.get_default_region()

        self._region = default_region.createChild('tracking')
        self._coordinate_field = create_finite_element_field(self._region)

        field_module = self._region.getFieldmodule()
        field_module.beginChange()
        self._label_field = field_module.createFieldStoredString()
        self._label_field.setName('label')
        node_set = field_module.findNodesetByName('datapoints')

        # Setup the selection fields
        self._selection_group_field = field_module.createFieldGroup()
        selection_group = self._selection_group_field.createFieldNodeGroup(node_set)
        self._selection_group = selection_group.getNodesetGroup()
        field_module.endChange()

    def clear(self):
        default_region = self._master_model.get_default_region()
        if self._region is not None:
            default_region.removeChild(self._region)

    def context_menu_requested(self, node_id, x, y):
        self._context_menu_callback(x, y, self._used_labels, self._unused_labels)

