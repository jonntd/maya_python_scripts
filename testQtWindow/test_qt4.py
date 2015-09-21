import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
 
class MyWnd(QDialog):
    def __init__(self,*args):
        QDialog.__init__(self,*args)
        uic.loadUi('test_qt4.ui', self)
 
        self.connect(self.spinbox, SIGNAL("valueChanged(int)"), self.log_to_console)
        self.connect(self.button,  SIGNAL("released()"),        self.push_me)
 
    def log_to_console(self,i):
        print i
 
    def push_me(self):
        print('push me button')
 
 
if __name__=="__main__":
    app = QApplication(sys.argv)
    wnd = MyWnd()
    wnd.show()
    sys.exit(app.exec_())