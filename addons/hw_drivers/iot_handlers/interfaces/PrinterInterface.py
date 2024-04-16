#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcupsimportConnectionascups_connection
fromreimportsub
fromthreadingimportLock

fromflectra.addons.hw_drivers.interfaceimportInterface

conn=cups_connection()
PPDs=conn.getPPDs()
cups_lock=Lock() #WecanonlymakeonecalltoCupsatatime

classPrinterInterface(Interface):
    _loop_delay=120
    connection_type='printer'
    printer_devices={}

    defget_devices(self):
        discovered_devices={}
        withcups_lock:
            printers=conn.getPrinters()
            devices=conn.getDevices()
            forprinter_name,printerinprinters.items():
                path=printer.get('device-uri',False)
                ifprinter_name!=self.get_identifier(path):
                    printer.update({'supported':True})#theseprintersareautomaticallysupported
                    device_class='network'
                    if'usb'inprinter.get('device-uri'):
                        device_class='direct'
                    printer.update({'device-class':device_class})
                    printer.update({'device-make-and-model':printer})#givenamesettedinCups
                    printer.update({'device-id':''})
                    devices.update({printer_name:printer})
        forpath,deviceindevices.items():
            identifier=self.get_identifier(path)
            device.update({'identifier':identifier})
            device.update({'url':path})
            device.update({'disconnect_counter':0})
            discovered_devices.update({identifier:device})
        self.printer_devices.update(discovered_devices)
        #Dealwithdeviceswhichareonthelistbutwerenotfoundduringthiscallof"get_devices"
        #Iftheyaren'tdetected3timesconsecutively,removethemfromthelistofavailabledevices
        fordeviceinlist(self.printer_devices):
            ifnotdiscovered_devices.get(device):
                disconnect_counter=self.printer_devices.get(device).get('disconnect_counter')
                ifdisconnect_counter>=2:
                    self.printer_devices.pop(device,None)
                else:
                    self.printer_devices[device].update({'disconnect_counter':disconnect_counter+1})
        returndict(self.printer_devices)

    defget_identifier(self,path):
        if'uuid='inpath:
            identifier=sub('[^a-zA-Z0-9_]','',path.split('uuid=')[1])
        elif'serial='inpath:
            identifier=sub('[^a-zA-Z0-9_]','',path.split('serial=')[1])
        else:
            identifier=sub('[^a-zA-Z0-9_]','',path)
        returnidentifier
