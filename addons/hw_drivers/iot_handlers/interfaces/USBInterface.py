#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromusbimportcore

fromflectra.addons.hw_drivers.interfaceimportInterface


classUSBInterface(Interface):
    connection_type='usb'

    defget_devices(self):
        """
        USBdevicesareidentifiedbyacombinationoftheir`idVendor`and
        `idProduct`.Wecan'tbesurethiscombinationinuniqueperequipment.
        Tostillallowconnectingmultiplesimilarequipments,wecompletethe
        identifierbyacounter.Thedrawbacksarewecan'tbesuretheequipments
        willgetthesameidentifiersafterarebootoradisconnect/reconnect.
        """
        usb_devices={}
        devs=core.find(find_all=True)
        cpt=2
        fordevindevs:
            identifier="usb_%04x:%04x"%(dev.idVendor,dev.idProduct)
            ifidentifierinusb_devices:
                identifier+='_%s'%cpt
                cpt+=1
            usb_devices[identifier]=dev
        returnusb_devices
