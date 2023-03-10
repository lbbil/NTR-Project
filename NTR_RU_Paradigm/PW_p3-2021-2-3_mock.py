from psychopy import visual, event, core, gui, sound, data, tools, info
from psychopy import gui
import csv
import tkinter as tk
import os, platform
import sys
import numpy as np
from datetime import datetime
from scipy.stats import norm
#
###############################################################################
## Trigger code start: Censor from here til Trigger code ends for laptop
## ALSO find "Trigger or Keypress" below and censor appropriately for running on laptop
class ScannerComs(object):
    '''
    Uses pyserial to monitor serial port for messages.  To be used in the scanner,
    for the button box.  Note that the port is different for the mock scanner
    and real scanner.
    # set to 3 for the real scanner, 2 for the mock scanner
    monitoring a serial port from the scanner is instead a queue of messages.  Care needs to be taken
    not to handle old messages by accident.  Like if the subject is pressing buttons before a trial,
    they might select a response when the trial starts.
    
    '''
    def __init__(self,port=2, timeout=0.001, baudrate=19200, verbose=False):
        self.verbose=verbose
        self.alive=False
        
        try:
            # stopbits?  bytesize?
            import serial
            self._coms = serial.Serial(port, timeout=timeout, baudrate=baudrate)
            if verbose:
                print('using serial port {}'.format(self._coms.portstr))
            self._str = 'ScannerComs(port={}, timeout={}, baudrate={})'.format(port,timeout,baudrate)
            self.alive = True
        except:
            self._coms = None
            print('could not connect to serial port.  This is OK if not hooked up to a scanner.  Else check your connections,ports,settings,pyserial installed,etc...')
            self._str = 'Dummy ScannerComs instance, never connected properly'
        self._messages=[]
        
    def close(self):
        if self._coms:
            self._coms.close()
            self._coms=None
            self._str='closed ScannerComs instance'
            self.alive=False
    
    def clear(self):
        '''
        clear all incoming messages
        '''
        if self._coms:
            self._coms.flushInput()
        self._messages=[]
    
    def _read(self):
        while True:
            msg = self._coms.read()
            if not msg:
                break
            self._messages.append(msg)
    
    def wait_for_message(self,*valid_messages):
        '''
        returns whenever a valid message is encountered
        '''
        if not self._coms:
            return
        
        old_settings = self._coms.getSettingsDict()
        settings = old_settings.copy()
        settings['timeout']=None
        self._coms.applySettingsDict(settings)
        while True:
            msg = self._coms.read()
            if msg:
                msg=int(msg)
            '''
            try:
                msg = msg.decode()
            except AttributeError:
                pass
            '''
            if msg in valid_messages:
                self._coms.applySettingsDict(old_settings)
                return
    
    def messages(self, clear_after=True, as_set=True):
        if self._coms:
            self._read()
            ret = self._messages
            #testing:
            old=ret
            ret=[]
            for m in old:
                '''
                try:
                    m=m.decode()
                except AttributeError:
                    pass
                '''
                if m:
                    m=int(m)
                ret.append(m)
        else:
            ret=[]
        
        if as_set:
            ret=set(ret)
        if clear_after:
            self._messages=[]
        return ret
    
    def __bool__(self):
        return self.alive
    def __repr__(self):
        return self._str
    
    __nonzero__=__bool__
    __str__=__repr__

##Added for the scanner. This uses the ScannerComs object you created earlier and allows you to "connect" with the scanner so you can receive responses.
port='COM4'## mock  ## JP 12-14-2022
##port='COM3'## MRI  ## JP 12-14-2022

scanner_coms = ScannerComs(port=port, timeout=0.001, baudrate=19200)
###############################################################################
### Trigger code ends

## JP 12-14-22
##Determine Monitor Resolution:
if platform.system() == "Windows":
    from win32api import GetSystemMetrics
    width, height = GetSystemMetrics(0), GetSystemMetrics(1)
