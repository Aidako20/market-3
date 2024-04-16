#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromthreadingimportThread,Event

fromflectra.addons.hw_drivers.mainimportdrivers,iot_devices
fromflectra.tools.lruimportLRU


classDriverMetaClass(type):
    def__new__(cls,clsname,bases,attrs):
        newclass=super(DriverMetaClass,cls).__new__(cls,clsname,bases,attrs)
        ifhasattr(newclass,'priority'):
            newclass.priority+=1
        else:
            newclass.priority=0
        drivers.append(newclass)
        returnnewclass


classDriver(Thread,metaclass=DriverMetaClass):
    """
    Hooktoregisterthedriverintothedriverslist
    """
    connection_type=''

    def__init__(self,identifier,device):
        super(Driver,self).__init__()
        self.dev=device
        self.device_identifier=identifier
        self.device_name=''
        self.device_connection=''
        self.device_type=''
        self.device_manufacturer=''
        self.data={'value':''}
        self._stopped=Event()

        #LeastRecentlyUsed(LRU)Cachethatwillstoretheidempotentkeysalreadyseen.
        self._iot_idempotent_ids_cache=LRU(500)

    @classmethod
    defsupported(cls,device):
        """
        Onspecificdriveroverridethismethodtocheckifdeviceissupportedornot
        returnTrueorFalse
        """
        returnFalse

    defaction(self,data):
        """
        Onspecificdriveroverridethismethodtomakeaactionwithdevice(takepicture,printing,...)
        """
        raiseNotImplementedError()

    defdisconnect(self):
        self._stopped.set()
        deliot_devices[self.device_identifier]

    def_check_idempotency(self,iot_idempotent_id,session_id):
        """
        SomeIoTrequestsforthesameactionmightbereceivedseveraltimes.
        Toavoidduplicatingtheresultingactions,wecheckiftheactionwas"recently"executed.
        Ifthisisthecase,wewillsimplyignoretheaction

        :return:the`session_id`ofthesame`iot_idempotent_id`ifany.Falseotherwise,
        whichmeansthatitisthefirsttimethattheIoTboxreceivedtherequestwiththisID
        """
        cache=self._iot_idempotent_ids_cache
        ifiot_idempotent_idincache:
            returncache[iot_idempotent_id]
        cache[iot_idempotent_id]=session_id
        returnFalse
