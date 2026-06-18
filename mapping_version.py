from qgis.PyQt.QtWidgets import QMessageBox,QTextEdit,QSizePolicy,QDialog
from qgis.PyQt.QtCore import Qt

# QT6
try :
    Dialog = Qt.WindowType.Dialog
    Window = Qt.WindowType.Window
    Rejected = QDialog.DialogCode.Rejected
    WindowCloseButtonHint = Qt.WindowType.WindowCloseButtonHint
    WindowTitleHint = Qt.WindowType.WindowTitleHint
    WindowStaysOnTopHint = Qt.WindowType.WindowStaysOnTopHint
    # Checked = Qt.CheckState.Checked
    # Unchecked = Qt.CheckState.Unchecked
    # ItemIsEnabled = Qt.ItemFlag.ItemIsEnabled
    # ItemIsUserCheckable = Qt.ItemFlag.ItemIsUserCheckable
    # MatchExactly = Qt.MatchFlag.MatchExactly
    # RightSide = QTabBar.ButtonPosition.RightSide
    # LeftSide = QTabBar.ButtonPosition.LeftSide
    Warning = QMessageBox.Icon.Warning
    YesRole = QMessageBox.ButtonRole.YesRole
    AcceptRole = QMessageBox.ButtonRole.AcceptRole
    Ok = QMessageBox.StandardButton.Ok
    # NoSelection = QAbstractItemView.SelectionMode.NoSelection
    # NoFocus = Qt.FocusPolicy.NoFocus
    # DisplayRole = Qt.ItemDataRole.DisplayRole
    # BackgroundRole = Qt.ItemDataRole.BackgroundRole
    # RightButton = Qt.MouseButton.RightButton
    MiddleButton = Qt.MouseButton.MiddleButton
    LeftButton = Qt.MouseButton.LeftButton
    # NoContextMenu = Qt.ContextMenuPolicy.NoContextMenu
    AlignCenter = Qt.AlignmentFlag.AlignCenter
    WaitCursor = Qt.CursorShape.WaitCursor
    # AscendingOrder = QtCore.Qt.SortOrder.AscendingOrder
    NoWrap = QTextEdit.LineWrapMode.NoWrap
    ScrollBarAlwaysOff = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    Expanding = QSizePolicy.Policy.Expanding
    CrossCursor = Qt.CursorShape.CrossCursor
    ArrowCursor = Qt.CursorShape.ArrowCursor
    red = Qt.GlobalColor.red


# QT5
except :
    Dialog = Qt.Dialog
    Window = Qt.Window
    Rejected = QDialog.Rejected
    WindowCloseButtonHint = Qt.WindowCloseButtonHint
    WindowTitleHint = Qt.WindowTitleHint
    WindowStaysOnTopHint = Qt.WindowStaysOnTopHint
    # Checked = Qt.Checked
    # Unchecked = Qt.Unchecked
    # ItemIsEnabled = Qt.ItemIsEnabled
    # ItemIsUserCheckable = Qt.ItemIsUserCheckable
    # MatchExactly = Qt.MatchFlag.MatchExactly
    # RightSide = QTabBar.RightSide
    # LeftSide = QTabBar.LeftSide
    Warning = QMessageBox.Warning
    YesRole = QMessageBox.YesRole
    AcceptRole = QMessageBox.AcceptRole
    Ok = QMessageBox.Ok
    # NoSelection = QListWidget.NoSelection
    # NoFocus = Qt.NoFocus
    # DisplayRole = Qt.DisplayRole
    # BackgroundRole = Qt.BackgroundRole
    # RightButton = Qt.RightButton
    MiddleButton = Qt.MiddleButton
    LeftButton = Qt.LeftButton
    # NoContextMenu = Qt.NoContextMenu
    AlignCenter = Qt.AlignCenter
    WaitCursor = Qt.WaitCursor
    # AscendingOrder = QtCore.Qt.AscendingOrder
    NoWrap = QTextEdit.NoWrap
    ScrollBarAlwaysOff = Qt.ScrollBarAlwaysOff
    Expanding = QSizePolicy.Expanding
    CrossCursor = Qt.CrossCursor
    ArrowCursor = Qt.ArrowCursor
    red = Qt.red
