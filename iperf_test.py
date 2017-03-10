import json
import argparse	
import time
import os
import pandas as pd
from attenuators import *
from adaura import *
import pyping

'''
Run an iperf test over attenuation levels and save to csv for plotting.
- Assumes that iperf server running on other endpoint
- Does both directions using -R for reverse
- It uses the same options as Iperf if needs to be passed through, to make things straightforward
- Assumes Iperf options order does not matter

Required inputs are:
- Destination IP

Optional:
- Port
- test length
- attenuation settings
- output file

'''
#JFW IP address and telnet port
host = "10.10.4.36"
port = "3001"

#Constants
IPERF_OUTPUT_FORMAT = ".json"
DEFAULT_IPERF_TEST_DURATION_SECONDS = '10'
DEFAULT_PARALLEL_IPERF_STREAMS = '4'
DEFAULT_SERVER_PORT = '5201'
BASE_DIRECTORY = '/Users/fan/Desktop/rvr_test/'

#TODO
# make it simplier to read csv, have forward/reverse 
# remove commands/options that false
# save tags to file
# use python logging module
# add check ping function to stop test

def generate_attenuation_settings(atten_list):
	'''Takes in a list of three values to generate values: start, stop, step.  
	   Returns a list of attenuation settings.
	   If None, just returns a list containing one value ['None']'''
	if atten_list == None:
		return ['0']
	else:
		return range(int(atten_list[0]), int(atten_list[1]),  int(atten_list[2]))
	

def get_time_string():
	return time.strftime("%Y_%m_%d_%H_%M_%S")
	
def build_iperf_command(input_dict, logfile):
	'''Takes a dictionary of args and returns an Iperf command as a string'''
	list_of_commands = ['iperf3']
	
	for key, val in input_dict.iteritems():
		key_str = '--' + str(key)
		list_of_commands.append(key_str)
		if val == True:
			pass
		elif val == False:
			pass
		else:
			list_of_commands.append(val[0])
			
	command = " ".join(list_of_commands)
	return command

def save_average_data(input_data_list, output_file_name):
	df = pd.DataFrame()
	for input_data in input_data_list:
		try:
			output_dict = {}
			output_dict["direction"] = input_data["direction"]
			output_dict["attenuation"] = input_data["attenuation"]
			output_dict["time"] = input_data["start"]["timestamp"]["time"]
			output_dict["seconds"] = input_data["end"]["sum_sent"]["seconds"]
			output_dict["sent_bytes"] = input_data["end"]["sum_sent"]["bytes"]
			output_dict["sent_mbits_per_second"] = float(input_data["end"]["sum_sent"]["bits_per_second"])/1000000
			output_dict["received_bytes"] = input_data["end"]["sum_received"]["bytes"]
			output_dict["received_mbits_per_second"] = float(input_data["end"]["sum_received"]["bits_per_second"])/1000000
			df = df.append(output_dict, ignore_index=True)
		except:
			print 'Failed to aggregate data:'
			print str(input_data)
			pass	
		
	csv_file_name = output_file_name + '_average.csv'
	df.to_csv(csv_file_name, index=False)


def save_interval_data(input_data_list, output_file_name):	
	df = pd.DataFrame()
	for input_data in input_data_list:	
		try:
			direction = input_data["direction"]
			attenuation = input_data["attenuation"]
			intervals = input_data["intervals"]
			interval_number = 0
			for interval in intervals:
				output_dict = {}
				interval_number += 1
				output_dict["direction"] = direction
				output_dict["attenuation"] = attenuation
				output_dict["interval"] = interval_number
				output_dict["start"] = interval["sum"]["start"]
				output_dict["end"] = interval["sum"]["end"]
				output_dict["seconds"] = interval["sum"]["seconds"]
				output_dict["bytes"] = interval["sum"]["bytes"]
				output_dict["mbits_per_second"] = float(interval["sum"]["bits_per_second"])/1000000
				df = df.append(output_dict, ignore_index=True)
		except:
			pass
	csv_file_name = output_file_name + '_intervals.csv'
	df.to_csv(csv_file_name, index=False)

