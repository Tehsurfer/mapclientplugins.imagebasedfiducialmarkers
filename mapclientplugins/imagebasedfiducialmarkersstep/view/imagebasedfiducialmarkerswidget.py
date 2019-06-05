from __future__ import division

from PySide import QtGui, QtCore

from opencmiss.zinchandlers.scenemanipulation import SceneManipulation

from mapclientplugins.imagebasedfiducialmarkersstep.handlers.datapointadder import DataPointAdder
from mapclientplugins.imagebasedfiducialmarkersstep.handlers.datapointeditor import DataPointEditor
from mapclientplugins.imagebasedfiducialmarkersstep.handlers.datapointremover import DataPointRemover
from mapclientplugins.imagebasedfiducialmarkersstep.static.strings import SET_TRACKING_POINTS_STRING
from mapclientplugins.imagebasedfiducialmarkersstep.tools.datapointtool import DataPointTool
from mapclientplugins.imagebasedfiducialmarkersstep.tools.trackingtool import TrackingTool
from mapclientplugins.imagebasedfiducialmarkersstep.view.annotator_ui\
    import Ui_AnnotatorWidget

PLAY_TEXT = 'Play'
STOP_TEXT = 'Stop'

import numpy as np
import pyqtgraph as pg

class ImageBasedFiducialMarkersWidget(QtGui.QWidget):

    def __init__(self, model, parent=None):
        super(ImageBasedFiducialMarkersWidget, self).__init__(parent)
        self._ui = Ui_AnnotatorWidget()
        self._ui.setupUi(self, model.get_shareable_open_gl_widget())
        self._ui.sceneviewer_widget.set_context(model.get_context())

        self._settings = {'view-parameters': {}}

        self._model = model
        self._model.reset()
        self._model.register_time_value_update_callback(self._update_time_value)
        self._image_plane_scene = model.get_image_plane_scene()
        self._image_plane_scene.create_graphics()
        self._image_plane_scene.set_image_material()
        self._done_callback = None

        self._image_plane_model = model.get_image_plane_model()
        self._reset_button_clicked()

        tracking_points_model = self._model.get_tracking_points_model()
        self._data_point_tool = DataPointTool(tracking_points_model, self._image_plane_model)
        self._tracking_tool = TrackingTool(model)

        self._setup_handlers()
        self._set_initial_ui_state()
        self._update_ui_state()

        self._prepared_data_location = ''

        self._make_connections()
        self._update_progress_bar()

    def _make_connections(self):
        self._ui.sceneviewer_widget.graphics_initialized.connect(self._graphics_initialized)
        self._ui.done_pushButton.clicked.connect(self._done_clicked)
        self._ui.timeValue_doubleSpinBox.valueChanged.connect(self._time_value_changed)
        # self._ui.timePlayStop_pushButton.clicked.connect(self._time_play_stop_clicked)
        self._ui.timeLoop_checkBox.clicked.connect(self._time_loop_clicked)
        # self._ui.track_pushButton.clicked.connect(self._track_button_clicked)
        self._ui.reset_pushButton.clicked.connect(self._reset_button_clicked)
        self._ui.nextFrame_pushButton.clicked.connect(self._next_frame_clicked)
        self._ui.previousFrame_pushButton.clicked.connect(self._prev_frame_clicked)
        self._ui.cloudUpdate.clicked.connect(self._cloud_sync)
        self._ui.plotProgress.clicked.connect(self._plot_progress)
        self._ui.pushButton.clicked.connect(self._add_group_to_drop_down_list)
        self._ui.groupBox.currentIndexChanged.connect(self._change_group)

    def _next_frame_clicked(self):
        current_frame = self._model.get_frame_index()
        new_frame = current_frame + self._ui.FrameMultiplier.value()
        self._model.set_frame_index(new_frame, current_frame)
        self._update_progress_bar()
        self._update_frame_counter(new_frame)
        self._change_group()

    def _prev_frame_clicked(self):
        current_frame = self._model.get_frame_index()
        new_frame = current_frame - self._ui.FrameMultiplier.value()
        self._model.set_frame_index(new_frame, current_frame)
        self._update_progress_bar()
        self._update_frame_counter(new_frame)

    def _update_progress_bar(self):
        total_annotated = len(self._model.cloudDB.data_dict['AnnotatedFrames'] ) + \
                          len(self._model._tracking_points_model._annotations.keys())
        fraction = total_annotated * self._ui.FrameMultiplier.value() / self._model.number_of_frames
        self._ui.progressBar.setProperty("value", fraction * 100)


    def _populate_groups_dropdown(self):
        groups = self._model.cloudDB.retrieve_groups()
        for item in groups:
            self._ui.groupBox.addItem(item)
        self._set_group(groups[0])

    def _add_group_to_drop_down_list(self):
        self._ui.groupBox.addItem(self._ui.group_lineEdit.text())
        self._model.cloudDB.add_group(self._ui.group_lineEdit.text())

    def _change_group(self):
        self._set_group(self._ui.groupBox.currentText())

    def _set_group(self, group):
        self._model._tracking_points_model.set_group(group)

    def _update_frame_counter(self, value):
        self._ui.label_2.setText(str(value))

    def _plot_progress(self):
        plot_data = np.zeros(self._model.number_of_frames)
        for frame in self._model.cloudDB.data_dict['AnnotatedFrames']:
            plot_data[int(frame)] = 1
        pg.plot(plot_data)

    def _cloud_sync(self):
        additions = self._model._tracking_points_model.get_additions()
        self._model.cloudDB.upload_additions_to_database(additions, modify=self._ui.modifcationsAllowed.isChecked())

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
        self._populate_groups_dropdown()
        self._ui.timeLoop_checkBox.setChecked(self._model.is_time_loop())
        self._frame_index_value_changed(1)
        self._enter_set_tracking_points()
        # minimum_label_width = self._calculate_minimum_label_width()
        # self._ui.statusText_label.setMinimumWidth(minimum_label_width)
        maximum_time = self._image_plane_model.get_frame_count() / self._image_plane_model.get_frames_per_second()
        frame_separation = 1 / self._image_plane_model.get_frames_per_second()
        self._ui.timeValue_doubleSpinBox.setDecimals(8)
        self._ui.timeValue_doubleSpinBox.setMinimum(frame_separation / 2)
        self._ui.timeValue_doubleSpinBox.setMaximum(maximum_time)
        self._ui.timeValue_doubleSpinBox.setSingleStep(frame_separation)
        self._ui.timeValue_doubleSpinBox.setValue(frame_separation / 2)

    def _calculate_minimum_label_width(self):
        # label = self._ui.statusText_label
        # label.setWordWrap(True)
        # label.setText(SET_TRACKING_POINTS_STRING)
        # maximum_width = 0
        # width = label.fontMetrics().boundingRect(label.text()).width()
        # maximum_width = max(maximum_width, width)
        # return maximum_width / 3.0
        pass

    def _update_ui_state(self):
        pass

    def _reset_button_clicked(self):
        tracking_points_model = self._model.get_tracking_points_model()
        tracking_points_model.create_model()
        tracking_points_model.set_context_menu_callback(self._show_context_menu)
        tracking_points_scene = self._model.get_tracking_points_scene()
        tracking_points_scene.create_graphics()

    def set_prepared_data_location(self, location):
        self._prepared_data_location = location

    def _cheat_button_clicked(self):
        self._tracking_tool.load_saved_data(self._prepared_data_location)

    def _track_button_clicked(self):

        if self._tracking_tool.count():
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            frame_index = self._model.get_frame_index()
            self._tracking_tool.track_key_points(frame_index)
            QtGui.QApplication.restoreOverrideCursor()

    def _setup_handlers(self):
        basic_handler = SceneManipulation()
        self._ui.sceneviewer_widget.register_handler(basic_handler)
        self._data_point_adder = DataPointAdder(QtCore.Qt.Key_A)
        self._data_point_adder.set_model(self._data_point_tool)
        self._data_point_remover = DataPointRemover(QtCore.Qt.Key_D)
        self._data_point_remover.set_model(self._data_point_tool)
        self._data_point_labeler = DataPointEditor(QtCore.Qt.Key_E)
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
        # max_time_value = frame_count / self._ui.framesPerSecond_spinBox.value()
        max_time_value = frame_count / self._image_plane_model.get_frames_per_second()

        if value > max_time_value:
            self._ui.timeValue_doubleSpinBox.setValue(max_time_value)
            self._time_play_stop_clicked()
        else:
            self._ui.timeValue_doubleSpinBox.setValue(value)
        self._ui.timeValue_doubleSpinBox.blockSignals(False)
        self._time_value_changed(value)

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
        if value == 1:
            self._model.set_frame_index(value,value, first_load=True)
        else:
            self._model.set_frame_index(value,value)
