#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromglobimportglob

fromflectra.addons.hw_drivers.interfaceimportInterface


classSerialInterface(Interface):
    connection_type='serial'

    defget_devices(self):
        serial_devices={}
        foridentifieringlob('/dev/serial/by-path/*'):
            serial_devices[identifier]={
                'identifier':identifier
            }
        returnserial_devices
