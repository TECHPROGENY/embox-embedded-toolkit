#!/usr/bin/env python3

import sys
import logging
import re
import os
import requests

from PyQt6.QtWidgets import QApplication,QDialog, QMainWindow, QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QHBoxLayout, QStackedWidget,QCheckBox
from PyQt6.QtCore import QProcess, QTimer, QTime, QRegularExpression, QByteArray,QIODevice,QSize
from PyQt6.QtNetwork import QTcpServer, QTcpSocket, QUdpSocket, QHostAddress, QAbstractSocket
from PyQt6.QtGui import QRegularExpressionValidator,QIcon,QColor,QIntValidator,QPalette
from PyQt6 import QtSerialPort
from random import randint
import pyqtgraph as pg
import paho.mqtt.client as mqtt

from qt_material import apply_stylesheet

print(os.path.dirname(os.path.abspath(__file__)))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class serial_PopupWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.combox_stylesheet ="""
        QComboBox {
            color: cyan;
        }
        """


        self.serial_parity_combo = QComboBox()
        self.serial_parity_combo.addItems(['NONE', 'EVEN', 'ODD', 'SPACE','MARK'])
        self.serial_parity_combo.setStyleSheet(self.combox_stylesheet)
        self.serial_parity_combo.setMinimumWidth(150)

        parity_layout = QHBoxLayout()
        parity_label =QLabel("Parity")
        parity_label.setStyleSheet("color : cyan")
        parity_layout.addWidget(parity_label)
        parity_layout.addWidget(self.serial_parity_combo)

        self.serial_stopbits_combo = QComboBox()
        self.serial_stopbits_combo.addItems(['1','1.5', '2'])
        self.serial_stopbits_combo.setStyleSheet(self.combox_stylesheet)
        self.serial_stopbits_combo.setMinimumWidth(150)

        stopbits_layout = QHBoxLayout()
        stopbits_label =QLabel("Stop bits")
        stopbits_label.setStyleSheet("color : cyan")
        stopbits_layout.addWidget(stopbits_label)
        stopbits_layout.addWidget(self.serial_stopbits_combo)

        self.serial_bytesize_combo = QComboBox()
        self.serial_bytesize_combo.addItems(['5', '6', '7', '8'])
        self.serial_bytesize_combo.setStyleSheet(self.combox_stylesheet)
        self.serial_bytesize_combo.setMinimumWidth(150)

        bytesize_layout = QHBoxLayout()
        bytesize_label = QLabel("Byte size")
        bytesize_label.setStyleSheet("color : cyan")
        bytesize_layout.addWidget(bytesize_label)
        bytesize_layout.addWidget(self.serial_bytesize_combo)

        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)

        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(parity_layout)
        main_layout.addLayout(stopbits_layout)
        main_layout.addLayout(bytesize_layout)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

                # self.parity = self.serial_parity_combo.currentText()
                # self.stopbits =self.serial_stopbits_combo.currentText()
                # self.bytesize =self.serial_bytesize_combo.currentText()

    def get_settings_value(self):
        return self.serial_parity_combo.currentText() ,self.serial_stopbits_combo.currentText(),self.serial_bytesize_combo.currentText()

