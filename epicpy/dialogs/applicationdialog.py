import sys
import os
import platform
from pathlib import Path
from typing import Optional

from qtpy.QtWidgets import (
    QDialog,
    QTextEdit,
    QPushButton,
    QToolButton,
    QLabel,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QApplication,
    QSizePolicy,
    QStyle,
    QMessageBox,
)
from qtpy.QtGui import QFont, QIcon
from qtpy.QtCore import QSize, Qt

from epicpy.utils.apputils import get_resource, has_epiccoder
from epicpy.utils.defaultfont import get_default_font


class EPICpyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Define widget variables for the two fields.
        self.label_text: Optional[QLabel] = None
        self.edit_text: Optional[QTextEdit] = None
        self.button_text_browse: Optional[QToolButton] = None
        self.button_text_default: Optional[QToolButton] = None
        self.button_epiccoder: Optional[QToolButton] = None

        self.label_data: Optional[QLabel] = None
        self.edit_data: Optional[QTextEdit] = None
        self.button_data_browse: Optional[QToolButton] = None
        self.button_data_default: Optional[QToolButton] = None
        self.button_data_placeholder: Optional[QToolButton] = None

        self.info_label: Optional[QLabel] = None
        self.sub_info_label: Optional[QLabel] = None
        self.button_ok: Optional[QPushButton] = None
        self.button_cancel: Optional[QPushButton] = None

        self.ok = False

        self.setFont(QApplication.instance().font())

        self.setWindowTitle("Applications to open EPICpy file types")
        self.setup_ui()
        self.create_connections()
        self.validate_fields()  # validate initial (empty) state

        # Check for epiccoder; if found, show the EPICcoder button
        # in the first row and show an equivalent placeholder in the data row.
        epiccoder_path = has_epiccoder()
        if epiccoder_path:
            self.button_epiccoder.setVisible(True)
            self.button_data_placeholder.setVisible(True)
        else:
            self.button_epiccoder.setVisible(False)
            self.button_data_placeholder.setVisible(False)

        # Set the default size of the dialog.
        self.resize(900, 250)

    def setup_ui(self):
        # ------------------------------
        # Top informational labels
        # ------------------------------
        # Update the text of the main info label.
        self.info_label = QLabel("Applications To Open EPICpy File Types")

        # Increase its font size by 2 points and make it bold.
        info_font = self.info_label.font()
        info_font.setPointSize(info_font.pointSize() + 2)
        info_font.setBold(True)
        self.info_label.setFont(info_font)

        # Create a new sub-label with blue, non-bold text.
        self.sub_info_label = QLabel(
            "An empty field results in EPICpy using your operating system's currently configured default application."
        )
        self.sub_info_label.setWordWrap(True)
        sub_font = QFont(self.sub_info_label.font())
        self.sub_info_label.setFont(sub_font)
        self.sub_info_label.setStyleSheet("color: blue;")

        # ------------------------------------------
        # Row 0: Combined Text Field (TXT & PRS)
        # ------------------------------------------
        self.label_text = QLabel("Text (*.txt, *.prs, etc.)")

        self.edit_text = QTextEdit()  # Multiline widget for text files
        self.edit_text.setAcceptRichText(False)
        # self.edit_text.setFont(self.font())
        # self.edit_text.document().setDefaultFont(self.font())
        # Two buttons for the text field: use QToolButton for icon+text.
        self.button_text_browse = QToolButton(self)
        self.button_text_default = QToolButton(self)  # Now used as a Clear button.
        # New EPICcoder tool button.
        self.button_epiccoder = QToolButton(self)

        # Set tool button style to show text under the icon.
        self.button_text_browse.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.button_text_default.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.button_epiccoder.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # Set icons, texts, and tooltips for text field buttons.
        self.button_text_browse.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        self.button_text_browse.setText("Select")
        self.button_text_browse.setToolTip("Select an application for editing text")

        # Update the default (now clear) button.
        self.button_text_default.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        self.button_text_default.setText("Clear")
        self.button_text_default.setToolTip("Clear the text field")

        # For the EPICcoder button, use epiccoder.png.
        self.button_epiccoder.setIcon(QIcon(str(get_resource("images", "epiccoder.png"))))
        self.button_epiccoder.setText("EPICcoder")
        self.button_epiccoder.setToolTip("Launch EPICcoder")

        # ------------------------------------------
        # Row 1: Data Field (*.csv)
        # ------------------------------------------
        self.label_data = QLabel("Data (*.csv)")
        self.edit_data = QTextEdit()  # Multiline widget for data files
        self.edit_data.setAcceptRichText(False)
        # self.edit_data.setFont(self.font())
        # self.edit_data.document().setDefaultFont(self.font())
        # Two buttons for the data field: also use QToolButton.
        self.button_data_browse = QToolButton(self)
        self.button_data_default = QToolButton(self)  # Now used as a Clear button.
        # Create a placeholder button for alignment.
        self.button_data_placeholder = QToolButton(self)

        self.button_data_browse.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.button_data_default.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.button_data_placeholder.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.button_data_placeholder.setAutoRaise(True)
        self.button_data_placeholder.setStyleSheet("QToolButton { border: none; background: none; }")

        self.button_data_browse.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        self.button_data_browse.setText("Select")
        self.button_data_browse.setToolTip("Select an application for editing rules")

        # Update the default (now clear) button for the data field.
        self.button_data_default.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        self.button_data_default.setText("Clear")
        self.button_data_default.setToolTip("Clear the data field")

        # Configure the placeholder: no icon, no text, disabled.
        self.button_data_placeholder.setIcon(QIcon())
        self.button_data_placeholder.setText("")
        self.button_data_placeholder.setEnabled(False)

        # Make the SP_DirOpenIcon and SP_DialogResetButton buttons 3 times larger.
        default_icon_size = self.style().pixelMetric(QStyle.PixelMetric.PM_ButtonIconSize)
        large_icon_size = QSize(default_icon_size * 3, default_icon_size * 3)
        for btn in (
            self.button_text_browse,
            self.button_text_default,
            self.button_epiccoder,
            self.button_data_browse,
            self.button_data_default,
            self.button_data_placeholder,
        ):
            btn.setIconSize(large_icon_size)
            # Set an 11-point font for the text under the icons.
            small_font = QFont(self.font())
            small_font.setPointSize(small_font.pointSize() - 3)
            btn.setFont(small_font)

        # ------------------------------------------
        # Bottom Buttons: Cancel and OK
        # ------------------------------------------
        self.button_cancel = QPushButton("Cancel")
        self.button_cancel.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
        self.button_ok = QPushButton("OK")
        self.button_ok.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))

        # Make the QTextEdits horizontally and vertically expandable.
        for edit in (self.edit_text, self.edit_data):
            edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            edit.setMinimumHeight(40)

        # Layout for the two rows.
        grid_layout = QGridLayout()
        # Row 0: Text field with buttons.
        grid_layout.addWidget(self.label_text, 0, 0)
        grid_layout.addWidget(self.edit_text, 0, 1)
        text_buttons_layout = QHBoxLayout()
        text_buttons_layout.addWidget(self.button_text_browse)
        text_buttons_layout.addWidget(self.button_text_default)
        text_buttons_layout.addWidget(self.button_epiccoder)
        grid_layout.addLayout(text_buttons_layout, 0, 2)
        # Row 1: Data field with buttons.
        grid_layout.addWidget(self.label_data, 1, 0)
        grid_layout.addWidget(self.edit_data, 1, 1)
        data_buttons_layout = QHBoxLayout()
        data_buttons_layout.addWidget(self.button_data_browse)
        data_buttons_layout.addWidget(self.button_data_default)
        data_buttons_layout.addWidget(self.button_data_placeholder)
        grid_layout.addLayout(data_buttons_layout, 1, 2)

        # Bottom buttons layout.
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # push buttons to the right
        button_layout.addWidget(self.button_cancel)
        button_layout.addWidget(self.button_ok)

        # Main vertical layout.
        main_layout = QVBoxLayout(self)
        # Add the two informational labels at the top.
        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.sub_info_label)
        main_layout.addLayout(grid_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def showEvent(self, event):
        super().showEvent(event)
        if self.button_epiccoder.isVisible():
            self.button_data_placeholder.setFixedSize(self.button_epiccoder.size())

    def create_connections(self):
        # When the browse buttons are clicked, open a file dialog.
        self.button_text_browse.clicked.connect(lambda: self.browse_file(self.edit_text))
        self.button_data_browse.clicked.connect(lambda: self.browse_file(self.edit_data))

        # The clear buttons now clear the text fields.
        self.button_text_default.clicked.connect(self.edit_text.clear)
        self.button_data_default.clicked.connect(self.edit_data.clear)
        # The EPICcoder button sets the text field to the output of has_epiccoder().
        self.button_epiccoder.clicked.connect(lambda: self.edit_text.setPlainText(has_epiccoder()))

        # Validate file paths whenever text changes.
        self.edit_text.textChanged.connect(self.validate_fields)
        self.edit_data.textChanged.connect(self.validate_fields)

        # Connect OK and Cancel buttons.
        self.button_ok.clicked.connect(self.ok_clicked)
        self.button_cancel.clicked.connect(self.cancel_clicked)

    def browse_file(self, target_edit):
        """
        Opens a file dialog (starting in the user's home directory) using a filter
        appropriate for executables. If a file is selected and is executable, its path
        is set in the provided QTextEdit. Otherwise, shows a dialog informing the user
        that the selected file is not an executable application.
        """
        home_dir = str(Path.home())
        filter_str = self.get_executable_filter()

        file_path, _ = QFileDialog.getOpenFileName(
            self,  # Parent widget (or None if not inside a class)
            "Select Executable",  # Dialog title (caption)
            home_dir,  # Default directory
            filter_str,  # File filter
        )

        if file_path:
            system = platform.system()
            if system == "Windows":
                # On Windows, ensure the file ends with ".exe"
                if not file_path.lower().endswith(".exe"):

                    QMessageBox.information(
                        self,  # Parent widget (if inside a class, otherwise use None)
                        "Invalid Executable",  # Title
                        "The selected file is not an executable application.",  # Message text
                        QMessageBox.StandardButton.Ok,  # Buttons
                    )

                    return
            else:
                # On macOS and Linux, check for executable permission.
                # Allow ".app" bundles on macOS without checking permissions.
                if system == "Darwin" and file_path.lower().endswith(".app"):
                    pass
                else:
                    if not os.access(file_path, os.X_OK):

                        QMessageBox.information(
                            self,  # Parent widget (use None if not inside a class)
                            "Invalid Executable",  # Title
                            "The selected file is not an executable application.",  # Message text
                            QMessageBox.StandardButton.Ok,  # Buttons
                        )

                        return
            target_edit.setPlainText(file_path)

    @staticmethod
    def get_executable_filter():
        """
        Returns a file filter string for the file open dialog depending on the OS.
        """
        system = platform.system()
        if system == "Windows":
            return "Executable Files (*.exe)"
        elif system == "Darwin":
            return "Applications (*.app);;Executable Files (*)"
        else:
            return "Executable Files (*)"

    def validate_fields(self):
        """
        Validates that each QTextEdit is either empty or contains a valid file path.
        Invalid fields are highlighted in red, and the OK button is enabled only if all fields are valid.
        """
        all_valid = True
        for edit in (self.edit_text, self.edit_data):
            path_str = edit.toPlainText().strip()
            if path_str == "":
                edit.setStyleSheet("")
            else:
                if os.path.isfile(path_str):
                    edit.setStyleSheet("")
                else:
                    edit.setStyleSheet("background-color: red;")
                    all_valid = False
        self.button_ok.setEnabled(all_valid)
        self.ok = all_valid

    def ok_clicked(self):
        """Called when OK is pressed; closes the dialog."""
        self.close()

    def cancel_clicked(self):
        """Called when Cancel is pressed; sets ok to False and closes the dialog."""
        self.ok = False
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # prepare the default font
    default_font = get_default_font(family="monospace", size=14)

    # Set the font for the application
    QApplication.instance().setFont(default_font)

    dialog = EPICpyDialog()
    dialog.show()
    app.exec()

    # After the dialog is closed, print the field contents.
    if dialog.ok:
        print("OK was pressed and all file paths are valid or empty.")
        print("Text field:", dialog.edit_text.toPlainText())
        print("Data field:", dialog.edit_data.toPlainText())
    else:
        print("Dialog was cancelled or contains invalid file paths.")

    sys.exit()
