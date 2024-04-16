#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportnamedtuple
fromcontextlibimportcontextmanager
importlogging
importserial
fromthreadingimportLock
importtime
importtraceback

fromflectraimport_
fromflectra.addons.hw_drivers.event_managerimportevent_manager
fromflectra.addons.hw_drivers.driverimportDriver

_logger=logging.getLogger(__name__)

SerialProtocol=namedtuple(
    'SerialProtocol',
    "namebaudratebytesizestopbitsparitytimeoutwriteTimeoutmeasureRegexpstatusRegexp"
    "commandTerminatorcommandDelaymeasureDelaynewMeasureDelay"
    "measureCommandemptyAnswerValid")


@contextmanager
defserial_connection(path,protocol,is_probing=False):
    """Opensaserialconnectiontoadeviceandclosesitautomaticallyafteruse.

    :parampath:pathtothedevice
    :typepath:string
    :paramprotocol:anobjectcontainingtheserialprotocoltoconnecttoadevice
    :typeprotocol:namedtuple
    :paramis_probing:aflagthetifsetto`True`makesthetimeoutslonger,defaultstoFalse
    :typeis_probing:bool,optional
    """

    PROBING_TIMEOUT=1
    port_config={
        'baudrate':protocol.baudrate,
        'bytesize':protocol.bytesize,
        'stopbits':protocol.stopbits,
        'parity':protocol.parity,
        'timeout':PROBING_TIMEOUTifis_probingelseprotocol.timeout,              #longertimeoutsforprobing
        'writeTimeout':PROBING_TIMEOUTifis_probingelseprotocol.writeTimeout     #longertimeoutsforprobing
    }
    connection=serial.Serial(path,**port_config)
    yieldconnection
    connection.close()


classSerialDriver(Driver):
    """Abstractbaseclassforserialdrivers."""

    _protocol=None
    connection_type='serial'

    STATUS_CONNECTED='connected'
    STATUS_ERROR='error'
    STATUS_CONNECTING='connecting'

    def__init__(self,identifier,device):
        """Attributesinitializationmethodfor`SerialDriver`.

        :paramdevice:pathtothedevice
        :typedevice:str
        """

        super(SerialDriver,self).__init__(identifier,device)
        self._actions={
            'get_status':self._push_status,
        }
        self.device_connection='serial'
        self._device_lock=Lock()
        self._status={'status':self.STATUS_CONNECTING,'message_title':'','message_body':''}
        self._set_name()

    def_get_raw_response(connection):
        pass

    def_push_status(self):
        """Updatesthecurrentstatusandpushesittothefrontend."""

        self.data['status']=self._status
        event_manager.device_changed(self)

    def_set_name(self):
        """Triestobuildthedevice'snamebasedonitstypeandprotocolnamebutfallsbackonadefaultnameifthatdoesn'twork."""

        try:
            name=('%sserial%s'%(self._protocol.name,self.device_type)).title()
        exceptException:
            name='UnknownSerialDevice'
        self.device_name=name

    def_take_measure(self):
        pass

    def_do_action(self,data):
        """Helperfunctionthatcallsaspecificactionmethodonthedevice.

        :paramdata:the`_actions`keymappedtotheactionmethodwewanttocall
        :typedata:string
        """

        try:
            withself._device_lock:
                self._actions[data['action']](data)
                time.sleep(self._protocol.commandDelay)
        exceptException:
            msg=_('Anerroroccuredwhileperformingaction%son%s')%(data,self.device_name)
            _logger.exception(msg)
            self._status={'status':self.STATUS_ERROR,'message_title':msg,'message_body':traceback.format_exc()}
            self._push_status()

    defaction(self,data):
        """Establishaconnectionwiththedeviceifneededandhaveitperformaspecificaction.

        :paramdata:the`_actions`keymappedtotheactionmethodwewanttocall
        :typedata:string
        """

        ifself._connectionandself._connection.isOpen():
            self._do_action(data)
        else:
            withserial_connection(self.device_identifier,self._protocol)asconnection:
                self._connection=connection
                self._do_action(data)

    defrun(self):
        """Continuouslygetsnewmeasuresfromthedevice."""

        try:
            withserial_connection(self.device_identifier,self._protocol)asconnection:
                self._connection=connection
                self._status['status']=self.STATUS_CONNECTED
                self._push_status()
                whilenotself._stopped.isSet():
                    self._take_measure()
                    time.sleep(self._protocol.newMeasureDelay)
        exceptException:
            msg=_('Errorwhilereading%s',self.device_name)
            _logger.exception(msg)
            self._status={'status':self.STATUS_ERROR,'message_title':msg,'message_body':traceback.format_exc()}
            self._push_status()
