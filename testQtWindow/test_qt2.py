import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MyWnd(QDialog):
    def __init__(self,*args):
        QDialog.__init__(self,*args)
        
if __name__=="__main__":
    app = QApplication(sys.argv)
    wnd = MyWnd()
    wnd.show()
    sys.exit(app.exec_())
