# linux-networkinterfaces (v0.2.0) [https://github.com/newdaynewburner/linux-networkinterfaces]
## By Brandon Hammond <newdaynewburner@gmail.com>
A module for working with network interfaces in Linux. It provides objects for controlling and getting information from the network interfaces on your system, using subprocess to execute system
calls behind the scenes.

### Quick Start Guide
Currently it supports working with wired and wireless interfaces, through the WiredInterface and WirelessInterface objects respectively, and there is also a superclass
called Interface that is the parent of the WiredInterface and WirelessInterface objects, and it contains methods that are not specific to any particular interface type, and it can be used to create
custom objects for other interface types like bridges and what not, although support for those will be added in the future. Below is a short usage example:

```
from linuxnetworkinterfaces import WiredInterface, WirelessInterface

wired = WiredInterface("eth0") # Controls the 'eth0' wired interface
wireless = WirelessInterface("wlan0", manager="networkmanager") # Controls the 'wlan0' wireless interface, which is controlled by the NetworkManager network manager

# Change the interfaces state
wired.set_state("up") # Bring it up
wired.set_state("down") # Take it down

# Show some attributes
state = wired.state # Current state
flags = wired,device_flags # Device flags that are currently set
print(state)
for flag in flags:
    print(flag)

# Putting a wireless interface into and taking it out of monitor mode (NetworkManager friendly!)
# Starting monitor mode
wireless.stop_management() # FOR NETWORKMANAGER COMPATABILITY
wireless.set_state("down")
wireless.set_mode("monitor")
wireless.set_state("up")

# Stopping monitor mode
wireless.set_state("down")
wireless.set_mode("managed")
wireless.start_management() # FOR NETWORKMANAGER COMPATABILITY
```

### Issues
If you have any problems, feature requests, or anything else just shoot me an email or open an issue on the module's GitHub page, typically I'll respond quickly.
