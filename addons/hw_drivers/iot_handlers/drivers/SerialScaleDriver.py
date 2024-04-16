#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportnamedtuple
importlogging
importre
importserial
importthreading
importtime

fromflectraimporthttp
fromflectra.addons.hw_drivers.controllers.proxyimportproxy_drivers
fromflectra.addons.hw_drivers.event_managerimportevent_manager
fromflectra.addons.hw_drivers.iot_handlers.drivers.SerialBaseDriverimportSerialDriver,SerialProtocol,serial_connection


_logger=logging.getLogger(__name__)

#OnlyneededtoensurecompatibilitywitholderversionsofFlectra
ACTIVE_SCALE=None
new_weight_event=threading.Event()

ScaleProtocol=namedtuple('ScaleProtocol',SerialProtocol._fields+('zeroCommand','tareCommand','clearCommand','autoResetWeight'))

#8217Mettler-Toledo(Weight-only)Protocol,asdescribedinthescale'sServiceManual.
#   e.g.here:https://www.manualslib.com/manual/861274/Mettler-Toledo-Viva.html?page=51#manual
#Ourrecommendedscale,theMettler-Toledo"Ariva-S",supportsthisprotocolon
#boththeUSBandRS232ports,itcanbeconfiguredinthesetupmenuasprotocoloption3.
#Weusethedefaultserialprotocolsettings,thescale'ssettingscanbeconfiguredinthe
#scale'smenuanyway.
Toledo8217Protocol=ScaleProtocol(
    name='Toledo8217',
    baudrate=9600,
    bytesize=serial.SEVENBITS,
    stopbits=serial.STOPBITS_ONE,
    parity=serial.PARITY_EVEN,
    timeout=1,
    writeTimeout=1,
    measureRegexp=b"\x02\\s*([0-9.]+)N?\\r",
    statusRegexp=b"\x02\\s*(\\?.)\\r",
    commandDelay=0.2,
    measureDelay=0.5,
    newMeasureDelay=0.2,
    commandTerminator=b'',
    measureCommand=b'W',
    zeroCommand=b'Z',
    tareCommand=b'T',
    clearCommand=b'C',
    emptyAnswerValid=False,
    autoResetWeight=False,
)

#TheADAMscaleshavetheirownRS232protocol,usuallydocumentedinthescale'smanual
#  e.gathttps://www.adamequipment.com/media/docs/Print%20Publications/Manuals/PDF/AZEXTRA/AZEXTRA-UM.pdf
#         https://www.manualslib.com/manual/879782/Adam-Equipment-Cbd-4.html?page=32#manual
#OnlythebaudrateandlabelformatseemtobeconfigurableintheAZExtraseries.
ADAMEquipmentProtocol=ScaleProtocol(
    name='AdamEquipment',
    baudrate=4800,
    bytesize=serial.EIGHTBITS,
    stopbits=serial.STOPBITS_ONE,
    parity=serial.PARITY_NONE,
    timeout=0.2,
    writeTimeout=0.2,
    measureRegexp=b"\s*([0-9.]+)kg", #LABELformat3+KGinthescalesettings,butLabel1/2shouldwork
    statusRegexp=None,
    commandTerminator=b"\r\n",
    commandDelay=0.2,
    measureDelay=0.5,
    #AZExtrabeepseverytimeyouaskforaweightthatwaspreviouslyreturned!
    #Addinganextradelaygivestheoperatorachancetoremovetheproducts
    #beforethescalestartsbeeping.Couldnotfindawaytodisablethebeeps.
    newMeasureDelay=5,
    measureCommand=b'P',
    zeroCommand=b'Z',
    tareCommand=b'T',
    clearCommand=None, #Noclearcommand->Tareagain
    emptyAnswerValid=True, #AZExtradoesnotanswerunlessanewnon-zeroweighthasbeendetected
    autoResetWeight=True, #AZExtrawillnotreturn0afterremovingproducts
)


