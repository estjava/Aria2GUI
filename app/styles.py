"""
styles.py
Semua stylesheet QSS untuk tampilan dark mode aplikasi.
"""

DARK_STYLE = """
QMainWindow, 
QWidget {
    background-color: #0f1117;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #1e2435;
    border-radius: 8px;
    margin-top: 12px;
    padding: 10px;
    color: #94a3b8;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QLineEdit {
    background-color: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e2e8f0;
    selection-background-color: #3b82f6;
}
QLineEdit:focus {
    border-color: #3b82f6;
}

QPushButton {
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton#btn_add {
    background-color: #3b82f6;
    color: white;
    border: none;
}
QPushButton#btn_add:hover   { background-color: #2563eb; }
QPushButton#btn_add:pressed { background-color: #1d4ed8; }

QPushButton#btn_pause {
    background-color: #1e2435;
    color: #facc15;
    border: 1px solid #2d3748;
}
QPushButton#btn_pause:hover { background-color: #2d3748; }

QPushButton#btn_resume {
    background-color: #1e2435;
    color: #4ade80;
    border: 1px solid #2d3748;
}
QPushButton#btn_resume:hover { background-color: #2d3748; }

QPushButton#btn_remove {
    background-color: #1e2435;
    color: #f87171;
    border: 1px solid #2d3748;
}
QPushButton#btn_remove:hover { background-color: #2d3748; }

QPushButton#btn_clear {
    background-color: #1e2435;
    color: #94a3b8;
    border: 1px solid #2d3748;
}
QPushButton#btn_clear:hover { background-color: #2d3748; }

QPushButton#btn_torrent {
    background-color: #1e2435;
    color: #a78bfa;
    border: 1px solid #2d3748;
}
QPushButton#btn_torrent:hover { background-color: #2d3748; }


QTableWidget {
    background-color: #0f1117;
    border: 1px solid #1a1f2e;
    gridline-color: #1a1f2e;
    border-radius: 8px;
    outline: none;
}
QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #1a1f2e;
}
QTableWidget::item:selected {
    background-color: #1e2a3a;
    color: #e2e8f0;
}
QTableView::showRow{
    border-bottom: 1px solid #1a1f2e;
}
QTableView::showColumn{
    border: 1px solid #1a1f2e;
}

QHeaderView::section {
    background-color: #1a1f2e;
    color: #64748b;
    padding: 8px 10px;
    border: none;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
}

QProgressBar {
    background-color: #1a1f2e;
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #3b82f6;
    border-radius: 3px;
}

QStatusBar {
    background-color: #0a0d14;
    color: #475569;
    border-top: 1px solid #1a1f2e;
    font-size: 11px;
    padding: 2px 10px;
}

QScrollBar:vertical {
    background: #0f1117;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #2d3748;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { 
height: 0; 
}

QMenu {
background-color: #1a1f2e;
border: 1px solid #2d3748;
border-radius: 8px;
padding: 4px;
color: #e2e8f0;
font-size: 13px;
}
QMenu::item { 
padding: 8px 20px 8px 12px; 
border-radius: 4px; 
}
QMenu::item:selected { 
background-color: #2d3748; 
}
QMenu::separator { 
height: 1px; 
background: #2d3748; 
margin: 4px 8px; 
}
QMenu::item:disabled { 
color: #475569; 
}


QTextEdit{background:transparent;border:none;font-size:13px;}
"""
