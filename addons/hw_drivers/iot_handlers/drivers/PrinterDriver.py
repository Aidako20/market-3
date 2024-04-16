#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

frombase64importb64decode
fromcupsimportIPPError,IPP_PRINTER_IDLE,IPP_PRINTER_PROCESSING,IPP_PRINTER_STOPPED
importdbus
importio
importlogging
importnetifacesasni
importos
fromPILimportImage,ImageOps
importre
importsubprocess
importtempfile
fromuuidimportgetnodeasget_mac

fromflectraimporthttp
fromflectra.addons.hw_drivers.connection_managerimportconnection_manager
fromflectra.addons.hw_drivers.controllers.proxyimportproxy_drivers
fromflectra.addons.hw_drivers.driverimportDriver
fromflectra.addons.hw_drivers.event_managerimportevent_manager
fromflectra.addons.hw_drivers.iot_handlers.interfaces.PrinterInterfaceimportPPDs,conn,cups_lock
fromflectra.addons.hw_drivers.mainimportiot_devices
fromflectra.addons.hw_drivers.toolsimporthelpers

_logger=logging.getLogger(__name__)

RECEIPT_PRINTER_COMMANDS={
    'star':{
        'center':b'\x1b\x1d\x61\x01',#ESCGSan
        'cut':b'\x1b\x64\x02', #ESCdn
        'title':b'\x1b\x69\x01\x01%s\x1b\x69\x00\x00', #ESCin1n2
        'drawers':[b'\x07',b'\x1a'] #BEL&SUB
    },
    'escpos':{
        'center':b'\x1b\x61\x01', #ESCan
        'cut':b'\x1d\x56\x41\n', #GSVm
        'title':b'\x1b\x21\x30%s\x1b\x21\x00', #ESC!n
        'drawers':[b'\x1b\x3d\x01',b'\x1b\x70\x00\x19\x19',b'\x1b\x70\x01\x19\x19'] #ESC=nthenESCpmt1t2
    }
}

defcups_notification_handler(message,uri,device_identifier,state,reason,accepting_jobs):
    ifdevice_identifieriniot_devices:
        reason=reasonifreason!='none'elseNone
        state_value={
            IPP_PRINTER_IDLE:'connected',
            IPP_PRINTER_PROCESSING:'processing',
            IPP_PRINTER_STOPPED:'stopped'
        }
        iot_devices[device_identifier].update_status(state_value[state],message,reason)

#CreateaCupssubscriptionifitdoesn'texistyet
try:
    conn.getSubscriptions('/printers/')
exceptIPPError:
    conn.createSubscription(
        uri='/printers/',
        recipient_uri='dbus://',
        events=['printer-state-changed']
    )

#ListenfornotificationsfromCups
bus=dbus.SystemBus()
bus.add_signal_receiver(cups_notification_handler,signal_name="PrinterStateChanged",dbus_interface="org.cups.cupsd.Notifier")


