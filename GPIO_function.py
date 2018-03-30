
#------------------------------------------------------------------------------
###MADE BY:ERICK TERRAZAS LAST EDIT:3/29/14###
###ECE 493 Senior Design: Project LISSA
##/////////////////////GPIO_func.py////////////////////////////////////////////////

# Objectives of file:
# 1.Drive high voltage for enable of FEM using GPIO pin of adafruit FT232h board
# 2.While Enable is driven high, another GPIO pin should be driven low for Rx
# 3. While enable is driven high, another GPIO pin should be driven high for Tx
# 4. Initialize USB PORT CONNECTION
# 5. Start up clock signal using extra GPIO pin
# NOTE: Threading is implemented in order to create a 'clock" with a frequency addherent
# to the sequential logic desired for control signal input (f = 1/ 40ms)

### MODULES------------------------------------------------------------------------
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
import time # For time
import threading

# END MODULES----------------------------------------------------------------------

###DEFINITIONS---------------------------------------------------------------------
class GPIO_function:
    clk_freq  =
    def __init__(self):
        print 'INITIALIZE GPIO BOARD'
        FT232H.use_FT232H()             #Temorarily disable FTDI Driver
        self.ft232h = FT232H.FT232H()   #Find device
        self.ft232h.setup(8,GPIO.OUT)   #PIN 8 maps to BOARD PORT C0    CONTROL SIGNAL
        self.ft232h.setup(9,GPIO.OUT)   #PIN 9 maps to BOARD PORT C1   ENABLE SIGNAL
        self.ft232h.setup(10,GPIO.OUT)  # PIN 10 maps to BOARD PORT C2   CLOCK SIGNAL
        self.initial = int(0)           #to be used for time displacement of cmd
        self.final = int(0)             #to be used for time displacement of cmd
        self.clock = threading.Thread(target=self.executeThread)      #Thread exclusively for CLOCK (C2)

    def ENABLE_FEM(self,switch=0):
        initial = time.clock()  #Start clocking in time displacement
               #zero for seq_switch means we want DC voltage levels
        if (switch == 0):  # We want to turn of DC voltage
            print
            '\nFEM SHUTTING DOWN...'
            self.ft232h.output(9,GPIO.LOW)  # TURN ENABLE  GPIO OFF(DC)
            time.sleep(0.4)  # Cautionary pause to avoid data overload of GPIO board
            #self.ft232h.output(8, GPIO.LOW)  # Drive Control signal to low voltage by default
            self.final = time.clock()  # time final timestamp
            print
            "Time elapsed:", (self.final - self.initial)
        elif (switch == 1):  # Turn on ENABLE
            print
            '\nFEM ACTIVATING...'
            self.ft232h.output(9, GPIO.HIGH)  # TURN ENABLE SIGNAL ON(DC)
            time.sleep(0.4)
            print
            "Time elapsed:", (self.final - self.initial)
        else:
            raise ValueError('MUST INPUT integer 1 (ON) or integer 0 (OFF)')
            return


    def TX_FEM(self):
        print '\nFEM ----> TX MODE'
        self.ft232h.output(8,GPIO.HIGH)          #DRIVE CONTROL SIGNAL TO HIGH VOLTAGE
        time.sleep(0.2)
        return

    def RX_FEM(self):
        print '\nFEM ----> RX MODE'
        self.ft232h.output(8,GPIO.LOW)           #DRIVE CONTROL SIGNAL TO LOW VOLTAGE
        time.sleep(0.2)
        return

    def runclock(self):
        self.clock.start()  #Run thread self.clock and therfore call def executeThread

    def shutdown(self):
        self.clock.exit()

    def executeThread(self):        #EXECUTES CLOCK SIGNAL USING GPIO PIN C2
        print "Thread {} starts at {}".format(1,time.strftime("%H:%M:%S",time.gmtime()))
        while True:
            #print "---Thread is High at {}".format(time.strftime("%H:%M:%S",time.gmtime()))
            self.ft232h.output(10,GPIO.HIGH)
            time.sleep(1/clkc_freq)
            #print "---Thread is Low at {}".format(time.strftime("%H:%M:%S", time.gmtime()))
            self.ft232h.output(10,GPIO.LOW)
            time.sleep(1/clkc_freq)

