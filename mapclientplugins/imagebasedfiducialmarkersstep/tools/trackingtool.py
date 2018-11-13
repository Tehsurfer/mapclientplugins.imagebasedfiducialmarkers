import numpy as np
import cv2

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
        self._object_tracker = LKOpticalFlow(win=(40, 40), max_level=2)
        self._key_index = -1

    def track_key_points(self):
        key_points = self._tracking_points_model.get_key_points()
        if len(key_points):
            coordinate_field = self._tracking_points_model.get_coordinate_field()
            field_module = coordinate_field.getFieldmodule()
            field_module.beginChange()
            image_points = self._image_plane_model.convert_to_image_coordinates(key_points)
            numpy_points = np.asarray(image_points, dtype=np.float32)
            number_of_images = self._image_plane_model.get_number_of_images()
            frames_per_second = self._master_model.get_frames_per_second()
            _, previous_gray_image = self._processor.get_filtered_image()
            image_index = self._key_index
            while image_index < number_of_images:
                time = self._image_plane_model.get_time_for_frame_index(image_index, frames_per_second)
                file_name = self._image_plane_model.get_image_file_name_at(image_index)
                self._process_image(file_name)
                _, current_gray_image = self._processor.get_filtered_image()

                new_numpy_points, st, err = self._object_tracker.lk(previous_gray_image, current_gray_image, numpy_points)
                new_image_points = [(int(point[0]) + 0.5, int(point[1]) + 0.5) for point in new_numpy_points]
                new_key_points = self._image_plane_model.convert_to_model_coordinates(new_image_points)
                self._tracking_points_model.set_key_points_at_time(new_key_points, time)
                numpy_points = new_numpy_points
                previous_gray_image = current_gray_image
                image_index += 1

            field_module.endChange()

    def analyse_roi(self, image_index, zinc_sceneviewer, element, rectangle_description):
        image_roi = self._convert_to_image_roi(zinc_sceneviewer, element, rectangle_description)
        image_key_points = self._analyse_roi(image_index, image_roi)
        # image_points = [key_point.pt for key_point in image_key_points]
        image_points = image_key_points.tolist()
        key_points = self._image_plane_model.convert_to_model_coordinates(image_points)

        self._tracking_points_model.create_electrode_key_points(key_points)

    def _process_image(self, file_name):
        self._processor.read_image(file_name)
        self._processor.rgb_and_blur_and_hsv(threshold=9)
        self._processor.detect_electrode()

    def _analyse_roi(self, image_index, image_roi):
        self._key_index = image_index
        file_name = self._image_plane_model.get_image_file_name_at(image_index)
        self._process_image(file_name)
        self._processor.mask_and_image(image_roi)
        self._processor.final_mask()
        image_points, dst = self._processor.draw_electrodes()
        return image_points

    def _convert_to_image_roi(self, scene_viewer, element, rectangle_description):
        """
        Return a description of the rectangle in image pixels.  The resulting description is [top left corner x and y,
        width, height].  E.g. (1, 0, 48, 140).

        :param scene_viewer:
        :param element:
        :param rectangle_description: top left and bottom right corners of the rectangle in NDC top left coordinates.
        :return: A tuple in image pixels (x, y, width, height) describing a rectangle.
        """
        x1 = rectangle_description[0]
        y1 = rectangle_description[1]
        x2 = rectangle_description[2]
        y2 = rectangle_description[3]
        coordinate_field = self._image_plane_model.get_coordinate_field()
        top_left_mesh_location = _determine_the_mesh_location(
            scene_viewer, x1, y1, element, coordinate_field)
        bottom_right_mesh_location = _determine_the_mesh_location(
            scene_viewer, x2, y2, element, coordinate_field)

        return self._image_plane_model.calculate_image_pixels_rectangle(top_left_mesh_location,
                                                                        bottom_right_mesh_location)


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
