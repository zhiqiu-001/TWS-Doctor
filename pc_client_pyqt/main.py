import sys
from PyQt6.QtWidgets import QApplication, QStyleFactory
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    
    # 使用Fusion样式
    app.setStyle(QStyleFactory.create("Fusion"))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()