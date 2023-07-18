import os
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QSize, QCoreApplication, QSettings
from subprocess import call
from PyQt5.QtWidgets import QApplication, QDialog
#from Ui_MAGicTableGUI import Ui_Dialog # don't need when using loadUi? setupUi not used here
from PyQt5.uic import loadUi
from PyQt5 import uic
SETTINGS_TRAY = 'settings/tray'



class MAGIcTableGUI_Runner(QDialog):
    def __init__(self):
        super(MAGIcTableGUI_Runner, self).__init__()
        self.settings = None
        self.ui = uic.loadUi('Ui_MAGIcTableGUI.ui', self)   # do not delete as this is one of the ways
        # self.ui = Ui_Dialog()
        # self.setupUi(self)
        self.loadSettings() # load setting from prev

        self.image = None
        os.chdir("../")

        print(sys.path)


        # self.save_setting_pushButton.clicked.

        # connect the slot to the signal by clicking the checkbox to save the state settings
        self.path_comboBox.currentIndexChanged.connect(self.path_selectionchange)
        self.id_comboBox.currentIndexChanged.connect(self.id_selectionchange)
        self.save_setting_pushButton.clicked.connect(self.saveSettings)

        self.run_pushButton.clicked.connect(lambda: self.run())

    def path_selectionchange(self, i):
        ## list the current combobox selections
        for count in range(self.path_comboBox.count()):
            print(self.path_comboBox.itemText(count))

    def id_selectionchange(self, i):
        ## list the current combobox selections
        for count in range(self.id_comboBox.count()):
            print(self.id_comboBox.itemText(count))


        # Slot checkbox to save the settings
    def saveSettings(self):
        print("save setting attempt")
        self.settings = QSettings("MyCom", "name")
        self.settings.beginGroup("set1")

        """ MODES """
        self.settings.setValue("p2p_radioButton_ln",  self.p2p_radioButton.isChecked())
        self.settings.setValue("fig8_radioButton_ln",  self.fig8_radioButton.isChecked())
        self.settings.setValue("path_comboBox_ln", self.path_comboBox.currentText())
        print("saved current path combobox text: ", self.path_comboBox.currentText())
       
        """ SUBJECT INFO """
        self.settings.setValue("sid_lineEdit_ln", self.sid_lineEdit.text())
        self.settings.setValue("rh_radioButton_ln", self.rh_radioButton.isChecked())
        self.settings.setValue("lh_radioButton_ln", self.lh_radioButton.isChecked())
        self.settings.setValue("timelimit_spinBox_ln", self.timelimit_spinBox.value()) # ln: lookup name
        self.settings.setValue("id_comboBox_ln", self.id_comboBox.currentText())
        print("saved current id combobox text: ", self.id_comboBox.currentText())

        # self.settings.setValue("id_comboBox_ln", str(self.id_comboBox.value()))


        """ CHECKBOXES """
        self.settings.setValue("display_checkbox_ln", self.display_checkbox.checkState())
        self.settings.setValue("obstacle_checkbox_ln", self.obstacle_checkbox.checkState())
        self.settings.setValue("display_trace_checkbox_ln", self.display_trace_checkbox.checkState())
        self.settings.setValue("display_clock_checkbox_ln", self.display_clock_checkbox.checkState())
        self.settings.setValue("target_sound_checkbox_ln", self.target_sound_checkbox.checkState())
        self.settings.setValue("target_visual_checbox_ln", self.target_visual_checbox.checkState())
        #self.settings.setValue("ask_for_note_checkbox_ln", self.ask_for_note_checkbox.checkState())
        
        p2p_radioButton = self.settings.value("p2p_radioButton_ln")
        fig8_radioButton = self.settings.value("fig8_radioButton_ln")
        rh_radioButton = self.settings.value("rh_radioButton_ln")
        lh_radioButton = self.settings.value("lh_radioButton_ln")

        if p2p_radioButton == 'true':
            p2p_bool = True
            self.tt = "p2p"
        else:
            p2p_bool = False
            self.tt = "fig8"
        if fig8_radioButton == 'true':
            self.tt = "fig8"
            fig8_bool = True
        else:
            self.tt = "p2p"
            fig8_bool = False

        if rh_radioButton == 'true':
            rh_bool = True
            self.hn = "r"
        else:
            rh_bool = False
            self.hn = "l"
        if lh_radioButton == 'true':
            lh_bool = True
            self.hn = "l"
        else:
            lh_bool = False
            self.hn = "r"

        print('save p2p,', bool(self.p2p_radioButton.isChecked()),  bool(self.fig8_radioButton.isChecked()))
        print("handedness:", self.hn)



        self.settings.endGroup()
        # settings.setValue(SETTINGS_TRAY, self.display_clock_checkbox.isChecked())
        # settings.sync()

    def loadSettings(self):
        print("Loading settings...")
        self.settings = QSettings('MyCom', 'name')
        # self.settings.clear() # may need to clear on errors
        print('All keys: ', self.settings.allKeys())

        if self.settings.allKeys(): # if keys exist
            self.settings.beginGroup("set1") # do not change the name

            """ MODES """
            p2p_radioButton = self.settings.value("p2p_radioButton_ln")
            fig8_radioButton = self.settings.value("fig8_radioButton_ln")
            # print('p2p,', p2p_radioButton,  fig8_radioButton)
            path_comboBox = self.settings.value("path_comboBox_ln")


            """ SUBJECT INFO """
            sid_lineEdit = self.settings.value("sid_lineEdit_ln")
            rh_radioButton = self.settings.value("rh_radioButton_ln")
            lh_radioButton = self.settings.value("lh_radioButton_ln")
            timeout = self.settings.value("timelimit_spinBox_ln")
            id_comboBox = self.settings.value("id_comboBox_ln")

            """ CHECKBOXES """

            # load key settings from prev save (find a cleaner way later) do not change the names
            display_checkbox = self.settings.value("display_checkbox_ln")
            obstacle_checkbox = self.settings.value("obstacle_checkbox_ln")
            display_trace_checkbox = self.settings.value("display_trace_checkbox_ln")
            display_clock_checkbox = self.settings.value("display_clock_checkbox_ln")
            target_sound_checkbox = self.settings.value("target_sound_checkbox_ln")
            target_visual_checbox = self.settings.value("target_visual_checbox_ln")
            #ask_for_note_checkbox = self.settings.value("ask_for_note_checkbox_ln")





            # print('what is it',p2p_radioButton)
            ## temp fix
            if p2p_radioButton == 'true':
                p2p_bool = True
                self.tt = "p2p"
            else:
                p2p_bool = False
                self.tt = "fig8"
            if fig8_radioButton == 'true':
                self.tt = "fig8"
                fig8_bool = True
            else:
                self.tt = "p2p"
                fig8_bool = False

            if rh_radioButton == 'true':
                rh_bool = True
                self.hn = "r"
            else:
                rh_bool = False
                self.hn = "l"
            if lh_radioButton == 'true':
                lh_bool = True
                self.hn = "l"
            else:
                lh_bool = False
                self.hn = "r"

            """ apply to the current window """
            """ MODES """
            self.p2p_radioButton.setChecked(p2p_bool)
            self.fig8_radioButton.setChecked(fig8_bool)

            self.path_comboBox.setProperty("value", path_comboBox )

            """ SUBJECT INFO """
            self.sid_lineEdit.setText(sid_lineEdit)
            self.rh_radioButton.setChecked(rh_bool)
            self.lh_radioButton.setChecked(lh_bool)
            self.timelimit_spinBox.setProperty("value", timeout)
            self.id_comboBox.setProperty("value", id_comboBox)

            """ CHECKBOXES """
            self.display_checkbox.setChecked(display_checkbox)
            self.obstacle_checkbox.setChecked(obstacle_checkbox)
            self.display_trace_checkbox.setChecked(display_trace_checkbox)
            self.display_clock_checkbox.setChecked(display_clock_checkbox)
            self.target_sound_checkbox.setChecked(target_sound_checkbox)
            self.target_visual_checbox.setChecked(target_visual_checbox)
            #self.ask_for_note_checkbox.setChecked(ask_for_note_checkbox)


            """ print out """
            print("loaded subject ID:", sid_lineEdit)
            print("loaded combobox text:", path_comboBox)
            print("loaded time limit:", timeout)
            print("loaded id box text:", id_comboBox)


            self.settings.endGroup()


    def run(self):
        # call(['python', path])

        display_int = 1 if self.display_checkbox.checkState() > 0 else 0
        obstacle_checkbox_int = 1 if self.display_checkbox.checkState() > 0 else 0
        display_trace_checkbox_int = 1 if self.display_trace_checkbox.checkState() > 0 else 0
        display_clock_checkbox_int = 1 if self.display_clock_checkbox.checkState() > 0 else 0
        target_sound_checkbox_int = 1 if self.target_sound_checkbox.checkState() > 0 else 0
        target_visual_checbox_int = 1 if self.target_visual_checbox.checkState() > 0 else 0
        ask_for_note_checkbox_int = 1 if self.ask_for_note_checkbox.checkState() > 0 else 0


        cmd = "python main.py -mod dual -tt " + self.tt \
              + " -pth " + self.path_comboBox.currentText() \
              + " -sid " + self.sid_lineEdit.text()\
              + " -hn " + self.hn\
              + " -t " + str(self.timelimit_spinBox.value()) \
              + " -idx " + self.id_comboBox.currentText()\
              + " -d " + str(display_int)
                       # + ' -obs ' + str(obstacle_checkbox_int) \
                       # + ' -tr ' + str(display_trace_checkbox_int)\
                       # + ' -clk ' + str(display_clock_checkbox_int) \
                       # + ' -ts ' + str(target_sound_checkbox_int) \
                       # + ' -tv ' + str(target_visual_checbox_int) \
                       # + ' -nt ' + str(ask_for_note_checkbox_int)

        print('Submitted arguments: ', cmd)
        os.system(cmd)
        QCoreApplication.instance().quit()




if __name__=='__main__':
    app=QApplication(sys.argv)
    window = MAGIcTableGUI_Runner()
    window.setWindowTitle('MAGIC_TABLE_GUI')
    window.show()
    sys.exit(app.exec_())
