#!/usr/bin/python

import commands
import serial, sys
import threading, time

import xbmc
import xbmcaddon

import json
import urllib2


__addon__ = xbmcaddon.Addon()
__setting__ = __addon__.getSetting
__addon_id__ = __addon__.getAddonInfo('id')
__localize__ = __addon__.getLocalizedString


class MyMonitor( xbmc.Monitor ):
    def __init__( self, *args, **kwargs ):
        xbmc.Monitor.__init__( self )

    def onSettingsChanged( self ):
        load_addon_settings()


def load_addon_settings():
    global sleep_time; serial_port; blink_freq

    # todo: default LED on or off

    #try:
    #    blink_sel = int(__setting__('frequency'))
    #except ValueError:
    blink_sel = 1

    if (blink_sel = 0):
        blink_freq = 0.5
    if (blink_sel = 1):
        blink_freq = 1
    if (blink_sel = 2):
        blink_freq = 2

    #try:
    #    serial_port = int(__setting__('serial'))
    #except ValueError:
    serial_port = 0

    #try:
    #    sleep_time = int(__setting__('sleep'))
    #except ValueError:
    sleep_time = 10

    return


class StopThread(StopIteration): pass


threading.SystemExit = SystemExit, StopThread


class MyThread(Thread):
    def stop(self):
        self.__stop = True

    def _bootstrap(self):
        if threading._trace_hook is not None:
            raise ValueError('Cannot run thread with tracing!')
        self.__stop = False
        sys.settrace(self.__trace)
        super()._bootstrap()

    def __trace(self, frame, event, arg):
        if self.__stop:
            raise StopThread()
        return self.__trace


def led_flash():
    while TRUE:
        s.setDTR(1)
        time.sleep(blink_freq)
        s.setDTR(0)
        time.sleep(blink_freq)


def json_request(kodi_request, host):
    PORT   =    8080
    URL    =    'http://' + host + ':' + str(PORT) + '/jsonrpc'
    HEADER =    {'Content-Type': 'application/json'}

    if host == 'localhost':
        response = xbmc.executeJSONRPC(json.dumps(kodi_request))
        if response:
            return json.loads(response.decode('utf-8','mixed'))

    request = urllib2.Request(URL, json.dumps(kodi_request), HEADER)
    with closing(urllib2.urlopen(request)) as response:
        return json.loads(response.read().decode('utf-8', 'mixed'))


def is_recording():
    result = False
    #http://192.168.178.12:8080/jsonrpc?request={ "jsonrpc": "2.0", "method": "PVR.GetProperties", "params": { "properties": [ "recording" ] }, "id": 1 }
    PVR_GET_PROPERTIES = {
        'jsonrpc': '2.0',
        'method': 'PVR.GetProperties',
        'params': {
            'properties': ['recording']
            },
        'id': 1
    }

    try:
        data = json_request(PVR_GET_PROPERTIES, 'localhost')
        if data['result']:
            result = True if data['result']['recording'].lower() == 'true' else False
    except KeyError:
        pass

    return result


if __name__ == '__main__':

    monitor = MyMonitor()
    xbmc.log(msg='[{}] Addon started.'.format(__addon_id__), level=xbmc.LOGNOTICE)
    load_addon_settings()

    #Open COM1
    s = serial.Serial(serial_port)
    # Turn off all lights
    s.setDTR(0)
    #s.setRTS(0)

    while not monitor.abortRequested():
        if is_recording():
            led_thread = MyThread(target=led_flash)
            led_thread.start()
            #continue doing stuff
        else:
            if led_thread and flashing_thread.isAlive():
                led_thread.stop()
        if monitor.waitForAbort(float(sleep_time)):
            break
#else:
#    load_addon_settings()
