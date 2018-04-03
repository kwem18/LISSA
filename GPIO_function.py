
#------------------------------------------------------------------------------
###MADE BY:ERICK TERRAZAS 3/30/18###
###ECE 493 Senior Design: Project LISSA
##/////////////////////GPIO_func.py////////////////////////////////////////////////

# Objectives of file:
# 1.Drive high voltage for enable of FEM using GPIO pin of adafruit FT232h board
# 2.While Enable is driven high, another GPIO pin should be driven low for Rx
# 3. While enable is driven high, another GPIO pin should be driven high for Tx
# 4. Initialize USB PORT CONNECTION
# NOTE: Threading is implemented in order to create a 'clock" with a frequency addherent
# to the sequential logic desired for control signal input (f = 1/ 40ms)

### MODULES------------------------------------------------------------------------
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
import time # For time
import threading            #For clock signal implementation

# END MODULES----------------------------------------------------------------------

###DEFINITIONS---------------------------------------------------------------------
class GPIO_function:
    clk_freq = float(25)
    def __init__(self,sync=0):
        print('INITIALIZE GPIO BOARD')
        FT232H.use_FT232H()             #Temorarily disable FTDI Driver
        self.ft232h = FT232H.FT232H()   #Find device
        self.ft232h.setup(8,GPIO.OUT)   #PIN 8 maps to BOARD PORT C0    CONTROL SIGNAL
        self.ft232h.setup(9,GPIO.OUT)   #PIN 9 maps to BOARD PORT C1   ENABLE SIGNAL
        self.ft232h.setup(10,GPIO.OUT)  # PIN 10 maps to BOARD PORT C2   CLOCK SIGNAL
        self.initial = int(0)           #to be used for time displacement of cmd
        self.final = int(0)             #to be used for time displacement of cmd
        self.clock = threading.Thread(target=self.run_clock)      #Thread exclusively for CLOCK (C2)
        self.paused = False
        self.pause_cond = threading.Condition(threading.Lock())
        self.clk_freq = float(25)       #Frequency of clock signal definition executeThread
        self.sync = int(sync)           #sync determines whether or not we want sequential ginsl in ADAFRUIT PIN C2
        self.off = int(1)
        self.clock.setDaemon(False)     #redundant line to make sure that thread ends when main function ends

    def ENABLE_FEM(self,switch=0):
        initial = time.clock()                  #Start clocking in time displacement
        if (switch == 0):                       # We want to turn off DC voltage
            print('\nFEM SHUTTING DOWN...')
            self.ft232h.output(9,GPIO.LOW)      # TURN ENABLE  GPIO OFF(DC)
            time.sleep(0.4)                     # Cautionary pause to avoid data overload of GPIO board
            #self.ft232h.output(8, GPIO.LOW)    # Drive Control signal to low voltage by default
            self.final = time.clock()           # time final timestamp
            print('Time elapsed:' + str((self.final - self.initial)) )
        elif (switch == 1):                     # Turn on ENABLE
            print('\nFEM ACTIVATING...')
            self.ft232h.output(9, GPIO.HIGH)    # TURN ENABLE SIGNAL ON(DC)
            time.sleep(0.4)                     #system sleep to prevent GPIO board data overload
            if self.sync == 1 & self.paused == False:        #FOr runnning lock for the first time
                self.start_clock()    #call runclock definition that starts thread (produces clock signal at pin C2(ADAFRUIT) )
            if self.sync == 1 & self.paused == True:     #FOr starting the clock again if paused
                self.resume_clock()
            print("Time elapsed: " + str(self.final - self.initial) )
        else:
            raise ValueError('MUST INPUT integer 1 (ON) or integer 0 (OFF)')



    def TX_FEM(self):
        print('\nFEM ----> TX MODE')
        self.ft232h.output(8,GPIO.HIGH)          #DRIVE CONTROL SIGNAL TO HIGH VOLTAGE
        time.sleep(0.2)
        return

    def RX_FEM(self):
        print('\nFEM ----> RX MODE')
        self.ft232h.output(8,GPIO.LOW)           #DRIVE CONTROL SIGNAL TO LOW VOLTAGE
        time.sleep(0.2)
        return

    def start_clock(self):     #runs clock thread intilzaed as self.clock (in __init__)
        self.clock.start()  #Run thread self.clock and therfore call def executeThread

    def resume_clock(self):
        self.paused = False
        self.pause_cond.notify()
        self.pause_cond.release()

    def pause_clock(self):
        self.paused = True
        self.pause_cond.acquire()


    def run_clock(self):        #EXECUTES CLOCK SIGNAL SOFTWARE LOGIC USING GPIO PIN C2
        half_period = (float(1) / self.clk_freq) / float(2)
        while self.off != 0:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()


                self.ft232h.output(10,GPIO.HIGH)        #Drive PIN C2 HIGH
                time.sleep(half_period)
                #print "---Thread is Low at {}".format(time.strftime("%H:%M:%S", time.gmtime()))
                self.ft232h.output(10,GPIO.LOW)         #Drive PIN C2 LOW
                time.sleep(half_period)


        # print('ENABLE_FEM(switch=1) called.\nCLOCK (PIN C2) START')
        # while self.off != 0:
        #     #print "---Thread is High at {}".format(time.strftime("%H:%M:%S",time.gmtime()))
        #     half_period = (float(1)/self.clk_freq)/float(2)
        #     self.ft232h.output(10,GPIO.HIGH)        #Drive PIN C2 HIGH
        #     time.sleep(half_period)
        #     #print "---Thread is Low at {}".format(time.strftime("%H:%M:%S", time.gmtime()))
        #     self.ft232h.output(10,GPIO.LOW)         #Drive PIN C2 LOW
        #     time.sleep(half_period)
        #
        # print('Thread is dead')

    def shutdown(self):
        if(self.sync==1):
            self.off = 0                  #STOP clock(PIN C2) using self.off

        self.ft232h.output(10,GPIO.LOW)
        time.sleep(0.2)
        self.ft232h.output(8,GPIO.LOW)      #Drive control port(PIN C0) LOW
        time.sleep(0.2)
        self.ft232h.output(9,GPIO.LOW)      #Drive Enable port (PIN C1) LOW
        time.sleep(0.2)
        print('Shutdown conducted.')