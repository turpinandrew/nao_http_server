

import requests
import time
import http

def send(msg):
    """msg is a dictionary."""
    r = "No response"
    try:
        r = requests.post("http://127.0.0.1:8000", data=msg)
    except:
        pass
    #print(r.status_code, r.reason)
    print(r.text[:300] + '...')


def test1():
    send({'text': 'Go'})
    send({'move':'Forward', 'speed':1})
    #send({'move': 'Turn', 'angle': -90})
    time.sleep(3)
    send({'text': 'Stop', 'move':'Stop'})

#send({'photo': 0})

#send({'posture': 'SitRelax', 'speed': 0.5})
#send({'posture': 'Sit'})

#send({'move': 'Rest'})

#send({'volume': 0})
#send({'text': 'Hello'})
#send({'volume': 50})
#send({'text': 'Hello'})

#test1()

#send({'get': 'battery'})
send({'hand': 'right', 'dx': 0.1, 'dy': 0.1})
#send({'move': 'Rest'})
