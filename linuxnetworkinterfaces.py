"""
linuxnetworkinterfaces.py

Module for working with network interfaces in Linux
"""

import os
import sys
import subprocess
from backend import NetworkManager
from exceptions import SystemCallError, AttributeSetSilentFailError

class Interface(object):
	""" Generic parent class object. Represents and controls a
	specific interface on the machine
	
	Methods:
		__init__() - Initialize the object
	"""
	
	def __init__(self, iface, debug=False):
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
		
	def __name__(self, set_name=None):
		""" Interface name
		"""
		if set_name is not None:
			try:
				subprocess.check_call(f"ip link set {self.iface} name {set_name}".split(" "))
			except subprocess.CalledProcessError as err_msg:
				raise SystemCallError(f"A system-level command returned a non-zero exit code! Full error message: {err_msg}")
			self.iface = set_name
		return self.iface
		
	def __alias__(self, set_alias=None):
		""" Interface alias name
		"""
		if set_alias is not None:
			try:
				subprocess.check_call(f"ip link set {self.iface} alias {set_alias}".split(" "))
			except subprocess.CalledProcessError as err_msg:
				raise SystemCallError(f"A system-level command returned a non-zero exit code! Full error message: {err_msg}")
			
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
			try:
				subprocess.check_call(f"ip link set {self.iface} address {set_hwaddr}".split(" "))
			except subprocess.CalledProcessError as err_msg:
				raise SystemCallError(f"A system-level command returned a non-zero exit code! Full error message: {err_msg}")
		
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
			try:
				subprocess.check_call(f"ip link set {self.iface} {set_state}".split(" "))
			except subprocess.CalledProcessError as err_msg:
				raise SystemCallError(f"A system-level command returned a non-zero exit code! Full error message: {err_msg}")
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
			try:
				subprocess.check_call(f"ip link set {self.iface} arp {sopt}]".split(" "))
			except subprocess.CalledProcessError as err_msg:
				raise SystemCallError(f"A system-level command returned a non-zero exit code! Full error message: {err_msg}")
		has_flag = False
		if "NOARP" in self.__flags__():
			has_flag = True
		return has_flag
		
	def __multicast__(self, set_flag=None):
		""" MULTICAST device flag
		"""
		if set_flag is not None:
			sopt = "on" if set_flag == True else "off"
			try:
				subprocess.check_call(f"ip link set {self.iface} multicast {sopt}]".split(" "))
			except subprocess.CalledProcessError as err_msg:
				raise SystemCallError(f"A system-level command returned a non-zero exit code! Full error message: {err_msg}")
		has_flag = False
		if "MULTICAST" in self.__flags__():
			has_flag = True
		return has_flag
		
	def __allmulti__(self, set_flag=None):
		""" ALLMULTI device flag
		"""
		if set_flag is not None:
			sopt = "on" if set_flag == True else "off"
			try:
				subprocess.check_call(f"ip link set {self.iface} allmulticast {sopt}]".split(" "))
			except subprocess.CalledProcessError as err_msg:
				raise SystemCallError(f"A system-level command returned a non-zero exit code! Full error message: {err_msg}")
		has_flag = False
		if "ALLMULTICAST" in self.__flags__():
			has_flag = True
		return has_flag
		
	def __promisc__(self, set_flag=None):
		""" PROMISC device flag"""
		if set_flag is not None:
			sopt = "on" if set_flag == True else "off"
			try:
				subprocess.check_call(f"ip link set {self.iface} promisc {sopt}".split(" "))
			except subprocess.CalledProcessError as err_msg:
				raise SystemCallError(f"A system-level command returned a non-zero exit code! Full error message: {err_msg}")
		has_flag = False
		if "PROMISC" in self.__flags__():
			has_flag = True
		return has_flag
		
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
			raise Exception(f"Unsupported flag '{flag}'!")
			return False
			
		# Make sure the flag was set and return False if it failed
		if not flag_set:
			raise AttributeSetSilentFailError(f"Tried to set the value of the '{flag}' device flag but its value remains unchanged!")
			return False
			
		# Return True upon success
		return True

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
		cur = self.__name__()
		self.name = self.__name__(set_name=name)
		if self.name == cur:
			raise AttributeSetSilentFailError(f"Tried to change the name of the interface '{self.iface}' to '{name}' but the name was not changed!")
		return self.name

	def set_alias(self, alias):
		""" Set the interfaces alias name
		"""
		self.alias = self.__alias__(set_alias=alias)
		return self.alias

	def set_hwaddr(self, hwaddr):
		""" Set a cloned MAC address
		"""
		cur = self.__hwaddr__()
		self.hwaddr = self.__hwaddr__(set_hwaddr=hwaddr)
		if self.hwaddr == cur:
			raise AttributeSetSilentFailError(f"Tried to set the hardware address of the interface but it was not changed!")
		return self.hwaddr

	def set_state(self, state):
		""" Set the interface's state
		"""
		cur = self.__state__()
		self.state = self.__state__(set_state=state)
		if self.state == cur:
			raise AttributeSetSilentFailError(f"Tried to change the state of the interface but it was not changed!")
		return self.state
		
class WiredInterface(Interface):
	""" Represents a wired network interface
	
	Methods:
		__init__() - Initialize the object
	"""
	
	def __init__(self, iface, manager=None, debug=False):
		""" Initialize the object
		"""
		super().__init__(iface, debug=debug)
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
	
	def __init__(self, iface, manager=None, debug=False):
		""" Initialize the object
		"""
		super().__init__(iface, debug=debug)
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
			try:
				subprocess.check_call(f"iw dev {self.iface} set type {set_mode}".split(" "))
			except subprocess.CalledProcessError as err_msg:
				raise SystemCallError(f"A system-level command returned a non-zero exit code! Full error message: {err_msg}")
			
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
			try:
				subprocess.check_call(f"iw dev {self.iface} set channel {str(set_channel)}".split(" "))
			except subprocess.CalledProcessError as err_msg:
				raise SystemCallError(f"A system-level command returned a non-zero exit code! Full error message: {err_msg}")
			
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

	def set_mode(self, mode):
		""" Set the interface's mode
		"""
		cur = self.__mode__()
		self.mode = self.__mode__(set_mode=mode)
		if self.mode == cur:
			raise AttributeSetSilentFailError(f"Tried to change the interface from {cur} mode to {mode} mode but the mode was not changed!")
		return self.mode

	def set_channel(self, channel):
		""" Set the interface's channel
		"""
		cur = self.__channel__()
		self.channel = self.__channel__(set_channel=channel)
		if self.channel == cur:
			raise AttributeSetSilentFailError(f"Tried to change the interface's channel from {cur} to {channel}, but the channel was not changed!")
		return self.channel
