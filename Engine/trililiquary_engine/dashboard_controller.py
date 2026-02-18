# dashboard_breaker_panel.py

from PySide6.QtWidgets import QGridLayout, QLabel, QCheckBox
from PySide6.QtCore import Qt

def populate_dashboard_breaker_panel(ui, groupbox_name="breakerPanelGroupBox"):
    """
    Populates the Dashboard Breaker Panel with 7x9 LED grid and 9 header labels.
    """
    groupbox = getattr(ui, groupbox_name, None)
    if not groupbox:
        print(f"❌ GroupBox '{groupbox_name}' not found in UI.")
        return

    layout = QGridLayout()
    layout.setSpacing(4)

    # Create column header labels
    for col in range(9):
        label = QLabel(f"{col + 1}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label, 0, col)

    # Create 7 rows of 9 LEDs
    for row in range(1, 8):  # rows 1-7 (row 0 is headers)
        for col in range(9):
            led = QCheckBox()
            led.setObjectName(f"led_r{row}_c{col + 1}")
            led.setStyleSheet("""
                QCheckBox::indicator {
                    width: 12px;
                    height: 12px;
                }
                QCheckBox::indicator:checked {
                    background-color: #00ff00;
                    border: 1px solid #00ff00;
                }
            """)
            layout.addWidget(led, row, col)

    groupbox.setLayout(layout)
