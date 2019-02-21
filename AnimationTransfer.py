import pymel.core as pm
import pymel.core.nodetypes as nt 
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile
from shiboken2 import wrapInstance       
from pymel.all import *

def GetParentsRecursive(list, joint):
    if joint.getParent() is not None:
        list.append(joint.getParent())
        GetParentsRecursive(list, joint.getParent())

def MultiplyParentBindposes(joint):
    time = pm.currentTime(query=True)
    SetTime(0)
    parents = []
    GetParentsRecursive(parents, joint)
    matrix = pm.datatypes.Matrix()
    
    for parent in parents:
        matrix = matrix * GetJointBindpose(parent) * GetJointOrientation(parent)
    SetTime(time)
    return matrix

def SetTime(time):
    pm.currentTime(time, edit=True)

def GetJointRotation(joint):
    """Gets rotation of joint at current key as Quaternion"""
    return joint.getRotation().asMatrix().rotate

def GetJointOrientation(joint):
    return joint.getOrientation().asMatrix()

def GetJointRotationAsMatrix(joint):
    return joint.getRotation().asMatrix()

def GetJointBindpose(joint):
    currentTime = pm.currentTime(query=True)
    SetTime(0)
    matrix = joint.getRotation().asMatrix()
    SetTime(currentTime)
    return matrix
    
def GetJointInverseBindpose(joint):
    return GetJointBindpose(joint).transpose()

def SetJointRotation(joint, quaternion):
    joint.setRotation(quaternion)
    
def IsolateKeyframeRotation(joint):
    return GetJointInverseBindpose(joint) * GetJointRotationAsMatrix(joint)

def KeyObject(object):
    pm.setKeyframe(object)

def KeyFirstFrame(joint):
    SetTime(0)
    KeyObject(str(joint))
    
def ItemExistsInList(item, list):
    for i in range(list.count()):
        if item == list.item(i).text():
            return True
    return False
    
