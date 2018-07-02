

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
    time.sleep(5)
    send({'text': 'Stop', 'move':'Stop'})

send({'photo': 0})
#send({'posture': 'SitRelax', 'speed': 0.5})
#send({'posture': 'Sit'})
