import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MyWnd(QDialog):
    def __init__(self,*args):
        QDialog.__init__(self,*args)

        self.setWindowTitle('my dialog')

        spinbox = QSpinBox()
        slider  = QSlider(Qt.Horizontal)
        button  = QPushButton('push me')

        spinbox.setRange(0, 130)
        slider.setRange(0, 130)

        self.connect(spinbox, SIGNAL("valueChanged(int)"), slider, SLOT("setValue(int)"))
        self.connect(slider,  SIGNAL("valueChanged(int)"), spinbox, SLOT("setValue(int)"))
        self.connect(spinbox, SIGNAL("valueChanged(int)"), self.log_to_console)
        self.connect(button,  SIGNAL("released()"),        self.push_me)

        spinbox.setValue(27)

        layout = QHBoxLayout()
        layout.addWidget(spinbox)
        layout.addWidget(slider)
        layout.addWidget(button)
        self.setLayout(layout)

    def log_to_console(self,i):
        print i

    def push_me(self):
        print('push me button')

        
if __name__=="__main__":
    app = QApplication(sys.argv)
    wnd = MyWnd()
    wnd.show()
    sys.exit(app.exec_())
