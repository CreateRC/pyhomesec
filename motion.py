from gpiozero import MotionSensor, LED, Button
import RPi.GPIO as io
from time import sleep
from datetime import datetime
import smtplib
import urllib.request

from cryptography.fernet import Fernet

def encryption():
    key = ""
    val = b"gAAAAABgL_ZlyFNSle9IMDA5GeIGOtdWNRXGSNnzqk3IWC2XR5mOwF5XL8vVFQ5UblgQj_Fk7m5n0zVPZh1XU0nKsdGOTRRNXQ=="
    f = Fernet(key)
    pw = str(f.decrypt(val))
    fin = pw[2:-1]
    return fin

def main():
    #Motion sensor
    motion = MotionSensor(21)

    #Reed switch (GPIO 20)
    io.setup(20, io.IN, pull_up_down=io.PUD_UP)

    #Define items
    ledAlert = LED(19, active_high = False)
    ledArmed = LED(26, active_high = False)
    button = Button(17, bounce_time = 0.25)

    #Create system
    armed = False
    tripped = False

    #Network access
    try:
            urllib.request.urlopen("http://www.google.com").close()

    except urllib.request.URLError:
        print("Network not up yet")
        time.sleep(10)
    else:
        print("Network connected")

    while True:
        #What even is time
        now = datetime.now()
        time = now.strftime("%H:%M:%S")

        #Begin system evaluation
        if button.value == 1:
            armed = not armed
            # The button means we want change, so change above
            # and test and print the status below
            if armed == False:
                ledArmed.off()
                print("\nSystem disarmed")
                notification(encryption(), time, 0)
                sleep(1)
            else:
                ledArmed.on()
                print("\nSystem armed")
                notification(encryption(), time, 1)
                sleep(1)
        else:
            status(armed, time)
            sleep(1)

        if armed == True:
            detection(motion, ledAlert, time)
        else:
            ledAlert.off()
            pass

def startup():
    #Allow sensor startup time
    print(f" ~ System startup...", end = "\r")
    sleep(3)

def status(armed, time):
    print(f" ~ Status: {armed} || Time: {time}", end = "\r")
    
def detection(motion, ledAlert, time):
    if (motion.value == 1) or io.input(20): #motion true, or reed true
        print("Motion Detected")
        ledAlert.on()
        notification(encryption(), time, 2)
    elif motion.value == 0:
        ledAlert.off()
    else:
        print("motion value !0 or 1")
    sleep(.5)

def notification(fin, time, msgtype):
    user = "pifreedom45@gmail.com"
    password = "{}".format(fin)
    to = ['5139030799@vtext.com']

    subject = 'Security System Alert'
    sent_from = user
    if msgtype == 0:
        body = 'System disarmed at ' + str(time)
    elif msgtype == 1:
        body = 'System armed at ' + str(time)
    else:
        body = 'Motion was detected at ' + str(time)

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % ('PiFreedom Security', to, subject, body)

    try:
            server = smtplib.SMTP_SSL('smtp.gmail.com',465)
            server.ehlo()
            server.login(user, password)
            server.sendmail(sent_from, to, email_text)
            server.close()
            print("Text sent!")
    except:
            print("Something went wrong")
    
startup()
main()




