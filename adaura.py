import serial
import time
import sys
import os
import glob

'''
DEPENDENCY:

sudo pip install pySerial

PARAMETERS:
  Total: 2
  A. searchStr     String to search for in serial COM port name
  B. command       Command to send to COM connection
DESCRIPTION
This script automatically finds and connects to serial COM port
with a specified search string designated by the first input
parameter.
REQUIREMENTS
OS:      Windows
Python:  2.7
MODULES
pySerial module installed
EXAMPLE USAGE
NT_attenuation_control.py "2-Channel RF Attenuator" "SAA 63"
// Will connect and set all channels to 63
NT_attenuation_control.py "4-Channel RF Attenuator" "STATUS"
// Will connect and returns the status of channels
'''

class ADUSB4A:

  '''

  Initialize USB-Serial port for AD-USB4A

  '''


  def __init__(self,port):

    self.port = port
    self.ser = serial.Serial(port=self.port,baudrate=115200,bytesize=8,timeout=0.5)
      

  '''

  Open USB-Serial port and flush buffer

  '''

  def open_ser(self):

    try: 
      self.ser.open()
    except Exception, e:
      print "error opening the serial port: " + str(e)
      exit()

    if self.ser.isOpen():
      try:
          self.ser.flushInput() #flush input buffer, discarding all its contents
          self.ser.flushOutput()#flush output buffer, aborting current output 
                   #and discard all that is in buffer
      except Exception, e1:
          print "error communicating...: " + str(e1)
    else:
      print "cannot open serial port "

  '''

  Set a single port to an attenuation value between 0 and 63 dB

  '''

  def set_port(self,port_n,att_val):
    self.ser.write('SET %s %s\r\n'%(port_n,att_val))
    time.sleep(0.2)
    self.response = self.ser.readlines()
    print "\n>> Port %s set to %s dB\n" %(port_n,att_val)

  '''

  Set all ports to an attenuation value between 0 and 63 dB

  '''

  def set_all_ports(self,att_val):
    self.ser.write('SAA %s\r\n'%att_val)
    time.sleep(0.2)
    self.response = self.ser.readlines()
    print "\n>> All ports set to %s dB\n" %att_val
   

  def get_status(self):
    self.ser.write('STATUS\r\n')
    time.sleep(0.2)
    self.response = self.ser.readlines()
    return self.response

def find_multiple_ADUSB4():
  #id1 = 0x100000749
  #id2 = 0x100000a67
  if sys.platform  == 'darwin':
    devices = glob.glob('/dev/tty.usbmodem*')
  elif sys.platform == 'linux2':
    devices = glob.glob('/dev/ttyACM*')  
  return devices

if __name__ == "__main__":

  devs = find_multiple_ADUSB4()
  print devs
  att1 = ADUSB4A(devs[1])
  att1.set_all_ports(sys.argv[1])  
  att2 = ADUSB4A(devs[0])
  att2.set_all_ports(sys.argv[2])

  ################################
  #print sys.argv[1]
  #print sys.argv[2]
  #att1.set_port(2,20)
  #AD_STAT = att1.get_status()
  #print AD_STAT[4]
  #for att in range (0,64):
  #  att1.set_all_ports(att)
  #  time.sleep(1)















