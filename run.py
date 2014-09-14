import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

import webbrowser
from app import app
import threading
import time

def delay_open():
	delay = 1
	print 'sleep for %s seconds' % delay
	time.sleep(delay)
	
	import socket
	
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('google.com', 8080))
		host = s.getsockname()[0]
	except:
		host = 'localhost'
	
	webbrowser.open_new_tab('http://%s:5000' % host)

threading.Thread(target=delay_open).start()
app.run(host='0.0.0.0', debug = False)
# app.run(host='0.0.0.0', debug = True)
