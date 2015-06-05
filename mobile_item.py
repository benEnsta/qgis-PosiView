'''
Created on 05.06.2015

@author: jrenken
'''
from PyQt4.QtCore import QObject, pyqtSlot
from qgis.core import QgsPoint
# from qgis.core import 


class MobileItem(QObject):
    '''
    A Mobile Item that reveives its position from a dataprovider and is displayed on the canvas
    Could be everything liek vehicles or simple beacons
    '''

    mobileItemCount = 0


    def __init__(self, iface, params = {}, parent = None):
        '''
        Constructor
        '''
        super(MobileItem, self).__init__(parent)

        self.iface = iface
        self.canvas = iface.mapCanvas()
        MobileItem.mobileItemCount += 1
        self.name = params.setdefault('Name', 'MobileItem_' + str(MobileItem.mobileItemCount))


    def properties(self):
        d = { 'Name' : self.name, 
              'timeout': self.timeoutTime, 
              'enabled': self.enabled,
              'provider' : self.dataProvider }
        d.update(self.marker.properties())
        return d


    def subscribePositionProvider(self, provider, filterId = None):
        provider.newDataReceived.connect(self.processNewData)
        if filterId != None:
            self.messageFilter[provider.name] = filterId
        elif provider.name in self.messageFilter.keys():
            del self.messageFilter[provider.name]

    
    
    def unsubscribePositionProvider(self, provider):
        try:
            provider.newDataReceived.disconnect( self.processData )
            del self.messageFilter[provider.name]
        except:
            pass

    @pyqtSlot(dict)
    def processNewData(self, data):
        if not self.enabled:
            return
        try:
            name = data['name']
            if name in self.messageFilter.keys():
                if data['id'] != self.messageFilter[name]:
                    return
        except:
            pass
        self.extData.update(data)
            
        if data.has_key('lat') and data.has_key('lon'):
            self.position = QgsPoint(data['lon'], data['lat'])
            pt = self.crsXform.transform(self.position)
            self.marker.newCoords(pt)
            self.newPosition.emit(self.position, data.get('depth', 0.0))
            self.timer.start(self.timeoutTime)
#             print self.name, " NewPosition: ", pt
            
        if data.has_key('heading'):
            self.newAttitude.emit(data['heading'], data.get('pitch', 0.0), data.get('roll', 0.0))
            self.marker.newHeading(data['heading'])
#             print self.name, ' New attitude ', data['heading'] 

    @pyqtSlot(float)
    def onScaleChange(self, scale):
        self.marker.updateSize()

    @pyqtSlot()
    def onCrsChange(self):
        crsDst = self.canvas.mapRenderer().destinationCrs()
        self.crsXform.setDestCRS(crsDst)

    @pyqtSlot(bool)
    def setEnabled(self, enabled):
        self.enabled = enabled
        self.marker.setVisible(self.enabled)
        self.marker.resetPosition()
        if self.enabled:
            self.timer.start(self.timeoutTime)
        else:
            self.timer.stop()
            
    @pyqtSlot()
    def deleteTrack(self):
        self.marker.deleteTrack()
