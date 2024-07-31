# TMAG5273-MicroPython
*v1.0.0*

TMAG5273-MicroPython is a MicroPython library for the [TMAG5273 3 axis hall effect sensor](https://www.sparkfun.com/products/23880).

This library supports the most common funationality of the TMAG5273. If your application requires hte more advanced features, please make an issue, make a PR, or contact me.

## XRP Robot Setup Guide ##
1) Upload `TMAG5273.py` to your XRP robot
	- [Click here](https://github.com/AlfredoSystems/TMAG5273-MircoPython/archive/refs/heads/main.zip) to download this repository. After that, unzip it
	- Connect to your robot with the [XRP code editor](https://xrpcode.wpi.edu/)
	- In the XRP Code editor, go to `file > Upload to XRP` and select `TMAG5273.py` from the repo you just downloaded
	- Save the file in the \lib folder, so that `FINAL PATH: /lib/TMAG5273.py`

1) Upload `TMAG5273_simple_magnetometer.py` to your XRP robot
	- In the XRP Code editor, go to `file > Upload to XRP` and select `TMAG5273_simple_magnetometer.py` from the repo you just downloaded
	- Save the file at the top level, so that `FINAL PATH: /TMAG5273_simple_magnetometer.py`
