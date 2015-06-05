'''
Created on 04.06.2015

@author: jrenken
'''
from dataprovider.datadevice.datadevice import DataDevice
from PyQt4.QtNetwork import QUdpSocket, QHostAddress, QAbstractSocket


class UdpDevice(DataDevice):
    '''
    Implementation of a UDP server socket
    '''


    def __init__(self, params = {}, parent = None):
        '''
        Constructor
        '''
        super(UdpDevice, self).__init__(params, parent)
        
        self.iodevice = QUdpSocket()
        self.reconnect = int(params.get('Reconnect', 1000))
        self.host = self.params.get('Host', None)
        self.port = int(self.params.get('Port', 2000))
        self.iodevice.readyRead.connect( self.readyRead )

    def connectDevice(self):
        result = False
        if self.host is None:
            result = self.iodevice.bind(self.port) is False
        else:        
            ha = QHostAddress(self.host)
            result = self.iodevice.bind(ha, self.port)  
        
        if result is False:
            if self.reconnect > 0:
                self.timer.singleShot(int, self, self.onReconnectTimer)
        else:
            self.deviceConnected.emit() 
            
    def disconnectDevice(self):
        if self.iodevice.state() is QAbstractSocket.BoundState:
            self.iodevice.disconnectFromHost()
            self.deviceDisconnected.emit()

    def readData(self):
        (data, ha, port) = self.iodevice.readDatagram(self.iodevice.pendingDatagramSize())
        self.remoteHost = ha.toString()
        self.remotePort = port 
        return data
    
    
        
        