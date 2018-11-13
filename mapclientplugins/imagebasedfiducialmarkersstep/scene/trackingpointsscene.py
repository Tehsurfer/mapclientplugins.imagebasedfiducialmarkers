from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph


class TrackingPointsScene(object):

    def __init__(self, master_model):
        self._master_model = master_model

    def create_graphics(self):
        tracking_points_model = self._master_model.get_tracking_points_model()
        coordinate_field = tracking_points_model.get_coordinate_field()
        region = tracking_points_model.get_region()
        scene = region.getScene()
        scene.beginChange()
        scene.removeAllGraphics()

        material_module = scene.getMaterialmodule()
        gold_material = material_module.findMaterialByName('cyan')
        green_material = material_module.findMaterialByName('green')

        points = scene.createGraphicsPoints()
        points.setName('key-points')
        points.setCoordinateField(coordinate_field)
        points.setMaterial(gold_material)
        points.setSelectedMaterial(green_material)
        points.setFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        attributes = points.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize(7.5)

        scene.setSelectionField(tracking_points_model.get_selection_field())
        scene.endChange()
