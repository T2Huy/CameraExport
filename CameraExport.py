from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMaya as om
import maya.OpenMayaUI as omui

import maya.cmds as cmds
import maya.mel as mel

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class CameraExportDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(CameraExportDialog, self).__init__(parent)

        self.setWindowTitle("Camera Export")
        self.setFixedSize(300, 75)

        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowTitleHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.camera_name_ld = QtWidgets.QLineEdit()
        self.export_btn = QtWidgets.QPushButton("Export")

    def create_layout(self):
        camera_name_layout = QtWidgets.QHBoxLayout()
        camera_name_layout.addWidget(self.camera_name_ld)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.export_btn)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Camera Name:", camera_name_layout)
        form_layout.addRow("", btn_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)

    def create_connections(self):
        self.export_btn.clicked.connect(self.export_animation)

    def get_camera_name(self):
        # Input Camera's name
        camera_full_name = self.camera_name_ld.text()

        # Select camera
        cmds.select(camera_full_name, replace=True)

        # Slicing camera name
        camera_name = camera_full_name[:13]
        # folder_name = camera_full_name[:8]
        # print(camera_name)

        return  camera_name

    # Bake simulation function
    def bake_camera_animation(self, start_frame, end_frame):
        cmds.bakeResults(
            simulation=True,
            t=(start_frame, end_frame),
            sampleBy=1,
            oversamplingRate=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            removeBakedAttributeFromLayer=False,
            removeBakedAnimFromLayer=False,
            bakeOnOverrideLayer=False,
            minimizeRotation=True,
            controlPoints=False,
            shape=True
        )

    # Game Exporter
    def export_camera_game_exporter(self, camera_name_ins, export_path_ins):
        # Open Game Exporter
        mel.eval('gameFbxExporter;')
        mel.eval(
            'string $animationTab = "gameExporterTabLayout|gameExporterWindow|gameExporterFormLayout|gameExporterAnimationTab";')
        mel.eval('tabLayout -edit -selectTab $animationTab gameExporterTabLayout;')
        mel.eval('gameExp_UpdatePrefix;')
        mel.eval('gameExp_PopulatePresetList();')
        mel.eval('gameExp_CreateExportTypeUIComponents();')
        mel.eval('setAttr "gameExporterPreset2.exportSetIndex" 2;')
        mel.eval('gameExp_AddNewAnimationClip 1;')
        cmds.setAttr('gameExporterPreset2.animClips[0].animClipName', f'{camera_name_ins}', type='string')
        cmds.setAttr('gameExporterPreset2.exportPath', f'{export_path_ins}', type='string')
        mel.eval('setAttr "gameExporterPreset2.bakeAnimation" 0;')
        mel.eval('setAttr "gameExporterPreset2.embedMedia" 0;')

        # For changes to Animation clip Name only we need to close and reopen the window
        if cmds.window("gameExporterWindow", exists=True):
            print('exists')
            cmds.deleteUI("gameExporterWindow")
        else:
            pass

        mel.eval('gameFbxExporter;')

    # Export Animation
    def export_animation(self):
        #get frame range
        start_frame = cmds.playbackOptions(query=True, minTime=True)
        end_frame = cmds.playbackOptions(query=True, maxTime=True)

        self.bake_camera_animation(start_frame, end_frame)
        camera_name = self.get_camera_name()

        export_path = f"C:/Users/My_PC/Desktop/Askstar/FBX_Cam"
        self.export_camera_game_exporter(camera_name, export_path)

if __name__ == "__main__":

    try:
        camera_export_dialog.close()
        camera_export_dialog.deleteLater()
    except:
        pass

    camera_export_dialog = CameraExportDialog()
    camera_export_dialog.show()
