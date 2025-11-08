"""
networkinterfaces.py

Module for working with network interfaces
"""

import os
import sys
import subprocess
import threading
from lib.backend import NetworkManager
from lib.exceptions import *

class Interface(object):
	""" Represents and controls a specific interface on the machine
	
	Methods:
		__init__() - Initialize the object
	"""
	
	def __init__(self, iface, debug=False, logger=None, strict_error_handling=False):
		""" Initialize the object
		"""
		# Interface
		self.iface = iface
		self.name = self.__name__()
		self.alias = self.__alias__()
		self.hwaddr = self.__hwaddr__()
		self.permaddr = self.__permaddr__()
		
		# State
		self.state = self.__state__()
				
		# Device flags
		self.device_flags = self.__flags__()
		self.noarp = self.__noarp__()
		self.multicast = self.__multicast__()
		self.allmulti = self.__allmulti__()
		self.promisc = self.__promisc__()
		
		# Messages & error handling
		self.debug = debug
		self.logger = logger
		self.strict_error_handling = strict_error_handling
		
	def __error_handler__(self, msg):
		""" Handle warnings, errors, and exceptions
		"""
		if self.strict_error_handling:
			if self.logger:
				self.logger.error(msg)
			raise Exception(msg)
		else:
			if self.logger:
				self.logger.warning(msg)
			return None
		
	def __name__(self, set_name=None):
		""" Interface name
		"""
		if set_name is not None:
			subprocess.check_output(f"ip link set {self.iface} name {set_name}".split(" ")).decode()
			self.iface = set_name
		return self.iface
		
	def __alias__(self, set_alias=None):
		""" Interface alias name
		"""
		if set_alias is not None:
			subprocess.check_output(f"ip link set {self.iface} alias {set_alias}".split(" ")).decode()
			
		sstr = subprocess.check_output(f"ip link show {self.iface}".split(" ")).decode(); slst = sstr.split(" ")
		alias = None
		index = 0
		for part in slst:
			if part == "alias":
				alias = slst[index + 1]
			index = index + 1
		return alias
		
	def __hwaddr__(self, set_hwaddr=None):
		""" MAC address used by the interface
		"""
		if set_hwaddr is not None:
			subprocess.check_output(f"ip link set {self.iface} address {set_hwaddr}".split(" ")).decode()
		
		sstr = subprocess.check_output(f"ip link show {self.iface}".split(" ")).decode(); slst = sstr.split(" ")
		hwaddr = None
		index = 0
		for part in slst:
			if part == "link/ether":
				hwaddr = slst[index + 1]
			index = index + 1
		return hwaddr
		
		
	def __permaddr__(self):
		""" Permanent MAC address of the device
		"""
		sstr = subprocess.check_output(f"ip link show {self.iface}".split(" ")).decode(); slst = sstr.split(" ")
		permaddr = None
		index = 0
		for part in slst:
			if part == "permaddr":
				permaddr = slst[index + 1]
			index = index + 1
		return permaddr
		
	def __state__(self, set_state=None):
		""" Interface state
		"""
		if set_state is not None:
			subprocess.check_output(f"ip link set {self.iface} {set_state}".split(" ")).decode()
		sstr = subprocess.check_output(f"ip link show {self.iface}".split(" ")).decode(); slst = sstr.split(" ")
		state = None
		index = 0
		for part in slst:
			if part == "state":
				state = slst[index + 1].lower()
			index = index + 1
		return state
		
	def __flags__(self):
		""" Return a list of device flags
		"""
		sstr = subprocess.check_output(f"ip link show {self.iface}".split(" ")).decode(); slst = sstr.split(" ")
		fstr = slst[2].strip("<>"); flst = fstr.split(",")
		return flst
		
	def __noarp__(self, set_flag=None):
		""" NOARP device flag
		"""
		if set_flag is not None:
			sopt = "on" if set_flag == True else "off"
			subprocess.check_output(f"ip link set {self.iface} arp {sopt}]".split(" "))
		has_flag = False
		if "NOARP" in self.__flags__():
			has_flag = True
		return has_flag
		
	def __multicast__(self, set_flag=None):
		""" MULTICAST device flag
		"""
		if set_flag is not None:
			sopt = "on" if set_flag == True else "off"
			subprocess.check_output(f"ip link set {self.iface} multicast {sopt}]".split(" "))
		has_flag = False
		if "MULTICAST" in self.__flags__():
			has_flag = True
		return has_flag
		
	def __allmulti__(self, set_flag=None):
		""" ALLMULTI device flag
		"""
		if set_flag is not None:
			sopt = "on" if set_flag == True else "off"
			subprocess.check_output(f"ip link set {self.iface} allmulticast {sopt}]".split(" "))
		has_flag = False
		if "ALLMULTICAST" in self.__flags__():
			has_flag = True
		return has_flag
		
	def __promisc__(self, set_flag=None):
		""" PROMISC device flag"""
		if set_flag is not None:
			sopt = "on" if set_flag == True else "off"
			subprocess.check_output(f"ip link set {self.iface} promisc {sopt}".split(" "))
		has_flag = False
		if "PROMISC" in self.__flags__():
			has_flag = True
		return has_flag
		
	def up(self):
		""" Bring the interface up
		"""
		
		# Try to bring the interface up & handle cases where it already is
		if self.__state__() != "up":
			state = self.__state__(set_state="up")
		else:
			self.__error_handler__(f"Tried to set state of interface '{self.iface}' to 'up', but that interface is already up!")
				
		# Handle cases where the interface fails to be brought up & return False to indicate failure
		if state != "up":
			self.__error_handler__(f"Tried to bring up interface '{self.iface}', but it failed! Interface state is '{state}'!")
			return False
			
		# Return True upon success
		return True
		
	def down(self,):
		""" Take the interface down
		"""

		# Try to take the interface down & handle cases where it already is
		if self.__state__() != "down":
			state = self.__state__(set_state="down")
		else:
			self.__error_handler__(f"Tried to set state of interface '{self.iface}' to 'down', but that interface is already down!")

		# Handle cases where the interface fails to be brought up & return False to indicate failure
		if state != "down":
			self.__error_handler__(f"Tried to take down interface '{self.iface}', but it failed! Interface state is '{state}'!")
			return False

		# Return True upon success
		return True

		
	def set_device_flag(self, flag, setting):
		""" Set a device flag
		"""
		# Determine the proper flag setting value & handle bad setting argument values
		sval = "on" if setting in ("on", True) else "off" if setting in ("off", False) else None
		if not setting:
			self.__error_handler__(f"Invalid device flag setting '{setting}'!")
			
		# Set the flag through the appropriate method or call the error handler method if a non-existent flag was specified
		if flag.lower() == "noarp":
			flag_set = self.__noarp__(set_flag=setting)
		elif flag.lower() == "multicast":
			flag_set = self.__multicast__(set_flag=setting)
		elif flag.lower() == "allmulti":
			flag_set = self.__allmulti___(set_flag=setting)
		elif flag.lower() == "promisc":
			flag_set = self.__promisc__(set_flag=setting)
		else:
			self.__error_handler__(f"Invalid device flag '{flag}'!")
			return False
			
		# Make sure the flag was set and return False if it failed
		if not flag_set:
			self.__error_handler__(f"Tried to set flag '{flag}' on interface '{self.iface}' but it failed! Currently set flags are {self.__flags__()}!")
			return False
			
		# Return True upon success
		return True
		
