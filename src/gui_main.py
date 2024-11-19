import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QPushButton, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from main import LocalAssistant

class ModelThread(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, assistant, text, mode="chat"):
        super().__init__()
        self.assistant = assistant
        self.text = text
        self.mode = mode
        
    def run(self):
        if self.mode == "json":
            response = self.assistant.format_json(self.text)
        else:
            response = self.assistant.process_input(self.text)
        self.finished.emit(response)

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.assistant = None
        self.init_ui()
        self.init_model()
        
    def init_ui(self):
        self.setWindowTitle('本地AI助手')
        self.setMinimumSize(800, 600)
        
        # 主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 聊天显示区域
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setFont(QFont('Microsoft YaHei', 10))
        layout.addWidget(self.chat_area)
        
        # 输入区域
        input_layout = QHBoxLayout()
        
        # 输入框
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(70)
        self.input_box.setFont(QFont('Microsoft YaHei', 10))
        input_layout.addWidget(self.input_box)
        
        # 按钮区域
        button_layout = QVBoxLayout()
        
        # 聊天按钮（原发送按钮）
        self.send_button = QPushButton('聊天')  # 改为"聊天"
        self.send_button.setFixedWidth(100)
        self.send_button.setFixedHeight(35)
        self.send_button.clicked.connect(lambda: self.send_message("chat"))
        button_layout.addWidget(self.send_button)
        
        # JSON格式化按钮
        self.json_button = QPushButton('JSON格式化')
        self.json_button.setFixedWidth(100)
        self.json_button.setFixedHeight(35)
        self.json_button.clicked.connect(lambda: self.send_message("json"))
        button_layout.addWidget(self.json_button)
        
        input_layout.addLayout(button_layout)
        layout.addLayout(input_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton {
                background-color: #98FB98;  /* 淡绿色 */
                color: #333;  /* 深色文字，提高可读性 */
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #90EE90;  /* 鼠标悬停时稍微深一点的绿色 */
            }
            QPushButton:disabled {
                background-color: #E0E0E0;  /* 禁用状态为灰色 */
                color: #888;
            }
        """)
        
        # 初始化提示
        self.chat_area.append("正在加载模型，请稍候...")
        
    def init_model(self):
        self.loading_thread = QThread()
        self.loading_thread.run = self.load_model
        self.loading_thread.start()
    
    def load_model(self):
        self.assistant = LocalAssistant()
        self.chat_area.append("模型加载完成！可以开始对话了。\n")
        self.send_button.setEnabled(True)
        self.json_button.setEnabled(True)
    
    def send_message(self, mode="chat"):
        if not self.assistant:
            return
            
        text = self.input_box.toPlainText().strip()
        if not text:
            return
            
        # 显示用户输入
        self.chat_area.append(f"你: {text}\n")
        
        # 在新线程中处理响应
        self.thread = ModelThread(self.assistant, text, mode)
        self.thread.finished.connect(self.handle_response)
        self.thread.start()
        
        # 清空输入框
        self.input_box.clear()
        self.send_button.setEnabled(False)
        self.json_button.setEnabled(False)
    
    def handle_response(self, response):
        self.chat_area.append(f"助手: {response}\n")
        self.send_button.setEnabled(True)
        self.json_button.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 