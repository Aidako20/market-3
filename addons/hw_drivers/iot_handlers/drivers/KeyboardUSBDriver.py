#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importctypes
importevdev
importjson
importlogging
fromlxmlimportetree
importos
frompathlibimportPath
fromqueueimportQueue,Empty
importre
importsubprocess
fromthreadingimportLock
importtime
importurllib3
fromusbimportutil

fromflectraimporthttp,_
fromflectra.addons.hw_drivers.controllers.proxyimportproxy_drivers
fromflectra.addons.hw_drivers.driverimportDriver
fromflectra.addons.hw_drivers.event_managerimportevent_manager
fromflectra.addons.hw_drivers.mainimportiot_devices
fromflectra.addons.hw_drivers.toolsimporthelpers

_logger=logging.getLogger(__name__)
xlib=ctypes.cdll.LoadLibrary('libX11.so.6')


classKeyboardUSBDriver(Driver):
    connection_type='usb'
    keyboard_layout_groups=[]
    available_layouts=[]

    def__init__(self,identifier,device):
        ifnothasattr(KeyboardUSBDriver,'display'):
            os.environ['XAUTHORITY']="/run/lightdm/pi/xauthority"
            KeyboardUSBDriver.display=xlib.XOpenDisplay(bytes(":0.0","utf-8"))

        super(KeyboardUSBDriver,self).__init__(identifier,device)
        self.device_connection='direct'
        self.device_name=self._set_name()

        #fromhttps://github.com/xkbcommon/libxkbcommon/blob/master/test/evdev-scancodes.h
        self._scancode_to_modifier={
            42:'left_shift',
            54:'right_shift',
            58:'caps_lock',
            69:'num_lock',
            100:'alt_gr',#rightalt
        }
        self._tracked_modifiers={modifier:Falseformodifierinself._scancode_to_modifier.values()}

        ifnotKeyboardUSBDriver.available_layouts:
            KeyboardUSBDriver.load_layouts_list()
        KeyboardUSBDriver.send_layouts_list()

        forevdev_devicein[evdev.InputDevice(path)forpathinevdev.list_devices()]:
            if(device.idVendor==evdev_device.info.vendor)and(device.idProduct==evdev_device.info.product):
                self.input_device=evdev_device

        self._set_device_type('scanner')ifself._is_scanner()elseself._set_device_type()

    @classmethod
    defsupported(cls,device):
        forcfgindevice:
            foritfincfg:
                ifitf.bInterfaceClass==3anditf.bInterfaceProtocol!=2:
                    device.interface_protocol=itf.bInterfaceProtocol
                    returnTrue
        returnFalse

    @classmethod
    defget_status(self):
        """Allows`hw_proxy.Proxy`toretrievethestatusofthescanners"""
        status='connected'ifany(iot_devices[d].device_type=="scanner"fordiniot_devices)else'disconnected'
        return{'status':status,'messages':''}

    @classmethod
    defsend_layouts_list(cls):
        server=helpers.get_flectra_server_url()
        ifserver:
            urllib3.disable_warnings()
            pm=urllib3.PoolManager(cert_reqs='CERT_NONE')
            server=server+'/iot/keyboard_layouts'
            try:
                pm.request('POST',server,fields={'available_layouts':json.dumps(cls.available_layouts)})
            exceptExceptionase:
                _logger.error('Couldnotreachconfiguredserver')
                _logger.error('Aerrorencountered:%s'%e)

    @classmethod
    defload_layouts_list(cls):
        tree=etree.parse("/usr/share/X11/xkb/rules/base.xml",etree.XMLParser(ns_clean=True,recover=True))
        layouts=tree.xpath("//layout")
        forlayoutinlayouts:
            layout_name=layout.xpath("./configItem/name")[0].text
            layout_description=layout.xpath("./configItem/description")[0].text
            KeyboardUSBDriver.available_layouts.append({
                'name':layout_description,
                'layout':layout_name,
            })
            forvariantinlayout.xpath("./variantList/variant"):
                variant_name=variant.xpath("./configItem/name")[0].text
                variant_description=variant.xpath("./configItem/description")[0].text
                KeyboardUSBDriver.available_layouts.append({
                    'name':variant_description,
                    'layout':layout_name,
                    'variant':variant_name,
                })

    def_set_name(self):
        try:
            manufacturer=util.get_string(self.dev,self.dev.iManufacturer)
            product=util.get_string(self.dev,self.dev.iProduct)
            returnre.sub(r"[^\w\-+/*&]",'',"%s-%s"%(manufacturer,product))
        exceptValueErrorase:
            _logger.warning(e)
            return_('Unknowninputdevice')

    defaction(self,data):
        ifdata.get('action',False)=='update_layout':
            layout={
                'layout':data.get('layout'),
                'variant':data.get('variant'),
            }
            self._change_keyboard_layout(layout)
            self.save_layout(layout)
        elifdata.get('action',False)=='update_is_scanner':
            is_scanner={'is_scanner':data.get('is_scanner')}
            self.save_is_scanner(is_scanner)
        else:
            self.data['value']=''
            event_manager.device_changed(self)

    defrun(self):
        try:
            foreventinself.input_device.read_loop():
                ifself._stopped.isSet():
                    break
                ifevent.type==evdev.ecodes.EV_KEY:
                    data=evdev.categorize(event)

                    modifier_name=self._scancode_to_modifier.get(data.scancode)
                    ifmodifier_name:
                        ifmodifier_namein('caps_lock','num_lock'):
                            ifdata.keystate==1:
                                self._tracked_modifiers[modifier_name]=notself._tracked_modifiers[modifier_name]
                        else:
                            self._tracked_modifiers[modifier_name]=bool(data.keystate) #1forkeydown,0forkeyup
                    elifdata.keystate==1:
                        self.key_input(data.scancode)

        exceptExceptionaserr:
            _logger.warning(err)

    def_change_keyboard_layout(self,new_layout):
        """Changethelayoutofthecurrentdevicetowhatisspecifiedin
        new_layout.

        Args:
            new_layout(dict):Adictcontainingtwokeys:
                -layout(str):Thelayoutcode
                -variant(str):Anoptionalkeytorepresentthevariantofthe
                                 selectedlayout
        """
        ifhasattr(self,'keyboard_layout'):
            KeyboardUSBDriver.keyboard_layout_groups.remove(self.keyboard_layout)

        ifnew_layout:
            self.keyboard_layout=new_layout.get('layout')or'us'
            ifnew_layout.get('variant'):
                self.keyboard_layout+="(%s)"%new_layout['variant']
        else:
            self.keyboard_layout='us'

        KeyboardUSBDriver.keyboard_layout_groups.append(self.keyboard_layout)
        subprocess.call(["setxkbmap","-display",":0.0",",".join(KeyboardUSBDriver.keyboard_layout_groups)])

        #Closethenre-opendisplaytorefreshthemapping
        xlib.XCloseDisplay(KeyboardUSBDriver.display)
        KeyboardUSBDriver.display=xlib.XOpenDisplay(bytes(":0.0","utf-8"))

    defsave_layout(self,layout):
        """Savethelayouttoafileontheboxtoreaditwhenrestartingit.
        Weneedthatinordertokeeptheselectedlayoutafterareboot.

        Args:
            new_layout(dict):Adictcontainingtwokeys:
                -layout(str):Thelayoutcode
                -variant(str):Anoptionalkeytorepresentthevariantofthe
                                 selectedlayout
        """
        file_path=Path.home()/'flectra-keyboard-layouts.conf'
        iffile_path.exists():
            data=json.loads(file_path.read_text())
        else:
            data={}
        data[self.device_identifier]=layout
        helpers.write_file('flectra-keyboard-layouts.conf',json.dumps(data))

    defsave_is_scanner(self,is_scanner):
        """Savethetypeofdevice.
        Weneedthatinordertokeeptheselectedtypeofdeviceafterareboot.
        """
        file_path=Path.home()/'flectra-keyboard-is-scanner.conf'
        iffile_path.exists():
            data=json.loads(file_path.read_text())
        else:
            data={}
        data[self.device_identifier]=is_scanner
        helpers.write_file('flectra-keyboard-is-scanner.conf',json.dumps(data))
        self._set_device_type('scanner')ifis_scanner.get('is_scanner')elseself._set_device_type()

    defload_layout(self):
        """Readthelayoutfromthesavedfiledandsetitascurrentlayout.
        Ifnofileornolayoutisfoundweuse'us'bydefault.
        """
        file_path=Path.home()/'flectra-keyboard-layouts.conf'
        iffile_path.exists():
            data=json.loads(file_path.read_text())
            layout=data.get(self.device_identifier,{'layout':'us'})
        else:
            layout={'layout':'us'}
        self._change_keyboard_layout(layout)

    def_is_scanner(self):
        """Readthedevicetypefromthesavedfiledandsetitascurrenttype.
        Ifnofileornodevicetypeisfoundwetrytodetectitautomatically.
        """
        device_name=self.device_name.lower()
        scanner_name=['barcode','scanner','reader']
        is_scanner=any(xindevice_nameforxinscanner_name)orself.dev.interface_protocol=='0'

        file_path=Path.home()/'flectra-keyboard-is-scanner.conf'
        iffile_path.exists():
            data=json.loads(file_path.read_text())
            is_scanner=data.get(self.device_identifier,{}).get('is_scanner',is_scanner)
        returnis_scanner

    def_keyboard_input(self,scancode):
        """Dealwithakeyboardinput.Sendthecharactercorrespondingtothe
        pressedkeyrepresentedbyitsscancodetotheconnectedFlectrainstance.

        Args:
            scancode(int):Thescancodeofthepressedkey.
        """
        self.data['value']=self._scancode_to_char(scancode)
        ifself.data['value']:
            event_manager.device_changed(self)

    def_barcode_scanner_input(self,scancode):
        """Dealwithabarcodescannerinput.Addthenewcharacterscannedto
        thecurrentbarcodeorcompletethebarcodeif"Return"ispressed.
        Whenabarcodeiscompleted,twotasksareperformed:
            -Sendadevice_changedupdatetotheeventmanagertonotifythe
            listenersthatthevaluehaschanged(usedinEnterprise).
            -Addthebarcodetothelistbarcodesthatarebeingqueriedin
            Community.

        Args:
            scancode(int):Thescancodeofthepressedkey.
        """
        ifscancode==28: #Return
            self.data['value']=self._current_barcode
            event_manager.device_changed(self)
            self._barcodes.put((time.time(),self._current_barcode))
            self._current_barcode=''
        else:
            self._current_barcode+=self._scancode_to_char(scancode)

    def_set_device_type(self,device_type='keyboard'):
        """Modifythedevicetypebetween'keyboard'and'scanner'

        Args:
            type(string):Typewantedtoswitch
        """
        ifdevice_type=='scanner':
            self.device_type='scanner'
            self.key_input=self._barcode_scanner_input
            self._barcodes=Queue()
            self._current_barcode=''
            self.input_device.grab()
            self.read_barcode_lock=Lock()
        else:
            self.device_type='keyboard'
            self.key_input=self._keyboard_input
        self.load_layout()

    def_scancode_to_char(self,scancode):
        """Translateareceivedscancodetoacharacterdependingonthe
        selectedkeyboardlayoutandthecurrentstateofthekeyboard's
        modifiers.

        Args:
            scancode(int):Thescancodeofthepressedkey,tobetranslatedto
                acharacter

        Returns:
            str:Thetranslatedscancode.
        """
        #Scancode->Keysym:Dependsonthekeyboardlayout
        group=KeyboardUSBDriver.keyboard_layout_groups.index(self.keyboard_layout)
        modifiers=self._get_active_modifiers(scancode)
        keysym=ctypes.c_int(xlib.XkbKeycodeToKeysym(KeyboardUSBDriver.display,scancode+8,group,modifiers))

        #TranslateKeysymtoacharacter
        key_pressed=ctypes.create_string_buffer(5)
        xlib.XkbTranslateKeySym(KeyboardUSBDriver.display,ctypes.byref(keysym),0,ctypes.byref(key_pressed),5,ctypes.byref(ctypes.c_int()))
        ifkey_pressed.value:
            returnkey_pressed.value.decode('utf-8')
        return''

    def_get_active_modifiers(self,scancode):
        """Getthestateofcurrentlyactivemodifiers.

        Args:
            scancode(int):Thescancodeofthekeybeingtranslated

        Returns:
            int:Thecurrentstateofthemodifiers:
                0--Lowercase
                1--Highercaseor(NumLock+keypressedonkeypad)
                2--AltGr
                3--Highercase+AltGr
        """
        modifiers=0
        uppercase=(self._tracked_modifiers['right_shift']orself._tracked_modifiers['left_shift'])^self._tracked_modifiers['caps_lock']
        ifuppercaseor(scancodein[71,72,73,75,76,77,79,80,81,82,83]andself._tracked_modifiers['num_lock']):
            modifiers+=1

        ifself._tracked_modifiers['alt_gr']:
            modifiers+=2

        returnmodifiers

    defread_next_barcode(self):
        """Getthevalueofthelastbarcodethatwasscannedbutnotsentyet
        andnotolderthan5seconds.ThisfunctionisusedinCommunity,when
        wedon'thaveaccesstotheIoTLongpolling.

        Returns:
            str:Thenextbarcodetobereadoranemptystring.
        """

        #Previousquerystillrunning,stopitbysendingafakebarcode
        ifself.read_barcode_lock.locked():
            self._barcodes.put((time.time(),""))

        withself.read_barcode_lock:
            try:
                timestamp,barcode=self._barcodes.get(True,55)
                iftimestamp>time.time()-5:
                    returnbarcode
            exceptEmpty:
                return''

proxy_drivers['scanner']=KeyboardUSBDriver


classKeyboardUSBController(http.Controller):
    @http.route('/hw_proxy/scanner',type='json',auth='none',cors='*')
    defget_barcode(self):
        scanners=[iot_devices[d]fordiniot_devicesifiot_devices[d].device_type=="scanner"]
        ifscanners:
            returnscanners[0].read_next_barcode()
        time.sleep(5)
        returnNone
