from psychopy import visual, event, core, gui, sound
import csv
import tkinter as tk
import os
import sys


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
    beep = sound.Sound('B', secs=0.1, volume=0.1)
    expectedTime = startFixationTime
    globalTimer = None
        
    win = visual.Window(color = (255, 255, 255), fullscr=True)
    fixation = visual.TextBox2(win, font=textFont, text='+', letterHeight=fixationSize, 
                                color=fixationColor, contrast=textContrast, 
                                alignment='center')
                
    for word, delay in trials: 
        
        if not imageMode:
            words.append(visual.TextBox2(win, font=textFont, text=word,
                                        letterHeight=wordSize, color=wordColor, 
                                        contrast=textContrast, alignment='center'))
        elif imageMode: 
            words.append(visual.ImageStim(win, image=f'images/{word}'))
            
        delays.append(delay)
                                
    startMessage = visual.TextBox2(win, font=textFont, text=instruction, 
                                    letterHeight=instructionSize, color=instructionColor, 
                                    contrast=textContrast, alignment='center', size=(2, None))
    startMessage.draw()
    win.flip()
    
    keyPressed = event.waitKeys(keyList=[*continueKey, quitKey], clearEvents=False)
    checkForQuitPress(keyPressed, quitKey)
    
    for i in range(len(trials)): 
        
        # First iteration
        if i == 0:
            fixation.draw()
            win.flip()
            keyPressed = event.waitKeys(keyList=[*continueKey, quitKey], clearEvents=False)
            checkForQuitPress(keyPressed, quitKey)
            globalTimer = core.Clock()
            while globalTimer.getTime() < expectedTime:
                checkForQuitPress(event.getKeys(), quitKey)
                            
        beep.play(when = win.getFutureFlipTime(clock='ptb'))
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
    continueKey = ['t']
    startFixationTime = 6
    textFont = 'Arial'
    textContrast = 1
    wordSize = 0.20
    wordColor = (-128, -128, -128)
    instruction = "Random instructions here. Read this if you want :)"
    instructionSize = 0.1
    instructionColor = (-128, -128, -128)
    fixationSize = 0.10
    fixationColor = (-128, -128, -128)
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