class QTextEditHandler(logging.Handler):
    def __init__(self, serial_console):
        super().__init__()
        self.server_console = serial_console

    def emit(self, record):
        msg = self.format(record)
        self.server_console.append(msg)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create the left side bar group box
        try:
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)

            self.qline_stylesheet = """
                QLineEdit {
                    color: cyan;
                }
            """

            self.combox_stylesheet ="""
                QComboBox {
                    color: cyan;
                }
                """

            # Create a vertical layout for the main window
            self.main_layout = QHBoxLayout()

            # Create a group box for the left sidebar
            self.left_bar_group = QGroupBox()
            self.left_bar_group_layout = QFormLayout()
            self.left_bar_group.setLayout(self.left_bar_group_layout)

            # Create buttons for the left sidebar
            self.server_button = QPushButton()
            self.server_button.setFixedSize(80,70)
            self.server_icon  = QIcon(resource_path("server2.png"))
            self.server_button.setIcon(self.server_icon)
            self.server_button.setIconSize(QSize(80,70))
            self.server_button.setObjectName('serverButton')

            self.client_button = QPushButton()
            self.client_icon  = QIcon(resource_path("client.png"))
            self.client_button.setIcon(self.client_icon)
            self.client_button.setFixedSize(80,70)
            self.client_button.setIconSize(QSize(80,70))
            self.client_button.setObjectName('clientButton')
            
            self.serial_button = QPushButton()
            self.serial_icon  = QIcon(resource_path("db89.png"))
            self.serial_button.setIcon(self.serial_icon)
            self.serial_button.setFixedSize(80,70)
            self.serial_button.setIconSize(QSize(80,70))
            self.serial_button.setObjectName('serialButton')


            # Add buttons to the left sidebar group box
            self.left_bar_group_layout.addRow(self.server_button)
            self.left_bar_group_layout.addRow(QLabel(""))
            self.left_bar_group_layout.addRow(self.client_button)
            self.left_bar_group_layout.addRow(QLabel(""))
            self.left_bar_group_layout.addRow(self.serial_button)
            self.left_bar_group_layout.addRow(QLabel(""))

            # Create a label for the right side text
            self.right_text = QLabel("This is the default text.")

            self.main_console = None
            self.serverConf()
            self.serialConf()
            self.client_conf()

            self.stacked_widget = QStackedWidget()

            # Create widgets to be displayed in the stacked widget
            self.server_widget = QLabel("Server Widget")
            self.client_widget = QLabel("Client Widget")
            self.serial_widget = QLabel("Serial Widget")
            self.network_widget = QLabel("Network Widget")
            self.security_widget = QLabel("Security Widget")
            self.about_widget = QLabel("About Widget")

            # Add widgets to the stacked widget
            self.stacked_widget.addWidget(self.server_form_widget)
            self.stacked_widget.addWidget(self.client_form_widget)
            self.stacked_widget.addWidget(self.serial_form_widget)
            self.stacked_widget.addWidget(self.network_widget)
            self.stacked_widget.addWidget(self.security_widget)
            self.stacked_widget.addWidget(self.about_widget)
            

            # Add the left sidebar and right text to the main layout
            self.main_layout.addWidget(self.left_bar_group)
            self.main_layout.addWidget(self.stacked_widget)


            # Set the main layout as the central widget
            self.central_widget.setLayout(self.main_layout)

            # Connect the buttons to their respective functions
            self.server_button.clicked.connect(self.on_serverButton_clicked)
            self.client_button.clicked.connect(self.on_clientButton_clicked)
            self.serial_button.clicked.connect(self.on_serialButton_clicked)
            
            # Set the window properties
            self.setWindowTitle("MBOX v0.1 Beta")
            self.setGeometry(100, 100, 1000, 600)
            self.show()
        except Exception as e:
            logging.exception(e)
            print(e)

    def serverConf(self):
        try:
            # Create the layout for the form
            self.server_form_widget = QWidget()
            self.server_form_layout = QFormLayout()
            self.server_form_widget.setLayout(self.server_form_layout)

            # Create the input fields for the form
            self.server_type_combo = QComboBox()
            
            self.server_type_combo.addItems(["--Select Server--","HTTP", "UDP", "TCP","MQTT"])
            self.server_type_combo.setCurrentIndex(0)
            self.server_type_combo.currentIndexChanged.connect(self.server_combo_box_changed)
            self.server_type_combo.setStyleSheet(self.combox_stylesheet)
            
            # self.server_type_combo.currentIndexChanged.connect(self.handle_server_type_change)

            self.server_port_input = QLineEdit()
            self.server_port_input.setPlaceholderText("Enter Port Number")
            self.server_port_input.setStyleSheet(self.qline_stylesheet)

            

            self.server_ip_label =QLabel("IP :")
            self.server_port_label =QLabel("Port :")

            self.server_ip_label.setStyleSheet("color : cyan")
            self.server_port_label.setStyleSheet("color : cyan")

            self.server_ip_input = QLineEdit()
            self.server_ip_input.setPlaceholderText("Enter ip address")
            self.server_ip_input.setText("127.0.0.1")
            self.server_ip_input.setStyleSheet(self.qline_stylesheet)

            self.server_address_bar = QHBoxLayout()
            self.server_address_bar.addWidget(self.server_ip_label)
            self.server_address_bar.addWidget(self.server_ip_input)
            self.server_address_bar.addWidget(self.server_port_label)
            self.server_address_bar.addWidget(self.server_port_input)


            self.server_send_data = QLineEdit()
            self.server_send_data.setPlaceholderText("Enter server response")
            self.server_send_data.returnPressed.connect(self.server_send_data_retuened)
            self.server_send_data.setStyleSheet(self.qline_stylesheet)


            server_port_regex = QRegularExpression("^[0-9]{1,5}$")
            server_ip_regex = QRegularExpression("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")

            server_port_validator = QRegularExpressionValidator(server_port_regex, self.server_port_input)
            self.server_port_input.setValidator(server_port_validator)

            server_ip_validator = QRegularExpressionValidator(server_ip_regex, self.server_ip_input)
            self.server_ip_input.setValidator(server_ip_validator)


            self.create_server_button = QPushButton("Start Server")
            self.create_server_button.clicked.connect(self.create_server)

            # Add the input fields to the form layout
            self.server_form_layout.addRow(self.server_type_combo)
            self.server_form_layout.addRow(self.server_address_bar)
            self.server_form_layout.addRow(self.server_send_data)
            self.server_form_layout.addRow(self.create_server_button)

            self.server_ip_input.setEnabled(False)
            self.server_port_input.setEnabled(False)
            self.server_send_data.setEnabled(False)
            self.create_server_button.setEnabled(False)
            # Create the log window
            self.server_console = QTextEdit()
            self.server_console.setReadOnly(True)
            self.server_form_layout.addRow(self.server_console)



            server_log_handler = QTextEditHandler(self.server_console)
            logging.getLogger().addHandler(server_log_handler)
            logging.getLogger().setLevel(logging.DEBUG)
            self.server_http_process = None
            self.server_udp_socket =None
            self.tcp_server =None
            self.broker_process =None
            self.isSERVERstarted = False
        except Exception as e:
            logging.exception(e)

    def server_combo_box_changed(self):
        try:
            selected_option = self.server_type_combo.currentText()
            if selected_option == "MQTT":
                self.server_ip_input.setText("127.0.0.1")
                self.server_ip_input.setDisabled(True)
                self.server_port_input.setDisabled(False)
                self.server_send_data.setDisabled(True)
                self.create_server_button.setDisabled(False)
                self.server_send_data.setPlaceholderText("Enter topic and data seprated by ':' eg: topic:data")
            elif selected_option == "HTTP":
                self.server_ip_input.setEnabled(True)
                self.server_port_input.setEnabled(True)
                self.server_send_data.setEnabled(True)
                self.create_server_button.setEnabled(True)
                self.server_send_data.setPlaceholderText("Enter path for files (.html,.js)")
            elif selected_option == "UDP" or selected_option == "TCP":
                self.server_ip_input.setEnabled(True)
                self.server_port_input.setEnabled(True)
                self.server_send_data.setEnabled(True)
                self.create_server_button.setEnabled(True)
                self.server_send_data.setPlaceholderText("Enter server response")
            else:
                self.server_ip_input.setEnabled(False)
                self.server_port_input.setEnabled(False)
                self.server_send_data.setEnabled(False)
                self.create_server_button.setEnabled(False)
        except Exception as e:
            logging.exception(e)

    def start_http_server(self):
        try:
        # Start HTTP server on serial_port 80
            self.cwd = None
            if self.server_send_data.text() !="":
                if not os.path.isdir(self.server_send_data.text()):
                    logging.debug(f"dir {self.server_send_data.text()} is not a dir")
                    return
                if os.path.exists(self.server_send_data.text()):
                    self.cwd =os.getcwd()
                    os.chdir(self.server_send_data.text())
                    logging.debug(f"Linking dir {self.server_send_data.text()}")
            self.server_http_process = QProcess(self)
            self.server_http_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
            self.server_http_process.readyReadStandardOutput.connect(self.http_handle_output)
            self.server_http_process.finished.connect(self.http_process_finished)
            self.server_http_process.start("python3", [ "-m", "http.server", self.server_port_input.text(), "--bind", self.server_ip_input.text()])
            self.create_server_button.setText("Stop Server")
            self.isSERVERstarted = True
        except Exception as e:
            logging.exception(e)
        
    def http_handle_output(self):
        try:
            # Log http_output from HTTP server to serial_console
            http_output = bytes(self.server_http_process.readAllStandardOutput()).decode()
            logging.debug(http_output)
        except Exception as e:
            logging.exception(e)

    def http_process_finished(self):
        try:
            # Destroy server_http_process and print message when finished
            self.server_http_process.terminate()
            self.server_http_process.waitForFinished()
            # logging.debug("HTTP server stopped")
            self.isSERVERstarted = False
            if self.cwd is not None :os.chdir(self.cwd)
        except Exception as e:
            logging.exception(e)

    def start_tcp_server(self):
        try:
            self.tcp_server = QTcpServer(self)
            self.tcp_server.listen(QHostAddress(self.server_ip_input.text()), int(self.server_port_input.text()))  # Listen on localhost, port 5000
            self.tcp_server.newConnection.connect(self.tcp_server_handle_connection)
        except Exception as e:
            logging.exception(e)



    def tcp_receive_data(self):
        try:
            tcp_client_socket = self.sender()
            tcp_message = tcp_client_socket.readAll().data().decode('utf-8')
            self.server_console.append(f'Received message: {tcp_message} from {tcp_client_socket.peerAddress().toString()}:{tcp_client_socket.peerPort()}')
            tcp_client_socket.write(self.server_send_data.text().encode())
        except Exception as e:
            logging.exception(e)

    def tcp_client_disconnected(self):
        try:
            tcp_client_socket = self.sender()
            self.server_console.append(f'Client disconnected: {tcp_client_socket.peerAddress().toString()}:{tcp_client_socket.peerPort()}')
            tcp_client_socket.deleteLater()
        except Exception as e:
            logging.exception(e)

    def start_udp_server(self):
        try:
            self.server_udp_socket = QUdpSocket(self)
            self.server_udp_socket.bind(QHostAddress(self.server_ip_input.text()),int(self.server_port_input.text()))  # Bind to port
            self.server_udp_socket.readyRead.connect(self.udp_receive_data)
        except Exception as e:
            logging.exception(e)
    
    def udp_receive_data(self):
        try:
            while self.server_udp_socket.hasPendingDatagrams():
                server_udp_datagram, server_udp_host, server_udp_port = self.server_udp_socket.readDatagram(self.server_udp_socket.pendingDatagramSize())
                server_udp_message = bytes(server_udp_datagram).decode('utf-8')
                self.server_console.append(f'Received message: {server_udp_message} from {server_udp_host.toString()}:{server_udp_port}')
            self.server_udp_socket.writeDatagram(self.server_send_data.text().encode(), QHostAddress(server_udp_host), int(server_udp_port))
        except Exception as e:
            logging.exception(e)

    def tcp_server_handle_connection(self):
        try:
            while self.tcp_server.hasPendingConnections():
                tcp_server_client_socket = self.tcp_server.nextPendingConnection()
                self.server_console.append(f'Client Connected: {tcp_server_client_socket.peerAddress().toString()}:{tcp_server_client_socket.peerPort()}')
                tcp_server_client_socket.readyRead.connect(self.tcp_receive_data)
                tcp_server_client_socket.disconnected.connect(self.tcp_client_disconnected)
        except Exception as e:
            logging.exception(e)

    def server_send_data_retuened(self):
        if self.server_type_combo.currentText() == "MQTT" and self.isSERVERstarted:
            print("Hi mqtt")
            if self.broker_process.state() != QProcess.ProcessState.Running:
                self.server_console.append("Broker is not running please start the server")
                return
            if ":" not in self.server_send_data.text():
                self.server_console.append("Wrong data type secified it should be in the format topic:data")
                return
            self._broker_started()
            mqtt_topic,mqtt_data =  self.server_send_data.text().split(":")
            try:
                self.mqtt_server_client.publish(mqtt_topic,mqtt_data)
                self.server_console.append(f"Published {mqtt_data} to topic {mqtt_topic}")
                self.mqtt_server_client.disconnect()
            except Exception as e:
                self.server_console.append(e)

    def create_server(self):
        try:
            if self.isSERVERstarted == False:
                if self.server_type_combo.currentText() == "--Select Server--" or self.server_ip_input.text() =="" or self.server_port_input.text() =="":
                    self.server_console.append("Please check your configuration")
                    return
                if self.server_type_combo.currentText() == "HTTP":
                    print("Http")
                    self.start_http_server()
                    if self.server_http_process:
                        self.server_type_combo.setDisabled(True)
                        self.server_ip_input.setDisabled(True)
                        self.server_port_input.setDisabled(True)
                        self.server_send_data.setDisabled(True)
                        self.server_console.append(f"{self.server_type_combo.currentText()} Server created on {self.server_ip_input.text()}:{self.server_port_input.text()}")
                        return
                    self.server_console.append(f"Failed to create {self.server_type_combo.currentText()} Server on {self.server_ip_input.text()}:{self.server_port_input.text()}")

                    
                elif self.server_type_combo.currentText() == "TCP":
                    print("TCP")
                    self.start_tcp_server()
                    if self.tcp_server:
                        self.isSERVERstarted = True
                        self.server_type_combo.setDisabled(True)
                        self.server_ip_input.setDisabled(True)
                        self.server_port_input.setDisabled(True)
                        self.create_server_button.setText("Stop Server")
                        self.server_console.append(f"{self.server_type_combo.currentText()} Server created on {self.server_ip_input.text()}:{self.server_port_input.text()}")
                    
                elif self.server_type_combo.currentText() == "UDP":
                    print("UDP")
                    self.start_udp_server()
                    if self.server_udp_socket:
                        self.isSERVERstarted = True
                        self.server_type_combo.setDisabled(True)
                        self.server_ip_input.setDisabled(True)
                        self.server_port_input.setDisabled(True)
                        self.create_server_button.setText("Stop Server")
                        self.server_console.append(f"{self.server_type_combo.currentText()} Server created on {self.server_ip_input.text()}:{self.server_port_input.text()}")


                elif self.server_type_combo.currentText() == "MQTT":
                    self.server_type_combo.setDisabled(True)
                    self.server_ip_input.setDisabled(True)
                    self.server_port_input.setDisabled(True)
                    self.server_send_data.setDisabled(True)
                    self.broker_process = QProcess(self)
                    self.broker_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
                    self.broker_process.readyReadStandardOutput.connect(self.broker_process_output)
                    self.broker_process.finished.connect(self.broker_process_finished)
                    self.broker_process.start("mosquitto", [ "-p", self.server_port_input.text()])

                else:
                    self.server_console.append("Please select a server type")

            else:
                if self.server_http_process:
                    self.server_http_process.terminate()
                    self.server_http_process.waitForFinished()
                    self.isSERVERstarted = False
                    self.server_type_combo.setDisabled(False)
                    self.server_ip_input.setDisabled(False)
                    self.server_port_input.setDisabled(False)
                    self.server_send_data.setDisabled(False)
                    self.server_http_process = None
                elif self.server_udp_socket:
                    self.server_udp_socket.deleteLater()
                    self.server_type_combo.setDisabled(False)
                    self.server_ip_input.setDisabled(False)
                    self.server_port_input.setDisabled(False)
                    self.server_send_data.setDisabled(True)
                    self.server_udp_socket = None
                elif self.tcp_server:
                    self.tcp_server.deleteLater()
                    self.server_type_combo.setDisabled(False)
                    self.server_ip_input.setDisabled(False)
                    self.server_port_input.setDisabled(False)
                    self.server_send_data.setDisabled(True)
                    self.tcp_server = None
                    
                elif self.broker_process:
                    # self.mqtt_server_client.disconnect()
                    self.broker_process.terminate()
                    self.broker_process.waitForFinished()
                    self.server_type_combo.setDisabled(False)
                    self.server_ip_input.setDisabled(True)
                    self.server_port_input.setDisabled(False)
                    self.server_send_data.setDisabled(True)
                else:
                    return
                self.isSERVERstarted = False
                self.create_server_button.setText("Sart Server")
                self.server_console.append(f"{self.server_type_combo.currentText()} Server Stoped!")

        except Exception as e:
            logging.exception(e)

    def _broker_started(self):
        
        self.mqtt_server_client = mqtt.Client()
        self.mqtt_server_client.connect("127.0.0.1",int(self.server_port_input.text()))
        self.isSERVERstarted = True
        

    def on_serverButton_clicked(self):
        #hellp
        try:
            self.stacked_widget.setCurrentWidget(self.server_form_widget)
            server_log_handler = QTextEditHandler(self.server_console)
            logging.getLogger().addHandler(server_log_handler)
            logging.getLogger().setLevel(logging.DEBUG)
            
        except Exception as e:
            logging.exception(e)
    
    def broker_process_output(self):
        broker_output = bytes(self.broker_process.readAllStandardOutput()).decode()
        self.server_console.append(broker_output)
        if re.search(r"mosquitto version .* running", broker_output):
            self.server_send_data.setDisabled(False)
            self.server_console.append("Created mosquitto broker")
            self.server_console.append("enter topic:data on the response filed above and press enter to publish")
            self.create_server_button.setText("Stop Server")
            self.isSERVERstarted = True
            # self._broker_started()
        if re.search(r"Error", broker_output):
            self.server_console.append("Failed to create mosquitto broker")
            self.create_server_button.setText("Start Server")
            self.server_send_data.setDisabled(True)
            self.server_type_combo.setDisabled(False)
            self.server_port_input.setDisabled(False)
            self.isSERVERstarted = False

            

    def broker_process_finished(self):
        self.broker_process.terminate()
        self.broker_process.waitForFinished()

        
    
    def on_clientButton_clicked(self):
        try:
            self.stacked_widget.setCurrentWidget(self.client_form_widget)
            client_log_handler = QTextEditHandler(self.client_console)
            logging.getLogger().addHandler(client_log_handler)
            logging.getLogger().setLevel(logging.DEBUG)
        except Exception as e:
            logging.exception(e)
    
    def on_serialButton_clicked(self):
        try:
            self.stacked_widget.setCurrentWidget(self.serial_form_widget)
            seraial_log_handler = QTextEditHandler(self.serial_console)
            logging.getLogger().addHandler(seraial_log_handler)
            logging.getLogger().setLevel(logging.DEBUG)
        except Exception as e:
            logging.exception(e)




    def serialConf(self):
        try:
            self.serial_form_widget = QWidget()
            self.serial_form_layout = QFormLayout()

            self.serial_orgnise = QHBoxLayout()
            self.serial_form_widget.setLayout(self.serial_form_layout)
            self.serial_port_combo = QComboBox()
            self.serial_port_combo.setStyleSheet(self.combox_stylesheet)

            serialPortInfos = QtSerialPort.QSerialPortInfo.availablePorts()
            serial_ports = [p.portName() for p in serialPortInfos]
            self.serial_port_combo.addItems(serial_ports)
            self.serial_port_combo.setCurrentIndex(0)

            self.serial_baudrate_combo = QComboBox()
            self.serial_baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
            self.serial_port_combo.setCurrentIndex(0)
            self.serial_baudrate_combo.setStyleSheet(self.combox_stylesheet)

            self.lineending_combobox = QComboBox()
            self.lineending_combobox.addItems(['NONE', 'NL', 'CR', 'NL & CR'])
            self.lineending_combobox.currentIndexChanged.connect(self.handle_lineending_change)
            self.lineending_combobox.setStyleSheet(self.combox_stylesheet)


            self.serial_connect_button = QPushButton("Connect")
            self.serial_connect_button.clicked.connect(self.connect_or_disconnect)

            self.serial_clear_button = QPushButton('Clear')
            self.serial_clear_button.clicked.connect(self.clear_console)

            self.serial_filter_button = QPushButton('Filter')
            self.serial_filter_button.clicked.connect(self.filter_console)

            self.serial_settings_button = QPushButton("Settings")
            self.serial_settings_button.clicked.connect(self.serial_show_popup)

            self.serial_ploter_button = QPushButton("Plotter", self)
            self.serial_ploter_button.clicked.connect(self.serial_ploter_open_window)

            self.serial_ploter_button.setDisabled(True)

            # Create a QLineEdit widget for entering filter serial_pattern
            self.serial_filter_pattern = QLineEdit()
            self.serial_filter_pattern.setPlaceholderText('Enter filter serial_pattern')
            self.serial_filter_pattern.setStyleSheet(self.qline_stylesheet)

            # self.filter_layout = QHBoxLayout()
            # self.filter_layout.addWidget(self.serial_filter_pattern)
            # self.filter_layout.addWidget(self.serial_filter_button)

            self.serial_console = QTextEdit()
            self.serial_console.setReadOnly(True)


            self.serial_send_input = QLineEdit()
            self.serial_send_input.returnPressed.connect(self.serial_send_data)
            self.serial_send_input.setStyleSheet(self.qline_stylesheet)
            
            self.serial_send_button = QPushButton("Send")
            self.serial_send_button.clicked.connect(self.serial_send_data)


            # self.serial_form_layout.addRow(QLabel("Port:"), self.serial_port_combo)
            # self.serial_form_layout.addRow(QLabel("Baudrate:"), self.serial_baudrate_combo)


            # self.serial_form_layout.addRow(self.serial_clear_button, self.serial_connect_button)
            
            # self.serial_form_layout.addRow(self.serial_filter_pattern, self.serial_filter_button)

            self.autoscroll_checkbox = QCheckBox()
            self.autoscroll_checkbox.setChecked(True)
            self.autoscroll_checkbox.stateChanged.connect(self.handle_autoscroll_change)

            serial_device_label =QLabel("Device:")
            serial_device_label.setStyleSheet("color : cyan")

            serial_baud_label =QLabel("Baud:")
            serial_baud_label.setStyleSheet("color : cyan")

            serial_lineencoding_label =QLabel("Line Encoding:")
            serial_lineencoding_label.setStyleSheet("color : cyan")

            serial_enableautoscroll_label =QLabel('Enable Autoscroll')
            serial_enableautoscroll_label.setStyleSheet("color : cyan")

            self.serial_port_combo.setMinimumWidth(150)
            self.serial_baudrate_combo.setMinimumWidth(150)
            self.lineending_combobox.setMinimumWidth(150)
            
            self.serial_orgnise.addWidget(serial_device_label)
            self.serial_orgnise.addWidget(self.serial_port_combo)
            self.serial_orgnise.addWidget(serial_baud_label)
            self.serial_orgnise.addWidget(self.serial_baudrate_combo)
            self.serial_orgnise.addWidget(serial_lineencoding_label)
            self.serial_orgnise.addWidget(self.lineending_combobox)
            self.serial_orgnise.addWidget(self.autoscroll_checkbox)
            self.serial_orgnise.addWidget(serial_enableautoscroll_label)
            self.serial_orgnise.addWidget(self.serial_connect_button)
            self.serial_orgnise.addWidget(self.serial_clear_button)
            self.serial_orgnise.addWidget(self.serial_settings_button)
            self.serial_orgnise.addWidget(self.serial_ploter_button)
            


            self.serial_form_layout.addRow(self.serial_orgnise)
            self.serial_form_layout.addRow(self.serial_filter_pattern)
            self.serial_form_layout.addRow(self.serial_console)


            self.serial_send_layout = QHBoxLayout()
            self.serial_send_layout.addWidget(self.serial_send_input)
            self.serial_send_layout.addWidget(self.serial_send_button)

            self.serial_form_layout.addRow(self.serial_send_layout)

            self.serial = None
            self.serial_connected = False
            self.serial_line_end = b''
            self.serial_console_stop_scroll = False
            self.serial_scrollbar =self.serial_console.verticalScrollBar()
            self.serial_scroll_pos = self.serial_scrollbar.value()


            self.serial_p_timer =QTimer()
            self.serial_p_timer.timeout.connect(self.refresh_ports)
            self.serial_p_timer.start(1000)

            self.parity = QtSerialPort.QSerialPort.Parity.NoParity
            self.stopbits =QtSerialPort.QSerialPort.StopBits.OneStop
            self.bytesize =QtSerialPort.QSerialPort.DataBits.Data8

            self.parity_dict = {'NONE': QtSerialPort.QSerialPort.Parity.NoParity, 'ODD': QtSerialPort.QSerialPort.Parity.OddParity, 'EVEN': QtSerialPort.QSerialPort.Parity.EvenParity,'MARK': QtSerialPort.QSerialPort.Parity.MarkParity,'SPACE': QtSerialPort.QSerialPort.Parity.SpaceParity}
            self.stopbits_dict = {'1':QtSerialPort.QSerialPort.StopBits.OneStop,'1.5':QtSerialPort.QSerialPort.StopBits.OneAndHalfStop,'2':QtSerialPort.QSerialPort.StopBits.TwoStop}
            self.bytesize_dict = {'5':QtSerialPort.QSerialPort.DataBits.Data5,'6':QtSerialPort.QSerialPort.DataBits.Data6,'7':QtSerialPort.QSerialPort.DataBits.Data7,'8':QtSerialPort.QSerialPort.DataBits.Data8}

        except Exception as e:
            logging.exception(e)


    def serial_show_popup(self):
        popup = serial_PopupWindow(self)
        if popup.exec() == 1:
            parity,stopbits,bytesize = popup.get_settings_value()
            self.parity =self.parity_dict[parity]
            self.stopbits = self.stopbits_dict[stopbits]
            self.bytesize =self.bytesize_dict[bytesize]
        else:
            print("Cancel button clicked")
    
    def handle_lineending_change(self, index):
        if index == 0:
            self.serial_line_end =b''
        elif index == 1:
            self.serial_line_end =b'\n'
        elif index == 2:
            self.serial_line_end =b'\r'
        elif index == 3:
            self.serial_line_end =b'\n\r'
            
    def handle_autoscroll_change(self, state):
        if state == 2:
            self.serial_console_stop_scroll = False
            self.serial_scrollbar =self.serial_console.verticalScrollBar()
            self.serial_scroll_pos = self.serial_scrollbar.value()
        else:
            self.serial_console_stop_scroll = True

    def refresh_ports(self):
        try:
            serialPortInfos = QtSerialPort.QSerialPortInfo.availablePorts()
            serial_ports = [p.portName() for p in serialPortInfos]
            self.serial_port_combo.clear()
            self.serial_port_combo.addItems(serial_ports)
            # time.sleep(1)
        except Exception as e:
            logging.exception(e)

    def connect_or_disconnect(self):
        try:
            if not self.serial_connected:
                self.serial_p_timer.stop()
                serial_port = self.serial_port_combo.currentText()
                baudrate = self.serial_baudrate_combo.currentText()
                self.serial_console.append(f'Connecting to {serial_port} with baudrate {baudrate} parity {self.parity} stop bits {self.stopbits} Data bits {self.bytesize}')
                self.serial_port = QtSerialPort.QSerialPort()
                self.serial_port.setPortName(serial_port)
                self.serial_port.setBaudRate(int(baudrate))
                self.serial_port.setDataBits(self.bytesize)
                self.serial_port.setParity(self.parity)
                self.serial_port.setStopBits(self.stopbits)
                self.serial_port.readyRead.connect(self.read_serial)
                # self.serial_port.errorOccurred.connect(self.handle_error)
                if not self.serial_port.open(QIODevice.OpenModeFlag.ReadWrite):
                    self.serial_console.append("Error", f"Could not open serial port {self.serial_port.portName()}")
                    return
                
                self.serial_connect_button.setText("Disconnect")
                self.serial_settings_button.setDisabled(True)
                self.serial_port_combo.setDisabled(True)
                self.serial_baudrate_combo.setDisabled(True)
                self.serial_ploter_button.setDisabled(False)
                self.serial_connected = True



            else:
                self.serial_port.close()
                self.serial_port=None
                self.serial_connect_button.setText("Connect")
                self.serial_settings_button.setDisabled(False)
                self.serial_port_combo.setDisabled(False)
                self.serial_baudrate_combo.setDisabled(False)
                self.serial_ploter_button.setDisabled(True)
                self.serial_connected = False
                self.serial_p_timer.start()
                print("port start")
        except Exception as e:
            logging.exception(e)



    def serial_send_data(self):
        try:
            data = self.serial_send_input.text()
            self.serial_port.write(data.encode())
            self.serial_port.write(self.serial_line_end)
            self.serial_send_input.clear()
        except Exception as e:
            logging.exception(e)

   

    def read_serial(self):
        try:
            self.serial_data = self.serial_port.readAll().data().decode()
            serial_pattern = self.serial_filter_pattern.text()
            if serial_pattern:
                serial_pattern = f'.*{serial_pattern}.*'  # Add .* at the beginning and end to match anywhere in the line
                if re.search(serial_pattern, self.serial_data):
                    self.serial_console.append(self.serial_data)
            else:
                self.serial_console.append(self.serial_data)

            if self.serial_console_stop_scroll:
                self.serial_scrollbar.setValue(self.serial_scroll_pos)
        except Exception as e:
            self.serial_console.append(f"Error Occured {e}")
            logging.exception(e)
            # self.connect_or_disconnect()

    def clear_console(self):
        try:
            self.serial_console.clear()
        except Exception as e:
            logging.exception(e)
    
    def filter_console(self):
        try:
            # Filter serial_console based on entered serial_pattern
            serial_pattern = self.serial_filter_pattern.text()
            if serial_pattern:
                serial_pattern = f'.*{serial_pattern}.*'  # Add .* at the beginning and end to match anywhere in the line
                serial_filtered_text = self.serial_console.toPlainText()
                serial_filtered_lines = []
                for line in serial_filtered_text.split('\n'):
                    if re.search(serial_pattern, line):
                        serial_filtered_lines.append(line)
                serial_filtered_text = '\n'.join(serial_filtered_lines)
                self.serial_console.setPlainText(serial_filtered_text)
        except Exception as e:
            logging.exception(e)



    def serial_ploter_open_window(self):
        self.serial_ploter_popup = QDialog(self)
        self.serial_ploter_popup.setWindowTitle('Serial Plotter')
        self.ploter_started =False
        
        self.serial_ploter_widget = pg.PlotWidget()

        # Create combo boxes for line colors and update interval
        self.serial_ploter_color_combo = QComboBox()
        self.serial_ploter_color_combo.addItems(['red', 'green', 'blue', 'black'])
        self.serial_ploter_color_combo.setStyleSheet(self.combox_stylesheet)
        self.serial_ploter_time_edit = QLineEdit()
        self.serial_ploter_time_edit.setStyleSheet(self.qline_stylesheet)
        self.serial_ploter_time_edit.setPlaceholderText("Enter time delay in (ms)")
        self.serial_ploter_time_edit.setValidator(QIntValidator())

        self.ploter_start_button = QPushButton("Start")
        self.ploter_start_button.clicked.connect(self.ploter_start_ploting)

        # Create labels for combo boxes
        self.serial_ploter_color_label = QLabel('Line Color:')
        self.serial_ploter_color_label.setStyleSheet("color : cyan")
        self.serial_ploter_update_label = QLabel('Update Interval (s):')
        self.serial_ploter_update_label.setStyleSheet("color : cyan")

        self.serial_ploter_layout_organise = QHBoxLayout()
        self.serial_ploter_layout_organise.addWidget(self.serial_ploter_color_label)
        self.serial_ploter_layout_organise.addWidget(self.serial_ploter_color_combo)
        self.serial_ploter_layout_organise.addWidget(self.serial_ploter_update_label)
        self.serial_ploter_layout_organise.addWidget(self.serial_ploter_time_edit)
        self.serial_ploter_layout_organise.addWidget(self.ploter_start_button)
        # self.serial_ploter_layout_organise.addWidget(self.serial_ploter_widget)

        # Create a form layout for the widget
        self.serial_ploter_layout = QFormLayout()
        # self.serial_ploter_layout.addRow(self.serial_ploter_color_label, self.serial_ploter_color_combo)
        # self.serial_ploter_layout.addRow(self.serial_ploter_update_label, self.serial_ploter_time_edit)
        self.serial_ploter_layout.addRow(self.serial_ploter_layout_organise)
        self.serial_ploter_layout.addRow(self.serial_ploter_widget)


        self.serial_ploter_x = [0,1]  # 100 time points
        self.serial_ploter_y = [0,1]  # 100 data points

        # Create a line series and add it to the plot
        self.serial_ploter_line = pg.PlotCurveItem(pen=pg.mkPen(color='r', width=1))
        self.serial_ploter_widget.addItem(self.serial_ploter_line)

        # Set plot title and axes labels
        self.serial_ploter_widget.setTitle('Auto Plotter')
        self.serial_ploter_widget.setLabel('bottom', 'Time', units='s')
        self.serial_ploter_widget.setLabel('left', 'Value')

        # Connect combo boxes to update line color and interval
        self.serial_ploter_color_combo.currentTextChanged.connect(self.update_line_color)
        self.serial_ploter_time_edit.textChanged.connect(self.update_update_interval)

        # Set initial values for line color and update interval
        self.serial_ploter_line_colour = QColor('red')
        self.serial_ploter_update_interval = 100

        # Set up timer to update the plot
        self.serial_ploter_triger_timer = QTimer()
        self.serial_ploter_triger_timer.timeout.connect(self.serial_ploter_update_plot)
        

        self.serial_ploter_elapsed_time = QTime(0, 0)


        self.serial_ploter_popup.setLayout(self.serial_ploter_layout)
        
        self.serial_ploter_popup.finished.connect(self.serial_ploter_handle_popup_closed)
        self.serial_ploter_popup.exec()
    
    def ploter_start_ploting(self):
        if not self.ploter_started:
            if self.serial_ploter_time_edit.text() != "":
                self.serial_ploter_update_interval = int(self.serial_ploter_time_edit.text())
            else:
                self.serial_ploter_update_interval = 100
            self.serial_ploter_triger_timer.start(self.serial_ploter_update_interval)
            self.ploter_start_button.setText("Stop")
            self.serial_ploter_time_edit.setDisabled(True)
            self.ploter_started = True
            return
        self.ploter_start_button.setText("Start")
        self.serial_ploter_triger_timer.stop()
        self.serial_ploter_time_edit.setDisabled(False)
        self.ploter_started =False




    def serial_ploter_handle_popup_closed(self, result):
        self.serial_ploter_triger_timer.stop()
        print("Closed")

    def serial_ploter_update_plot(self):
        self.serial_ploter_elapsed_time = self.serial_ploter_elapsed_time.addMSecs(self.serial_ploter_update_interval)

        # self.serial_ploter_x = self.serial_ploter_x[1:]  # Remove the first y element.
        if len(self.serial_ploter_x) > 100:
            self.serial_ploter_x = self.serial_ploter_x[1:]
        self.serial_ploter_x.append(self.serial_ploter_x[-1] + 1)  # Add a new value 1 higher than the last.

        if len(self.serial_ploter_y) > 100:
            self.serial_ploter_y = self.serial_ploter_y[1:]  # Remove the first
        if "MPLOT:" in self.serial_data:
            self.serial_ploter_y.append( int(self.serial_data.strip("MPLOT:")))  # Add a new random value.
        else:
            self.serial_ploter_y.append(0)

        self.serial_ploter_line.setData(self.serial_ploter_x, self.serial_ploter_y)  # Update the data.


    def update_line_color(self, color):
        # Update the line color based on the selected combo box value
        self.serial_ploter_line_colour = QColor(color)
        self.serial_ploter_line.setPen(pg.mkPen(color=self.serial_ploter_line_colour, width=1))

    def update_update_interval(self, interval):
        # Update the update interval based on the selected combo box value
        self.serial_ploter_update_interval = int(interval) * 1000
        self.serial_ploter_triger_timer.setInterval(self.serial_ploter_update_interval)






    def client_conf(self):
        try:

            self.client_protocol_combobox = QComboBox()
            self.client_protocol_combobox.addItem('Select')
            self.client_protocol_combobox.addItem('HTTP')
            self.client_protocol_combobox.addItem('UDP')
            self.client_protocol_combobox.addItem('TCP')
            self.client_protocol_combobox.addItem('MQTT')
            self.client_protocol_combobox.setMinimumWidth(150)
            self.client_protocol_combobox.setStyleSheet(self.combox_stylesheet)
            self.client_protocol_combobox.activated.connect(self.on_client_combo_box_activated)


            self.client_ip_edit = QLineEdit()
            self.client_ip_edit.setStyleSheet(self.qline_stylesheet)
            self.client_ip_edit.setPlaceholderText("IP Address")
            self.client_port_edit = QLineEdit()
            self.client_port_edit.setPlaceholderText("PORT")
            self.client_port_edit.setStyleSheet(self.qline_stylesheet)

            client_ip_regex = QRegularExpression("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
            client_port_regex = QRegularExpression("^[0-9]{1,5}$")

            client_ip_validator = QRegularExpressionValidator(client_ip_regex, self.client_ip_edit)
            self.client_ip_edit.setValidator(client_ip_validator)

            client_port_validator = QRegularExpressionValidator(client_port_regex, self.client_port_edit)
            self.client_port_edit.setValidator(client_port_validator)

            self.client_connect_button = QPushButton('Connect')
            self.client_connect_button.clicked.connect(self.client_connect_to_server)
            self.client_connect_button.setDisabled(True)

            self.client_send_edit = QLineEdit()
            self.client_send_edit.setDisabled(True)
            self.client_send_edit.setStyleSheet(self.qline_stylesheet)

            self.client_send_button = QPushButton('Send')
            self.client_send_button.clicked.connect(self.client_send_data)
            self.client_send_button.setDisabled(True)

            self.client_console = QTextEdit()
            self.client_console.setReadOnly(True)

            self.client_link_layout = QHBoxLayout()
            self.client_link_layout.addWidget(self.client_protocol_combobox)
            # self.client_link_layout.addWidget(QLabel("IP :"))
            self.client_link_layout.addWidget(self.client_ip_edit)
            colon_label =QLabel(":")
            colon_label.setStyleSheet("color : cyan")
            
            self.client_link_layout.addWidget(colon_label)
            self.client_link_layout.addWidget(self.client_port_edit)
            self.client_link_layout.addWidget(self.client_connect_button)

            # Set up client_layout
            self.client_layout = QFormLayout()

            self.client_form_widget = QWidget()
            self.client_form_widget.setLayout(self.client_layout)
            self.client_send_label = QLabel("Send :")
            self.client_send_label.setStyleSheet("color : cyan")

            # self.client_layout.addRow('Protocol:', self.client_protocol_combobox)
            self.client_layout.addRow(self.client_link_layout)
            # self.client_layout.addRow(self.client_connect_button)
            self.client_layout.addRow(self.client_send_label, self.client_send_edit)
            self.client_layout.addRow(self.client_send_button)
            self.client_layout.addRow(self.client_console)
            self.client_socket = None
            self.mqtt_client = None
        except Exception as e:
            logging.exception(e)

    def client_connect_to_server(self):
        try:
            client_protocol = self.client_protocol_combobox.currentText()

            if client_protocol =="HTTP":
                self.client_send_button.setDisabled(False)
                if  self.client_connect_button.text() == "GET":
                    self.client_connect_button.setText("POST")
                    self.client_send_edit.setDisabled(False)
                    return
                if  self.client_connect_button.text() == "POST":
                    self.client_connect_button.setText("PUT")
                    self.client_send_edit.setDisabled(False)
                    return
                if  self.client_connect_button.text() == "PUT":
                    self.client_connect_button.setText("DELETE")
                    self.client_send_edit.setDisabled(True)
                    return
                else:
                    self.client_connect_button.setText("GET")
                    self.client_send_edit.setDisabled(True)
                    return
                
            if self.client_socket is not None: 
                if self.client_socket.isOpen():
                    self.client_socket.close()
                self.client_socket = None
                self.client_connect_button.setText("Connect")
                self.client_protocol_combobox.setDisabled(False)
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
                self.client_ip_edit.setDisabled(False)
                self.client_port_edit.setDisabled(False)
                return

            if client_protocol == 'UDP':
                self.client_socket = QUdpSocket(self)
                self.client_socket.readyRead.connect(self.client_receive_data)
                self.client_socket.errorOccurred.connect(self.client_socket_display_error)
                if self.client_socket is not None:
                    self.client_send_edit.setDisabled(False)
                    self.client_send_button.setDisabled(False)
                    self.client_ip_edit.setDisabled(True)
                    self.client_port_edit.setDisabled(True)
                    self.client_protocol_combobox.setDisabled(True)
                    self.client_connect_button.setText("Disconnect")
                    return
                else:
                    self.log_message('Error: Creating the socket.')
                    self.client_send_edit.setDisabled(True)
                    self.client_send_button.setDisabled(True)
                    self.client_ip_edit.setDisabled(False)
                    self.client_port_edit.setDisabled(False)
                    self.client_socket =None
                    return

            elif client_protocol == 'TCP':
                if self.client_ip_edit.text() != "" and self.client_port_edit.text() != "":
                    self.client_url = self.client_ip_edit.text()
                    self.client_port = int(self.client_port_edit.text())
                    self.log_message(f'GOT {self.client_url} {self.client_port}')
                else:
                    self.log_message('Error: Check your IP and PORT number.')
                    self.client_send_edit.setDisabled(True)
                    self.client_send_button.setDisabled(True)
                    return
                self.client_socket = QTcpSocket()
                self.client_socket.readyRead.connect(self.client_receive_data)
                self.client_socket.errorOccurred.connect(self.client_socket_display_error)
                self.client_socket.connectToHost(self.client_url, self.client_port)
                if self.client_socket is not None and self.client_socket.isOpen():
                    self.client_send_edit.setDisabled(False)
                    self.client_send_button.setDisabled(False)
                    self.client_protocol_combobox.setDisabled(True)
                    self.client_ip_edit.setDisabled(True)
                    self.client_port_edit.setDisabled(True)
                    self.client_connect_button.setText("Disconnect")
                    return
                else:
                    self.log_message('Error: Creating the socket.')
                    self.client_send_edit.setDisabled(True)
                    self.client_send_button.setDisabled(True)
                    self.client_socket =None
                    self.client_ip_edit.setDisabled(False)
                    self.client_port_edit.setDisabled(False)
                    return
            elif client_protocol == 'MQTT':
                if self.mqtt_client == None:
                    if self.client_ip_edit.text() != "" and self.client_port_edit.text() != "":
                        self.client_url = self.client_ip_edit.text()
                        self.client_port = int(self.client_port_edit.text())
                        self.log_message(f'GOT {self.client_url} {self.client_port}')
                    else:
                        self.log_message('Error: Check your IP and PORT number.')
                        self.client_send_edit.setDisabled(True)
                        self.client_send_button.setDisabled(True)
                        return
                    self.mqtt_client = mqtt.Client()
                    self.mqtt_client.on_connect = self.on_connect
                    self.mqtt_client.on_message = self.on_message
                    self.mqtt_client.connect(self.client_url,port=self.client_port)
                    self.mqtt_client.loop_start()
                    if not self.mqtt_client == None:
                        self.client_send_edit.setDisabled(False)
                        self.client_send_button.setDisabled(False)
                        self.client_protocol_combobox.setDisabled(True)
                        self.client_ip_edit.setDisabled(True)
                        self.client_port_edit.setDisabled(True)
                        self.client_connect_button.setText("Disconnect")
                        return
                
                self.client_connect_button.setText("Connect")
                self.client_protocol_combobox.setDisabled(False)
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
                self.client_ip_edit.setDisabled(False)
                self.client_port_edit.setDisabled(False)


        except Exception as e:
            logging.exception(e)
    def on_connect(self, client, userdata, flags, rc):
        self.log_message(f"Connected with result code {str(rc)}")

    def on_message(self, client, userdata, message):
        self.log_message(f"Received message '{str(message.payload)}' on topic '{message.topic}'")

    def client_send_data(self):
        try:
            print("send button clicked")
            if self.client_ip_edit.text() != "" and self.client_port_edit.text() != "":
                self.client_url = self.client_ip_edit.text()
                self.client_port = int(self.client_port_edit.text())
                self.log_message(f'GOT {self.client_url} {self.client_port}')
            else:
                self.log_message('Error: Check your IP and PORT number.')
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
                return
            if self.client_protocol_combobox.currentText() == 'UDP':
                print("UDP")
                client_message = self.client_send_edit.text().encode()
                self.client_socket.writeDatagram(client_message, QHostAddress(self.client_url), self.client_port)

            elif self.client_protocol_combobox.currentText() == 'TCP':
                if self.client_socket is None or not self.client_socket.isOpen():
                    self.log_message('Error: Socket is not connected.')
                    return
                client_message = self.client_send_edit.text().encode()
                self.client_socket.write(QByteArray(client_message))
                self.client_socket.flush()
            elif self.client_protocol_combobox.currentText() == 'HTTP':
                print(f"send button clicked for htt with {self.client_connect_button.text()}")
                if self.client_connect_button.text() == "GET":
                    self.client_http_get_request()
                elif self.client_connect_button.text() == "POST":
                    self.client_http_post_request()
                elif self.client_connect_button.text() == "PUT":
                    self.client_http_put_request()
                elif self.client_connect_button.text() == "DELETE":
                    self.client_http_post_request()
            elif self.client_protocol_combobox.currentText() == 'MQTT':
                mqtt_topic = self.client_send_edit.text()
                self.mqtt_client.unsubscribe(mqtt_topic)
                self.mqtt_client.subscribe(mqtt_topic)
                self.log_message(f'subscribed to topic :{mqtt_topic}')

                
        except Exception as e:
            logging.exception(e)


    def client_receive_data(self):
        try:
            if self.client_protocol_combobox.currentText() == 'UDP':
                while self.client_socket.hasPendingDatagrams():
                    client_udp_datagram, client_udp_host, client_udp_port = self.client_socket.readDatagram(self.client_socket.pendingDatagramSize())
                    client_udp_message = QByteArray(client_udp_datagram).data().decode()
                    self.log_message(f'Received UDP data: {client_udp_message}')

            elif self.client_protocol_combobox.currentText() == 'TCP':
                client_tcp_data = self.client_socket.readAll().data().decode()
                self.log_message(f'Received TCP data: {client_tcp_data}')
        except Exception as e:
                logging.exception(e)


    def log_message(self, client_message):
        try:
            self.client_console.append(client_message)
        except Exception as e:
                logging.exception(e)
    

    def on_client_combo_box_activated(self, index):
        try:
            combo_box = self.sender()  # Get the sender of the signal
            client_selected_option = combo_box.itemText(index)  # Get the text of the selected item
            print(f"Activated: {client_selected_option}")
            if client_selected_option == "Select":
                self.client_send_label.setText("Send :")
                self.client_connect_button.setText("Connect")
                self.client_connect_button.setDisabled(True)
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
                return
            if client_selected_option == "HTTP":
                self.client_send_label.setText("Send :")
                self.client_connect_button.setDisabled(False)
                self.client_connect_button.setText("GET")
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(False)
                self.client_send_button.setText("Request")
                return
            if client_selected_option == "MQTT":
                self.client_send_label.setText("Topic :")
                self.client_connect_button.setDisabled(False)
                self.client_connect_button.setText("Connect")
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(False)
                self.client_send_button.setText("Subscribe")
                self.client_send_button.setDisabled(True)
                return
            self.client_send_button.setText("Send")
            self.client_send_label.setText("Send :")
            self.client_connect_button.setText("Connect")
            self.client_connect_button.setDisabled(False)
            self.client_send_edit.setDisabled(True)
            self.client_send_button.setDisabled(True)
        except Exception as e:
                logging.exception(e)
    
    def client_socket_display_error(self, client_socket_error):
        try:
            if client_socket_error == QAbstractSocket.SocketError.ConnectionRefusedError:
                self.client_console.append("Error: Connection refused. Make sure the server is running.")
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
                
            elif client_socket_error == QAbstractSocket.SocketError.HostNotFoundError:
                self.client_console.append("Error: Host not found. Please check the server IP address.")
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
                
            elif client_socket_error == QAbstractSocket.SocketError.SocketTimeoutError:
                self.client_console.append("Error: Connection timed out.")
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
                
            else:
                self.client_console.append(f"Error: {self.client_socket.errorString()}")
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
        except Exception as e:
                logging.exception(e)

    def client_http_get_request(self):
        http_client_url = f"http://{self.client_url}:{self.client_port}/"
        self.log_message(f"Performing GET : {http_client_url}")
        
        response = requests.get(http_client_url)
        self.log_message(response.text)

    def client_http_post_request(self):
        http_client_url = f"http://{self.client_url}:{self.client_port}/"
        self.client_console.append(f"Performing POST : {http_client_url}")
        # params = self.param_edit.text()
        response = requests.post(http_client_url, data=self.client_send_edit.text())
        self.client_console.append(response.text)
    
    def client_http_put_request(self):
        http_client_url = f"http://{self.client_url}:{self.client_port}/"
        self.client_console.append(f"Performing POST : {http_client_url}")
        # params = self.param_edit.text()
        response = requests.put(http_client_url, data=self.client_send_edit.text())
        self.client_console.append(response.text)
    
    def client_http_put_request(self):
        http_client_url = f"http://{self.client_url}:{self.client_port}/"
        self.client_console.append(f"Performing POST : {http_client_url}")
        # params = self.param_edit.text()
        response = requests.delete(http_client_url)
        self.client_console.append(response.text)

            


    def closeEvent(self, event):
        try:
            # Terminate the process if the window is closed
            if self.server_http_process:
                if self.server_http_process.state() != QProcess.ProcessState.NotRunning:
                    self.server_http_process.terminate()
                    self.server_http_process.waitForFinished()
            if self.broker_process is not None:
                self.broker_process.terminate()
                self.broker_process.waitForFinished()

            super().closeEvent(event)
        except Exception as e:
            logging.exception(e)



if __name__ == "__main__":
    fh = logging.FileHandler("mbox.log")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logging.getLogger().addHandler(fh)
    app = QApplication(sys.argv)
    

    app.setWindowIcon(QIcon(resource_path('icon.ico')))
    palette = app.palette()
    
    window = MainWindow()
    if palette.color(QPalette.ColorRole.WindowText).value() < 146:
        apply_stylesheet(app, theme='dark_cyan.xml', invert_secondary=False)
    else:
        apply_stylesheet(app, theme='light_cyan_500.xml', invert_secondary=True)
    sys.exit(app.exec())