classPrinterDriver(Driver):
    connection_type='printer'

    def__init__(self,identifier,device):
        super(PrinterDriver,self).__init__(identifier,device)
        self.device_type='printer'
        self.device_connection=device['device-class'].lower()
        self.device_name=device['device-make-and-model']
        self.state={
            'status':'connecting',
            'message':'Connectingtoprinter',
            'reason':None,
        }
        self.send_status()

        self.receipt_protocol='star'if'STR_T'indevice['device-id']else'escpos'
        if'direct'inself.device_connectionandany(cmdindevice['device-id']forcmdin['CMD:STAR;','CMD:ESC/POS;']):
            self.print_status()

    @classmethod
    defsupported(cls,device):
        ifdevice.get('supported',False):
            returnTrue
        protocol=['dnssd','lpd','socket']
        ifany(xindevice['url']forxinprotocol)anddevice['device-make-and-model']!='Unknown'or'direct'indevice['device-class']:
            model=cls.get_device_model(device)
            ppdFile=''
            forppdinPPDs:
                ifmodelandmodelinPPDs[ppd]['ppd-product']:
                    ppdFile=ppd
                    break
            withcups_lock:
                ifppdFile:
                    conn.addPrinter(name=device['identifier'],ppdname=ppdFile,device=device['url'])
                else:
                    conn.addPrinter(name=device['identifier'],device=device['url'])
                conn.setPrinterInfo(device['identifier'],device['device-make-and-model'])
                conn.enablePrinter(device['identifier'])
                conn.acceptJobs(device['identifier'])
                conn.setPrinterUsersAllowed(device['identifier'],['all'])
                conn.addPrinterOptionDefault(device['identifier'],"usb-no-reattach","true")
                conn.addPrinterOptionDefault(device['identifier'],"usb-unidir","true")
            returnTrue
        returnFalse

    @classmethod
    defget_device_model(cls,device):
        device_model=""
        ifdevice.get('device-id'):
            fordevice_idin[device_lofordevice_loindevice['device-id'].split(';')]:
                ifany(xindevice_idforxin['MDL','MODEL']):
                    device_model=device_id.split(':')[1]
                    break
        elifdevice.get('device-make-and-model'):
            device_model=device['device-make-and-model']
        returnre.sub("[\(].*?[\)]","",device_model).strip()

    @classmethod
    defget_status(cls):
        status='connected'ifany(iot_devices[d].device_type=="printer"andiot_devices[d].device_connection=='direct'fordiniot_devices)else'disconnected'
        return{'status':status,'messages':''}

    defaction(self,data):
        ifdata.get('action')=='cashbox':
            self.open_cashbox()
        elifdata.get('action')=='print_receipt':
            self.print_receipt(b64decode(data['receipt']))
        else:
            self.print_raw(b64decode(data['document']))

    defdisconnect(self):
        self.update_status('disconnected','Printerwasdisconnected')
        super(PrinterDriver,self).disconnect()

    defupdate_status(self,status,message,reason=None):
        """Updatesthestateofthecurrentprinter.

        Args:
            status(str):Thenewvalueofthestatus
            message(str):Acomprehensivemessagedescribingthestatus
            reason(str):Thereasonfothecurrentstatus
        """
        ifself.state['status']!=statusorself.state['reason']!=reason:
            self.state={
                'status':status,
                'message':message,
                'reason':reason,
            }
            self.send_status()

    defsend_status(self):
        """SendsthecurrentstatusoftheprintertotheconnectedFlectrainstance.
        """
        self.data={
            'value':'',
            'state':self.state,
        }
        event_manager.device_changed(self)

    defprint_raw(self,data):
        process=subprocess.Popen(["lp","-d",self.device_identifier],stdin=subprocess.PIPE)
        process.communicate(data)

    defprint_receipt(self,receipt):
        im=Image.open(io.BytesIO(receipt))

        #Converttogreyscalethentoblackandwhite
        im=im.convert("L")
        im=ImageOps.invert(im)
        im=im.convert("1")

        print_command=getattr(self,'format_%s'%self.receipt_protocol)(im)
        self.print_raw(print_command)

    defformat_star(self,im):
        width=int((im.width+7)/8)

        raster_init=b'\x1b\x2a\x72\x41'
        raster_page_length=b'\x1b\x2a\x72\x50\x30\x00'
        raster_send=b'\x62'
        raster_close=b'\x1b\x2a\x72\x42'

        raster_data=b''
        dots=im.tobytes()
        whilelen(dots):
            raster_data+=raster_send+width.to_bytes(2,'little')+dots[:width]
            dots=dots[width:]

        returnraster_init+raster_page_length+raster_data+raster_close

    defformat_escpos(self,im):
        width=int((im.width+7)/8)

        raster_send=b'\x1d\x76\x30\x00'
        max_slice_height=255

        raster_data=b''
        dots=im.tobytes()
        whilelen(dots):
            im_slice=dots[:width*max_slice_height]
            slice_height=int(len(im_slice)/width)
            raster_data+=raster_send+width.to_bytes(2,'little')+slice_height.to_bytes(2,'little')+im_slice
            dots=dots[width*max_slice_height:]

        returnraster_data+RECEIPT_PRINTER_COMMANDS['escpos']['cut']

    defprint_status(self):
        """PrintsthestatusticketoftheIoTBoxonthecurrentprinter."""
        wlan=''
        ip=''
        mac=''
        homepage=''
        pairing_code=''

        ssid=helpers.get_ssid()
        wlan='\nWirelessnetwork:\n%s\n\n'%ssid

        interfaces=ni.interfaces()
        ips=[]
        foriface_idininterfaces:
            iface_obj=ni.ifaddresses(iface_id)
            ifconfigs=iface_obj.get(ni.AF_INET,[])
            forconfinifconfigs:
                ifconf.get('addr')andconf.get('addr'):
                    ips.append(conf.get('addr'))
        iflen(ips)==0:
            ip='\nERROR:CouldnotconnecttoLAN\n\nPleasecheckthattheIoTBoxiscorrec-\ntlyconnectedwithanetworkcable,\nthattheLANissetupwithDHCP,and\nthatnetworkaddressesareavailable'
        eliflen(ips)==1:
            ip='\nIPAddress:\n%s\n'%ips[0]
        else:
            ip='\nIPAddresses:\n%s\n'%'\n'.join(ips)

        iflen(ips)>=1:
            ips_filtered=[iforiinipsifi!='127.0.0.1']
            main_ips=ips_filteredandips_filtered[0]or'127.0.0.1'
            mac='\nMACAddress:\n%s\n'%helpers.get_mac_address()
            homepage='\nHomepage:\nhttp://%s:7073\n\n'%main_ips

        code=connection_manager.pairing_code
        ifcode:
            pairing_code='\nPairingCode:\n%s\n'%code

        commands=RECEIPT_PRINTER_COMMANDS[self.receipt_protocol]
        title=commands['title']%b'IoTBoxStatus'
        self.print_raw(commands['center']+title+b'\n'+wlan.encode()+mac.encode()+ip.encode()+homepage.encode()+pairing_code.encode()+commands['cut'])

    defopen_cashbox(self):
        """Sendsasignaltothecurrentprintertoopentheconnectedcashbox."""
        commands=RECEIPT_PRINTER_COMMANDS[self.receipt_protocol]
        fordrawerincommands['drawers']:
            self.print_raw(drawer)


classPrinterController(http.Controller):

    @http.route('/hw_proxy/default_printer_action',type='json',auth='none',cors='*')
    defdefault_printer_action(self,data):
        printer=next((dfordiniot_devicesifiot_devices[d].device_type=='printer'andiot_devices[d].device_connection=='direct'),None)
        ifprinter:
            iot_devices[printer].action(data)
            returnTrue
        returnFalse

proxy_drivers['printer']=PrinterDriver
