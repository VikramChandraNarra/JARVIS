import sys
import os
import requests
from qtpy.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QLabel, QVBoxLayout, QWidget, QPushButton, QDialog
from qtpy.QtCore import QUrl, QTimer, Qt
from qtpy.QtGui import QPixmap, QImage
from qtpy.QtWebEngineWidgets import QWebEngineView
from PIL import Image
import pytesseract

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Simple Web Browser')

        self.browser = QWebEngineView()
        self.browser.urlChanged.connect(self.print_url)  # Connect urlChanged signal to print_url method
        url = QUrl('https://education.nationalgeographic.org/resource/photosynthesis/')  # Create a QUrl object from the URL string
        self.browser.setUrl(url)  # Pass the QUrl object to setUrl()

        self.setCentralWidget(self.browser)

        # Create actions for back and forward navigation
        self.back_action = QAction('Back', self)
        self.back_action.triggered.connect(self.browser.back)
        self.forward_action = QAction('Forward', self)
        self.forward_action.triggered.connect(self.browser.forward)

        # Create a toolbar and add the back and forward actions to it
        self.toolbar = QToolBar()
        self.toolbar.addAction(self.back_action)
        self.toolbar.addAction(self.forward_action)
        self.addToolBar(self.toolbar)

        # Schedule the capture of webpage screenshots
        self.capture_interval_seconds = 5  # Interval between captures in seconds
        self.num_screenshots = 10  # Number of screenshots to capture
        self.output_folder = 'screenshots'  # Output folder for saving screenshots
        self.capture_count = 0  # Initialize capture count
        self.capture_webpage_screenshots()  # Start capturing screenshots

        # Schedule the display of the image after 5 seconds
        QTimer.singleShot(5000, self.display_image_from_url)

    def print_url(self, url):
        print(f"URL changed to: {url}")

    def capture_webpage_screenshots(self):
        # Create the output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

        if self.capture_count < self.num_screenshots:
            # Disconnect the urlChanged signal temporarily
            self.browser.urlChanged.disconnect(self.print_url)

            # Capture a screenshot of the webpage
            screenshot = self.browser.grab()  # Capture the entire content of the QWebEngineView
            screenshot_path = os.path.join(self.output_folder, f'screenshot_{self.capture_count}.png')

            # Save the screenshot to the output folder
            screenshot.save(screenshot_path)

            # Print the path of the saved screenshot
            print(f'Screenshot saved: {screenshot_path}')

            # Increment the capture count
            self.capture_count += 1

            # Reconnect the urlChanged signal
            self.browser.urlChanged.connect(self.print_url)

            # Schedule the next capture
            QTimer.singleShot(self.capture_interval_seconds * 1000, self.capture_webpage_screenshots)

    def extract_text_from_screenshots(self):
        for i in range(self.num_screenshots):
            screenshot_path = os.path.join(self.output_folder, f'screenshot_{i}.png')
            if os.path.exists(screenshot_path):
                # Open the screenshot using Pillow
                screenshot = Image.open(screenshot_path)

                # Use pytesseract to extract text from the screenshot
                extracted_text = pytesseract.image_to_string(screenshot)

                # Print the extracted text
                print(f'Extracted text from {screenshot_path}:')
                print(extracted_text)
            else:
                print(f'Screenshot {screenshot_path} not found')

    def display_image_from_url(self):
        # Download the image from the URL
        image_url = "https://www.science-sparks.com/wp-content/uploads/2020/04/Photosynthesis-Diagram-1024x759.jpg"
        response = requests.get(image_url)
        if response.status_code == 200:
            # Convert the image data to a QPixmap
            image_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)

            # Create a QLabel to display the image
            image_label = QLabel()
            image_label.setPixmap(pixmap)

            # Create a dialog to show the image
            dialog = QDialog(self)
            dialog.setWindowTitle('Image Viewer')
            dialog_layout = QVBoxLayout()
            dialog_layout.addWidget(image_label)
            dialog.setLayout(dialog_layout)
            dialog.setWindowFlag(Qt.WindowStaysOnTopHint)  # Keep the dialog on top of other windows
            dialog.exec_()
        else:
            print(f"Failed to download image from {image_url}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()

    # Run the application
    app.exec_()

    # Schedule the extraction of text from screenshots after the application exits
    QTimer.singleShot(0, window.extract_text_from_screenshots)

    # Exit the application
    sys.exit(app.exec_())

