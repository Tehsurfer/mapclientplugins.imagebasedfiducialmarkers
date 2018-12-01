from __future__ import division

from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT
from opencmiss.zinchandlers.keyactivatedhandler import KeyActivatedHandler


class RectangleTool(KeyActivatedHandler):

    def __init__(self, key_code):
        super(RectangleTool, self).__init__(key_code)
        self._start_position = None
        self._rectangle_box = None
        self._rectangle_box_centered_description = [-1.0, -1.0, -1.0, -1.0]
        self._rectangle_box_top_left_bottom_right_description = [-1.0, -1.0, -1.0, -1.0]

    def enter(self):
        pass

    def leave(self):
        pass

    def mouse_press_event(self, event):
        super(RectangleTool, self).mouse_press_event(event)
        if self._processing_mouse_events:
            self._start_position = (event.x(), event.y())

    def mouse_move_event(self, event):
        super(RectangleTool, self).mouse_move_event(event)
        if self._processing_mouse_events:
            self._update_rectangle_box_description(event.x(), event.y())
            self._update_and_or_create_rectangle_box()

    def mouse_release_event(self, event):
        super(RectangleTool, self).mouse_release_event(event)
        if self._processing_mouse_events:
            x = event.x()
            y = event.y()
            self._update_rectangle_box_description(x, y)

    def get_rectangle_box_description(self):
        return self._rectangle_box_top_left_bottom_right_description

    def _update_rectangle_box_description(self, x, y):
        x_diff = float(x - self._start_position[0])
        y_diff = float(y - self._start_position[1])
        if abs(x_diff) < 0.0001:
            x_diff = 1
        if abs(y_diff) < 0.0001:
            y_diff = 1
        x_off = float(self._start_position[0]) / x_diff + 0.5
        y_off = float(self._start_position[1]) / y_diff + 0.5
        self._rectangle_box_centered_description = [x_diff, y_diff, x_off, y_off]
        self._rectangle_box_top_left_bottom_right_description = [self._start_position[0], self._start_position[1],
                                                                 x, y]

    def _update_and_or_create_rectangle_box(self):
        # Using a non-ideal workaround for creating a rubber band for selection.
        # This will create strange visual artifacts when using two scene viewers looking at
        # the same scene.  Waiting on a proper solution in the API.
        # Note if the standard glyphs haven't been defined then the
        # selection box will not be visible
        x_diff = self._rectangle_box_centered_description[0]
        y_diff = self._rectangle_box_centered_description[1]
        x_off = self._rectangle_box_centered_description[2]
        y_off = self._rectangle_box_centered_description[3]

        scene = self._zinc_sceneviewer.getScene()
        scene.beginChange()
        if self._rectangle_box is None:
            material_module = scene.getMaterialmodule()
            blue_material = material_module.findMaterialByName('blue')
            self._rectangle_box = scene.createGraphicsPoints()
            self._rectangle_box.setScenecoordinatesystem(SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT)
            self._rectangle_box.setMaterial(blue_material)
        attributes = self._rectangle_box.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_CUBE_WIREFRAME)
        attributes.setBaseSize([x_diff, y_diff, 0.999])
        attributes.setGlyphOffset([x_off, -y_off, 0])
        scene.endChange()

    def remove_rectangle_box(self):
        if self._rectangle_box is not None:
            scene = self._rectangle_box.getScene()
            scene.removeGraphics(self._rectangle_box)
            self._rectangle_box = None