def _save_average_data(input_data_list, output_file_name):
	df = pd.DataFrame()
	for input_data in input_data_list:
		try:
			output_dict = {}
			output_dict["attenuation"] = input_data["attenuation"]
			direction = input_data["direction"]
			output_dict[(str(direction) + "_bits_per_second")] = float(input_data["end"]["sum_received"]["bits_per_second"])/1000000
			output_df = pd.DataFrame(output_dict)
			df = pd.merge(df, output_df)
		except:
			print 'Failed to aggregate data:'
			print str(input_data)
			pass	
			
	csv_file_name = output_file_name + '_average.csv'
	df.to_csv(csv_file_name, index=False)

	
def _save_interval_data(input_data_list, output_file_name):	
	df = pd.DataFrame()
	for input_data in input_data_list:	
		try:
			direction = input_data["direction"]
			attenuation = input_data["attenuation"]
			intervals = input_data["intervals"]
			interval_number = 0
			for interval in intervals:
				output_dict = {}
				interval_number += 1
				output_dict["direction"] = direction
				output_dict["attenuation"] = attenuation
				output_dict["interval"] = interval_number
				output_dict["start"] = interval["sum"]["start"]
				output_dict["end"] = interval["sum"]["end"]
				output_dict["seconds"] = interval["sum"]["seconds"]
				output_dict["bytes"] = interval["sum"]["bytes"]
				output_dict["mbits_per_second"] = float(interval["sum"]["bits_per_second"])/1000000
				df = df.append(output_dict, ignore_index=True)
		except:
			pass
	csv_file_name = output_file_name + '_intervals.csv'
	df.to_csv(csv_file_name, index=False)



def aggregate_files(list_of_files):
	'''Aggregate a list of json files and a return a list of results.'''
	
	print "Aggregating files: "
	for file in list_of_files:
		print file
	
	data_list = []	
	#read in iperf data
	for file in list_of_files:
		with open(file) as data_file:    
			data = json.load(data_file)
			#data['direction'] = direction # add direction
			#data['attenuation'] = str(attenuation)
		
		data_list.append(data)		
	return data_list

