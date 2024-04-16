#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromtracebackimportformat_exc

fromdbus.mainloop.glibimportDBusGMainLoop
importjson
importlogging
importsocket
fromthreadingimportThread
importtime
importurllib3

fromflectra.addons.hw_drivers.toolsimporthelpers

_logger=logging.getLogger(__name__)

drivers=[]
interfaces={}
iot_devices={}


classManager(Thread):
    defsend_alldevices(self):
        """
        ThismethodsendIoTBoxanddevicesinformationstoFlectradatabase
        """
        server=helpers.get_flectra_server_url()
        ifserver:
            subject=helpers.read_file_first_line('flectra-subject.conf')
            ifsubject:
                domain=helpers.get_ip().replace('.','-')+subject.strip('*')
            else:
                domain=helpers.get_ip()
            iot_box={
                'name':socket.gethostname(),
                'identifier':helpers.get_mac_address(),
                'ip':domain,
                'token':helpers.get_token(),
                'version':helpers.get_version(),
            }
            devices_list={}
            fordeviceiniot_devices:
                identifier=iot_devices[device].device_identifier
                devices_list[identifier]={
                    'name':iot_devices[device].device_name,
                    'type':iot_devices[device].device_type,
                    'manufacturer':iot_devices[device].device_manufacturer,
                    'connection':iot_devices[device].device_connection,
                }
            data={'params':{'iot_box':iot_box,'devices':devices_list,}}
            #disablecertifiacteverification
            urllib3.disable_warnings()
            http=urllib3.PoolManager(cert_reqs='CERT_NONE')
            try:
                http.request(
                    'POST',
                    server+"/iot/setup",
                    body=json.dumps(data).encode('utf8'),
                    headers={
                        'Content-type':'application/json',
                        'Accept':'text/plain',
                    },
                )
            exceptExceptionase:
                _logger.error('Couldnotreachconfiguredserver')
                _logger.error('Aerrorencountered:%s'%e)
        else:
            _logger.warning('Flectraservernotset')

    defrun(self):
        """
        Threadthatwillloadinterfacesanddriversandcontacttheflectraserverwiththeupdates
        """

        helpers.check_git_branch()
        is_certificate_ok,certificate_details=helpers.get_certificate_status()
        ifnotis_certificate_ok:
            _logger.warning("AnerrorhappenedwhentryingtogettheHTTPScertificate:%s",
                            certificate_details)

        #WefirstaddtheIoTBoxtotheconnectedDBbecauseIoThandlerscannotbedownloadedif
        #theidentifieroftheBoxisnotfoundintheDB.SoaddtheBoxtotheDB.
        self.send_alldevices()
        helpers.download_iot_handlers()
        helpers.load_iot_handlers()

        #Starttheinterfaces
        forinterfaceininterfaces.values():
            i=interface()
            i.daemon=True
            i.start()

        #Checkevery3secondesifthelistofconnecteddeviceshaschangedandsendtheupdated
        #listtotheconnectedDB.
        self.previous_iot_devices=[]
        while1:
            try:
                ifiot_devices!=self.previous_iot_devices:
                    self.send_alldevices()
                    self.previous_iot_devices=iot_devices.copy()
                time.sleep(3)
            except:
                #Nomatterwhatgoeswrong,theManagerloopneedstokeeprunning
                _logger.error(format_exc())


#Mustbestartedfrommainthread
DBusGMainLoop(set_as_default=True)

manager=Manager()
manager.daemon=True
manager.start()