class WiredInterface(Interface):
	""" Represents a wired network interface
	
	Methods:
		__init__() - Initialize the object
	"""
	
	def __init__(self, iface, manager=None, debug=False, logger=None, strict_error_handling=False):
		""" Initialize the object
		"""
		super().__init__(iface, debug=debug, logger=logger, strict_error_handling=strict_error_handling)
		self.iface_type = "wired"
		self.manager = manager
		self.manager_backend = None
		if self.manager == "networkmanager":
			self.manager_backend = NetworkManager(self)
		
class WirelessInterface(Interface):
	""" Represents a wireless network interface
	
	Methods:
		__init__() - Initialize the object
	"""
	
	def __init__(self, iface, manager=None, debug=False, logger=None, strict_error_handling=False):
		""" Initialize the object
		"""
		super().__init__(iface, debug=debug, logger=logger, strict_error_handling=strict_error_handling)
		self.iface_type = "wireless"
		self.manager = manager
		self.manager_backend = None
		if self.manager == "networkmanager":
			self.manager_backend = NetworkManager(self)
		self.default_mode = "managed"
		self.mode = self.__mode__()
		self.channel = self.__channel__()
		
	def __mode__(self, set_mode=None):
		""" Get or set the mode
		"""
		if set_mode is not None:
			subprocess.check_output(f"iw dev {self.iface} set type {set_mode}".split(" ")).decode()
			
		sstr = subprocess.check_output(f"iw dev {self.iface} info".split(" ")).decode(); slst = sstr.split(" ")
		mode = None
		index = 0
		for part in slst:
			if "type" in part:
				mstr = slst[index + 1]
				mode, _ = mstr.split("\n\t")
				break
			index = index + 1
		return mode
		
	def __channel__(self, set_channel=None):
		""" Get or set the channel
		"""
		if set_channel is not None:
			subprocess.check_output(f"iw dev {self.iface} set channel {str(set_channel)}".split(" ")).decode()
			
		sstr = subprocess.check_output(f"iw dev {self.iface} info".split(" ")).decode(); slst = sstr.split(" ")
		channel = None
		index = 0
		for part in slst:
			if "channel" in part:
				channel = int(slst[index + 1])
				break
			index = index + 1
		return channel
		
	def get_supported_channels(self):
		""" Get a list of the 2.4G and 5G channels supported by the interface
		"""
		pass

	def start_management(self):
		""" Allow the interface to be controlled by its manager
		"""
		self.manager_backend.include()
		return None

	def stop_management(self):
		""" Do not allow the interface to be controlled by its manager
		"""
		self.manager_backend.exclude()
		return None

	def set_name(self, name):
		""" Set the interface's name
		"""
		self.name = self.__name__(set_name=name)
		return self.name

	def set_hwaddr(self, hwaddr):
		""" Set a cloned MAC address
		"""
		self.hwaddr = self.__hwaddr__(set_hwaddr=hwaddr)
		return self.hwaddr

	def set_state(self, state):
		""" Set the interface's state
		"""
		self.state = self.__state__(set_state=state)
		return self.state

	def set_mode(self, mode):
		""" Set the interface's mode
		"""
		self.mode = self.__mode__(set_mode=mode)
		return self.mode

	def set_channel(self, channel):
		""" Set the interface's channel
		"""
		self.channel = self.__channel__(set_channel=channel)
		return self.channel
