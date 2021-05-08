from pkg_resources import resource_filename
from pypredict.sat import Sat
from PyQt5 import QtWidgets
from pypredict.app import ApplicationWindow
import sys
from PyQt5 import QtWidgets, QtGui, QtCore

data_path = resource_filename("pypredict","data/")

SUCHAI = Sat(name="SUCHAI", tlepath="{}cubesat.txt".format(data_path), cat="CubeSat")
HODOYOSHI3 = Sat(name="HODOYOSHI-3", tlepath="{}resource.txt".format(data_path), cat="Earth Resources")
HODOYOSHI4 = Sat(name="HODOYOSHI-4", tlepath="{}resource.txt".format(data_path), cat="Earth Resources")
CUBESATXI_IV = Sat(name="CUBESAT XI-IV (CO-57)", tlepath="{}cubesat.txt".format(data_path), cat="CubeSat")
MrzSat=Sat(name="MrzSat", cat="CubeSat")
CZ = Sat(name="Long March 5", cat="Rocketbody")
ISS = Sat(name="ISS (ZARYA)", tlepath="{}tdrss.txt".format(data_path), cat="Tracking and Data Relay")


Sats = [CZ, MrzSat, ISS]


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow(Sats=Sats)
    application.show()
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()

   
    
    
