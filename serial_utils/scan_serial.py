
import sys
import glob
import serial
import logging
import errno

def scan_serial():
    """scan for available ports. return a list of serial names"""
    available = []

    possible_ports = []

    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        possible_ports += glob.glob("/dev/rfcomm[0-9]*")
        possible_ports += glob.glob("/dev/ttyUSB[0-9]*")
        possible_ports += glob.glob("/dev/ttyS[0-9]*")
        possible_ports += glob.glob("/dev/ttyACM[0-9]*")
        #possible_ports += glob.glob("/dev/pts/[0-9]*")  # for obdsim

    elif sys.platform.startswith('win'):
        possible_ports += [r"COM%d" % i for i in range(256)]  # on win, the pseudo ports are also COM - harder to distinguish

    elif sys.platform.startswith('darwin'):
        exclude = [
            '/dev/tty.Bluetooth-Incoming-Port',
            '/dev/tty.Bluetooth-Modem'
        ]
        #possible_ports += glob.glob("/dev/ttys00[0-9]*")  # for obdsim
        possible_ports += [port for port in glob.glob('/dev/tty.*') if port not in exclude]

    # possible_ports += glob.glob('/dev/pts/[0-9]*') # for obdsim

    for port in possible_ports:
        if _try_port(port):
            available.append(port)
    print('Available ports: '+str(available))
    return available

def _try_port(portStr):
    """returns boolean for port availability"""
    try:
        s = serial.Serial(portStr)
        s.close()  # explicit close 'cause of delayed GC in java
        return True
    except serial.SerialException as err:
        logging.error(err)
    except OSError as e:
        if e.errno != errno.ENOENT:  # permit "no such file or directory" errors
            raise e

    return False