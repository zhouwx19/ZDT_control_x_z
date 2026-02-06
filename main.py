# main.py
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from serial_mgr import SerialMgr
from motor import Motor

import time

class Win(QWidget):
    def __init__(self):
        super().__init__()
        self.ser_mgr = SerialMgr()
        self.motor1 = None
        self.motor2 = None

        self.setWindowTitle("双电机控制")
        self.resize(420, 420)

        layout = QVBoxLayout()

        # 串口区
        self.port_box = QComboBox()
        self.btn_open = QPushButton("打开串口")
        self.btn_close = QPushButton("关闭串口")
        layout.addWidget(QLabel("CH340串口"))
        layout.addWidget(self.port_box)
        h = QHBoxLayout()
        h.addWidget(self.btn_open)
        h.addWidget(self.btn_close)
        layout.addLayout(h)

        self.lab_state = QLabel("串口状态：未连接")
        self.lab_state.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lab_state)

        # 电机1参数
        group1 = QGroupBox("电机(X轴)")
        form1 = QFormLayout()
        self.speed1 = QLineEdit("0.5")
        self.speed1.setAlignment(Qt.AlignCenter)
        self.dist1 = QLineEdit("0")
        self.dist1.setAlignment(Qt.AlignCenter)
        self.acc1 = QLineEdit("0")
        self.acc1.setAlignment(Qt.AlignCenter)
        self.curpos1 = QLineEdit("0")
        self.curpos1.setAlignment(Qt.AlignCenter)
        self.curpos1.setReadOnly(True)
        self.curpos1.setStyleSheet("border: none;") 
       # self.btn_update1 = QPushButton("更新位置")

        form1.addRow("设置速度(mm/s)", self.speed1)
        form1.addRow("设置位置(mm)", self.dist1)
        hpos1 = QHBoxLayout()
        hpos1.addWidget(self.curpos1)
        #hpos1.addWidget(self.btn_update1)
        form1.addRow("当前位置(mm)", hpos1)

        group1.setLayout(form1)
        layout.addWidget(group1)
        self.btn_move1 = QPushButton("电机1(X轴)运动")
        self.btn_home1 = QPushButton("电机1(X轴)回零")
        layout.addWidget(self.btn_move1)
        layout.addWidget(self.btn_home1)

        # 电机2参数
        group2 = QGroupBox("电机2(Z轴)")
        form2 = QFormLayout()
        self.speed2 = QLineEdit("0.5")
        self.speed2.setAlignment(Qt.AlignCenter)
        self.dist2 = QLineEdit("0")
        self.dist2.setAlignment(Qt.AlignCenter)
        self.acc2 = QLineEdit("0")
        self.acc2.setAlignment(Qt.AlignCenter)
        self.curpos2 = QLineEdit("0")
        self.curpos2.setAlignment(Qt.AlignCenter)
        self.curpos2.setReadOnly(True)
        self.curpos2.setStyleSheet("border: none;") 
        #self.btn_update2 = QPushButton("更新位置")

        form2.addRow("设置速度(mm/s)", self.speed2)
        form2.addRow("设置位置(mm)", self.dist2)
        hpos2 = QHBoxLayout()
        hpos2.addWidget(self.curpos2)
       # hpos2.addWidget(self.btn_update2)
        form2.addRow("当前位置(mm)", hpos2)

        group2.setLayout(form2)
        layout.addWidget(group2)
        self.btn_move2 = QPushButton("电机2(Z轴)运动")
        self.btn_home2 = QPushButton("电机2(Z轴)回零")
        layout.addWidget(self.btn_move2)
        layout.addWidget(self.btn_home2)

        self.setLayout(layout)

        # 信号
        self.btn_open.clicked.connect(self.open_port)
        self.btn_close.clicked.connect(self.close_port)
        self.btn_move1.clicked.connect(self.move1)
        self.btn_move2.clicked.connect(self.move2)
        self.btn_home1.clicked.connect(self.home1)
        self.btn_home2.clicked.connect(self.home2)
        #self.btn_update1.clicked.connect(self.update_position1)
       # self.btn_update2.clicked.connect(self.update_position2)


        self.auto_scan()
        self.auto_motor = None   # 当前正在自动刷新的电机 (1 或 2)

        # -------- 自动位置刷新定时器 --------
        self.pos_timer = QTimer()
        self.pos_timer.setInterval(400)   # 200 ms
        self.pos_timer.timeout.connect(self.update_positions)


    def auto_scan(self):
        self.port_box.clear()
        ports = self.ser_mgr.scan_ch340()
        self.port_box.addItems(ports)
        #self.ports.setAlignment(Qt.AlignCenter)

    def start_auto_update(self, motor_id):
        self.auto_motor = motor_id
        if not self.pos_timer.isActive():
            self.pos_timer.start()

    def stop_auto_update(self):
        if self.pos_timer.isActive():
            self.pos_timer.stop()
        self.auto_motor = None

    def open_port(self):
        if self.port_box.count() == 0:
            QMessageBox.warning(self, "提示", "没有串口")
            self.lab_state.setStyleSheet("color:red;")
            return
        self.ser_mgr.open(self.port_box.currentText())
        self.motor1 = Motor(self.ser_mgr.ser, 1)
        self.motor2 = Motor(self.ser_mgr.ser, 2)
        self.motor1.enable()
        self.motor2.enable()
        self.lab_state.setText("串口状态：已连接")
        self.lab_state.setStyleSheet("color:blue;")


        #串口打开后立即读取两台电机位置
        self.update_positions_temp()

    def close_port(self):
        self.ser_mgr.close()
        self.motor1 = None
        self.motor2 = None
        self.lab_state.setText("串口状态：已关闭")
        self.lab_state.setStyleSheet("color:red;")
        self.stop_auto_update()   # <<< 新增
        #self.ser_mgr.close()


    

    def update_positions(self):

        if self.auto_motor == 1 and self.motor1:
            pos = self.motor1.read_motor_position()
            self.curpos1.setText(f"{pos:.3f}")

            if hasattr(self, "last_pos1"):
                if abs(pos - self.last_pos1) < 0.001:
                    self.stop_auto_update()

            self.last_pos1 = pos

        elif self.auto_motor == 2 and self.motor2:
            pos = self.motor2.read_motor_position()
            self.curpos2.setText(f"{pos:.3f}")

            if hasattr(self, "last_pos2"):
                if abs(pos - self.last_pos2) < 0.001:
                    self.stop_auto_update()

            self.last_pos2 = pos

    def update_positions_temp(self):
        if not self.motor1 or not self.motor2:
            return

        pos1 = self.motor1.read_motor_position()
        pos2 = self.motor2.read_motor_position()

        self.curpos1.setText(f"{pos1:.3f}")
        self.curpos2.setText(f"{pos2:.3f}")

         # 如果两次位置变化都很小 -> 认为停止
        if hasattr(self, "last_pos1"):
            if abs(pos1 - self.last_pos1) < 0.001 and \
            abs(pos2 - self.last_pos2) < 0.001:
                self.stop_auto_update()

        self.last_pos1 = pos1
        self.last_pos2 = pos2


    def update_position1(self):
        if not self.motor1:
            return
        pos1 = self.motor1.read_motor_position()
        self.curpos1.setText(f"{pos1:.3f}")

    def update_position2(self):
        if not self.motor2:
            return
        pos2 = self.motor2.read_motor_position()
        self.curpos2.setText(f"{pos2:.3f}")

    def move1(self):
        self.setFocus() 
        QApplication.processEvents()
        if not self.motor1: return
        speed1 = float(self.speed1.text())
        dist1  = float(self.dist1.text())
        acc1   = int(self.acc1.text())
        self.motor1.move_single(
            float(speed1),
            float(dist1),
            int(acc1)
        )
        self.start_auto_update(1)

    def move2(self):
        self.setFocus() 
        QApplication.processEvents()
        if not self.motor2: return
        speed2 = float(self.speed2.text())
        dist2  = float(self.dist2.text())
        acc2   = int(self.acc2.text())
        self.motor2.move_single(
            float(speed2),
            float(dist2),
            int(acc2)
        )
        self.start_auto_update(2)
        #self.update_positions()

    def home1(self):
        if self.motor1:
            self.motor1.home()
            self.start_auto_update(1)

    def home2(self):
        if self.motor2:
            self.motor2.home()
            self.start_auto_update(2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Win()
    w.show()
    sys.exit(app.exec_())