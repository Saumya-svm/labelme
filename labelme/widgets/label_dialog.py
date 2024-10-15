import re

from qtpy import QT_VERSION
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import labelme.utils
from labelme.logger import logger

QT5 = QT_VERSION[0] == "5"


# TODO(unknown):
# - Calculate optimal position so as not to go out of screen area.


class LabelQLineEdit(QtWidgets.QLineEdit):
    def setListWidget(self, list_widget):
        self.list_widget = list_widget

    def keyPressEvent(self, e):
        if e.key() in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down]:
            self.list_widget.keyPressEvent(e)
        else:
            super(LabelQLineEdit, self).keyPressEvent(e)


class LabelDialog(QtWidgets.QDialog):
    def __init__(
        self,
        text="Enter object label",
        parent=None,
        labels=None,
        sort_labels=True,
        show_text_field=True,
        completion="startswith",
        fit_to_content=None,
        flags=None,
    ):
        if fit_to_content is None:
            fit_to_content = {"row": False, "column": True}
        self._fit_to_content = fit_to_content

        super(LabelDialog, self).__init__(parent)
        self.edit = LabelQLineEdit()
        self.edit.setPlaceholderText(text)
        self.edit.setValidator(labelme.utils.labelValidator())
        self.edit.editingFinished.connect(self.postProcess)
        if flags:
            self.edit.textChanged.connect(self.updateFlags)
        self.edit_group_id = QtWidgets.QLineEdit()
        self.edit_group_id.setPlaceholderText("Group ID")
        self.edit_group_id.setValidator(
            QtGui.QRegExpValidator(QtCore.QRegExp(r"\d*"), None)
        )
        layout = QtWidgets.QVBoxLayout()
        if show_text_field:
            layout_edit = QtWidgets.QHBoxLayout()
            layout_edit.addWidget(self.edit, 6)
            layout_edit.addWidget(self.edit_group_id, 2)
            layout.addLayout(layout_edit)
        # buttons
        self.buttonBox = bb = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            self,
        )
        bb.button(bb.Ok).setIcon(labelme.utils.newIcon("done"))
        bb.button(bb.Cancel).setIcon(labelme.utils.newIcon("undo"))
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)
        # label_list
        self.labelList = QtWidgets.QListWidget()
        if self._fit_to_content["row"]:
            self.labelList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        if self._fit_to_content["column"]:
            self.labelList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._sort_labels = sort_labels
        if labels:
            self.labelList.addItems(labels)
        if self._sort_labels:
            self.labelList.sortItems()
        else:
            self.labelList.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.labelList.currentItemChanged.connect(self.labelSelected)
        self.labelList.itemDoubleClicked.connect(self.labelDoubleClicked)
        self.labelList.setFixedHeight(150)
        self.edit.setListWidget(self.labelList)
        layout.addWidget(self.labelList)
        # label_flags
        if flags is None:
            flags = {}
        self._flags = flags
        self.flagsLayout = QtWidgets.QVBoxLayout()
        self.resetFlags()
        layout.addItem(self.flagsLayout)
        self.edit.textChanged.connect(self.updateFlags)
        # text edit
        # self.editDescription = QtWidgets.QTextEdit()
        # self.editDescription.setPlaceholderText("Language Code")
        # self.editDescription.setFixedHeight(50)
        # layout.addWidget(self.editDescription)

        self.editDescription = QtWidgets.QComboBox()
        self.editDescription.addItem("Select Script")
        self.editDescription.addItem("english")
        self.editDescription.addItem("telugu")
        self.editDescription.addItem("hindi")
        self.editDescription.addItem("bengali")
        self.editDescription.addItem("gujarati")
        self.editDescription.addItem("tamil")
        self.editDescription.addItem("kannada")
        self.editDescription.addItem("malayalam")
        self.editDescription.addItem("odia")
        self.editDescription.addItem("punjabi")
        self.editDescription.addItem("marathi")
        self.editDescription.addItem("to be blurred - unlcear text boundaries")
        self.editDescription.addItem("to be blurred - personally identifiable information")
        self.editDescription.addItem("unidentifiable - text unclear or blurred")
        self.editDescription.addItem("unidentifiable - text clear but cant identify script or transcription")
        layout.addWidget(self.editDescription)
	
        # self.character = QtWidgets.QTextEdit()
        # self.character.setPlaceholderText("Characteristic")
        # self.character.setFixedHeight(50)
        # layout.addWidget(self.character)
        self.character1 = QtWidgets.QComboBox()
        self.character1.addItem("Select Line Orientation")
        self.character1.addItem("Horizontal")
        self.character1.addItem("Vertical")
        self.character1.addItem("Multi Oriented")
        self.character1.addItem("Not a line")
        layout.addWidget(self.character1)
        
        self.character2 = QtWidgets.QComboBox()
        self.character2.addItem("Select Curve Orientation")
        self.character2.addItem("Horizontal Curve")
        self.character2.addItem("Vertical Curve")
        self.character2.addItem("Circular")
        self.character2.addItem("Wavy")
        layout.addWidget(self.character2)

        self.character3 = QtWidgets.QComboBox()
        self.character3.addItem("Select Occlusion")
        self.character3.addItem("Occluded")
        self.character3.addItem("Not occluded")
        layout.addWidget(self.character3)

        self.character4 = QtWidgets.QComboBox()
        self.character4.addItem("Select Dimension")
        self.character4.addItem("2d Text")
        self.character4.addItem("3d Text")
        layout.addWidget(self.character4)

        self.character5 = QtWidgets.QComboBox()
        self.character5.addItem("Select Point of View")
        self.character5.addItem("Normal")
        self.character5.addItem("Perspective")
        self.character5.setCurrentIndex(1)  # Set "Normal" as the default value
        layout.addWidget(self.character5)


        self.character6 = QtWidgets.QComboBox()
        self.character6.addItem("Select Lighting Condition")
        self.character6.addItem("Naturally Lit")
        self.character6.addItem("Poor Illumination")
        self.character6.addItem("External Light Exposure")
        layout.addWidget(self.character6)

        self.character7 = QtWidgets.QComboBox()
        self.character7.addItem("Select Background Type")
        self.character7.addItem("Complex")
        self.character7.addItem("Simple")
        layout.addWidget(self.character7)

        # well lit, poor illumination, light exposure
        # horizontal, vertical, multioriented
        # horizontal curved, vertical curved, circular curved, wavy curved
        # non occluded, occluded
        # 2d Text, 3d Text
        # normal, perspective
        # which are occlusion attribute, complex background attribute, distortion attribute, raised attribute, wordart attribute, and handwritten attribute.

        self.setLayout(layout)
        # completion
        completer = QtWidgets.QCompleter()
        if not QT5 and completion != "startswith":
            logger.warn(
                "completion other than 'startswith' is only "
                "supported with Qt5. Using 'startswith'"
            )
            completion = "startswith"
        if completion == "startswith":
            completer.setCompletionMode(QtWidgets.QCompleter.InlineCompletion)
            # Default settings.
            # completer.setFilterMode(QtCore.Qt.MatchStartsWith)
        elif completion == "contains":
            completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
            completer.setFilterMode(QtCore.Qt.MatchContains)
        else:
            raise ValueError("Unsupported completion: {}".format(completion))
        completer.setModel(self.labelList.model())
        self.edit.setCompleter(completer)

    def addLabelHistory(self, label):
        if self.labelList.findItems(label, QtCore.Qt.MatchExactly):
            return
        self.labelList.addItem(label)
        if self._sort_labels:
            self.labelList.sortItems()

    def labelSelected(self, item):
        self.edit.setText(item.text())

    def validate(self):
        text = self.edit.text()
        if hasattr(text, "strip"):
            text = text.strip()
        else:
            text = text.trimmed()
        if text:
            self.accept()

    def labelDoubleClicked(self, item):
        self.validate()

    def postProcess(self):
        text = self.edit.text()
        if hasattr(text, "strip"):
            text = text.strip()
        else:
            text = text.trimmed()
        self.edit.setText(text)

    def updateFlags(self, label_new):
        # keep state of shared flags
        flags_old = self.getFlags()

        flags_new = {}
        for pattern, keys in self._flags.items():
            if re.match(pattern, label_new):
                for key in keys:
                    flags_new[key] = flags_old.get(key, False)
        self.setFlags(flags_new)

    def deleteFlags(self):
        for i in reversed(range(self.flagsLayout.count())):
            item = self.flagsLayout.itemAt(i).widget()
            self.flagsLayout.removeWidget(item)
            item.setParent(None)

    def resetFlags(self, label=""):
        flags = {}
        for pattern, keys in self._flags.items():
            if re.match(pattern, label):
                for key in keys:
                    flags[key] = False
        self.setFlags(flags)

    def setFlags(self, flags):
        self.deleteFlags()
        for key in flags:
            item = QtWidgets.QCheckBox(key, self)
            item.setChecked(flags[key])
            self.flagsLayout.addWidget(item)
            item.show()

    def getFlags(self):
        flags = {}
        for i in range(self.flagsLayout.count()):
            item = self.flagsLayout.itemAt(i).widget()
            flags[item.text()] = item.isChecked()
        return flags

    def getGroupId(self):
        group_id = self.edit_group_id.text()
        if group_id:
            return int(group_id)
        return None

    def popUp(self, text=None, move=True, flags=None, group_id=None, description=None, character1=None, character2=None, character3=None, character4=None, character5=None, character6=None, character7=None):
        if self._fit_to_content["row"]:
            self.labelList.setMinimumHeight(
                self.labelList.sizeHintForRow(0) * self.labelList.count() + 2
            )
        if self._fit_to_content["column"]:
            self.labelList.setMinimumWidth(self.labelList.sizeHintForColumn(0) + 2)
        # if text is None, the previous label in self.edit is kept
        if text is None:
            text = self.edit.text() or 'No Text'
        # description is always initialized by empty text c.f., self.edit.text
        if description is None:
            description = ""
        print(description, "description")
        try:
            self.editDescription.setEditText(description)
        except:
            self.editDescription.setEditText(description[0][0])
        # self.editDescription.setPlainText(description)
        var = [character2, character3, character4, character5, character6, character7]
        selfvar = [self.character2, self.character3, self.character4, self.character5, self.character6, self.character7]
        for i, j in zip(var, selfvar):
            if i is None:
                i = ""
            try:
                j.setEditText(i)
            except:
                j.setEditText(i[0])
            
        selfvar = [self.character2, self.character3, self.character4, self.character5, self.character6, self.character7]
        if character1 is None:
            character1 = ""
        try:
            self.character1.setEditText(character1)
        except:
            self.character1.setEditText(character1[0])
        # self.character.setPlainText(character)
        if flags:
            self.setFlags(flags)
        else:
            self.resetFlags(text)
        self.edit.setText(text)
        self.edit.setSelection(0, len(text))
        if group_id is None:
            self.edit_group_id.clear()
        else:
            self.edit_group_id.setText(str(group_id))
        items = self.labelList.findItems(text, QtCore.Qt.MatchFixedString)
        if items:
            if len(items) != 1:
                logger.warning("Label list has duplicate '{}'".format(text))
            self.labelList.setCurrentItem(items[0])
            row = self.labelList.row(items[0])
            self.edit.completer().setCurrentRow(row)
        self.edit.setFocus(QtCore.Qt.PopupFocusReason)
        if move:
            self.move(QtGui.QCursor.pos())
        if self.exec_():
            return (
                self.edit.text(),
                self.getFlags(),
                self.getGroupId(),
                # self.editDescription.toPlainText(),
                self.editDescription.currentText(),
                # self.character.toPlainText()
                self.character1.currentText(),*[i.currentText() for i in selfvar]
            )
        else:
            return None, None, None, None, None, None, None, None, None, None, None
