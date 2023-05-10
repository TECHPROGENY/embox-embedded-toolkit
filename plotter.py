from PyQt6.QtCore import QTimer,QTime
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QFormLayout
import pyqtgraph as pg
from random import randint
import pyqtgraph as pg


class AutoPlotter(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle('Serial Plotter')
        self.setGeometry(100, 100, 800, 600)

        # Create a plot widget
        self.plot_widget = pg.PlotWidget()

        # Create combo boxes for line colors and update interval
        self.serial_ploter_color_combo = QComboBox()
        self.serial_ploter_color_combo.addItems(['red', 'green', 'blue', 'black'])
        self.serial_ploter_time_edit = QLineEdit()
        self.serial_ploter_time_edit.setPlaceholderText("Enter time delay in (ms)")

        # Create labels for combo boxes
        self.serial_ploter_color_label = QLabel('Line Color:')
        self.serial_ploter_update_label = QLabel('Update Interval (s):')

        # Create a form layout for the widget
        self.serial_ploter_layout = QFormLayout()
        self.serial_ploter_layout.addRow(self.serial_ploter_color_label, self.serial_ploter_color_combo)
        self.serial_ploter_layout.addRow(self.serial_ploter_update_label, self.serial_ploter_time_edit)
        self.serial_ploter_layout.addRow(self.plot_widget)

        # Create a widget to hold the form layout and set it as the main window widget
        widget = QWidget()
        widget.setLayout(self.serial_ploter_layout)
        self.setCentralWidget(widget)

        self.x = [0,1]  # 100 time points
        self.y = [0,1]  # 100 data points

        # Create a line series and add it to the plot
        self.series = pg.PlotCurveItem(pen=pg.mkPen(color='r', width=1))
        self.plot_widget.addItem(self.series)

        # Set plot title and axes labels
        self.plot_widget.setTitle('Auto Plotter')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.setLabel('left', 'Value')

        # Connect combo boxes to update line color and interval
        self.serial_ploter_color_combo.currentTextChanged.connect(self.update_line_color)
        self.serial_ploter_time_edit.textChanged.connect(self.update_update_interval)

        # Set initial values for line color and update interval
        self.line_color = QColor('red')
        self.update_interval = 100

        # Set up timer to update the plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self.update_interval)

        self.elapsed_time = QTime(0, 0)

    def update_plot(self):
        self.elapsed_time = self.elapsed_time.addMSecs(self.update_interval)

        # self.x = self.x[1:]  # Remove the first y element.
        if len(self.x) > 100:
            self.x = self.x[1:]
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        if len(self.y) > 100:
            self.y = self.y[1:]  # Remove the first
        self.y.append( randint(0,100))  # Add a new random value.

        self.series.setData(self.x, self.y)  # Update the data.


    def update_line_color(self, color):
        # Update the line color based on the selected combo box value
        self.line_color = QColor(color)
        self.series.setPen(pg.mkPen(color=self.line_color, width=1))

    def update_update_interval(self, interval):
        # Update the update interval based on the selected combo box value
        self.update_interval = int(interval) * 1000
        self.timer.setInterval(self.update_interval)


if __name__ == '__main__':
    app = QApplication([])
    window = AutoPlotter()
    window.show()
    app.exec()