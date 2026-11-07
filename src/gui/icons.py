from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap


def create_new_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Document body
    pen = QPen(QColor(80, 80, 80), 1.5)
    painter.setPen(pen)
    painter.setBrush(QBrush(QColor(245, 245, 245)))
    painter.drawRoundedRect(QRectF(6, 4, 18, 24), 2, 2)

    # Lines on document
    pen_lines = QPen(QColor(160, 160, 160), 1.5)
    painter.setPen(pen_lines)
    painter.drawLine(10, 10, 18, 10)
    painter.drawLine(10, 14, 20, 14)
    painter.drawLine(10, 18, 17, 18)

    # Plus badge
    painter.setPen(QPen(QColor(40, 140, 40), 1.5))
    painter.setBrush(QBrush(QColor(80, 200, 80)))
    painter.drawEllipse(QRectF(15, 15, 13, 13))

    painter.setPen(QPen(QColor(255, 255, 255), 2))
    painter.drawLine(21, 18, 21, 25)
    painter.drawLine(18, 21, 25, 21)

    painter.end()
    return QIcon(pixmap)


def create_open_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Folder back
    painter.setPen(QPen(QColor(180, 140, 40), 1.5))
    painter.setBrush(QBrush(QColor(240, 190, 70)))
    path_back = QPainterPath()
    path_back.moveTo(4, 10)
    path_back.lineTo(12, 10)
    path_back.lineTo(15, 13)
    path_back.lineTo(26, 13)
    path_back.lineTo(26, 26)
    path_back.lineTo(4, 26)
    path_back.closeSubpath()
    painter.drawPath(path_back)

    # Folder front (open)
    painter.setPen(QPen(QColor(170, 130, 30), 1.5))
    painter.setBrush(QBrush(QColor(255, 210, 90)))
    path_front = QPainterPath()
    path_front.moveTo(2, 26)
    path_front.lineTo(7, 15)
    path_front.lineTo(29, 15)
    path_front.lineTo(24, 26)
    path_front.closeSubpath()
    painter.drawPath(path_front)

    painter.end()
    return QIcon(pixmap)


def create_save_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Floppy disk body
    painter.setPen(QPen(QColor(40, 80, 140), 1.5))
    painter.setBrush(QBrush(QColor(60, 120, 200)))
    painter.drawRoundedRect(QRectF(5, 5, 22, 22), 2, 2)

    # Metal shutter / top label
    painter.setPen(QPen(QColor(30, 60, 110), 1.0))
    painter.setBrush(QBrush(QColor(230, 230, 230)))
    painter.drawRect(QRectF(9, 5, 14, 9))

    # Slider cutout
    painter.setBrush(QBrush(QColor(60, 120, 200)))
    painter.drawRect(QRectF(11, 7, 3, 5))

    # Bottom label
    painter.setBrush(QBrush(QColor(250, 250, 250)))
    painter.drawRoundedRect(QRectF(8, 17, 16, 10), 1, 1)

    painter.end()
    return QIcon(pixmap)


def create_undo_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setPen(QPen(QColor(50, 100, 170), 1.5))
    painter.setBrush(QBrush(QColor(80, 150, 230)))

    path = QPainterPath()
    path.moveTo(6, 16)
    path.lineTo(14, 9)
    path.lineTo(14, 13)
    path.cubicTo(22, 13, 27, 16, 27, 24)
    path.cubicTo(24, 18, 19, 18, 14, 18)
    path.lineTo(14, 23)
    path.closeSubpath()
    painter.drawPath(path)

    painter.end()
    return QIcon(pixmap)


def create_redo_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setPen(QPen(QColor(50, 100, 170), 1.5))
    painter.setBrush(QBrush(QColor(80, 150, 230)))

    path = QPainterPath()
    path.moveTo(26, 16)
    path.lineTo(18, 9)
    path.lineTo(18, 13)
    path.cubicTo(10, 13, 5, 16, 5, 24)
    path.cubicTo(8, 18, 13, 18, 18, 18)
    path.lineTo(18, 23)
    path.closeSubpath()
    painter.drawPath(path)

    painter.end()
    return QIcon(pixmap)


