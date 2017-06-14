import sys
from random import random
from time import ctime
from os import system
from os.path import join as p_join
from os.path import dirname
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSlot, QLocale, QTimer, pyqtSignal

MEMORY_DURATION = 5
MEMORY_ADDITIONAL_TIME = 2.5

def add_history(digits, accuracy, time):
    with open("history.txt", 'a') as txt:
        txt.write(
            "{}d {}% {}s\t".format(digits, accuracy, time) +
                ctime() + '\n'
            )

class WmtApp(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(
            p_join(dirname(__file__), 'StartingScreen.ui'), baseinstance=self)

        self.ui.show()

    @pyqtSlot()
    def startTraining(self):
        self.ui.hide()
        self.trainingWindow = WmtTraining(self)

    @pyqtSlot()
    def openHelp(self):
        WmtHelp(self)
        
    @pyqtSlot(int)
    def digitsChanged(self, new_digit):
        self.digits = new_digit

    @pyqtSlot(int)
    def questionsChanged(self, new_questions):
        self.questions = new_questions

class WmtHelp(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(
            p_join(dirname(__file__), 'HelpScreen.ui'), baseinstance=self)

        self.ui.show()


class WmtTraining(QtWidgets.QWidget):
    def __init__(self, options_screen, parent=None):
        #load ui
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(
            p_join(dirname(__file__), 'TrainingScreen.ui'), baseinstance=self)

        #copy values
        self.digits, self.questions = (
            options_screen.DigitsSlider.value(),
            options_screen.QuestionsSlider.value())
        self.options_screen = options_screen

        #initialize values
        self.correct_answer = 0
        self.time = 0.0
        self.count_mode = -1
        self.memory_time = (
            MEMORY_DURATION + (self.digits - 6) * MEMORY_ADDITIONAL_TIME
            )
        self.elapsed_times = []

        #make questions
        self.que_gen = (
            str(random())[2:2+self.digits] for x in range(self.questions)
            )
        self.last_que = next(self.que_gen)

        #init and run update timer
        self.time_update_cycle = 10#ms
        self.time_updater = QTimer()
        self.time_updater.timeout.connect(self.updateTime)
        self.time_updater.start(self.time_update_cycle)

        #show ui
        self.ui.show()
        self.startQuestion()
    
    @pyqtSlot()
    def updateTime(self):
        #calc new time
        self.time += (self.time_update_cycle / 1000) * self.count_mode
        if self.time < 0:
            self.time = 0

        #set TimeLabel
        self.setTimeLabel(self.time)
        
    @pyqtSlot()
    def startQuestion(self):
        #update CorrectLabel
        self.setCorrectLabel(self.correct_answer)

        #update NumberLabel
        self.setNumberLabel(self.last_que)

        #disable text input
        self.NumberInput.setDisabled(True)

        #set count mode to decrease
        self.count_mode = -1

        #set time label to memory time
        self.time = self.memory_time

        #set timer to hide question
        QTimer.singleShot(self.memory_time * 1000, self.hideQuestion)
        pass
        
    @pyqtSlot()
    def hideQuestion(self):
        #hide number
        self.setNumberLabel('')
        
        #enable text input
        self.NumberInput.setDisabled(False)

        #focus cursor to numberinput
        QTimer.singleShot(0, self.NumberInput.setFocus)
        
        #set count mode to increase
        self.count_mode = 1

        #set time label to zero
        self.time = 0.0

    @pyqtSlot()
    def returnPressed(self):
        self.elapsed_times.append(self.time)
        
        #if correct
        correct = self.last_que[::-1]
        if self.NumberInput.text() == correct:
            #increase correct_answer
           self.correct_answer += 1

        self.NumberInput.setText('')

        #get new question
        try:
            self.last_que = next(self.que_gen)
            
            #start new question
            self.startQuestion()
        #if no question, open score
        except:
            score_screen = WmtScore(self)
            self.ui.hide()

    def setCorrectLabel(self, num):
        self.CorrectLabel.setText(
            str(num) + ' / ' + str(self.questions)
            )

    def setTimeLabel(self, _t):
        self.TimeLabel.setText(
            '{:0.2f}'.format(_t)
            )

    def setNumberLabel(self, question):
        self.NumberLabel.setText(
            question
            )

class WmtScore(QtWidgets.QDialog):
    def __init__(self, training_screen, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(
            p_join(dirname(__file__), 'ScoreScreen.ui'), baseinstance=self)

        self.options = training_screen.options_screen

        #calc scores
        digits = training_screen.digits
        accuracy = training_screen.correct_answer / \
                   training_screen.questions * 1000 // 1 / 10
        average_time = sum(training_screen.elapsed_times) / \
                       len(training_screen.elapsed_times) * 100 // 1 / 100

        #write to history
        add_history(digits, accuracy, average_time)

        #set labels
        self.DigitsLabel.setText(str(digits))
        self.CorrectAnswersLabel.setText(str(training_screen.correct_answer))
        self.AccuracyLabel.setText(str(accuracy))
        self.AverageTimeLabel.setText(str(average_time))

        self.ui.show()

    @pyqtSlot()
    def returnToOptions(self):
        self.ui.hide()
        self.options.show()
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = WmtApp()
    sys.exit(app.exec())