elif platform.system() == "Darwin":
    p = subp.Popen(shlex.split("system_profiler SPDisplaysDataType"), stdout=subp.PIPE)		
    output = subp.check_output(('grep', 'Resolution'), stdin=p.stdout).decode("utf-8")
    if "Retina" in output:
          width = 1440
          height =900
    else:
        width, height = [int(x.strip(' ')) for x in output.split(':')[-1].split(' x ')]
## JP 12-14-22


## set definitions
def checkForQuitPress(keyPressed, quitKey):
    if quitKey in keyPressed:
        raise Exception("User manually exited the program.")
        
        
def appendTime(timeRecords, time):
    timeRecords.append(time)
    
    
def psychoPyRetrieveUserInput():
    win = gui.Dlg(title="Input subject's name and input file name.")
    win.addField("Subject name:")
    win.addField("Input file name (EXCLUDE file extension): ")
    win.show()
    return win.data[0], win.data[1] + '.csv'
    

def generateRepeatFileName(subjectName, inputFileName):
    duplicateNum = 0
    name = inputFileName[:-4]
    while os.path.exists(f'{subjectName}/output_for_{name}_duplicate_{duplicateNum}.csv'):
        duplicateNum += 1
    
    return f'{name}_duplicate_{duplicateNum}.csv'


def parseExperimentInputData(fileName):
    trials = []
    
    with open(fileName, 'r') as file:
        reader = csv.reader(file)
        next(reader) # skips the header
        
        for row in reader:
            row = (row[0], float(row[1]))
            trials.append(row)
    
    return trials
    

def runExperiment(imageMode, trials, startFixationTime, continueKey, textFont, textContrast,
                    wordSize, wordColor, instruction, instructionSize, instructionColor, 
                    fixationSize, fixationColor, quitKey):
    words = []
    delays = []
    wordTimes = []
    fixTimes = []
    beep = sound.Sound('B', secs=0.1, volume=0.6)
    expectedTime = startFixationTime
    globalTimer = None
        
    win = visual.Window(color = (0, 0, 0), fullscr=True, colorSpace='rgb255') ## SET TO SPECIFIC COMPUTER
   ## win = visual.Window(size=(width, height), fullscr=True, allowGUI=False, units = "norm",
   ## monitor='testMonitor', colorSpace='rgb', name='win') 

    ##Turn off Mouse
    event.Mouse(visible = False, newPos = [1,-1])

    #fixation = visual.TextBox2(win, font=textFont, text='+', letterHeight=fixationSize, 
    #                            color=fixationColor, contrast=textContrast, 
    #                            alignment='center')
    #fixation = visual.TextBox2(win, font=textFont, text='+', letterHeight=fixationSize, 
    #                            color=fixationColor, contrast=textContrast, alignment='center', 
    #                            pos=(0,0))
    
    fixation =visual.TextStim(win, text='+', font=textFont, pos=(0.0, 0.0), 
                                    color=wordColor, colorSpace='rgb255', height=fixationSize,
                                    opacity=1.0, contrast=textContrast, alignText='center', anchorHoriz='center', 
                                    anchorVert='center')    

    for word, delay in trials: 
        if not imageMode:
           #words.append(visual.TextBox2(win, font=textFont, text=word,
           #letterHeight=wordSize, color=wordColor, 
           #contrast=textContrast, alignment='center',pos=(0,0)))
           
           words.append(visual.TextStim(win, text=word, font=textFont, pos=(0.0, 0.0), 
           color=wordColor, colorSpace='rgb255', height=wordSize,
           opacity=1.0, contrast=textContrast, alignText='center', anchorHoriz='center', 
           anchorVert='center'))

        elif imageMode: 
            words.append(visual.ImageStim(win, image=f'images/{word}'))

        delays.append(delay)

    #startMessage = visual.TextBox2(win, font=textFont, text=instruction, 
    #                                letterHeight=instructionSize, color=instructionColor, 
    #                                contrast=textContrast, alignment='center',pos=(0,0))
    #                                
    startMessage =visual.TextStim(win, text=instruction, font=textFont, pos=(0.0, 0.0), 
                                    color=wordColor, colorSpace='rgb255', height=instructionSize,
                                    opacity=1.0, contrast=textContrast, alignText='center', anchorHoriz='center', 
                                    anchorVert='center')                               

    startMessage.draw()
    win.flip()
    
    keyPressed = event.waitKeys(keyList=[*continueKey, quitKey], clearEvents=False)
    checkForQuitPress(keyPressed, quitKey)
    
    for i in range(len(trials)): 
        
        # First iteration
        if i == 0:
            fixation.draw()
            win.flip()
            
            ## Trigger or Keypress JP 12-14-2022
            scanner_coms.wait_for_message(5) ## censor for laptop/uncensor for MRI; 5 for Mock
            ##scanner_coms.wait_for_message(6) ## censor for laptop/uncensor for MRI; 6 for MRI
            ##keyPressed = event.waitKeys(keyList=[*continueKey, quitKey], clearEvents=False) #censor for MRI/uncensor for laptop
            ## JP 12-14-2022
            
            checkForQuitPress(keyPressed, quitKey)
            globalTimer = core.Clock()
            while globalTimer.getTime() < expectedTime:
                checkForQuitPress(event.getKeys(), quitKey)
                            
                            
                            
        beep.play(when = win.getFutureFlipTime(clock='ptb'))
        core.wait(0.1) ## JP 12-14-22
        beep.stop()## JP 12-14-22
        
        expectedTime += 1
        words[i].draw()
        win.callOnFlip(appendTime, wordTimes, globalTimer.getTime())
        win.flip()
        while globalTimer.getTime() < expectedTime:
            checkForQuitPress(event.getKeys(), quitKey)
        
        expectedTime += delays[i]
        fixation.draw()
        win.callOnFlip(appendTime, fixTimes, globalTimer.getTime())
        win.flip()
        while globalTimer.getTime() < expectedTime:
            checkForQuitPress(event.getKeys(), quitKey)
    
    print("Total time elapsed: " + str(globalTimer.getTime()))
    print("Time expected: " + str(expectedTime))
    win.close()
    
    return wordTimes, fixTimes

    
