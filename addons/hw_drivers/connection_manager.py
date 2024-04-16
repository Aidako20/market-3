#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta
importlogging
importsubprocess
importrequests
fromthreadingimportThread
importtime
importurllib3

fromflectra.modules.moduleimportget_resource_path
fromflectra.addons.hw_drivers.mainimportiot_devices,manager
fromflectra.addons.hw_drivers.toolsimporthelpers

_logger=logging.getLogger(__name__)

classConnectionManager(Thread):
    def__init__(self):
        super(ConnectionManager,self).__init__()
        self.pairing_code=False
        self.pairing_uuid=False

    defrun(self):
        ifnothelpers.get_flectra_server_url()andnothelpers.access_point():
            end_time=datetime.now()+timedelta(minutes=5)
            while(datetime.now()<end_time):
                self._connect_box()
                time.sleep(10)
            self.pairing_code=False
            self.pairing_uuid=False
            self._refresh_displays()

    def_connect_box(self):
        data={
            'jsonrpc':2.0,
            'params':{
                'pairing_code':self.pairing_code,
                'pairing_uuid':self.pairing_uuid,
            }
        }

        try:
            urllib3.disable_warnings()
            req=requests.post('https://iot-proxy.flectrahq.com/flectra-enterprise/iot/connect-box',json=data,verify=False)
            result=req.json().get('result',{})
            ifall(keyinresultforkeyin['pairing_code','pairing_uuid']):
                self.pairing_code=result['pairing_code']
                self.pairing_uuid=result['pairing_uuid']
            elifall(keyinresultforkeyin['url','token','db_uuid','enterprise_code']):
                self._connect_to_server(result['url'],result['token'],result['db_uuid'],result['enterprise_code'])
        exceptExceptionase:
            _logger.error('Couldnotreachiot-proxy.flectrahq.com')
            _logger.error('Aerrorencountered:%s'%e)

    def_connect_to_server(self,url,token,db_uuid,enterprise_code):
        ifdb_uuidandenterprise_code:
            helpers.add_credential(db_uuid,enterprise_code)

        #SaveDBURLandtoken
        subprocess.check_call([get_resource_path('point_of_sale','tools/posbox/configuration/connect_to_server.sh'),url,'',token,'noreboot'])
        #NotifytheDB,sothatthekanbanviewalreadyshowstheIoTBox
        manager.send_alldevices()
        #Restarttocheckoutthegitbranch,getacertificate,loadtheIoThandlers...
        subprocess.check_call(["sudo","service","flectra","restart"])

    def_refresh_displays(self):
        """Refreshalldisplaystohidethepairingcode"""
        fordiniot_devices:
            ifiot_devices[d].device_type=='display':
                iot_devices[d].action({
                    'action':'display_refresh'
                })

connection_manager=ConnectionManager()
connection_manager.daemon=True
connection_manager.start()