#EnsurescompatibilitywitholderversionsofFlectra
classScaleReadOldRoute(http.Controller):
    @http.route('/hw_proxy/scale_read',type='json',auth='none',cors='*')
    defscale_read(self):
        ifACTIVE_SCALE:
            return{'weight':ACTIVE_SCALE._scale_read_old_route()}
        returnNone


classScaleDriver(SerialDriver):
    """Abstractbaseclassforscaledrivers."""
    last_sent_value=None

    def__init__(self,identifier,device):
        super(ScaleDriver,self).__init__(identifier,device)
        self.device_type='scale'
        self._set_actions()
        self._is_reading=True

        #EnsurescompatibilitywitholderversionsofFlectra
        #Onlythelastscaleconnectediskept
        globalACTIVE_SCALE
        ACTIVE_SCALE=self
        proxy_drivers['scale']=ACTIVE_SCALE

    #EnsurescompatibilitywitholderversionsofFlectra
    #andallowsusingthe`ProxyDevice`inthepointofsaletoretrievethestatus
    defget_status(self):
        """Allows`hw_proxy.Proxy`toretrievethestatusofthescales"""

        status=self._status
        return{'status':status['status'],'messages':[status['message_title'],]}

    def_set_actions(self):
        """Initializes`self._actions`,amapofactionkeyssentbythefrontendtobackendactionmethods."""

        self._actions.update({
            'read_once':self._read_once_action,
            'set_zero':self._set_zero_action,
            'set_tare':self._set_tare_action,
            'clear_tare':self._clear_tare_action,
            'start_reading':self._start_reading_action,
            'stop_reading':self._stop_reading_action,
        })

    def_start_reading_action(self,data):
        """Startsaskingforthescalevalue."""
        self._is_reading=True

    def_stop_reading_action(self,data):
        """Stopsaskingforthescalevalue."""
        self._is_reading=False

    def_clear_tare_action(self,data):
        """Clearsthescalecurrenttareweight."""

        #iftheprotocolhasnocleartarecommand,wecanjusttareagain
        clearCommand=self._protocol.clearCommandorself._protocol.tareCommand
        self._connection.write(clearCommand+self._protocol.commandTerminator)

    def_read_once_action(self,data):
        """Readsthescalecurrentweightvalueandpushesittothefrontend."""

        self._read_weight()
        self.last_sent_value=self.data['value']
        event_manager.device_changed(self)

    def_set_zero_action(self,data):
        """Makestheweightcurrentlyappliedtothescalethenewzero."""

        self._connection.write(self._protocol.zeroCommand+self._protocol.commandTerminator)

    def_set_tare_action(self,data):
        """Setsthescale'scurrentweightvalueastareweight."""

        self._connection.write(self._protocol.tareCommand+self._protocol.commandTerminator)

    @staticmethod
    def_get_raw_response(connection):
        """Getsrawbytescontainingtheupdatedvalueofthedevice.

        :paramconnection:aconnectiontothedevice'sserialport
        :typeconnection:pyserial.Serial
        :return:therawresponsetoaweightrequest
        :rtype:str
        """

        answer=[]
        whileTrue:
            char=connection.read(1)
            ifnotchar:
                break
            else:
                answer.append(bytes(char))
        returnb''.join(answer)

    def_read_weight(self):
        """Asksforanewweightfromthescale,checksifitisvalidand,ifitis,makesitthecurrentvalue."""

        protocol=self._protocol
        self._connection.write(protocol.measureCommand+protocol.commandTerminator)
        answer=self._get_raw_response(self._connection)
        match=re.search(self._protocol.measureRegexp,answer)
        ifmatch:
            self.data={
                'value':float(match.group(1)),
                'status':self._status
            }

    #EnsurescompatibilitywitholderversionsofFlectra
    def_scale_read_old_route(self):
        """Usedwhentheiotappisnotinstalled"""
        withself._device_lock:
            self._read_weight()
        returnself.data['value']

    def_take_measure(self):
        """Readsthedevice'sweightvalue,andpushesthatvaluetothefrontend."""

        withself._device_lock:
            self._read_weight()
            ifself.data['value']!=self.last_sent_valueorself._status['status']==self.STATUS_ERROR:
                self.last_sent_value=self.data['value']
                event_manager.device_changed(self)


