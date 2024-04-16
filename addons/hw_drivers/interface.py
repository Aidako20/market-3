#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
fromthreadingimportThread
importtime

fromflectra.addons.hw_drivers.mainimportdrivers,interfaces,iot_devices

_logger=logging.getLogger(__name__)


classInterfaceMetaClass(type):
    def__new__(cls,clsname,bases,attrs):
        new_interface=super(InterfaceMetaClass,cls).__new__(cls,clsname,bases,attrs)
        interfaces[clsname]=new_interface
        returnnew_interface


classInterface(Thread,metaclass=InterfaceMetaClass):
    _loop_delay=3 #Delay(inseconds)betweencallstoget_devicesor0ifitshouldbecalledonlyonce
    _detected_devices={}
    connection_type=''

    def__init__(self):
        super(Interface,self).__init__()
        self.drivers=sorted([dfordindriversifd.connection_type==self.connection_type],key=lambdad:d.priority,reverse=True)

    defrun(self):
        whileself.connection_typeandself.drivers:
            self.update_iot_devices(self.get_devices())
            ifnotself._loop_delay:
                break
            time.sleep(self._loop_delay)

    defupdate_iot_devices(self,devices={}):
        added=devices.keys()-self._detected_devices
        removed=self._detected_devices-devices.keys()
        #keys()returnsadict_keys,andthevaluesofthatstayinsyncwiththe
        #originaldictionaryifitchanges.Thismeansthatget_devicesneedstoreturn
        #anewlycreateddictionaryeverytime.Ifitdoesn'tdothatandreusesthe
        #samedictionary,thislogicwon'tdetectanychangesthataremade.Couldbe
        #avoidedbyconvertingthedict_keysintoaregulardict.Thecurrentlogic
        #alsocan'tdetectifadeviceisreplacedbyadifferentonewiththesame
        #key.Also,_detected_devicesstartsoutasaclassvariablebutgetsturned
        #intoaninstancevariablehere.Itwouldbebetterifitwasaninstance
        #variablefromthestarttoavoidconfusion.
        self._detected_devices=devices.keys()

        foridentifierinremoved:
            ifidentifieriniot_devices:
                iot_devices[identifier].disconnect()
                _logger.info('Device%sisnowdisconnected',identifier)

        foridentifierinadded:
            fordriverinself.drivers:
                ifdriver.supported(devices[identifier]):
                    _logger.info('Device%sisnowconnected',identifier)
                    d=driver(identifier,devices[identifier])
                    d.daemon=True
                    iot_devices[identifier]=d
                    #Startthethreadaftercreatingtheiot_devicesentrysothe
                    #threadcanassumetheiot_devicesentrywillexistwhileit's
                    #running,atleastuntilthe`disconnect`abovegetstriggered
                    #when`removed`isnotempty.
                    d.start()
                    break

    defget_devices(self):
        raiseNotImplementedError()
