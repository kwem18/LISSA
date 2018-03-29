
#------------------------------------------------------------------------------
###MADE BY:ERICK TERRAZAS 3/28/14###
###ECE 493 Senior Design: Project LISSA
##/////////////////////GPIO_func.py////////////////////////////////////////////////

# Objectives of file:
# 1.Drive high voltage for enable of FEM using GPIO pin of adafruit FT232h board
# 2.While Enable is driven high, another GPIO pin should be driven low for Rx
# 3. While enable is driven high, another GPIO pin should be driven high for Tx
# 4. Initialize USB PORT CONNECTION

### MODULES------------------------------------------------------------------------
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
import time # For time


# END MODULES----------------------------------------------------------------------

###DEFINITIONS---------------------------------------------------------------------
class GPIO_function:

    def __init__(self):
        print 'INITIALIZE GPIO BOARD'
        FT232H.use_FT232H()             #Temorarily disable FTDI Driver
        self.ft232h = FT232H.FT232H()    #Find device
        self.ft232h.setup(8,GPIO.OUT)    #PIN 8 maps to BOARD PORT C0    CONTROL SIGNAL
        self.ft232h.setup(9,GPIO.OUT)   #PINT 9 maps to BOARD PORT C1   ENABLE SIGNAL
        self.initial = int(0)
        self.final = int(0)


    def ENABLE_FEM(self,switch):
        initial = time.clock()  #Start clocking in time displacement
        if (switch == 0):
            print '\nFEM SHUTTING DOWN...'
            self.ft232h.output(9,GPIO.LOW)       #TURN ENABLE SIGNAL OFF
            time.sleep(0.4)                 #Cautionary pause to avoid data overload of GPIO board
            self.ft232h.output(8,GPIO.LOW)       #Drive Control signal to low voltage
            self.final = time.clock()
            print "Time elapsed:",(self.final- self.initial)

        elif (switch == 1):
            print '\nFEM ACTIVATING...'
            self.ft232h.output(9,GPIO.HIGH)      #TURN ENABLE SIGNAL ON
            time.sleep(0.4)
            print "Time elapsed:",(self.final - self.initial)

        else:
            raise ValueError('MUST INPUT integer 1 (ON) or integer 0 (OFF)')
            return

        return


    def TX_FEM(self):
        print '\nFEM ----> TX MODE'
        self.ft232h.output(8,GPIO.HIGH)          #DRIVE CONTROL SIGNAL TO HIGH VOLTAGE
        time.sleep(0.4)
        return

    def RX_FEM(self):
        print '\nFEM ----> RX MODE'
        self.ft232h.output(8,GPIO.LOW)           #DRIVE CONTROL SIGNAL TO LOW VOLTAGE
        time.sleep(0.4)
        return


