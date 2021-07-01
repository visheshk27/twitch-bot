import socket
import random
import pyautogui
import time
import random
from threading import Thread
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os

TWICH_NAME = ""
TOKEN_FILE = open(os.path.dirname(os.path.realpath(__file__)) + '/twitch-auth.txt', 'r')
TOKEN = TOKEN_FILE.read()
TOKEN_FILE.close()

class TinderBot():
    def __init__(self):
        self.driver = webdriver.Chrome()


    def start(self):
        self.driver.get('https://tinder.com')
     

        # # Like the girl
    def clickLike(self):
        try:
            clickLike = self.driver.find_element_by_xpath('//*[@id="Tinder"]/body')
            clickLike.send_keys(Keys.ARROW_RIGHT)
        except:
            print('except!')

        # # Disike the girl
    def clickDislike(self):
        clickDislike = self.driver.find_element_by_xpath('//*[@id="Tinder"]/body')
        clickDislike.send_keys(Keys.ARROW_LEFT)

        # # Handle picture scrolling....
    def nextPic(self):
        nPic = self.driver.find_element_by_xpath('//*[@id="Tinder"]/body')
        nPic.send_keys(Keys.SPACE)

        # Send message to match
    def matchMessage(self):
        msgIn = self.driver.find_element_by_xpath('//*[@id="chat-text-area"]')
        msgIn.click()
        theMessage = ('hi :D')
        msgIn.send_keys(theMessage)
        sendBtn = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div/div/div[3]/div[3]/form/button')
        sendBtn.click()


def like():
    bot.clickLike()

def dislike():
    bot.clickDislike()

def sendTinMessage():
    bot.matchMessage()
    




min = 1
max = 10

eventLoop = False

votingStarted = False
votingTied = False
votingYes = []
votingNo = []
votingYesPrevious = []
votingNoPrevious = []
votingWonPrevious = False
votingTieBreakerEnabled = True
votingWinnerWhoCanMessage = False

SERVER = "irc.twitch.tv"
PORT = 6667
PASS = TOKEN
BOT ="TwitchBot"
CHANNEL = TWICH_NAME
OWNER = TWICH_NAME
irc = socket.socket()
irc.connect((SERVER, PORT))
irc.send((  "PASS " + PASS + "\n" +
            "NICK " + BOT + "\n" +
            "JOIN #" + CHANNEL + "\n").encode())

bot = TinderBot()
sleep(2)
bot.start()

def joinchat():
    Loading = True
    while Loading:
        readbuffer_join = irc.recv(1024)
        readbuffer_join = readbuffer_join.decode()
        for line in readbuffer_join.split("\n")[0:-1]:
            print(line)
            loading = loadingComplete(line)
        if loading == False:
            break

def loadingComplete(line):
    if("End of /NAMES list" in line):
        print("Bot has joined " + CHANNEL + "'s Channel!")
        sendMessage(irc, "Chat room joined!")
        return False
    else:
        return True

def loadingComplete(line):
    if("End of /NAMES list" in line):
        print("Bot has joined " + CHANNEL + "'s Channel!")
        sendMessage(irc, "Chat room joined!")
        return False
    else:
        return True

def sendMessage(irc, message):
    messageTemp = "PRIVMSG #" + CHANNEL + " :" + message
    irc.send((messageTemp + "\n").encode())

def getUser(line):
    seperate = line.split(":", 2)
    user = seperate[1].split("!", 1)[0]
    return user

def getMessage(line):
    try:
        message = (line.split(":", 2))[2]
    except:
        message = ""

    return message

def Console(line):
    if "PRIVMSG" in line:
        return False
    else: 
        return True

def rollDice():
    return random.randint(min,max)


joinchat()

def votingEndWinnerMessaging(winner, winnerDidType = False):
    global votingWinnerWhoCanMessage

    if votingWinnerWhoCanMessage == winner:
        if winnerDidType:
            sendMessage(irc, "@" + votingWinnerWhoCanMessage + " Your message has been sent! Everyone can now vote for the next swipe by typing '!vote yes' or '!vote no'")
        else:
            sendMessage(irc, "@" + votingWinnerWhoCanMessage + " Your 30 seconds is up! Everyone can now vote for the next swipe by typing '!vote yes' or '!vote no'")
        
        votingWinnerWhoCanMessage = False

def votingChooseWinner():
    global eventLoop, votingStarted, votingTied, votingYes, votingNo, votingYesPrevious, votingNoPrevious, votingWonPrevious, votingTieBreakerEnabled, votingWinnerWhoCanMessage
    # Choose a user randomly from the list of people who voted for the winning result
    winner = False
    if votingWonPrevious == "yes":
        winner = random.choice(votingYesPrevious).lower()
    elif votingWonPrevious == "no":
        winner = random.choice(votingNoPrevious).lower()

    if winner != False:
        if votingStarted != False:
            # Stop the current swipe vote because there was a match to message
            votingStarted = False

        print("OMG THE FREAKING USER " + winner + " WON THE FREAKIN SWIPE THINGY SO GG")

        # Notify the user that won how to send a message
        sendMessage(irc, "@" + winner + " has 30 seconds to message the current match! Type '!msg your chat message' to send this match a message.")
        
        # Save the winner to our global variable
        votingWinnerWhoCanMessage = winner
        
        # Give the winning user 30 seconds to message the match
        sleep(30)

        votingEndWinnerMessaging(winner)