def getTargetPath(subjectName, fileName):
    targetPath = subjectName
    
    if os.path.isdir(targetPath):
        targetPath += f'/output_for_{fileName}'
        
    else:
        os.mkdir(targetPath)
        targetPath += f'/output_for_{fileName}'
        
    return targetPath
    
    
if __name__ == '__main__':
    
    # -------------------- CUSTOMIZE PROGRAM HERE --------------------
    continueKey = ['6']
    startFixationTime = 3.75
    textFont = 'Arial'
    textContrast = 1
    wordSize = 0.22
    wordColor = (190, 190, 190)
    instruction = "Read the made up words out loud. Try not to move your head."
    instructionSize = 0.1
    instructionColor = (190, 190, 190)
    fixationSize = 0.14
    fixationColor = (190, 190, 190)
    quitKey = 'q'
    imageMode = False
    
    subjectName, fileName = psychoPyRetrieveUserInput()
    if not os.path.exists(fileName):
        raise Exception("Invalid file.")
    
    trials = parseExperimentInputData(fileName)
    if os.path.exists(f'{subjectName}/output_for_{fileName}'):
        
        win = gui.Dlg(title = "Confirm repeat run!")

        win.addField(f"{fileName} has already been ran for the subject,  {subjectName}.\n" 
        + "Proceed anyways?", choices=(('NO', 'YES')))
        win.show()
        if win.data[0] == 'NO':
            core.quit()
        elif win.data[0] == 'YES': 
            fileName = generateRepeatFileName(subjectName, fileName)
    
    wordTimes, fixTimes = runExperiment(imageMode, trials, startFixationTime, continueKey, textFont,
                            textContrast, wordSize, wordColor, instruction, instructionSize, 
                            instructionColor, fixationSize, fixationColor, quitKey) 
                            
  
    targetOutputPath = getTargetPath(subjectName, fileName)
    with open(targetOutputPath, 'w', newline='') as file:
        
        writer = csv.writer(file)
        writer.writerow(['word', 'delay', 'word onset', 'fix onset'])
        
        for i, (word, delay) in enumerate(trials):
            row = [word, delay, wordTimes[i], fixTimes[i]]
            writer.writerow(row)
