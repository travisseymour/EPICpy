"""
EPICcoder is a minimal programmer's text editor created for use with the
EPIC, EPICpy and pyEPIC simulation environments.
Copyright (C) 2022 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
from functools import partial
from typing import Optional

import sys
from pathlib import Path

from PyQt5.QtCore import QSettings, Qt, QSize, QDir, QModelIndex, QRect
from PyQt5.QtGui import QIcon, QFont, QPixmap, QResizeEvent, QCloseEvent
from PyQt5.QtWidgets import (
    QMainWindow,
    QLabel,
    QFrame,
    QSizePolicy,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QFileSystemModel,
    QTreeView,
    QLineEdit,
    QCheckBox,
    QListWidget,
    QSpacerItem,
    QTabWidget,
    QMessageBox,
    QFileDialog,
    QApplication, QMenu, QAction, QDialog,
)

from epiccoder.customeditor import CustomEditor
from epiccoder.duplicatedlg import DuplicateFileNameWin
from epiccoder.fuzzy_searcher import SearchItem, SearchWorker
from epiccoder.aboutwindow import AboutWin
from epiccoder.version import __version__

from fbs_runtime.application_context.PyQt5 import ApplicationContext

int_gen = (
    i for i in range(sys.maxsize)
)  # generator for successive integers from 1 to sys.maxsize


class MainWindow(QMainWindow):
    def __init__(self, context: ApplicationContext):
        super(QMainWindow, self).__init__()

        self.context = context
        self.force_close: bool = False

        # add before init
        self.side_bar_clr = "#282c34"

        # init settings
        self.settings = QSettings()
        self.main_window_width = self.settings.value(
            "main_window_width", type=int, defaultValue=1300
        )
        self.main_window_height = self.settings.value(
            "main_window_height", type=int, defaultValue=900
        )

        self.init_ui()

        self.current_file = None
        self.current_side_bar = None

        self.setWindowIcon(QIcon(self.context.get_resource("uiicons", "app-icon.svg")))

    def init_ui(self):
        self.setWindowTitle(f"EPIC Coder v{__version__}")
        self.resize(self.main_window_width, self.main_window_height)

        style_sheet = Path(self.context.get_resource("css/style.qss")).read_text()
        style_sheet = style_sheet.replace(
            ":/icons/close-icon.svg",
            self.context.get_resource("uiicons", "close-icon.svg"),
        )
        self.setStyleSheet(style_sheet)

        # setup font
        self.window_font = QFont("Fira Code")
        self.window_font.setPointSize(12)
        self.setFont(self.window_font)

        self.set_up_menu()
        self.set_up_body()
        self.statusBar().showMessage("hello")

        self.last_hsplit_sizes = [400, self.width()-400]
        self.hsplit.setSizes(self.last_hsplit_sizes)
        self.show()

    def set_up_menu(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        # Open File/Folder

        open_file = file_menu.addAction("Open File")
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.open_file)

        open_folder = file_menu.addAction("Open Folder")
        open_folder.setShortcut("Ctrl+K")
        open_folder.triggered.connect(self.open_folder)

        file_menu.addSeparator()

        # Save/SaveAs File

        save_file = file_menu.addAction("Save")
        save_file.setShortcut("Ctrl+S")
        save_file.triggered.connect(self.save_file)

        save_as = file_menu.addAction("Save As")
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.triggered.connect(self.save_as)

        file_menu.addSeparator()

        # New File SubMenu & Actions
        new_file_menu = QMenu('New File', self)

        txt_action = QAction('Text File (*.txt)', self)
        txt_action.triggered.connect(partial(self.new_file, '.txt'))
        prs_action = QAction('EPIC Production Rule File (*.prs)', self)
        prs_action.triggered.connect(partial(self.new_file, '.prs'))
        py_action = QAction('Python Code File (*.py)', self)
        py_action.triggered.connect(partial(self.new_file, '.py'))
        cpp_action = QAction('C++ Code File (*.cpp)', self)
        cpp_action.triggered.connect(partial(self.new_file, '.cpp'))
        h_action = QAction('C++ Header File (*.h)', self)
        h_action.triggered.connect(partial(self.new_file, '.h'))

        for obj in (txt_action, prs_action, py_action, cpp_action, h_action):
            new_file_menu.addAction(obj)

        file_menu.addMenu(new_file_menu)

        file_menu.addSeparator()

        # Duplicate File

        self.dupe_file = file_menu.addAction("Duplicate")
        self.dupe_file.setShortcut("Ctrl+D")
        self.dupe_file.triggered.connect(self.duplicate_file)
        self.dupe_file.setEnabled(False)

        file_menu.addSeparator()

        # Delete File

        self.delete_file = file_menu.addAction("Delete")
        self.delete_file.setShortcut("Ctrl+X")
        self.delete_file.triggered.connect(self.remove_file)
        self.delete_file.setEnabled(False)

        file_menu.addSeparator()

        # Quit Action

        quit_app = file_menu.addAction("Quit")
        quit_app.setShortcut("Ctrl+Q")
        quit_app.triggered.connect(self.close)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")

        copy_action = edit_menu.addAction("Copy")
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)

        paste_action = edit_menu.addAction("Paste")
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)

        # Help menu

        help_menu = menu_bar.addMenu("Help")

        about = help_menu.addAction("About")
        about.setShortcut("Ctrl+A")
        about.triggered.connect(self.show_about)

        # help = help_menu.addAction("Help")
        # help.setShortcut("Ctrl+H")
        # help.triggered.connect(self.show_help)

    def show_about(self):
        about = AboutWin(self, context=self.context)
        about.show()

    def show_help(self):
        ...

    def get_editor(self, file_path: Path) -> CustomEditor:  # QsciScintilla:
        editor = CustomEditor(file_path=file_path, star_func=self.add_star)
        return editor

    def is_binary(self, path):
        """
        Check if file is binary
        """
        with open(path, "rb") as f:
            return b"\0" in f.read(1024)

    def add_star(self, file_path: Path):
        for i in range(self.tab_view.count()):
            if str(self.tab_view.tabText(i)).endswith(
                f"{Path(file_path.parent.name, file_path.name)}"
            ):
                self.tab_view.setTabText(i, f"*{self.tab_view.tabText(i).strip('*')}")
                return

    def next_new_file_path(self, file_type: str, stem: str='untitled') -> Path:
        _stem = stem if stem else 'untitled'
        expected_fts = ['.txt', '.prs', '.cpp', '.h', '.py']
        assert file_type.lower() in expected_fts, f"new_new_file_path() requires a filetype in {expected_fts}"
        for _ in range(9999):
            p = Path(self.model.rootPath(), f"{_stem}{next(int_gen)}{file_type.lower()}")
            if not p.exists():
                return p
        return Path(self.model.rootPath(), f"{_stem}{next(int_gen)}{file_type.lower()}")

    def set_new_tab(self, path: Path, is_new_file=False, file_type: str='txt'):
        if path and isinstance(path, Path) and not path.is_file():
            return

        new_file_path = self.next_new_file_path(file_type) if is_new_file else path
        editor: CustomEditor = self.get_editor(new_file_path)

        if is_new_file:
            self.tab_view.addTab(
                editor, f"*{Path(new_file_path.parent.name, new_file_path.name)}"
            )
            self.setWindowTitle(str(new_file_path))
            self.statusBar().showMessage(f"Opened '{new_file_path.name}")
            self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
            self.current_file = None
            return

        if self.is_binary(path):
            self.statusBar().showMessage("Cannot Open Binary File", 2000)
            return

        # check if file already open
        for i in range(self.tab_view.count()):
            # print(f"{self.tab_view.widget(i).file_type=}")  # keep to remind me that I can access widget..need shortly
            if str(self.tab_view.tabText(i)).endswith(
                f"{Path(new_file_path.parent.name, new_file_path.name)}"
            ):
                self.tab_view.setCurrentIndex(i)
                self.current_file = new_file_path
                return

        # create new tab
        self.tab_view.addTab(
            editor, f"{Path(new_file_path.parent.name, new_file_path.name)}"
        )
        editor.setText(new_file_path.read_text())
        self.setWindowTitle(str(new_file_path))
        self.current_file = new_file_path
        self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
        self.statusBar().showMessage(f"Opened {new_file_path.name}", 5000)

        self.dupe_file.setEnabled(self.tab_view.count())
        self.delete_file.setEnabled(self.tab_view.count())

    def set_cursor_pointer(self, e):
        self.setCursor(Qt.PointingHandCursor)

    def set_cursor_arrow(self, e):
        self.setCursor(Qt.ArrowCursor)

    def get_side_bar_label(self, path, name):
        label = QLabel()
        label.setPixmap(QPixmap(path).scaled(QSize(30, 30)))
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setFont(self.window_font)
        label.mousePressEvent = lambda e: self.show_hide_tab(e, name)
        # Changing Cursor on hover
        label.enterEvent = self.set_cursor_pointer
        label.leaveEvent = self.set_cursor_arrow
        return label

    def get_frame(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame.setFrameShadow(QFrame.Plain)
        frame.setContentsMargins(0, 0, 0, 0)
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #21252b;
                border-radius: 5px;
                border: none;
                padding: 5px;
                color: #D3D3D3;
            }
            QFrame:hover {
                color: white;
            }
        """
        )
        return frame

    def set_up_body(self):

        # Body
        body_frame = QFrame()
        body_frame.setFrameShape(QFrame.NoFrame)
        body_frame.setFrameShadow(QFrame.Plain)
        body_frame.setLineWidth(0)
        body_frame.setMidLineWidth(0)
        body_frame.setContentsMargins(0, 0, 0, 0)
        body_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body_frame.setLayout(body)

        ##############################
        ###### SIDE BAR ##########
        self.side_bar = QFrame()
        self.side_bar.setFrameShape(QFrame.StyledPanel)
        self.side_bar.setFrameShadow(QFrame.Plain)
        self.side_bar.setStyleSheet(
            f"""
            background-color: {self.side_bar_clr};
        """
        )
        side_bar_layout = QVBoxLayout()
        side_bar_layout.setContentsMargins(5, 10, 5, 0)
        side_bar_layout.setSpacing(0)
        side_bar_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        # setup labels
        folder_label = self.get_side_bar_label(
            self.context.get_resource("uiicons", "folder-icon-blue.svg"), "folder-icon"
        )
        side_bar_layout.addWidget(folder_label)

        search_label = self.get_side_bar_label(
            self.context.get_resource("uiicons", "search-icon.svg"), "search-icon"
        )
        side_bar_layout.addWidget(search_label)

        self.side_bar.setLayout(side_bar_layout)

        # split view
        self.hsplit = QSplitter(Qt.Horizontal)

        ##############################
        ###### FILE MANAGER ##########

        # frame and layout to hold tree view (file manager)
        self.file_manager_frame = self.get_frame()

        # self.file_manager_frame.setMaximumWidth(400)
        # self.file_manager_frame.setMinimumWidth(200)
        self.file_manager_frame.setMaximumWidth(self.window().width())
        self.file_manager_frame.setMinimumWidth(200)
        tree_frame_layout = QVBoxLayout()
        tree_frame_layout.setContentsMargins(0, 0, 0, 0)
        tree_frame_layout.setSpacing(0)

        # Create file system model to show in tree view
        self.model = QFileSystemModel()
        self.model.setRootPath(os.getcwd())
        # File system filters
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)

        ##############################
        ###### FILE VIEWER ##########
        self.tree_view = QTreeView()
        self.tree_view.setFont(QFont("Fira Code", 13))
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(os.getcwd()))
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setSelectionBehavior(QTreeView.SelectRows)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        # add custom context menu
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.tree_view_context_menu)
        # handling click
        # self.tree_view.clicked.connect(self.tree_view_clicked)
        self.tree_view.doubleClicked.connect(self.tree_view_clicked)
        self.tree_view.setIndentation(10)
        self.tree_view.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        # Hide header and hide other columns except for name
        self.tree_view.setHeaderHidden(True)  # hiding header
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)

        ##############################
        ###### SEARCH VIEW ##########
        self.search_frame = self.get_frame()
        self.search_frame.setMaximumWidth(self.window().width())
        self.search_frame.setMinimumWidth(200)

        search_layout = QVBoxLayout()
        search_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        search_layout.setContentsMargins(0, 10, 0, 0)
        search_layout.setSpacing(0)

        search_input = QLineEdit()
        search_input.setPlaceholderText("Search")
        search_input.setFont(self.window_font)
        search_input.setAlignment(Qt.AlignmentFlag.AlignTop)
        search_input.setStyleSheet(
            """
        QLineEdit {
            background-color: #21252b;
            border-radius: 5px;
            border: 1px solid #D3D3D3;
            padding: 5px;
            color: #D3D3D3;
        }

        QLineEdit:hover {
            color: white;
            }
        """
        )

        ############# CHECKBOX ################
        self.search_checkbox = QCheckBox("Search in modules")
        self.search_checkbox.setFont(self.window_font)
        self.search_checkbox.setStyleSheet("color: white; margin-bottom: 10px;")

        self.search_worker = SearchWorker()
        self.search_worker.finished.connect(self.search_finished)

        search_input.textChanged.connect(
            lambda text: self.search_worker.update(
                text,
                self.model.rootDirectory().absolutePath(),
                self.search_checkbox.isChecked(),
            )
        )

        ##############################
        ###### SEARCH ListView ##########
        self.search_list_view = QListWidget()
        self.search_list_view.setFont(QFont("Fira Code", 13))
        self.search_list_view.setStyleSheet(
            """
        QListWidget {
            background-color: #21252b;
            border-radius: 5px;
            border: 1px solid #D3D3D3;
            padding: 5px;
            color: #D3D3D3;
        }
        """
        )

        self.search_list_view.itemClicked.connect(self.search_list_view_clicked)

        search_layout.addWidget(self.search_checkbox)
        search_layout.addWidget(search_input)
        search_layout.addSpacerItem(
            QSpacerItem(5, 5, QSizePolicy.Minimum, QSizePolicy.Minimum)
        )
        search_layout.addWidget(self.search_list_view)

        self.search_frame.setLayout(search_layout)

        # setup layout
        tree_frame_layout.addWidget(self.tree_view)
        self.file_manager_frame.setLayout(tree_frame_layout)

        ##############################
        ###### TAB VIEW ##########

        # Tab Widget to add editor to
        self.tab_view = QTabWidget()
        self.tab_view.setContentsMargins(0, 0, 0, 0)
        self.tab_view.setTabsClosable(True)
        self.tab_view.setMovable(True)
        self.tab_view.setDocumentMode(True)
        self.tab_view.tabCloseRequested.connect(self.close_tab)

        ##############################
        ###### SETUP WIDGETS ##########

        # add tree view and tab view
        self.hsplit.addWidget(self.file_manager_frame)
        self.hsplit.addWidget(self.tab_view)

        body.addWidget(self.side_bar)
        body.addWidget(self.hsplit)

        body_frame.setLayout(body)

        self.setCentralWidget(body_frame)

    def search_finished(self, items):
        self.search_list_view.clear()
        for i in items:
            self.search_list_view.addItem(i)

    def search_list_view_clicked(self, item: SearchItem):
        self.set_new_tab(Path(item.full_path))
        editor: CustomEditor = self.tab_view.currentWidget()
        editor.setCursorPosition(item.lineno, item.end)
        editor.setFocus()

    def close_tab(self, index, quiet: bool = False):
        if self.tab_view.tabText(index).startswith("*"):
            if not quiet:
                ret = QMessageBox.question(
                    self,
                    "Changed File Alert!",
                    f"Close {Path(self.tab_view.tabText(index)).name} and Ignore Changes?",
                    buttons=QMessageBox.Yes | QMessageBox.No,
                )
                if ret == QMessageBox.No:
                    return

        self.tab_view.removeTab(index)

        self.dupe_file.setEnabled(self.tab_view.count())
        self.delete_file.setEnabled(self.tab_view.count())

    def show_hide_tab(self, e, type_):
        if type_ == "folder-icon":
            if not (self.file_manager_frame in self.hsplit.children()):
                # restore file manager
                self.hsplit.replaceWidget(0, self.file_manager_frame)
                # self.file_manager_frame.setMaximumWidth(self.window().width())
                # self.file_manager_frame.setMinimumWidth(200)
                # restore previous file manager width
                w = self.hsplit.width()
                self.hsplit.setSizes(self.last_hsplit_sizes)

        elif type_ == "search-icon":
            if not (self.search_frame in self.hsplit.children()):
                # remember hsplit before search
                self.last_hsplit_sizes = self.hsplit.sizes()
                # restore search interface
                self.hsplit.replaceWidget(0, self.search_frame)
                self.search_frame.setMaximumWidth(self.window().width())
                self.search_frame.setMinimumWidth(200)

        if self.current_side_bar == type_:
            frame = self.hsplit.children()[0]
            if frame.isHidden():
                frame.show()
            else:
                frame.hide()



        self.current_side_bar = type_

    def tree_view_context_menu(self, pos):
        ...

    def tree_view_clicked(self, index: QModelIndex):
        path = self.model.filePath(index)
        try:
            p = Path(path)
            self.set_new_tab(p)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Problem With Folder Choice",
                f"Unable to open {str(path)}: {str(e)}",
            )

    def new_file(self, file_type: str):
        self.set_new_tab(None, is_new_file=True, file_type=file_type)

    def verify_duplicate_file_name(self, dupe_path: Path)->Optional[Path]:
        dlg = DuplicateFileNameWin(dupe_path)
        dlg.exec_()
        if dlg.result():
            return dlg.path_result
        else:
            return None

    def duplicate_file(self):
        if not self.tab_view.count():
            return

        p = Path(self.current_file)
        dupe_path = self.next_new_file_path(file_type=p.suffix, stem=p.stem)
        dupe_path = self.verify_duplicate_file_name(dupe_path)
        if dupe_path is None:
            return
        _ = dupe_path.write_text(p.read_text())
        self.set_new_tab(path=dupe_path, is_new_file=False, file_type=p.suffix)

    def remove_file(self):
        if not self.tab_view.count() or self.tab_view.currentWidget() is None:
            return

        p = Path(self.current_file)

        ret = QMessageBox.question(
            self,
            "FIle Deletion Warning!",
            f"Are You Sure You Want To Delete {str(p)}?\n\nThis operation cannot be undone!",
            buttons=QMessageBox.Yes | QMessageBox.No,
        )
        if ret == QMessageBox.No:
            return

        try:
            p.unlink(missing_ok=True)
            self.close_tab(self.tab_view.currentIndex(), quiet=True)
            if self.tab_view.count():
                self.current_file = self.tab_view.currentWidget().file_path
            else:
                self.current_file = None
        except Exception as e:
            QMessageBox.critical(
                self,
                f'File I/O Error!',
                f'Unable To Delete File {str(p)}: ({str(e)})',
            )


    def save_file(self):
        if self.current_file is None and self.tab_view.count() > 0:
            self.save_as()

        editor: CustomEditor = self.tab_view.currentWidget()

        self.current_file.write_text(editor.text())
        # self.tab_view.setTabText(self.tab_view.currentIndex(), self.current_file.name)
        self.tab_view.setTabText(
            self.tab_view.currentIndex(),
            f"{Path(self.current_file.parent.name, self.current_file.name)}",
        )
        self.statusBar().showMessage(f"Saved {self.current_file.name}", 2000)

    def save_as(self):
        # save as
        editor = self.tab_view.currentWidget()
        if editor is None:
            return

        initial_name = str(self.tab_view.currentWidget().file_path)
        if self.tab_view.currentWidget().file_path.suffix:
            initial_filter = (
                f"*{self.tab_view.currentWidget().file_path.suffix.lower()}"
            )
        else:
            initial_filter = ""

        file_path = QFileDialog.getSaveFileName(
            self,
            caption="Save As",
            directory=initial_name,
            filter="All Files (*);;PRS Rule Files (*.prs);;"
            "Text Files (*.txt);;Python Files (*.py);;"
            "C++ Code Files (*.cpp);;C++ Header Files (*.h)",
            initialFilter=initial_filter,
        )[0]

        if file_path == "":
            self.statusBar().showMessage("Cancelled", 2000)
            return

        path = Path(file_path)
        try:
            path.write_text(editor.text())
        except IOError as e:
            self.statusBar().showMessage("Write Error: {e}", 5000)
            return

        # self.tab_view.setTabText(self.tab_view.currentIndex(), path.name)
        self.tab_view.setTabText(
            self.tab_view.currentIndex(), f"{Path(path.parent.name, path.name)}"
        )

        self.statusBar().showMessage(f"Saved {path.name}", 2000)
        self.current_file = path

    def open_file(self, file_path: Optional[Path] = None):
        if isinstance(file_path, Path) and Path(file_path).is_file():
            f = file_path
        else:
            # open file
            ops = QFileDialog.Options()  # this is optional
            ops |= QFileDialog.DontUseNativeDialog
            # TODO: add support for opening multiple files later. for now it can only open one at a time
            new_file, _ = QFileDialog.getOpenFileName(
                self,
                caption="Pick A File",
                directory=str(self.model.rootDirectory().absolutePath()),
                filter="All Files (*);;PRS Rule Files (*.prs);;"
                "Text Files (*.txt);;Python Files (*.py);;"
                "C++ Code Files (*.cpp);;C++ Header Files (*.h)",
                options=ops,
            )
            if new_file == "":
                self.statusBar().showMessage("Cancelled", 2000)
                return
            f = Path(new_file)

        self.set_new_tab(f)

    def open_folder(self):
        # open folder
        ops = QFileDialog.Options()  # this is optional
        ops |= QFileDialog.DontUseNativeDialog

        new_folder = QFileDialog.getExistingDirectory(
            self, "Pick A Folder", "", options=ops
        )
        if new_folder:
            self.model.setRootPath(new_folder)
            self.tree_view.setRootIndex(self.model.index(new_folder))
            self.statusBar().showMessage(f"Opened {new_folder}", 2000)

    def set_folder(self, folder: Path):
        if folder.is_dir():
            self.model.setRootPath(str(folder))
            self.tree_view.setRootIndex(self.model.index(str(folder)))
            self.statusBar().showMessage(f"Opened in {str(folder)}", 2000)

    def copy(self):
        editor = self.tab_view.currentWidget()
        if editor is not None:
            editor.copy()

    def paste(self):
        editor = self.tab_view.currentWidget()
        if editor is not None:
            editor.paste()

    def resizeEvent(self, event: QResizeEvent):
        self.settings.setValue("main_window_width", self.size().width())
        self.settings.setValue("main_window_height", self.size().height())

    def closeEvent(self, event: QCloseEvent):
        if not self.force_close:
            for i in range(self.tab_view.count()):
                if str(self.tab_view.tabText(i)).startswith("*"):

                    ret = QMessageBox.question(
                        self,
                        "Changed File Alert!",
                        "Close Application and Ignore Changes?",
                        buttons=QMessageBox.Yes | QMessageBox.No,
                    )
                    if ret == QMessageBox.Yes:
                        event.accept()
                    else:
                        event.ignore()
                    return

                    # self.tab_view.setTabText(i, f"*{self.tab_view.tabText(i).strip('*')}")
        event.accept()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.set_folder(
        Path("/home/nogard/Dropbox/Documents/python_coding/EPICcoder/samples")
    )
    sys.exit(app.exec())
