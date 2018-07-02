"""
Simple server to receive HTTP POST data and act on it as NAO commands.


Andrew Turpin
Mon  2 Jul 2018 11:10:56 AEST
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#import SocketServer
import cgi

import naoqi

class Handler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        print("hi")
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        #self.nao_ip = nao_ip
        #self.nao_port = nao_port

    def _set_headers(self, type="text/html"):
        self.send_response(200)
        self.send_header('Content-type', type)
        self.end_headers()

    def response(self, msg):
        self._set_headers("text/html")
        #self.wfile.write("<html><body>{}</body></html>".format(msg))
        self.wfile.write("{}".format(msg))

    def do_GET(self):
        self.response("GET not implemented")

    def do_HEAD(self):
        self._set_headers()
        
    def _get_speed(self, form):
        speed = 1.0
        if 'speed' in form:
            speed = float(form['speed'].value)
        if speed < -1.0 or speed > 1.0:
            speed = 1.0
        return speed

    def _handle_move(self, form):
        """Process the move command in form['move'].value.
           Commands are "Forward", "Back", "Stop".
           Use speed = form['speed'].value if present and in [-1,1].
        """

        if not proxies['motion'].robotIsWakeUp():
            proxies['motion'].wakeUp()

        proxies['motion'].moveInit()

        speed = self._get_speed(form)

        if form['move'].value == "Forward":
            proxies['motion'].moveToward( speed, 0, 0)
        elif form['move'].value == "Back":
            proxies['motion'].moveToward(-speed, 0, 0)
        elif form['move'].value == "Stop":
            proxies['motion'].stopMove()

        self.response('{} {} m/s'.format(form['move'].value, speed))

    def _handle_autonomous(self, form):
        """Turn Autonomous Listening on.off.
        """
        if 'auto' not in proxies:   # simulated NAO
            self.response('Set Autonomous Listening {}'.format(form['autoListen'].value))
            return

        if form['autoListen'].value in ['True','true', 'On', 'on']:
            proxies['auto'].setExpressiveListeningEnabled(True)
            self.response('Set Autonomous Listening On')
        else:
            proxies['auto'].setExpressiveListeningEnabled(False)
            self.response('Set Autonomous Listening Off')

    def _handle_photo(self, form):
        """Take a photo.
        """
        PATH = '/var/www/robotsgate/'
        FILE = 'camera.jpg'

        if 'photo' not in proxies:   # simulated NAO
            self.response('<html><body>An image from bot.</body></html>')
            return

        if form['photo'].value in [0,1]:   # 0 == top camera
            proxies['photo'].setCameraID(form['photo'].value)
        else:
            proxies['photo'].setCameraID(0) # default to top

        proxies['photo'].setPictureFormat('jpg')
        proxies['photo'].takePicture(PATH, FILE)
    
        self._set_headers("image/jpeg")
        myfile = open("{}/{}".format(PATH, FILE), 'rb')
        self.wfile.write(myfile.read())
            
    def _handle_posture(self, form):
        """Move to posture.
        """
        available = proxies['posture'].getPostureList()
        print(available)

        if form['posture'].value not in available:
            self.response(','.join(available))
        else:
            speed = self._get_speed(form)
            proxies['posture'].goToPosture(form['posture'].value, speed)
            self.response('Changed posture: {}'.format(form['posture'].value))

    def do_POST(self):
        form = cgi.FieldStorage(
                    fp=self.rfile, 
                    headers=self.headers,
                    environ={'REQUEST_METHOD':'POST',
                              'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        #print(form)    
        #print(form.keys())
        if 'text' in form:
            proxies['tts'].say(form["text"].value)
            self.response("Said: {}".format(form["text"].value))

        if 'move'       in form: self._handle_move(form)
        if 'autoListen' in form: self._handle_autonomous(form)
        if 'photo'      in form: self._handle_photo(form)
        if 'posture'    in form: self._handle_posture(form)
 
        
def run(server_class=HTTPServer, handler_class=Handler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

proxies = {}
if __name__ == "__main__":
    from sys import argv

    if len(argv) == 4:
        port = int(argv[1])
        nao_ip = argv[2]
        nao_port = int(argv[3])

        try:
            proxies['auto'] = naoqi.ALProxy("ALAutonomousMoves", nao_ip, nao_port)
            proxies['photo'] = naoqi.ALProxy("ALPhotoCapture", nao_ip, nao_port)
        except RuntimeError as e:
            print(e)

        proxies['tts'] = naoqi.ALProxy("ALTextToSpeech", nao_ip, nao_port)
        proxies['motion'] = naoqi.ALProxy("ALMotion", nao_ip, nao_port)
        proxies['posture'] = naoqi.ALProxy("ALRobotPosture", nao_ip, nao_port)

        run(port=port)
    else:
        print("Usage: python2.7 {} server_port nao_ip nao_port".format(argv[0]))
