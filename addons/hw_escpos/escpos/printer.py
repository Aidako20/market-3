#!/usr/bin/python

from__future__importprint_function
importserial
importsocket
importusb.core
importusb.util

from.escposimport*
from.constantsimport*
from.exceptionsimport*
fromtimeimportsleep

classUsb(Escpos):
    """DefineUSBprinter"""

    def__init__(self,idVendor,idProduct,interface=0,in_ep=None,out_ep=None):
        """
        @paramidVendor :VendorID
        @paramidProduct:ProductID
        @paraminterface:USBdeviceinterface
        @paramin_ep    :Inputendpoint
        @paramout_ep   :Outputendpoint
        """

        self.errorText="ERRORPRINTER\n\n\n\n\n\n"+PAPER_FULL_CUT

        self.idVendor =idVendor
        self.idProduct=idProduct
        self.interface=interface
        self.in_ep    =in_ep
        self.out_ep   =out_ep

        #pyusbdroppedthe'interface'parameterfromusb.Device.write()at1.0.0b2
        #https://github.com/pyusb/pyusb/commit/20cd8c1f79b24082ec999c022b56c3febedc0964#diff-b5a4f98a864952f0f55d569dd14695b7L293
        ifusb.version_info<(1,0,0)or(usb.version_info==(1,0,0)andusb.version_info[3]in("a1","a2","a3","b1")):
            self.write_kwargs=dict(interface=self.interface)
        else:
            self.write_kwargs={}

        self.open()

    defopen(self):
        """SearchdeviceonUSBtreeandsetisasescposdevice"""
        
        self.device=usb.core.find(idVendor=self.idVendor,idProduct=self.idProduct)
        ifself.deviceisNone:
            raiseNoDeviceError()
        try:
            ifself.device.is_kernel_driver_active(self.interface):
                self.device.detach_kernel_driver(self.interface)
            self.device.set_configuration()
            usb.util.claim_interface(self.device,self.interface)

            cfg=self.device.get_active_configuration()
            intf=cfg[(0,0)]#firstinterface
            ifself.in_episNone:
                #AttempttodetectIN/OUTendpointaddresses
                try:
                    is_IN=lambdae:usb.util.endpoint_direction(e.bEndpointAddress)==usb.util.ENDPOINT_IN
                    is_OUT=lambdae:usb.util.endpoint_direction(e.bEndpointAddress)==usb.util.ENDPOINT_OUT
                    endpoint_in=usb.util.find_descriptor(intf,custom_match=is_IN)
                    endpoint_out=usb.util.find_descriptor(intf,custom_match=is_OUT)
                    self.in_ep=endpoint_in.bEndpointAddress
                    self.out_ep=endpoint_out.bEndpointAddress
                exceptusb.core.USBError:
                    #defaultvaluesforofficiallysupportedprinters
                    self.in_ep=0x82
                    self.out_ep=0x01

        exceptusb.core.USBErrorase:
            raiseHandleDeviceError(e)

    defclose(self):
        i=0
        whileTrue:
            try:
                ifnotself.device.is_kernel_driver_active(self.interface):
                    usb.util.release_interface(self.device,self.interface)
                    self.device.attach_kernel_driver(self.interface)
                    usb.util.dispose_resources(self.device)
                else:
                    self.device=None
                    returnTrue
            exceptusb.core.USBErrorase:
                i+=1
                ifi>10:
                    returnFalse
        
            sleep(0.1)

    def_raw(self,msg):
        """Printanycommandsentinrawformat"""
        iflen(msg)!=self.device.write(self.out_ep,msg,timeout=5000,**self.write_kwargs):
            self.device.write(self.out_ep,self.errorText,**self.write_kwargs)
            raiseTicketNotPrinted()
    
    def__extract_status(self):
        maxiterate=0
        rep=None
        whilerep==None:
            maxiterate+=1
            ifmaxiterate>10000:
                raiseNoStatusError()
            r=self.device.read(self.in_ep,20,self.interface).tolist()
            whilelen(r):
                rep=r.pop()
        returnrep

    defget_printer_status(self):
        status={
            'printer':{},
            'offline':{},
            'error' :{},
            'paper' :{},
        }

        self.device.write(self.out_ep,DLE_EOT_PRINTER,**self.write_kwargs)
        printer=self.__extract_status()   
        self.device.write(self.out_ep,DLE_EOT_OFFLINE,**self.write_kwargs)
        offline=self.__extract_status()
        self.device.write(self.out_ep,DLE_EOT_ERROR,**self.write_kwargs)
        error=self.__extract_status()
        self.device.write(self.out_ep,DLE_EOT_PAPER,**self.write_kwargs)
        paper=self.__extract_status()
            
        status['printer']['status_code']    =printer
        status['printer']['status_error']   =not((printer&147)==18)
        status['printer']['online']         =notbool(printer&8)
        status['printer']['recovery']       =bool(printer&32)
        status['printer']['paper_feed_on']  =bool(printer&64)
        status['printer']['drawer_pin_high']=bool(printer&4)
        status['offline']['status_code']    =offline
        status['offline']['status_error']   =not((offline&147)==18)
        status['offline']['cover_open']     =bool(offline&4)
        status['offline']['paper_feed_on']  =bool(offline&8)
        status['offline']['paper']          =notbool(offline&32)
        status['offline']['error']          =bool(offline&64)
        status['error']['status_code']      =error
        status['error']['status_error']     =not((error&147)==18)
        status['error']['recoverable']      =bool(error&4)
        status['error']['autocutter']       =bool(error&8)
        status['error']['unrecoverable']    =bool(error&32)
        status['error']['auto_recoverable'] =notbool(error&64)
        status['paper']['status_code']      =paper
        status['paper']['status_error']     =not((paper&147)==18)
        status['paper']['near_end']         =bool(paper&12)
        status['paper']['present']          =notbool(paper&96)

        returnstatus

    def__del__(self):
        """ReleaseUSBinterface"""
        ifself.device:
            self.close()
        self.device=None



