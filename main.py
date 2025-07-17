import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QPushButton, QLabel, QTabWidget, QTextEdit,
                            QFileDialog, QHBoxLayout, QGridLayout, QButtonGroup)
from PyQt6.QtCore import QProcess, QProcessEnvironment
import time

class FlashTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("刷机工具箱")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建设备信息标签
        self.device_info_label = QLabel("当前设备: 检测中...")
        self.device_info_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        
        # 设置WinUI3风格
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f3f3;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QTabBar::tab {
                background-color: #f3f3f3;
                color: #333333;
                border: 1px solid #e5e5e5;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0078d7;
                color: white;
                border-bottom: 2px solid #0078d7;
            }
            QTabBar::tab:hover {
                background-color: #e5f1fb;
            }
        """)
        
        # 创建主界面
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Root选项卡
        self.root_tab = QWidget()
        self.tabs.addTab(self.root_tab, "Root工具")
        self.setup_root_tab()
        
        # ADB选项卡
        self.adb_tab = QWidget()
        self.tabs.addTab(self.adb_tab, "ADB工具")
        self.setup_adb_tab()
        
        # Fastboot选项卡
        self.fastboot_tab = QWidget()
        self.tabs.addTab(self.fastboot_tab, "Fastboot工具")
        self.setup_fastboot_tab()
        
        # 日志选项卡
        self.log_tab = QWidget()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout = QVBoxLayout()
        log_layout.addWidget(self.log_output)
        self.log_tab.setLayout(log_layout)
        self.tabs.addTab(self.log_tab, "日志")
        
        self.layout.addWidget(self.device_info_label)
        
        # 初始化ADB进程
        self.adb_process = QProcess()
        self.adb_process.readyReadStandardOutput.connect(self.handle_adb_output)
        self.adb_process.readyReadStandardError.connect(self.handle_adb_error)
        
        # 初始化Fastboot进程
        self.fastboot_process = QProcess()
        self.fastboot_process.readyReadStandardOutput.connect(self.handle_fastboot_output)
        self.fastboot_process.readyReadStandardError.connect(self.handle_fastboot_error)
    
    def setup_adb_tab(self):
        layout = QVBoxLayout(self.adb_tab)
        
        # 设备连接
        self.device_label = QLabel("设备状态: 未连接")
        layout.addWidget(self.device_label)
        
        # ADB命令按钮
        self.btn_devices = QPushButton("列出设备")
        self.btn_devices.clicked.connect(self.run_adb_devices)
        layout.addWidget(self.btn_devices)
        
        self.btn_reboot_bootloader = QPushButton("重启到Fastboot")
        self.btn_reboot_bootloader.clicked.connect(self.run_adb_reboot_bootloader)
        layout.addWidget(self.btn_reboot_bootloader)
        
        self.btn_reboot_recovery = QPushButton("重启到Recovery")
        self.btn_reboot_recovery.clicked.connect(self.run_adb_reboot_recovery)
        layout.addWidget(self.btn_reboot_recovery)

        self.btn_reboot_system = QPushButton("重启到System")
        self.btn_reboot_system.clicked.connect(self.run_adb_reboot_system)
        layout.addWidget(self.btn_reboot_system)
        
        self.btn_install_apk = QPushButton("安装APK")
        self.btn_install_apk.clicked.connect(self.install_apk)
        layout.addWidget(self.btn_install_apk)
    
    def setup_fastboot_tab(self):
        layout = QVBoxLayout(self.fastboot_tab)
        
        # Fastboot命令按钮
        self.btn_devices_fastboot = QPushButton("列出Fastboot设备")
        self.btn_devices_fastboot.clicked.connect(self.run_fastboot_devices)
        layout.addWidget(self.btn_devices_fastboot)
        
        self.btn_flash_recovery = QPushButton("刷入Recovery")
        self.btn_flash_recovery.clicked.connect(self.flash_recovery)
        layout.addWidget(self.btn_flash_recovery)
        
        self.btn_flash_system = QPushButton("刷入System")
        self.btn_flash_system.clicked.connect(self.flash_system)
        layout.addWidget(self.btn_flash_system)

        self.btn_flash_boot = QPushButton("刷入Boot")
        self.btn_flash_boot.clicked.connect(self.flash_boot)
        layout.addWidget(self.btn_flash_boot)
        
        self.btn_reboot_system = QPushButton("重启到System")
        self.btn_reboot_system.clicked.connect(self.run_fastboot_reboot_system)
        layout.addWidget(self.btn_reboot_system)
    
    def setup_root_tab(self):
        layout = QVBoxLayout(self.root_tab)
        
        # Root命令按钮
        self.btn_root = QPushButton("开启Root之旅")
        self.btn_root.clicked.connect(self.start_root_journey)
        layout.addWidget(self.btn_root)
        
        # 下方隐藏控件
        layout1 = QHBoxLayout(self.central_widget)
        layout.addLayout(layout1)
        layout3 = QGridLayout(self.central_widget)
        layout1.addLayout(layout3)
        # Root管理器选择
        self.root_manager_label = QLabel("选择Root管理器:")
        layout.addWidget(self.root_manager_label)
        self.root_manager_label.setVisible(False),
        
        # 管理器按钮组
        self.manager_button_group = QButtonGroup()
        
        self.magisk_label = QLabel("Magisk")
        layout.addWidget(self.magisk_label)
        self.magisk_label.setVisible(False),
        self.btn_magisk = QPushButton("选择")
        self.btn_magisk.setCheckable(True)
        layout.addWidget(self.btn_magisk)
        self.manager_button_group.addButton(self.btn_magisk)
        self.btn_magisk.setVisible(False)
        self.btn_magisk.clicked.connect(self.run_root_magisk)
        
        self.apatch_label = QLabel("Apatch")
        layout.addWidget(self.apatch_label)
        self.apatch_label.setVisible(False),
        self.btn_apatch = QPushButton("选择")
        self.btn_apatch.setCheckable(True)
        layout.addWidget(self.btn_apatch)
        self.manager_button_group.addButton(self.btn_apatch)
        self.btn_apatch.setVisible(False)
        self.btn_apatch.clicked.connect(self.run_root_apatch)
        
        self.kernelsu_label = QLabel("KernelSU")
        layout.addWidget(self.kernelsu_label)
        self.kernelsu_label.setVisible(False),
        self.btn_kernelsu = QPushButton("选择")
        self.btn_kernelsu.setCheckable(True)
        layout.addWidget(self.btn_kernelsu)
        self.manager_button_group.addButton(self.btn_kernelsu)
        self.btn_kernelsu.setVisible(False)
        self.btn_kernelsu.clicked.connect(self.run_root_kernelsu)
        
        # 默认选中第一个
        self.btn_magisk.setChecked(True)

        #结束Root之旅
        self.end_root = QPushButton("结束Root之旅")
        layout.addWidget(self.end_root)
        self.end_root.setVisible(False)
        self.end_root.clicked.connect(self.exit)
    
    def run_adb_command(self, command):
        self.log_output.append(f"执行命令: adb {command}")
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PATH", f"{os.getcwd()};{env.value('PATH')}")
        self.adb_process.setProcessEnvironment(env)
        self.adb_process.start("adb", command.split())
        
    def detect_device_model(self):
        """检测连接的设备型号"""
        self.adb_process.start("adb", "shell getprop ro.product.model".split())
        self.adb_process.waitForFinished()
        model = self.adb_process.readAllStandardOutput().data().decode().strip()
        
        self.adb_process.start("adb", "shell getprop ro.product.manufacturer".split())
        self.adb_process.waitForFinished()
        manufacturer = self.adb_process.readAllStandardOutput().data().decode().strip()
        
        if model and manufacturer:
            device_info = f"{manufacturer} {model}"
            self.log_output.append(f"检测到设备: {device_info}")
            self.device_info_label.setText(f"当前设备: {device_info}")
        else:
            self.log_output.append("未检测到设备或获取信息失败")
            self.device_info_label.setText("当前设备: 未连接")
    
    def run_fastboot_command(self, command):
        self.log_output.append(f"执行命令: fastboot {command}")
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PATH", f"{os.getcwd()};{env.value('PATH')}")
        self.fastboot_process.setProcessEnvironment(env)
        self.fastboot_process.start("fastboot", command.split())

    def run_adb_devices(self):
        self.run_adb_command("devices")
    
    def run_adb_reboot_bootloader(self):
        self.run_adb_command("reboot bootloader")
    
    def run_adb_reboot_recovery(self):
        self.run_adb_command("reboot recovery")
    
    def run_adb_reboot_system(self):
        self.run_adb_command("reboot")
    
    def run_fastboot_devices(self):
        self.run_fastboot_command("devices")
    
    def run_fastboot_reboot_system(self):
        self.run_fastboot_command("reboot")
    
    def exit(self):
        sys.exit(app.exec())
    
    def install_apk(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择APK文件", "", "APK文件 (*.apk)")
        if file_path:
            self.run_adb_command(f"install {file_path}")
    
    def flash_recovery(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择Recovery镜像", "", "镜像文件 (*.img)")
        if file_path:
            self.run_fastboot_command(f"flash recovery {file_path}")
    
    def flash_system(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择System镜像", "", "镜像文件 (*.img)")
        if file_path:
            self.run_fastboot_command(f"flash system {file_path}")
    
    def flash_boot(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择Boot镜像", "", "镜像文件 (*.img)")
        if file_path:
            self.run_fastboot_command(f"flash boot {file_path}")

    def run_root_apatch(self):
        self.run_adb_command(f"install ./Apatch.apk")
        self.log_output.append("请在手机上点击确认，打开Apatch并修补镜像")
        file_path, _ = QFileDialog.getOpenFileName(self, "选择修补好的Boot镜像", "", "镜像文件 (*.img)")
        if file_path:
            self.run_fastboot_command(f"flash boot {file_path}")
        self.end_root_journey()
    
    def run_root_kernelsu(self):
        self.run_adb_command(f"install ./KernelSU.apk")
        self.log_output.append("请在手机上点击确认，打开KernelSU并修补镜像")
        file_path, _ = QFileDialog.getOpenFileName(self, "选择修补好的Boot镜像", "", "镜像文件 (*.img)")
        if file_path:
            self.run_fastboot_command(f"flash boot {file_path}")
        self.end_root_journey()

    def run_root_magisk(self):
        self.run_adb_command(f"install ./Magisk.apk")
        self.log_output.append("请在手机上点击确认，打开Magisk并修补镜像")
        file_path, _ = QFileDialog.getOpenFileName(self, "选择修补好的Boot镜像", "", "镜像文件 (*.img)")
        if file_path:
            self.run_fastboot_command(f"flash boot {file_path}")
        self.end_root_journey()
    
    def handle_adb_output(self):
        output = self.adb_process.readAllStandardOutput().data().decode().strip()
        if output:
            self.log_output.append(output)
            if "List of devices attached" in output:
                lines = output.split('\n')
                if len(lines) > 1 and lines[1].strip():
                    self.device_label.setText("设备状态: 已连接")
                else:
                    self.device_label.setText("设备状态: 未连接")
    
    def handle_adb_error(self):
        error = self.adb_process.readAllStandardError().data().decode().strip()
        if error:
            self.log_output.append(f"错误: {error}")
    
    def handle_fastboot_output(self):
        output = self.fastboot_process.readAllStandardOutput().data().decode().strip()
        if output:
            self.log_output.append(output)
    
    def handle_fastboot_error(self):
        error = self.fastboot_process.readAllStandardError().data().decode().strip()
        if error:
            self.log_output.append(f"错误: {error}")
            
    def start_root_journey(self):
        """启动Root之旅动画效果"""
        from PyQt6.QtCore import QPropertyAnimation, QRect
        
        # 创建动画
        self.animation = QPropertyAnimation(self.btn_root, b"geometry")
        self.animation.setDuration(750)
        self.animation.setStartValue(self.btn_root.geometry())
        self.animation.setEndValue(QRect(
            self.btn_root.x(), 
            self.btn_root.y() - self.btn_root.height() - 260,
            self.btn_root.width(),
            self.btn_root.height()
        ))
        self.animation.finished.connect(lambda: [
            time.sleep(0.1),
            self.btn_root.setVisible(False),
            time.sleep(0.1),
            self.magisk_label.setVisible(True),
            time.sleep(0.1),
            self.apatch_label.setVisible(True),
            time.sleep(0.1),
            self.kernelsu_label.setVisible(True),
            time.sleep(0.1),
            self.btn_magisk.setVisible(True),
            time.sleep(0.1),
            self.btn_apatch.setVisible(True),
            time.sleep(0.1),
            self.btn_kernelsu.setVisible(True),
            time.sleep(0.1),
            self.root_manager_label.setVisible(True),
        ])
        self.animation.start()

    def end_root_journey(self):
        """结束Root之旅动画效果"""
        from PyQt6.QtCore import QPropertyAnimation, QRect
        
        # 创建动画
        self.animation = QPropertyAnimation(self.btn_root, b"geometry")
        self.animation.setDuration(750)
        self.animation.setStartValue(self.btn_root.geometry())
        self.animation.setEndValue(QRect(
            self.btn_root.x(), 
            self.btn_root.y() - self.btn_root.height() - 260,
            self.btn_root.width(),
            self.btn_root.height()
        ))
        self.animation.finished.connect(lambda: [
            time.sleep(0.1),
            self.magisk_label.setVisible(False),
            time.sleep(0.1),
            self.apatch_label.setVisible(False),
            time.sleep(0.1),
            self.kernelsu_label.setVisible(False),
            time.sleep(0.1),
            self.btn_magisk.setVisible(False),
            time.sleep(0.1),
            self.btn_apatch.setVisible(False),
            time.sleep(0.1),
            self.btn_kernelsu.setVisible(False),
            time.sleep(0.1),
            self.root_manager_label.setVisible(False),
            time.sleep(0.1),
            self.end_root.setVisible(True)
        ])
        self.animation.start()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlashTool()
    window.show()
    sys.exit(app.exec())
