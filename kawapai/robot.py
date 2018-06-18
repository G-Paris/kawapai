from telnetlib import IAC, DO, DONT, WILL, WONT, SB, SE, TTYPE, NAOFFD, ECHO
import telnetlib, socket, time, threading

class KawaBot:
	"""
	Python interface to Kawasaki Robotics. 
	inspired by:
	http://code.activestate.com/recipes/52228-remote-control-with-telnetlib/
	"""
	def __init__(self, host="127.0.0.1", port=10300):
		# If connecting to K-roset D+ controller or earlier controller connect through port: 9105
		# If connecting to K-roset E controller or later controller connect through one of ports: 10000, 10300
		# NOTE: Simulated D+ controller or earlier does NOT support opening additional tcp-ip ports over localhost
		# Movement server will therfor NOT work on D+
		#self.logger = logging.getLogger("kawa")
		self.host = host
		self.port = port
		self.env_term = "VT100"
		self.user = "as" # khidl also possible, effect unknown. different permissions?
		self.telnet = telnetlib.Telnet()
		self.connect()

	def telnet_process_options(self, socket, cmd, opt):			
		IS = b'\00'
		# Inspired by
		# https://github.com/rapid7/metasploit-framework/blob/master/lib/msf/core/exploit/telnet.rb
		# https://github.com/jquast/x84/blob/cf3dff9be7280f424f6bcb0ea2fe13d16e7a5d97/x84/default/telnet.py
		if cmd == WILL and opt == ECHO: #hex:ff fb 01 name:IAC WILL ECHO description:(I will echo)
				socket.sendall(IAC + DO + opt) #hex(ff fd 01), name(IAC DO ECHO), descr(please use echo)
		elif cmd == DO and opt == TTYPE: #hex(ff fd 18), name(IAC DO TTYPE), descr(please send environment type)
				socket.sendall(IAC + WILL + TTYPE) #hex(ff fb 18), name(IAC WILL TTYPE), descr(Dont worry, i'll send environment type)
		elif cmd == SB:
			socket.sendall(IAC + SB + TTYPE + IS + self.env_term.encode() + IS + IAC + SE)
			# hex(ff fa 18 00 b"VT100" 00 ff f0) name(IAC SB TTYPE iS VT100 IS IAC SE) descr(Start subnegotiation, environment type is VT100, end negotation)
		elif cmd == SE: # server letting us know sub negotiation has ended
			pass # do nothing
		else: print("Unexpected telnet negotiation")

	def connect(self):
		print("Connecting to kawasaki robot")
		self.telnet.set_option_negotiation_callback(self.telnet_process_options)
		self.telnet.open(self.host, self.port, 1)
		time.sleep(0.5) #Allow TELNET negotaion to finish
		self.telnet.read_until(b"n: ") 
		self.telnet.write(self.user.encode() + b"\r\n")
		self.telnet.read_until(b">")
		print("Connected succesfully\n")

	def disconnect(self):
		print("Disconnecting")
		command = b"signal(-2010)\r\n"
		self.telnet.write(command)
		time.sleep(1)
		print(self.telnet.read_until(b">").decode())
		self.telnet.close()

	def AS_command(self, command=None):
		if command == None:
			print("No command specified, check kawa documentation")
			return
		command = command.encode + b"\r\n"
		self.telnet.write(command)
		self.telnet.read_until(b">")

	def load_as_file(self, file_location=None):
		max_chars = 492 # Max amount of characters that can be accepted per write to kawa.
		if file_location != None:
			print("Transfering {} to kawasaki".format(file_location))
			inputfile = open(file_location, 'r')
			file_text = inputfile.read() # Store Kawa-as code from file in local varianle
			text_split = [file_text[i:i+max_chars] for i in range(0, len(file_text), max_chars)] #Split AS code in sendable blocks
			print("File consists of {} characters".format(len(file_text)))
			self.telnet.write(b"load kawa.as\r\n")
			self.telnet.read_until(b'.as').decode("ascii")
			self.telnet.write(b'\x02A    0\x17')
			self.telnet.read_until(b"\x17")
			print("Sending file.... ")
			for i in range(0, len(text_split), 1):
				self.telnet.write(b'\x02C    0' + text_split[i].encode() + b'\x17')
				self.telnet.read_until(b"\x17")
			self.telnet.write(b'\x02' + b'C    0' + b'\x1a\x17')
			#Finish transfering .as file and start confirmation
			self.telnet.read_until(b"Confirm !")
			self.telnet.write(b'\r\n')
			self.telnet.read_until(b"E\x17")
			self.telnet.write(b'\x02' + b'E    0' + b'\x17')
			#Read until command prompt and continue
			self.telnet.read_until(b">")
			print(".... Done, great success!\n")
		else: print("No file specified\n")

	def abort_kill_all(self):
		for command in ["pcabort "]:
			for i in range(1, 6):
				prog_number = str(i) + ":"
				self.telnet.write(command.encode() + prog_number.encode() + b"\r\n")
				self.telnet.read_until(b">")
		for command in ["abort ", "pckill\r\n1", "kill\r\n1"]:
			self.telnet.write(command.encode() + b"\r\n")
			self.telnet.read_until(b">")

	def payload_weight(self, kg=0, centre_of_mass=(0,0,0)):
		command = 	("weight " + str(kg) + ", " + 
					str(centre_of_mass[0]) + ", " + 
					str(centre_of_mass[1]) + ", " + 
					str(centre_of_mass[2]) + "\r\n").encode()
		self.telnet.write(command)
		print(self.telnet.read_until(b">"))

	def delete_eveything_in_robot_memory(self):
		command = b"sysinit\r\n"
		self.telnet.write(command)
		self.telnet.read_until(b"(Yes:1, No:0)")
		command = b"1\r\n"
		self.telnet.write(command)
		self.telnet.read_until(b">")

	def motor_power_on(self):
		command = b"zpow on\r\n"
		self.telnet.write(command)
		self.telnet.read_until(b">")

	def motor_power_off(self):
		command = b"zpow off\r\n"
		self.telnet.write(command)
		self.telnet.read_until(b">")

	def get_status(self):
		command = b"status\r\n"
		self.telnet.write(command)
		print(self.telnet.read_until(b">").decode("ascii"))

	def get_kawa_position(self):
		command = b"where\r\n"
		self.telnet.write(command)
		print(self.telnet.read_until(b">").decode("ascii"))

	def get_kawa_error(self):
		command = b"errlog\r\n"
		self.telnet.write(command)
		print(self.telnet.read_until(b">").decode("ascii"))
	
	def reset_error(self):
		command = b"ereset\r\n"
		self.telnet.write(command)
		print(self.telnet.read_until(b">").decode("ascii"))

	def get_kawa_id(self):
		command = b"ID\r\n"
		self.telnet.write(command)
		print(self.telnet.read_until(b">").decode("ascii"))

	def initiate_kawabot(self):
		print("Initiating kawabot")
		command = b"pcexe init_kawa\r\n"
		self.telnet.write(command)
		print(self.telnet.read_until(b"completed").decode("ascii"))
		command = b"\r\n"
		self.telnet.write(command)
		#time.sleep(0.1)
		print(self.telnet.read_until(b">").decode("ascii"))

	def connect_to_movement_server(self, movement_server_port=11112):
		print("Connecting to movement server")
		command = b"pcexe 1: recv_tcp_serv\r\n"
		self.telnet.write(command)
		self.telnet.read_until(b">").decode("ascii")
		self.movement_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.movement_server.connect((self.host, movement_server_port))
		self.movement_seq_num = 0
		print("Activating movement server")
		command = b"pcexe 2: read_tcp_buffer\r\n"
		self.telnet.write(command)
		self.telnet.read_until(b">").decode("ascii")
		print("Start moving robot")
		command = b"exe move_kawa\r\n"
		self.telnet.write(command)
		self.telnet.read_until(b">").decode("ascii")
		print("Connected to and activated movement server succesfully!\n")

	def jmove(self, joint_0, joint_1, joint_2, joint_3, joint_4, joint_5, speed=100, accuracy=10, acceleration=100, deceleration=100, break_cp=0):
		# EXAMPLE joint_trajectory_point = "\x02|\x01|45|11|00|10|400|100|100|0|-40|20|-50|0|10|100|\x03"
		msg_start = "\x02|\x01|"
		msg_seq_num = "|11|" + str(self.movement_seq_num).zfill(2) 
		msg_end = msg_seq_num + "|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|\x03".format(
			speed, accuracy, acceleration, deceleration, break_cp, 
			joint_0, joint_1, joint_2, joint_3, joint_4, joint_5)
		joint_trajectory_point = msg_start + str(len(msg_end)) + msg_end
		try:
			self.movement_server.send(joint_trajectory_point.encode())		
			if self.movement_seq_num == 99:
				self.movement_seq_num = 0
			else:
				self.movement_seq_num += 1
		except socket.error:
			print("No chooch")

	def close_movement_server(self):
		self.movement_server.close()
		
	def close_pose_update_server(self):
		self.pose_server.close()

	def connect_to_pose_update_server(self, pose_update_server_port=11111):
		print("Connecting to pose update server")
		command = b"pcexe 4: send_pos_serv\r\n"
		self.current_pose = 0
		self.telnet.write(command)
		self.telnet.read_until(b">").decode("ascii")
		self.pose_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.pose_server.connect((self.host, pose_update_server_port))
		self.pose_server.settimeout(1)
		print("Connected to pose update server succesfully!\n")

	def get_current_pose(self):
		return self.pose_server.recv(1024)

#################################################
############### Testing functions ###############
#################################################

	def connect_to_tcp_test(self):
		print("Connecting to tcp server")
		command = b"pcexe 1: recv_traj_serv\r\n"
		self.telnet.write(command)
		self.telnet.read_until(b">").decode("ascii")
		command = b"pcexe 2: read_per_char\r\n"
		self.telnet.write(command)
		self.telnet.read_until(b">").decode("ascii")

		movement_server_port = 11112
		self.tcp_test_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.tcp_test_server.connect((self.host, movement_server_port))
		print("Connected succesfully!\n")

	def send_tcp_test_message(self, message="hello!"):	
		try:
			print(message)
			self.tcp_test_server.send(message.encode())		
		except socket.error:
			print("No chooch")

	def close_to_tcp_test(self):
		command = b"signal(-2010)\r\n"
		self.telnet.write(command)
		time.sleep(1)
		print(self.telnet.read_until(b">").decode())
		self.tcp_test_server.close()