#--------------------------------------------------------------

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class AnimationTransferUI(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(AnimationTransferUI, self).__init__(*args, **kwargs)
        self.setWindowTitle("Animation Transfer v1.0")
        self.initUI()
        self.setParent(maya_main_window())
        self.setWindowFlags(QtCore.Qt.Window)

    def transfer(self):
        startTime = 0
        endTime = 0
        if self.ui.timeSliderRadio.isChecked():
            startTime = cmds.playbackOptions(min=True, query=True)
            endTime = cmds.playbackOptions(max=True, query=True)
        else:
            startTime = pm.playbackOptions(ast=True, query=True)
            endTime = pm.playbackOptions(aet=True, query=True)

        start = int(startTime) if int(startTime) > 0 else 1
        print(start)
        end = int(endTime)

        self.TransferAnimationPerJoint(start, end)

        """Filter if box is checked"""
        if self.ui.applyFilter.isChecked():
            command = "filterCurve "
            for i in range(self.ui.targetList.count()):
                joint = self.ui.targetList.item(i).text()
                command = command + " ".join(cmds.listConnections(joint, t="animCurve"))
                command = command + " "
            command = command + ";"
            print(command)
            mel.eval(command)
            
        """Transfer root translation if box is checked"""
        if self.ui.transferRoot.isChecked():
            currentFrame = int(startTime)
            if (currentFrame < 1):
                currentFrame = 1
            
            sRoot = nt.Joint(self.ui.sourceList.item(0).text()).root()
            tRoot = nt.Joint(self.ui.targetList.item(0).text()).root()
            
            while currentFrame <= end:
                SetTime(currentFrame)
                tRoot.setTranslation(sRoot.getTranslation())
                currentFrame += 1
        self.ui.progressBar.setValue(self.ui.progressBar.minimum())
        self.ui.jointProgressBar.setValue(self.ui.jointProgressBar.minimum())
        self.ui.transferLayout.setVisible(True)
        self.ui.progressLayout.setVisible(False)
        self.ui.statusbar.showMessage("Transfer finished.")

    def TransferSourceToTargetAllFrames(self, source, target, start, end, step):
        """Transfer all frames from source to target in range start to end"""
        self.ui.statusbar.showMessage(("Transfering " + str(source)))
        
        sCurrentOrientation = source.getOrientation().asMatrix()
        sCurrentOrientationInverse = sCurrentOrientation.transpose()
        sParents = MultiplyParentBindposes(source)
        sParentsInverse = sParents.transpose()
        sCurrentAndParents = sParents * sCurrentOrientation
        sCurrentAndParentsInverse = sCurrentOrientationInverse * sParentsInverse
        
        tCurrentOrientation = target.getOrientation().asMatrix()
        tCurrentOrientationInverse = tCurrentOrientation.transpose()
        tParents = MultiplyParentBindposes(target)
        tParentsInverse = tParents.transpose()
        tCurrentAndParents = tCurrentOrientation * tParents
        tCurrentAndParentsInverse = tParentsInverse * tCurrentOrientationInverse
        
        tBindpose = GetJointBindpose(target)
        
        """Key target at frame 0, in case it is not keyed already"""
        KeyFirstFrame(target)
        
        currentFrame = start
        while currentFrame <= end:
            self.ui.jointProgressBar.setValue(currentFrame)
            SetTime(currentFrame)
            KeyObject(str(target))
            
            isolatedRotation = IsolateKeyframeRotation(source)
            worldspaceRotation = sCurrentAndParentsInverse * isolatedRotation * sCurrentAndParents
            translatedRotation = tCurrentAndParents * worldspaceRotation * tCurrentAndParentsInverse
            finalRotation = tBindpose * translatedRotation
            SetJointRotation(target, finalRotation.rotate)
            
            currentFrame += step

    def TransferAnimationPerJoint(self, start, end):
        jointCount = self.ui.sourceList.count()
        step = self.ui.frameStep.value()
        self.ui.transferLayout.setVisible(False)
        self.ui.progressLayout.setVisible(True)
        self.ui.progressBar.setRange(0, jointCount)
        self.ui.jointProgressBar.setRange(start, end)
        
        for i in range(jointCount):
            self.ui.progressBar.setValue(i)
            sourceJoint = nt.Joint(self.ui.sourceList.item(i).text())
            targetJoint = nt.Joint(self.ui.targetList.item(i).text())
            self.TransferSourceToTargetAllFrames(sourceJoint, targetJoint, start, end, step)

# ------------ UI stuff ------------
    def initUI(self):
        """Init UI"""
        loader = QUiLoader()   
        splitPath = os.path.realpath(__file__).split("\\")
        uiPath = "/".join(splitPath[:-1]) + "/animation_transfer.ui"
        file = QFile(uiPath)      
        file.open(QFile.ReadOnly)        
        self.ui = loader.load(file)     
        file.close()
        
        #Init ui 
        self.ui.setParent(maya_main_window())
        self.ui.setWindowFlags(QtCore.Qt.Window)
        self.ui.show()
        self.setCentralWidget(self.ui)
        self.ui.progressLayout.setVisible(False)
        
        #Init signals
        self.ui.loadSourceButton.clicked.connect(self.onLoadSource)
        self.ui.loadTargetButton.clicked.connect(self.onLoadTarget)
        self.ui.transferButton.clicked.connect(self.transfer)
        self.ui.loadSourceSelectionButton.clicked.connect(self.onLoadSourceSelection)
        self.ui.loadTargetSelectionButton.clicked.connect(self.onLoadTargetSelection)
        self.ui.clearSourceButton.clicked.connect(self.onClearSource)
        self.ui.clearTargetButton.clicked.connect(self.onClearTarget)
        
    def onLoadSource(self):
        """Load source skeleton from selection (assumes root is last selection)"""
        selected = pm.ls(sl=True, type='joint', tail=1)
        if selected:
            self.ui.sourceList.clear()
            children = pm.listRelatives(selected[0], ad=True)
            children.reverse()
            children.insert(0, selected[0])
            for i in children:
                self.ui.sourceList.addItem(str(i))
                
    def onLoadTarget(self):
        """Load target skeleton from selection (assumes root is last selection)"""
        selected = pm.ls(sl=True, type='joint', tail=1)
        if selected:
            self.ui.targetList.clear()
            children = pm.listRelatives(selected[0], ad=True)
            children.reverse()
            children.insert(0, selected[0])
            for i in children:
                self.ui.targetList.addItem(str(i))
                
    def onLoadSourceSelection(self):
        selection = pm.ls(sl=True, type="joint")
        
        for joint in selection:
            if not ItemExistsInList(str(joint), self.ui.targetList) and not ItemExistsInList(str(joint), self.ui.sourceList):
                self.ui.sourceList.addItem(str(joint))
    
    def onLoadTargetSelection(self):
        selection = pm.ls(sl=True, type="joint")
        
        for joint in selection:
            if not ItemExistsInList(str(joint), self.ui.targetList) and not ItemExistsInList(str(joint), self.ui.sourceList):
                self.ui.targetList.addItem(str(joint))
    
    def onClearSource(self):
        self.ui.sourceList.clear()      
        
    def onClearTarget(self):
        self.ui.targetList.clear()          

def run():
    app = QApplication.instance() 
    win = AnimationTransferUI()
    win.show()
    app.exec_()