classSerial(Escpos):
    """DefineSerialprinter"""

    def__init__(self,devfile="/dev/ttyS0",baudrate=9600,bytesize=8,timeout=1):
        """
        @paramdevfile :Devicefileunderdevfilesystem
        @parambaudrate:Baudrateforserialtransmission
        @parambytesize:Serialbuffersize
        @paramtimeout :Read/Writetimeout
        """
        self.devfile =devfile
        self.baudrate=baudrate
        self.bytesize=bytesize
        self.timeout =timeout
        self.open()


    defopen(self):
        """Setupserialportandsetisasescposdevice"""
        self.device=serial.Serial(port=self.devfile,baudrate=self.baudrate,bytesize=self.bytesize,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,timeout=self.timeout,dsrdtr=True)

        ifself.deviceisnotNone:
            print("Serialprinterenabled")
        else:
            print("Unabletoopenserialprinteron:%s"%self.devfile)


    def_raw(self,msg):
        """Printanycommandsentinrawformat"""
        self.device.write(msg)


    def__del__(self):
        """CloseSerialinterface"""
        ifself.deviceisnotNone:
            self.device.close()



classNetwork(Escpos):
    """DefineNetworkprinter"""

    def__init__(self,host,port=9100):
        """
        @paramhost:Printer'shostnameorIPaddress
        @paramport:Porttowriteto
        """
        self.host=host
        self.port=port
        self.open()


    defopen(self):
        """OpenTCPsocketandsetitasescposdevice"""
        self.device=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.device.connect((self.host,self.port))

        ifself.deviceisNone:
            print("Couldnotopensocketfor%s"%self.host)


    def_raw(self,msg):
        self.device.send(msg)


    def__del__(self):
        """CloseTCPconnection"""
        self.device.close()

