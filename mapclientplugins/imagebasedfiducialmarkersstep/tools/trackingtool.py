
import numpy as np

from sparc.videotracking.processing import Processing
from sparc.videotracking.lkopticalflow import LKOpticalFlow

from opencmiss.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_LOCAL, \
    SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT
from opencmiss.zinc.field import FieldFindMeshLocation


class TrackingTool(object):

    def __init__(self, model):
        self._master_model = model
        self._tracking_points_model = model.get_tracking_points_model()
        self._image_plane_model = model.get_image_plane_model()
        self._processor = Processing()
        self._object_tracker = LKOpticalFlow(win=(20, 20), max_level=2)
        self._key_index = -1

    def track_key_points(self, start_index):
        key_points = self._tracking_points_model.get_key_points()
        if len(key_points):
            coordinate_field = self._tracking_points_model.get_coordinate_field()
            field_module = coordinate_field.getFieldmodule()
            field_module.beginChange()
            image_points = self._image_plane_model.convert_to_image_coordinates(key_points)
            numpy_points = np.asarray(image_points, dtype=np.float32)
            number_of_images = self._image_plane_model.get_frame_count()

            image_index = start_index
            file_name = self._image_plane_model.get_image_file_name_at(image_index)
            self._process_image(file_name)
            previous_gray_image = self._processor.get_gray_image()
            while image_index < number_of_images:
                time = self._image_plane_model.get_time_for_frame_index(image_index)
                file_name = self._image_plane_model.get_image_file_name_at(image_index)
                self._process_image(file_name)
                current_gray_image = self._processor.get_gray_image()

                new_numpy_points, st, err = self._object_tracker.lk(previous_gray_image, current_gray_image, numpy_points)
                new_image_points = [(float(point[0]), float(point[1])) for point in new_numpy_points]
                new_key_points = self._image_plane_model.convert_to_model_coordinates(new_image_points)
                self._tracking_points_model.set_key_points_at_time(new_key_points, time)
                numpy_points = new_numpy_points
                previous_gray_image = current_gray_image
                image_index += 1

            field_module.endChange()

    def count(self):
        return self._tracking_points_model.count()

    def _process_image(self, file_name):
        self._processor.read_image(file_name)
        self._processor.rgb_and_blur_and_hsv(threshold=9)


def _determine_the_mesh_location(scene_viewer, x, y, element, coordinate_field):
    mesh = element.getMesh()
    field_module = mesh.getFieldmodule()
    field_module.beginChange()
    element_group = field_module.createFieldElementGroup(mesh)
    mesh_group = element_group.getMeshGroup()
    mesh_group.addElement(element)
    field_mouse_location = field_module.createFieldConstant([x, -y])

    field_scene_viewer_projection = field_module.createFieldSceneviewerProjection(
        scene_viewer, SCENECOORDINATESYSTEM_LOCAL, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT)

    field_projection = field_module.createFieldProjection(coordinate_field, field_scene_viewer_projection)
    field_x_y_projection = field_module.createFieldComponent(field_projection, [1, 2])
    field_find_mesh_location = field_module.createFieldFindMeshLocation(field_mouse_location,
                                                                        field_x_y_projection, mesh_group)
    field_find_mesh_location.setSearchMode(FieldFindMeshLocation.SEARCH_MODE_NEAREST)

    field_cache = field_module.createFieldcache()

    found_element, xi_location = field_find_mesh_location.evaluateMeshLocation(field_cache, 2)

    del field_cache
    del field_find_mesh_location
    del field_x_y_projection
    del field_projection
    del field_scene_viewer_projection
    del field_mouse_location
    del mesh_group
    del element_group
    del coordinate_field

    field_module.endChange()

    return found_element, xi_location