if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument('-t', 
						'--time',  
						help="Duration of Iperf test in seconds", 
						nargs=1,
						default=[DEFAULT_IPERF_TEST_DURATION_SECONDS]) 
	
	parser.add_argument('-i', 
						'--interval',  
						help="Reporting interval", 
						nargs=1,
						default=['1']) 
	
	parser.add_argument('-J', 
						'--json',  
						help="output in JSON format",
						action='store_true')
	
	parser.add_argument('-V', 
						'--verbose',  
						help="More detailed output than before",
						default=True,
						action='store_true')						
	
	parser.add_argument('-Z', 
						'--zerocopy',  
						help="Use a 'zero copy' sendfile() method of sending data. This uses much less CPU.",
						default=True,
						action='store_true')

	parser.add_argument('-P', 
						'--parallel',  
						help="number of parallel client streams to run",
						nargs=1,
						default=[DEFAULT_PARALLEL_IPERF_STREAMS])
						
	parser.add_argument('-c', 
						'--client',  
						help="IP Address of client",
						nargs=1,
						required=True) 
	
	parser.add_argument('-p', 
						'--port',  
						help="Server Port", 
						nargs=1,
						default=[DEFAULT_SERVER_PORT]) 
					
	parser.add_argument('--logfile',  
						help="Logfile", 
						nargs=1,
						default=[None]
						) 
	
	parser.add_argument('--tags',  
						help="Tags to add", 
						nargs='+') 
	
	parser.add_argument('-a',
						'--attenuation',
						help="Attenuation settings for test to run.  Values are start, stop, step",
						nargs=3)
						
	
	parser.add_argument('-al',
						'--attenuation_list',
						help="List of atenuation settings to run.  Takes priority over -a",
						nargs='+')

	parser.add_argument('-po',
						'--attenuator_port',
						help="List of attenuator ports",
						nargs='+')

	args = parser.parse_args()

	#create dictionary of args for easier manipulation
	args_dict = args.__dict__

	#process arguments to create file name
	current_time = get_time_string()
	if args_dict['logfile'][0] == None:
		file_name = current_time
		dir = BASE_DIRECTORY + current_time  + '/'
	else:
		file_name = args_dict['logfile'][0] + '_'  + current_time	
		dir = BASE_DIRECTORY + current_time  + '_' + args_dict['logfile'][0] + '/'
	#create directory to save - yes there is replication in file name and directory, but that's currently intentional
	del args_dict['logfile']
	
	if not os.path.exists(dir):
		os.makedirs(dir)
	
	#create the full file_name
	full_file_name = dir + file_name

	attenuation_ports = args_dict['attenuator_port']
		
	if args_dict['attenuation_list'] != None:
		attenuation_settings = args_dict['attenuation_list']
	else:
		attenuation_list = args_dict['attenuation']
		#generate attenuation settings
		attenuation_settings = generate_attenuation_settings(attenuation_list)
	del args_dict['attenuation']	
	del args_dict['attenuation_list']
	del args_dict['attenuator_port']	

	###############   change me to switch between manual attenuator and  auto ##################
	#attenuators = [ManualAttenuator()]
	#attenuators = [MiniAttenuator('192.168.0.121'), MiniAttenuator('192.168.0.110')]
	###############   change me to switch between manual attenuator and  auto ##################
	
	#check to make sure attenuation settings are valid
	print 'Using attenuation settings: ' + str(attenuation_settings)
	#print 'Applying attenuation settings to these ports: ' + str(attenuation_ports)
	#print 'Checking to make sure attenuation settings are valid.'
	#for attenuator in attenuators:
	#	attenuator.check_attenuation_values(attenuation_settings)
	#print 'Attenuation settings are valid.'
	
	#remove tags 
	tags = args_dict['tags']
	del args_dict['tags']
	
	#get the test time
	test_time = args_dict['time'][0]
	
	#process arguments to generate command to run Iperf						
	iperf_command = build_iperf_command(args_dict, file_name)

	files_list = []

	#tn = telnetlib.Telnet(host,port)
	for attenuation in attenuation_settings:
		#for p in attenuation_ports:		
		#attenuation_str = 'SA ' + str(p) + ' ' + str(attenuation) + '\r\n'
		attenuation_str = 'Attenuation ' + str(attenuation) + '\r\n'
		print attenuation_str
		
		set attenuations on ADUSB4A
		devs = find_multiple_ADUSB4()
  		print devs
  		att1 = ADUSB4A(devs[0])
  		att1.set_all_ports(attenuation)  
  		#att2 = ADUSB4A(devs[1])
  		#att2.set_all_ports(attenuation)		
		#tn.write(attenuation_str)
		time.sleep(1)
		
		##############
		#add check ping function here
		response = pyping.ping(args_dict['client'][0])
		
		if not response.ret_code == 0:
			print 'Client Disconnected!!!'
			break
		
		##############
							
		for direction in ["forward", "reverse"]:
				
			#run iperf test output to file
			logfile_name = full_file_name + '_' + direction + '_att' + str(attenuation) + '_log' + IPERF_OUTPUT_FORMAT
			if direction == "reverse":
				full_iperf_command = iperf_command + ' -R > ' + "\"" + logfile_name + "\""
			else:
				full_iperf_command = iperf_command + ' > ' + "\"" + logfile_name + "\""
			print '\nRunning: ' + full_iperf_command		
			os.system(full_iperf_command)
			
			files_list.append(logfile_name)
			
			#read in file and add direction and attenuation
			data_file = open(logfile_name, 'r+')   
			data = json.load(data_file)
			data['direction'] = direction # add direction
			data['attenuation'] = str(attenuation)
			data['iperf_command'] = str(full_iperf_command)
			
			#delete the contents of the file					
			data_file.seek(0)
			data_file.truncate()
			
			#write out data to file				
			json_string = json.dumps(data, indent=2)
			data_file.write(json_string)
			data_file.close()
		
	#set attenuators back to 0	
	#for attenuator in attenuators:		
	#	attenuator.set_attenuation("0")
	att1.set_all_ports(0)
	#att2.set_all_ports(0)
		
	#aggregate the files		
	json_files = aggregate_files(files_list)
					
	#save average data to CSV file
	save_average_data(json_files, full_file_name)
	
	#save interval data to CSV file
	save_interval_data(json_files, full_file_name)

	print "\n\n------------ Test Finished ------------\n\n"