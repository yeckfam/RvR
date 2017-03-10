import time
import telnetlib

class VariableAttenuator:

	def __init__(self):
		self._min_attenuation = 0
		self._max_attenuation = 1000


	def check_attenuation_values(self, values):
	
		for value in values:
			#check to see if attenuation is between min/max
			if (float(value) > self._max_attenuation):
				print float(value)
				print self._max_attenuation
				print 'Attenuation setting %s is higher than max setting of %s.' %(str(value), str(self._min_attenuation))
				exit()	
					
			if (float(value) <self._min_attenuation):
				print float(value)
				print self._min_attenuation
				print 'Attenuation setting %s is lower than min setting of %s.', (str(value), str(self._max_attenuation))
				exit()		


class ManualAttenuator(VariableAttenuator):

	def set_attenuation(self, value):
		self.attenuation = value
		if value == 'None':
			pass
		else:
			raw_input("\nSet attenuation to %sdB, then press enter to continue." % (value))


	def __init__(self):
 		self._min_attenuation = 0
		self._max_attenuation = 70

 				
class MiniAttenuator(VariableAttenuator):
	def __init__(self, ip):
		self.ip = ip
		self.tries = 3 #number of times it will try a command
		self._min_attenuation = 0
		self._max_attenuation = 90

		
	def _open_connection(self):
		#TODO: check to to see if telnet connection actually opens successfully and catch this
		telnet_connection = telnetlib.Telnet(self.ip)
		time.sleep(0.1)
		return telnet_connection	


	def _close_connection(self, telnet_connection):
		telnet_connection.close()


	def set_attenuation(self, value):		
		''' This sets the attenuation on Attenuator.  
			It opens and then closes the telnet connection to the attenuator every time it set it,
			Because some of these devices suck at having a persistent connection open to them.
		'''
		tn = self._open_connection()
		
		for i in range(self.tries):		
			attenuation_str = 'setatt=' + str(value) + '\r\n'
			tn.write(attenuation_str)
			tn.expect([r'\S*[0|1]\S*'], timeout=5)
			
			setting = self._get_attenuation(tn)
			if setting == -1:
				print 'Attenuator failed to set to: ' + str(value)				
				continue
			if float(setting) == float(value):
				print 'Attenuator correctly set to: ' + str(value)
				break		
			
		self._close_connection(tn)

		
	def _get_attenuation(self, telnet_connection):
		telnet_connection.write('att?\n')
		setting = telnet_connection.expect([r'\S*\w+\.\w+\S*'], timeout=5)
		if setting[0] == -1:
			#this means 
			return -1
		else:
			return setting[2].strip()

class JFWAttenuator(VariableAttenuator):
	def __init__(self, port):
		self.port = port
		self.tries = 3 #number of times it will try a command
		self._min_attenuation = 0
		self._max_attenuation = 95

		
	def _open_connection(self):
		#TODO: check to to see if telnet connection actually opens successfully and catch this
		host = "10.10.4.36"
		port = "3001"

		telnet_connection = telnetlib.Telnet(host,port)
		time.sleep(0.1)
		return telnet_connection	


	def _close_connection(self, telnet_connection):
		telnet_connection.close()


	def set_attenuation(self, value):		
		''' This sets the attenuation on Attenuator.  
			It opens and then closes the telnet connection to the attenuator every time it set it,
			Because some of these devices suck at having a persistent connection open to them.
		'''
		tn = self._open_connection()
		
		for i in range(self.tries):		
			#attenuation_str = 'SA' + self.port + str(value) + '\n'
			tn.write("SA 1 31" + "\n")
			#tn.expect([r'\S*[0|1]\S*'], timeout=5)
			
			#setting = self._get_attenuation(tn)
			#if setting == -1:
			#	print 'Attenuator failed to set to: ' + str(value)				
			#	continue
			#if float(setting) == float(value):
			#	print 'Attenuator correctly set to: ' + str(value)
			#	break		
			
		#self._close_connection(tn)

		
	#def _get_attenuation(self, telnet_connection):
	#	telnet_connection.write('att?\n')
	#	setting = telnet_connection.expect([r'\S*\w+\.\w+\S*'], timeout=5)
	#	if setting[0] == -1:
	#		#this means 
	#		return -1
	#	else:
	#		return setting[2].strip()
			
