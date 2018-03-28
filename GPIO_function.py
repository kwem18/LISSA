###ERICK TERRAZAS 3/28/14###
###ECE 493 Senior Design: Project LISSA
##/////////////////////GPIO_func.py////////////////////////////////////////////////

# Objectives of file:
# 1.Drive high voltage for enable of FEM using GPIO pin of adafruit FT232h board
# 2.While Enable is driven high, another GPIO pin should be driven low for Rx
# 3. While enable is driven high, another GPIO pin should be driven hihg for Tx
# 4. Initialize USB PORT CONNECTION

### MODULES------------------------------------------------------------------------
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
import time # For time stamp


# END MODULES----------------------------------------------------------------------

###DEFINITIONS---------------------------------------------------------------------

def INIT_FEM():
    print 'INITIALIZE GPIO BOARD...'
    FT232H.use_FT232H()         #Temorarily disable FTDI Driver
    ft232h = FT232H.FT232H()    #Find device
    ft232h.setup(8,GPIO.OUT)    #PIN 8 maps to BOARD PORT C0    CONTROL SIGNAL
    ft232h.setup(9,GPIO.OUT)   #PINT 9 maps to BOARD PORT C1   ENABLE SIGNAL
    return


def ENABLE_FEM(switch):
    initial = time.clock()  #Start clocking in time displacement
    #FT232H.use_FT232H() #Temorarily dsiable FTDI Driver
    #ft232h = FT232H.FT232H()    #Find device
    #ft232h.setup(8,GPIO.OUT)    #PIN 8 maps to BOARD PORT C0    CONTROL SIGNAL
    #ft232h.sestup(9,GPIO.OUT)   #PINT 9 maps to BOARD PORT C1   ENABLE SIGNAL
    if (switch == 0):
        print '\nFEM SHUTTING DOWN...'
        ft232h.output(9,GPIO.LOW)       #TURN ENABLE SIGNAL OFF
        time,sleep(0.4)                 #Cautionary pause to avoid data overload of GPIO board
        ft232h.output(8,GPIO.LOW)       #Drive Control signal to low voltage
        final = time.clock()
        print "Time elapsed:",final-initial

    elif (switch == 1):
        print '\nFEM ACTIVATING...'
        ft232h.output(9,GPIO.HIGH)      #TURN ENABLE SIGNAL ON
        time.sleep(0.4)
        print
        "Time elapsed:", final - initial

    else:
        raise ValueError('MUST INPUT integer 1 (ON) or integer 0 (OFF)')
        return

    return


def TX_FEM():
    print '\nFEM ----> TX MODE'
    ft232h.output(8,GPIO.HIGH)          #DRIVE CONTROL SIGNAL TO HIGH VOLTAGE
    time.sleep(0.4)
    return

def RX_FEM():
    print '\nFEM ----> RX MODE'
    ft232h.output(8,GPIO.LOW)           #DRIVE CONTROL SIGNAL TO LOW VOLTAGE
    time.sleep(0.4)
    return