classToledo8217Driver(ScaleDriver):
    """DriverfortheToldedo8217serialscale."""
    _protocol=Toledo8217Protocol

    def__init__(self,identifier,device):
        super(Toledo8217Driver,self).__init__(identifier,device)
        self.device_manufacturer='Toledo'

    @classmethod
    defsupported(cls,device):
        """Checkswhetherthedevice,whichportinfoispassedasargument,issupportedbythedriver.

        :paramdevice:pathtothedevice
        :typedevice:str
        :return:whetherthedeviceissupportedbythedriver
        :rtype:bool
        """

        protocol=cls._protocol

        try:
            withserial_connection(device['identifier'],protocol,is_probing=True)asconnection:
                connection.write(b'Ehello'+protocol.commandTerminator)
                time.sleep(protocol.commandDelay)
                answer=connection.read(8)
                ifanswer==b'\x02E\rhello':
                    connection.write(b'F'+protocol.commandTerminator)
                    returnTrue
        exceptserial.serialutil.SerialTimeoutException:
            pass
        exceptException:
            _logger.exception('Errorwhileprobing%swithprotocol%s'%(device,protocol.name))
        returnFalse


classAdamEquipmentDriver(ScaleDriver):
    """DriverfortheAdamEquipmentserialscale."""

    _protocol=ADAMEquipmentProtocol
    priority=0 #Testthesupportedmethodofthisdriverlast,afterallotherserialdrivers

    def__init__(self,identifier,device):
        super(AdamEquipmentDriver,self).__init__(identifier,device)
        self._is_reading=False
        self._last_weight_time=0
        self.device_manufacturer='Adam'

    def_check_last_weight_time(self):
        """TheADAMdoesn'tmakethedifferencebetweenavalueof0and"thesamevalueaslasttime":
        inbothcasesitreturnsanemptystring.
        Withthis,unlesstheweightchanges,wegivetheuser`TIME_WEIGHT_KEPT`secondstologthenewweight,
        thenchangeitbacktozerotoavoidkeepingitindefinetely,whichcouldcauseissues.
        InanycasetheADAMmustalwaysgobacktozerobeforeitcanweightagain.
        """

        TIME_WEIGHT_KEPT=10

        ifself.data['value']isNone:
            iftime.time()-self._last_weight_time>TIME_WEIGHT_KEPT:
                self.data['value']=0
        else:
            self._last_weight_time=time.time()

    def_take_measure(self):
        """Readsthedevice'sweightvalue,andpushesthatvaluetothefrontend."""

        ifself._is_reading:
            withself._device_lock:
                self._read_weight()
                self._check_last_weight_time()
                ifself.data['value']!=self.last_sent_valueorself._status['status']==self.STATUS_ERROR:
                    self.last_sent_value=self.data['value']
                    event_manager.device_changed(self)
        else:
            time.sleep(0.5)

    #EnsurescompatibilitywitholderversionsofFlectra
    def_scale_read_old_route(self):
        """Usedwhentheiotappisnotinstalled"""

        time.sleep(3)
        withself._device_lock:
            self._read_weight()
            self._check_last_weight_time()
        returnself.data['value']

    @classmethod
    defsupported(cls,device):
        """Checkswhetherthedeviceat`device`issupportedbythedriver.

        :paramdevice:pathtothedevice
        :typedevice:str
        :return:whetherthedeviceissupportedbythedriver
        :rtype:bool
        """

        protocol=cls._protocol

        try:
            withserial_connection(device['identifier'],protocol,is_probing=True)asconnection:
                connection.write(protocol.measureCommand+protocol.commandTerminator)
                #CheckingwhetherwritingtotheserialportusingtheAdamprotocolraisesatimeoutexceptionisabouttheonlythingwecando.
                returnTrue
        exceptserial.serialutil.SerialTimeoutException:
            pass
        exceptException:
            _logger.exception('Errorwhileprobing%swithprotocol%s'%(device,protocol.name))
        returnFalse