def create_copy_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Back document
    painter.setPen(QPen(QColor(100, 100, 100), 1.5))
    painter.setBrush(QBrush(QColor(230, 230, 230)))
    painter.drawRoundedRect(QRectF(5, 5, 16, 19), 2, 2)

    # Front document
    painter.setPen(QPen(QColor(60, 110, 180), 1.5))
    painter.setBrush(QBrush(QColor(250, 250, 255)))
    painter.drawRoundedRect(QRectF(11, 9, 16, 19), 2, 2)

    # Content lines
    painter.setPen(QPen(QColor(160, 180, 210), 1.5))
    painter.drawLine(14, 14, 22, 14)
    painter.drawLine(14, 18, 24, 18)
    painter.drawLine(14, 22, 20, 22)

    painter.end()
    return QIcon(pixmap)


def create_cut_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setPen(QPen(QColor(60, 130, 200), 2.0))
    painter.setBrush(Qt.BrushStyle.NoBrush)

    # Scissors handles
    painter.drawEllipse(QRectF(5, 19, 8, 8))
    painter.drawEllipse(QRectF(19, 19, 8, 8))

    # Scissors blades
    painter.drawLine(10, 20, 24, 6)
    painter.drawLine(22, 20, 8, 6)

    # Pivot pin
    painter.setBrush(QBrush(QColor(40, 80, 140)))
    painter.drawEllipse(QRectF(14.5, 12.5, 3, 3))

    painter.end()
    return QIcon(pixmap)


def create_paste_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Clipboard board
    painter.setPen(QPen(QColor(140, 100, 50), 1.5))
    painter.setBrush(QBrush(QColor(190, 140, 80)))
    painter.drawRoundedRect(QRectF(5, 7, 20, 22), 2, 2)

    # Clip at top
    painter.setPen(QPen(QColor(100, 100, 100), 1.5))
    painter.setBrush(QBrush(QColor(220, 220, 220)))
    painter.drawRoundedRect(QRectF(10, 4, 10, 5), 1, 1)

    # Paper on clipboard
    painter.setPen(QPen(QColor(80, 80, 80), 1.2))
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    painter.drawRect(QRectF(10, 11, 17, 18))

    # Lines on paper
    painter.setPen(QPen(QColor(180, 180, 180), 1.2))
    painter.drawLine(13, 16, 23, 16)
    painter.drawLine(13, 20, 24, 20)
    painter.drawLine(13, 24, 20, 24)

    painter.end()
    return QIcon(pixmap)


def create_run_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Outer circle
    painter.setPen(QPen(QColor(30, 120, 40), 2.0))
    painter.setBrush(QBrush(QColor(40, 160, 60)))
    painter.drawEllipse(QRectF(4, 4, 24, 24))

    # Inner play triangle
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    path = QPainterPath()
    path.moveTo(12, 9)
    path.lineTo(23, 16)
    path.lineTo(12, 23)
    path.closeSubpath()
    painter.drawPath(path)

    painter.end()
    return QIcon(pixmap)


def create_help_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Outer circle
    painter.setPen(QPen(QColor(40, 100, 170), 2.0))
    painter.setBrush(QBrush(QColor(60, 130, 210)))
    painter.drawEllipse(QRectF(4, 4, 24, 24))

    # Question mark
    painter.setPen(QPen(QColor(255, 255, 255), 2.5))
    font = QFont("SansSerif", 13, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(QRectF(4, 3, 24, 24), Qt.AlignmentFlag.AlignCenter, "?")

    painter.end()
    return QIcon(pixmap)


def create_about_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Outer circle
    painter.setPen(QPen(QColor(70, 70, 70), 2.0))
    painter.setBrush(QBrush(QColor(100, 100, 100)))
    painter.drawEllipse(QRectF(4, 4, 24, 24))

    # Letter "i"
    painter.setPen(QPen(QColor(255, 255, 255), 2.5))
    font = QFont("Serif", 13, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(QRectF(4, 3, 24, 24), Qt.AlignmentFlag.AlignCenter, "i")

    painter.end()
    return QIcon(pixmap)
