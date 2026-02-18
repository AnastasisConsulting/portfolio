# clickable_image_label.py

from PySide6.QtWidgets import QLabel, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PIL import Image
import os

class ClickableImageLabel(QLabel):
    def __init__(self, parent=None, save_folder=None):
        super().__init__(parent)
        self.save_folder = save_folder
        self.image_path = None

        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            border: 2px dashed #00aaff;
            color: #888;
            font: 9pt Consolas;
        """)
        self.setText("Click here or drag an image to upload")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_file_dialog()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.process_image(file_path)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if file_path:
            self.process_image(file_path)

    def process_image(self, file_path):
        if not self.save_folder:
            print("⚠️ No save_folder defined for image.")
            return

        os.makedirs(self.save_folder, exist_ok=True)
        dest_path = os.path.join(self.save_folder, "image.png")

        try:
            img = Image.open(file_path).resize((200, 100))
            img.save(dest_path, format="PNG")

            self.image_path = dest_path
            self.setPixmap(QPixmap(dest_path).scaled(
                self.width(),
                self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        except Exception as e:
            print(f"❌ Image processing error: {e}")