def votingFinished(winningVote, votingYes, votingNo):
    global eventLoop, votingStarted, votingTied, votingYesPrevious, votingNoPrevious, votingWonPrevious, votingTieBreakerEnabled, votingWinnerWhoCanMessage
    
    if votingWinnerWhoCanMessage != False:
        # Do not continue if the stream owner typed !match
        return
    
    votingWonPrevious = winningVote

    finalMessage = False
    if winningVote == "yes":
        finalMessage = "Yes won with " + str(len(votingYesPrevious)) + " votes to " + str(len(votingNoPrevious)) + ". Swiping right..."
        like()
    else:
        finalMessage = "No won with " + str(len(votingYesPrevious)) + " votes to " + str(len(votingNoPrevious)) + ". Swiping left..."
        dislike()

    print(finalMessage)
    sendMessage(irc, finalMessage)



def votingTimer():
    global eventLoop, votingStarted, votingTied, votingYes, votingNo, votingYesPrevious, votingNoPrevious, votingWonPrevious, votingTieBreakerEnabled, votingWinnerWhoCanMessage
    
    if votingStarted == False:
        return False

    print("VOTING HAS STARTED!!!")
    sendMessage(irc, "Swipe voting has started. Type '!vote yes' to swipe right or '!vote no' to swipe left. If we match then a voter is selected at random to send a message and has 30 seconds to write and submit it to chat")

    for x in range(0,10):
        if votingWinnerWhoCanMessage != False:
            # Do not continue if the stream owner typed !match
            return

        sleep(2)

        if votingWinnerWhoCanMessage != False:
            # Do not continue if the stream owner typed !match
            return

        print("SCROLLING THROUGH PIC (" + str(x+1) + ")")
        bot.nextPic()

    if votingWinnerWhoCanMessage != False:
        # Do not continue if the stream owner typed !match
        return

    # Save the list of people who voted
    votingYesPrevious = votingYes.copy()
    votingNoPrevious = votingNo.copy()

    # If there was previously an unsettled tie, reset that
    votingTied = False
    
    # Check how many people voted yes vs no
    votingYesCount = len(votingYes)
    votingNoCount = len(votingNo)

    if votingYesCount == votingNoCount:
        if votingTieBreakerEnabled:
            # Tie breaker minigame
            # print("IT'S A TIE! WHOEVER TYPES !tie yes OR !tie no FIRST WINS THE TIE BREAKER!")
            # Randomly select yes or no
            votingFinished(random.choice(["yes", "no"]), votingYesPrevious, votingNoPrevious)
            votingTied = True
        else:
            # Randomly select yes or no
            votingFinished(random.choice(["yes", "no"]), votingYesPrevious, votingNoPrevious)
    elif votingYesCount > votingNoCount:
        votingFinished("yes", votingYesPrevious, votingNoPrevious)
    elif votingNoCount > votingYesCount:
        votingFinished("no", votingYesPrevious, votingNoPrevious)

    # Reset the voting data for the next round of votes
    votingStarted = False
    votingYes = []
    votingNo = []

def main():
    global eventLoop, votingStarted, votingTied, votingYes, votingNo, votingYesPrevious, votingNoPrevious, votingWonPrevious, votingTieBreakerEnabled, votingWinnerWhoCanMessage

    

    # read what chat is saying, input by inpuit
    while True:
        try:
            readbuffer = irc.recv(1024).decode()
        except:
            readbuffer = ""
        for line in readbuffer.split("\r\n"):
            if line == "":
                continue
    # handle if the input is a twitch ping
            elif "PING" in line and Console(line):
                msgg = "PONG tmi.twitch.tv\r\n".encode()
                irc.send(msgg)
                print(msgg)
                continue
            else:
                user = getUser(line)
                message = getMessage(line)
                print(user + " : " + message)

                messageLower = message.lstrip().lower()
                if messageLower[0:5] == "!vote" and user not in votingYes and user not in votingNo and votingWinnerWhoCanMessage == False:
                    if "!vote yes" in messageLower:
                        # Add this user to the list of people who have voted yes
                        votingYes.append(user)
                    elif "!vote no" in messageLower:
                        # Add this user to the list of people who have voted no
                        votingNo.append(user)

                    # Start the voting timer if it hasn't been started yet
                    if votingStarted == False:
                        votingStarted = Thread(target=votingTimer, args=())
                        votingStarted.start()
                elif messageLower[0:6] == "!match" and user == OWNER and votingWinnerWhoCanMessage == False:
                    # Owner is requesting to choose someone that gets to message the match, choose a user at random
                    thread = Thread(target=votingChooseWinner, args=())
                    thread.start()
                elif messageLower[0:4] == "!msg" and user.lower() == votingWinnerWhoCanMessage:
                    # Click the message text input on the match popup
                    sendTinMessage()

                    # Winning user is messaging a match, send keyboard text input
                    pyautogui.typewrite(messageLower[5:] + '\n', interval=.1)

                    votingEndWinnerMessaging(votingWinnerWhoCanMessage, True)

                if votingTied and votingWinnerWhoCanMessage == False:
                    tieLower = message.lstrip().lower()
                    if tieLower[0:4] == "!tie":
                        if "!tie yes" in tieLower:
                            votingFinished("yes", votingYesPrevious, votingNoPrevious)
                        elif "!tie no" in tieLower:
                           votingFinished("no", votingYesPrevious, votingNoPrevious)

                        votingTied = False




if __name__ == '__main__':
    # Start processing chat messages
    main()
