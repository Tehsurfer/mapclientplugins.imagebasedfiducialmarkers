
from PySide import QtGui, QtCore

from opencmiss.zinchandlers.scenemanipulation import SceneManipulation

from mapclientplugins.imagebasedfiducialmarkersstep.handlers.datapointadder import DataPointAdder
from mapclientplugins.imagebasedfiducialmarkersstep.handlers.datapointlabeller import DataPointLabeler
from mapclientplugins.imagebasedfiducialmarkersstep.handlers.datapointremover import DataPointRemover
from mapclientplugins.imagebasedfiducialmarkersstep.static.strings import SET_TRACKING_POINTS_STRING
from mapclientplugins.imagebasedfiducialmarkersstep.tools.datapointtool import DataPointTool
from mapclientplugins.imagebasedfiducialmarkersstep.tools.trackingtool import TrackingTool
from mapclientplugins.imagebasedfiducialmarkersstep.view.ui_imagebasedfiducialmarkerswidget\
    import Ui_ImageBasedFiducialMarkersWidget

PLAY_TEXT = 'Play'
STOP_TEXT = 'Stop'


class ImageBasedFiducialMarkersWidget(QtGui.QWidget):

    def __init__(self, model, parent=None):
        super(ImageBasedFiducialMarkersWidget, self).__init__(parent)
        self._ui = Ui_ImageBasedFiducialMarkersWidget()
        self._ui.setupUi(model.get_shareable_open_gl_widget(), self)
        self._ui.sceneviewer_widget.set_context(model.get_context())

        self._settings = {'view-parameters': {}}

        self._model = model
        self._model.reset()
        self._model.register_time_value_update_callback(self._update_time_value)
        self._model.register_frame_index_update_callback(self._update_frame_index)
        self._image_plane_scene = model.get_image_plane_scene()
        self._image_plane_scene.create_graphics()
        self._image_plane_scene.set_image_material()
        self._done_callback = None

        self._image_plane_model = model.get_image_plane_model()
        tracking_points_model = model.get_tracking_points_model()
        tracking_points_model.create_model()
        tracking_points_model.set_context_menu_callback(self._show_context_menu)
        tracking_points_scene = model.get_tracking_points_scene()
        tracking_points_scene.create_graphics()

        self._data_point_tool = DataPointTool(tracking_points_model, self._image_plane_model)
        self._tracking_tool = TrackingTool(model)

        self._setup_handlers()
        self._set_initial_ui_state()
        self._update_ui_state()

        self._make_connections()

    def _make_connections(self):
        self._ui.sceneviewer_widget.graphics_initialized.connect(self._graphics_initialized)
        self._ui.done_pushButton.clicked.connect(self._done_clicked)
        self._ui.timeValue_doubleSpinBox.valueChanged.connect(self._time_value_changed)
        self._ui.timePlayStop_pushButton.clicked.connect(self._time_play_stop_clicked)
        self._ui.frameIndex_spinBox.valueChanged.connect(self._frame_index_value_changed)
        self._ui.framesPerSecond_spinBox.valueChanged.connect(self._frames_per_second_value_changed)
        self._ui.timeLoop_checkBox.clicked.connect(self._time_loop_clicked)
        self._ui.track_pushButton.clicked.connect(self._track_button_clicked)

    def _done_clicked(self):
        self._model.done()
        self._done_callback()

    def _graphics_initialized(self):
        """
        Callback for when SceneviewerWidget is initialised
        Set custom scene from model
        """
        scene_viewer = self._ui.sceneviewer_widget.get_zinc_sceneviewer()
        if scene_viewer is not None:
            scene = self._model.get_scene()
            self._ui.sceneviewer_widget.set_tumble_rate(0)
            self._ui.sceneviewer_widget.set_scene(scene)
            if len(self._settings['view-parameters']) == 0:
                self._view_all()
            else:
                eye = self._settings['view-parameters']['eye']
                look_at = self._settings['view-parameters']['look_at']
                up = self._settings['view-parameters']['up']
                angle = self._settings['view-parameters']['angle']
                self._ui.sceneviewer_widget.set_view_parameters(eye, look_at, up, angle)

    def _set_initial_ui_state(self):
        self._ui.timeLoop_checkBox.setChecked(self._model.is_time_loop())
        self._frame_index_value_changed(1)
        self._enter_set_tracking_points()
        minimum_label_width = self._calculate_minimum_label_width()
        self._ui.statusText_label.setMinimumWidth(minimum_label_width)

    def _calculate_minimum_label_width(self):
        label = self._ui.statusText_label
        label.setWordWrap(True)
        label.setText(SET_TRACKING_POINTS_STRING)
        maximum_width = 0
        width = label.fontMetrics().boundingRect(label.text()).width()
        maximum_width = max(maximum_width, width)
        return maximum_width / 3.0

    def _update_ui_state(self):
        pass

    def _track_button_clicked(self):
        if self._tracking_tool.count():
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            frame_index = self._ui.frameIndex_spinBox.value()
            self._tracking_tool.track_key_points(frame_index)
            QtGui.QApplication.restoreOverrideCursor()

    def _setup_handlers(self):
        basic_handler = SceneManipulation()
        self._ui.sceneviewer_widget.register_handler(basic_handler)
        self._data_point_adder = DataPointAdder(QtCore.Qt.Key_A)
        self._data_point_adder.set_model(self._data_point_tool)
        self._data_point_remover = DataPointRemover(QtCore.Qt.Key_D)
        self._data_point_remover.set_model(self._data_point_tool)
        self._data_point_labeler = DataPointLabeler(QtCore.Qt.Key_E)
        self._data_point_labeler.set_model(self._data_point_tool)

    def _enter_set_tracking_points(self):
        self._ui.sceneviewer_widget.register_handler(self._data_point_adder)
        self._ui.sceneviewer_widget.register_handler(self._data_point_remover)
        self._ui.sceneviewer_widget.register_handler(self._data_point_labeler)
        self._ui.sceneviewer_widget.register_key_listener(
            QtCore.Qt.Key_Return, self._track_button_clicked)

    def _leave_set_tracking_points(self):
        self._ui.sceneviewer_widget.unregister_handler(self._data_point_adder)
        self._ui.sceneviewer_widget.unregister_handler(self._data_point_remover)
        self._ui.sceneviewer_widget.unregister_handler(self._data_point_labeler)
        self._ui.sceneviewer_widget.unregister_key_listener(QtCore.Qt.Key_Return)

        # Perform the tracking for all images.
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self._tracking_tool.track_key_points()
        QtGui.QApplication.restoreOverrideCursor()

    def _enter_finalise_tracking_points(self):
        self._ui.sceneviewer_widget.register_handler(self._data_point_adder)
        self._ui.sceneviewer_widget.register_handler(self._data_point_remover)

    def _leave_finalise_tracking_points(self):
        self._ui.sceneviewer_widget.unregister_handler(self._data_point_adder)
        self._ui.sceneviewer_widget.unregister_handler(self._data_point_remover)

    def _view_all(self):
        if self._ui.sceneviewer_widget.get_zinc_sceneviewer() is not None:
            self._ui.sceneviewer_widget.view_all()

    def _add_labels_as_actions(self, menu, labels):
        for label in labels:
            label_action = QtGui.QAction(menu)
            label_action.setText(label)
            label_action.triggered.connect(self._label_clicked)
            menu.addAction(label_action)

    def _show_context_menu(self, x, y, used_labels, unused_labels):
        menu = QtGui.QMenu(self._ui.sceneviewer_widget)

        self._add_labels_as_actions(menu, unused_labels)
        menu.addSeparator()
        self._add_labels_as_actions(menu, used_labels)

        menu.exec_(self.mapToGlobal(QtCore.QPoint(x, y) + self._ui.sceneviewer_widget.pos()))

    def _label_clicked(self):
        sender = self.sender()
        print(sender.text())

    def register_done_callback(self, done_callback):
        self._done_callback = done_callback

    def set_settings(self, settings):
        self._settings.update(settings)

    def get_settings(self):
        eye, look_at, up, angle = self._ui.sceneviewer_widget.get_view_parameters()
        self._settings['view-parameters'] = {'eye': eye, 'look_at': look_at, 'up': up, 'angle': angle}
        return self._settings

    def _update_time_value(self, value):
        self._ui.timeValue_doubleSpinBox.blockSignals(True)
        frame_count = self._image_plane_model.get_frame_count()
        max_time_value = frame_count / self._ui.framesPerSecond_spinBox.value()

        if value > max_time_value:
            self._ui.timeValue_doubleSpinBox.setValue(max_time_value)
            self._time_play_stop_clicked()
        else:
            self._ui.timeValue_doubleSpinBox.setValue(value)
        self._ui.timeValue_doubleSpinBox.blockSignals(False)

    def _update_frame_index(self, value):
        self._ui.frameIndex_spinBox.blockSignals(True)
        self._ui.frameIndex_spinBox.setValue(value)
        self._ui.frameIndex_spinBox.blockSignals(False)

    def _time_value_changed(self, value):
        self._model.set_time_value(value)

    def _time_duration_changed(self, value):
        self._model.set_time_duration(value)

    def _time_play_stop_clicked(self):
        current_text = self._ui.timePlayStop_pushButton.text()
        if current_text == PLAY_TEXT:
            self._ui.timePlayStop_pushButton.setText(STOP_TEXT)
            self._model.play()
        else:
            self._ui.timePlayStop_pushButton.setText(PLAY_TEXT)
            self._model.stop()

    def _time_loop_clicked(self):
        self._model.set_time_loop(self._ui.timeLoop_checkBox.isChecked())

    def _frame_index_value_changed(self, value):
        self._model.set_frame_index(value)

    def _frames_per_second_value_changed(self, value):
        self._model.set_frames_per_second(value)
        self._ui.timeValue_doubleSpinBox.setMaximum(self._image_plane_model.get_frame_count() / value)
