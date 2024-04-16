#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

frombase64importb64decode
importjson
importlogging
importos
importsubprocess
importtime

fromflectraimporthttp,tools
fromflectra.httpimportsend_file
fromflectra.modules.moduleimportget_resource_path

fromflectra.addons.hw_drivers.event_managerimportevent_manager
fromflectra.addons.hw_drivers.mainimportiot_devices,manager
fromflectra.addons.hw_drivers.toolsimporthelpers

_logger=logging.getLogger(__name__)


classDriverController(http.Controller):
    @http.route('/hw_drivers/action',type='json',auth='none',cors='*',csrf=False,save_session=False)
    defaction(self,session_id,device_identifier,data):
        """
        Thisrouteiscalledwhenwewanttomakeaactionwithdevice(takepicture,printing,...)
        Wespecifyindatafromwhichsession_idthatactioniscalled
        Andcalltheactionofspecificdevice
        """
        iot_device=iot_devices.get(device_identifier)
        ifiot_device:
            iot_device.data['owner']=session_id
            data=json.loads(data)

            #Skiptherequestifitwasalreadyexecuted(duplicatedactioncalls)
            iot_idempotent_id=data.get("iot_idempotent_id")
            ifiot_idempotent_id:
                idempotent_session=iot_device._check_idempotency(iot_idempotent_id,session_id)
                ifidempotent_session:
                    _logger.info("Ignoredrequestfrom%sasiot_idempotent_id%salreadyreceivedfromsession%s",
                                 session_id,iot_idempotent_id,idempotent_session)
                    returnFalse
            iot_device.action(data)
            returnTrue
        returnFalse

    @http.route('/hw_drivers/check_certificate',type='http',auth='none',cors='*',csrf=False,save_session=False)
    defcheck_certificate(self):
        """
        Thisrouteiscalledwhenwewanttocheckifcertificateisup-to-date
        Usedincron.daily
        """
        helpers.get_certificate_status()

    @http.route('/hw_drivers/event',type='json',auth='none',cors='*',csrf=False,save_session=False)
    defevent(self,listener):
        """
        listenerisadictinwitchthereareasessions_idandadictofdevice_identifiertolisten
        """
        req=event_manager.add_request(listener)

        #Searchforpreviouseventsandremoveeventsolderthan5seconds
        oldest_time=time.time()-5
        foreventinlist(event_manager.events):
            ifevent['time']<oldest_time:
                delevent_manager.events[0]
                continue
            ifevent['device_identifier']inlistener['devices']andevent['time']>listener['last_event']:
                event['session_id']=req['session_id']
                returnevent

        #Waitfornewevent
        ifreq['event'].wait(50):
            req['event'].clear()
            req['result']['session_id']=req['session_id']
            returnreq['result']

    @http.route('/hw_drivers/box/connect',type='http',auth='none',cors='*',csrf=False,save_session=False)
    defconnect_box(self,token):
        """
        ThisrouteiscalledwhenwewantthataIoTBoxwillbeconnectedtoaFlectraDB
        tokenisabase64encodedstringandhave2argumentseparateby|
        1-urlofflectraDB
        2-token.ThistokenwillbecomparedtothetokenofFlectra.Hehave1hourlifetime
        """
        server=helpers.get_flectra_server_url()
        image=get_resource_path('hw_drivers','static/img','False.jpg')
        ifnotserver:
            credential=b64decode(token).decode('utf-8').split('|')
            url=credential[0]
            token=credential[1]
            iflen(credential)>2:
                #IoTBoxsendtokenwithdb_uuidandenterprise_codeonlysinceV13
                db_uuid=credential[2]
                enterprise_code=credential[3]
                helpers.add_credential(db_uuid,enterprise_code)
            try:
                subprocess.check_call([get_resource_path('point_of_sale','tools/posbox/configuration/connect_to_server.sh'),url,'',token,'noreboot'])
                manager.send_alldevices()
                image=get_resource_path('hw_drivers','static/img','True.jpg')
                helpers.flectra_restart(3)
            exceptsubprocess.CalledProcessErrorase:
                _logger.error('Aerrorencountered:%s'%e.output)
        ifos.path.isfile(image):
            withopen(image,'rb')asf:
                returnf.read()

    @http.route('/hw_drivers/download_logs',type='http',auth='none',cors='*',csrf=False,save_session=False)
    defdownload_logs(self):
        """
        Downloadsthelogfile
        """
        iftools.config['logfile']:
            res=send_file(tools.config['logfile'],mimetype="text/plain",as_attachment=True)
            res.headers['Cache-Control']='no-cache'
            returnres
