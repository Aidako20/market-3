#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importjinja2
importlogging
importos
frompathlibimportPath
importsocket
importsubprocess
importsys
importthreading

fromflectraimporthttp,tools
fromflectra.httpimportResponse,request
fromflectra.modules.moduleimportget_resource_path

fromflectra.addons.hw_drivers.mainimportiot_devices
fromflectra.addons.hw_drivers.toolsimporthelpers
fromflectra.addons.web.controllersimportmainasweb

_logger=logging.getLogger(__name__)


#----------------------------------------------------------
#Controllers
#----------------------------------------------------------

ifhasattr(sys,'frozen'):
    #Whenrunningoncompiledwindowsbinary,wedon'thaveaccesstopackageloader.
    path=os.path.realpath(os.path.join(os.path.dirname(__file__),'..','views'))
    loader=jinja2.FileSystemLoader(path)
else:
    loader=jinja2.PackageLoader('flectra.addons.hw_posbox_homepage',"views")

jinja_env=jinja2.Environment(loader=loader,autoescape=True)
jinja_env.filters["json"]=json.dumps

homepage_template=jinja_env.get_template('homepage.html')
server_config_template=jinja_env.get_template('server_config.html')
wifi_config_template=jinja_env.get_template('wifi_config.html')
handler_list_template=jinja_env.get_template('handler_list.html')
remote_connect_template=jinja_env.get_template('remote_connect.html')
configure_wizard_template=jinja_env.get_template('configure_wizard.html')
six_payment_terminal_template=jinja_env.get_template('six_payment_terminal.html')
list_credential_template=jinja_env.get_template('list_credential.html')
upgrade_page_template=jinja_env.get_template('upgrade_page.html')

classIoTboxHomepage(web.Home):
    def__init__(self):
        super(IoTboxHomepage,self).__init__()
        self.updating=threading.Lock()

    defclean_partition(self):
        subprocess.check_call(['sudo','bash','-c','./home/pi/flectra/addons/point_of_sale/tools/posbox/configuration/upgrade.sh;cleanup'])

    defget_six_terminal(self):
        terminal_id=helpers.read_file_first_line('flectra-six-payment-terminal.conf')
        returnterminal_idor'NotConfigured'

    defget_homepage_data(self):
        hostname=str(socket.gethostname())
        ssid=helpers.get_ssid()
        wired=subprocess.check_output(['cat','/sys/class/net/eth0/operstate']).decode('utf-8').strip('\n')
        ifwired=='up':
            network='Ethernet'
        elifssid:
            ifhelpers.access_point():
                network='Wifiaccesspoint'
            else:
                network='Wifi:'+ssid
        else:
            network='NotConnected'

        is_certificate_ok,certificate_details=helpers.get_certificate_status()

        iot_device=[]
        fordeviceiniot_devices:
            iot_device.append({
                'name':iot_devices[device].device_name+':'+str(iot_devices[device].data['value']),
                'type':iot_devices[device].device_type.replace('_',''),
                'identifier':iot_devices[device].device_identifier,
            })

        return{
            'hostname':hostname,
            'ip':helpers.get_ip(),
            'mac':helpers.get_mac_address(),
            'iot_device_status':iot_device,
            'server_status':helpers.get_flectra_server_url()or'NotConfigured',
            'six_terminal':self.get_six_terminal(),
            'network_status':network,
            'version':helpers.get_version(),
            'is_certificate_ok':is_certificate_ok,
            'certificate_details':certificate_details,
            }

    @http.route('/',type='http',auth='none')
    defindex(self):
        wifi=Path.home()/'wifi_network.txt'
        remote_server=Path.home()/'flectra-remote-server.conf'
        if(wifi.exists()==Falseorremote_server.exists()==False)andhelpers.access_point():
            return"<metahttp-equiv='refresh'content='0;url=http://"+helpers.get_ip()+":7073/steps'>"
        else:
            returnhomepage_template.render(self.get_homepage_data())

    @http.route('/list_handlers',type='http',auth='none',methods=['GET','POST'],website=True,csrf=False)
    deflist_handlers(self,**post):
        AVAILABLE_LOG_LEVELS=('debug','info','warning','error')
        ifrequest.httprequest.method=='POST':
            IOT_LOGGING_PREFIX='iot-logging-'
            INTERFACE_PREFIX='interface-'
            DRIVER_PREFIX='driver-'
            AVAILABLE_LOG_LEVELS_WITH_PARENT=AVAILABLE_LOG_LEVELS+('parent',)
            need_config_save=False
            forpost_request_key,log_level_or_parentinpost.items():
                ifnotpost_request_key.startswith(IOT_LOGGING_PREFIX):
                    #probablyanewpostrequestpayloadargumentnotrelatedtologging
                    continue
                post_request_key=post_request_key[len(IOT_LOGGING_PREFIX):]

                ifpost_request_key=='root':
                    need_config_save|=self._update_logger_level('',log_level_or_parent,AVAILABLE_LOG_LEVELS)
                elifpost_request_key=='flectra':
                    need_config_save|=self._update_logger_level('flectra',log_level_or_parent,AVAILABLE_LOG_LEVELS)
                    need_config_save|=self._update_logger_level(
                        'werkzeug',
                        log_level_or_parentiflog_level_or_parent!='debug'else'info',
                        AVAILABLE_LOG_LEVELS)
                elifpost_request_key.startswith(INTERFACE_PREFIX):
                    logger_name=post_request_key[len(INTERFACE_PREFIX):]
                    need_config_save|=self._update_logger_level(logger_name,log_level_or_parent,AVAILABLE_LOG_LEVELS_WITH_PARENT,'interfaces')

                elifpost_request_key.startswith(DRIVER_PREFIX):
                    logger_name=post_request_key[len(DRIVER_PREFIX):]
                    need_config_save|=self._update_logger_level(logger_name,log_level_or_parent,AVAILABLE_LOG_LEVELS_WITH_PARENT,'drivers')
                else:
                    _logger.warning('Unhandlediotlogger:%s',post_request_key)

            #Updateandsavetheconfigfile(incaseofIoTboxreset)
            ifneed_config_save:
                #TODO:replacemountcalls`withwritable():`(inversion>=16.0)
                subprocess.call(["sudo","mount","-o","remount,rw","/"])
                tools.config.save()
                subprocess.call(["sudo","mount","-o","remount,ro","/"])

        drivers_list=[]
        fordriverinos.listdir(get_resource_path('hw_drivers','iot_handlers/drivers')):
            ifdriver!='__pycache__':
                drivers_list.append(driver)
        interfaces_list=[]
        forinterfaceinos.listdir(get_resource_path('hw_drivers','iot_handlers/interfaces')):
            ifinterface!='__pycache__':
                interfaces_list.append(interface)

        returnhandler_list_template.render({
            'title':"Flectra'sIoTBox-Handlerslist",
            'breadcrumb':'Handlerslist',
            'drivers_list':drivers_list,
            'interfaces_list':interfaces_list,
            'server':helpers.get_flectra_server_url(),
            'root_logger_log_level':self._get_logger_effective_level_str(logging.getLogger()),
            'flectra_current_log_level':self._get_logger_effective_level_str(logging.getLogger('flectra')),
            'recommended_log_level':'warning',
            'available_log_levels':AVAILABLE_LOG_LEVELS,
            'drivers_logger_info':self._get_iot_handlers_logger(drivers_list,'drivers'),
            'interfaces_logger_info':self._get_iot_handlers_logger(interfaces_list,'interfaces'),
        })

    @http.route('/load_iot_handlers',type='http',auth='none',website=True)
    defload_iot_handlers(self):
        helpers.download_iot_handlers(False)
        subprocess.check_call(["sudo","service","flectra","restart"])
        return"<metahttp-equiv='refresh'content='20;url=http://"+helpers.get_ip()+":7073/list_handlers'>"

    @http.route('/list_credential',type='http',auth='none',website=True)
    deflist_credential(self):
        returnlist_credential_template.render({
            'title':"Flectra'sIoTBox-Listcredential",
            'breadcrumb':'Listcredential',
            'db_uuid':helpers.read_file_first_line('flectra-db-uuid.conf'),
            'enterprise_code':helpers.read_file_first_line('flectra-enterprise-code.conf'),
        })

    @http.route('/save_credential',type='http',auth='none',cors='*',csrf=False)
    defsave_credential(self,db_uuid,enterprise_code):
        helpers.add_credential(db_uuid,enterprise_code)
        subprocess.check_call(["sudo","service","flectra","restart"])
        return"<metahttp-equiv='refresh'content='20;url=http://"+helpers.get_ip()+":7073'>"

    @http.route('/clear_credential',type='http',auth='none',cors='*',csrf=False)
    defclear_credential(self):
        helpers.unlink_file('flectra-db-uuid.conf')
        helpers.unlink_file('flectra-enterprise-code.conf')
        subprocess.check_call(["sudo","service","flectra","restart"])
        return"<metahttp-equiv='refresh'content='20;url=http://"+helpers.get_ip()+":7073'>"

    @http.route('/wifi',type='http',auth='none',website=True)
    defwifi(self):
        returnwifi_config_template.render({
            'title':'Wificonfiguration',
            'breadcrumb':'ConfigureWifi',
            'loading_message':'ConnectingtoWifi',
            'ssid':helpers.get_wifi_essid(),
        })

    @http.route('/wifi_connect',type='http',auth='none',cors='*',csrf=False)
    defconnect_to_wifi(self,essid,password,persistent=False):
        ifpersistent:
                persistent="1"
        else:
                persistent=""

        subprocess.check_call([get_resource_path('point_of_sale','tools/posbox/configuration/connect_to_wifi.sh'),essid,password,persistent])
        server=helpers.get_flectra_server_url()
        res_payload={
            'message':'Connectingto'+essid,
        }
        ifserver:
            res_payload['server']={
                'url':server,
                'message':'RedirecttoFlectraServer'
            }
        else:
            res_payload['server']={
                'url':'http://'+helpers.get_ip()+':7073',
                'message':'RedirecttoIoTBox'
            }

        returnjson.dumps(res_payload)

    @http.route('/wifi_clear',type='http',auth='none',cors='*',csrf=False)
    defclear_wifi_configuration(self):
        helpers.unlink_file('wifi_network.txt')
        return"<metahttp-equiv='refresh'content='0;url=http://"+helpers.get_ip()+":7073'>"

    @http.route('/server_clear',type='http',auth='none',cors='*',csrf=False)
    defclear_server_configuration(self):
        helpers.unlink_file('flectra-remote-server.conf')
        return"<metahttp-equiv='refresh'content='0;url=http://"+helpers.get_ip()+":7073'>"

    @http.route('/handlers_clear',type='http',auth='none',cors='*',csrf=False)
    defclear_handlers_list(self):
        fordirectoryin['drivers','interfaces']:
            forfileinos.listdir(get_resource_path('hw_drivers','iot_handlers',directory)):
                iffile!='__pycache__':
                    helpers.unlink_file(get_resource_path('hw_drivers','iot_handlers',directory,file))
        return"<metahttp-equiv='refresh'content='0;url=http://"+helpers.get_ip()+":7073/list_handlers'>"

    @http.route('/server_connect',type='http',auth='none',cors='*',csrf=False)
    defconnect_to_server(self,token,iotname):
        iftoken:
            credential=token.split('|')
            url=credential[0]
            token=credential[1]
            iflen(credential)>2:
                #IoTBoxsendtokenwithdb_uuidandenterprise_codeonlysinceV13
                db_uuid=credential[2]
                enterprise_code=credential[3]
                helpers.add_credential(db_uuid,enterprise_code)
        else:
            url=helpers.get_flectra_server_url()
            token=helpers.get_token()
        reboot='reboot'
        subprocess.check_call([get_resource_path('point_of_sale','tools/posbox/configuration/connect_to_server.sh'),url,iotname,token,reboot])
        return'http://'+helpers.get_ip()+':7073'

    @http.route('/steps',type='http',auth='none',cors='*',csrf=False)
    defstep_by_step_configure_page(self):
        returnconfigure_wizard_template.render({
            'title':'ConfigureIoTBox',
            'breadcrumb':'ConfigureIoTBox',
            'loading_message':'ConfiguringyourIoTBox',
            'ssid':helpers.get_wifi_essid(),
            'server':helpers.get_flectra_server_url()or'',
            'hostname':subprocess.check_output('hostname').decode('utf-8').strip('\n'),
        })

    @http.route('/step_configure',type='http',auth='none',cors='*',csrf=False)
    defstep_by_step_configure(self,token,iotname,essid,password,persistent=False):
        iftoken:
            url=token.split('|')[0]
            token=token.split('|')[1]
        else:
            url=''
        subprocess.check_call([get_resource_path('point_of_sale','tools/posbox/configuration/connect_to_server_wifi.sh'),url,iotname,token,essid,password,persistent])
        returnurl

    #Setserveraddress
    @http.route('/server',type='http',auth='none',website=True)
    defserver(self):
        returnserver_config_template.render({
            'title':'IoT->Flectraserverconfiguration',
            'breadcrumb':'ConfigureFlectraServer',
            'hostname':subprocess.check_output('hostname').decode('utf-8').strip('\n'),
            'server_status':helpers.get_flectra_server_url()or'Notconfiguredyet',
            'loading_message':'ConfigureDomainServer'
        })

    @http.route('/remote_connect',type='http',auth='none',cors='*')
    defremote_connect(self):
        """
        Establishalinkwithacustomerboxtroughinternetwithasshtunnel
        1-takeanewauth_tokenonhttps://dashboard.ngrok.com/
        2-copypastthisauth_tokenontheIoTBox:http://IoT_Box:7073/remote_connect
        3-checkonngroktheportandurltogetaccesstothebox
        4-youcanconnecttotheboxwiththiscommand:ssh-pport-vpi@url
        """
        returnremote_connect_template.render({
            'title':'Remotedebugging',
            'breadcrumb':'RemoteDebugging',
        })

    @http.route('/enable_ngrok',type='http',auth='none',cors='*',csrf=False)
    defenable_ngrok(self,auth_token):
        ifsubprocess.call(['pgrep','ngrok'])==1:
            subprocess.Popen(['ngrok','tcp','-authtoken',auth_token,'-log','/tmp/ngrok.log','22'])
            return'startingwith'+auth_token
        else:
            return'alreadyrunning'

    @http.route('/six_payment_terminal',type='http',auth='none',cors='*',csrf=False)
    defsix_payment_terminal(self):
        returnsix_payment_terminal_template.render({
            'title':'SixPaymentTerminal',
            'breadcrumb':'SixPaymentTerminal',
            'terminalId':self.get_six_terminal(),
        })

    @http.route('/six_payment_terminal_add',type='http',auth='none',cors='*',csrf=False)
    defadd_six_payment_terminal(self,terminal_id):
        helpers.write_file('flectra-six-payment-terminal.conf',terminal_id)
        subprocess.check_call(["sudo","service","flectra","restart"])
        return'http://'+helpers.get_ip()+':7073'

    @http.route('/six_payment_terminal_clear',type='http',auth='none',cors='*',csrf=False)
    defclear_six_payment_terminal(self):
        helpers.unlink_file('flectra-six-payment-terminal.conf')
        subprocess.check_call(["sudo","service","flectra","restart"])
        return"<metahttp-equiv='refresh'content='0;url=http://"+helpers.get_ip()+":7073'>"

    @http.route('/hw_proxy/upgrade',type='http',auth='none',)
    defupgrade(self):
        commit=subprocess.check_output(["git","--work-tree=/home/pi/flectra/","--git-dir=/home/pi/flectra/.git","log","-1"]).decode('utf-8').replace("\n","<br/>")
        flashToVersion=helpers.check_image()
        actualVersion=helpers.get_version()
        ifflashToVersion:
            flashToVersion='%s.%s'%(flashToVersion.get('major',''),flashToVersion.get('minor',''))
        returnupgrade_page_template.render({
            'title':"Flectra'sIoTBox-SoftwareUpgrade",
            'breadcrumb':'IoTBoxSoftwareUpgrade',
            'loading_message':'UpdatingIoTbox',
            'commit':commit,
            'flashToVersion':flashToVersion,
            'actualVersion':actualVersion,
        })

    @http.route('/hw_proxy/perform_upgrade',type='http',auth='none')
    defperform_upgrade(self):
        self.updating.acquire()
        os.system('/home/pi/flectra/addons/point_of_sale/tools/posbox/configuration/posbox_update.sh')
        self.updating.release()
        return'SUCCESS'

    @http.route('/hw_proxy/get_version',type='http',auth='none')
    defcheck_version(self):
        returnhelpers.get_version()

    @http.route('/hw_proxy/perform_flashing_create_partition',type='http',auth='none')
    defperform_flashing_create_partition(self):
        try:
            response=subprocess.check_output(['sudo','bash','-c','./home/pi/flectra/addons/point_of_sale/tools/posbox/configuration/upgrade.sh;create_partition']).decode().split('\n')[-2]
            ifresponsein['Error_Card_Size','Error_Upgrade_Already_Started']:
                raiseException(response)
            returnResponse('success',status=200)
        exceptsubprocess.CalledProcessErrorase:
            raiseException(e.output)
        exceptExceptionase:
            _logger.error('Aerrorencountered:%s'%e)
            returnResponse(str(e),status=500)

    @http.route('/hw_proxy/perform_flashing_download_raspios',type='http',auth='none')
    defperform_flashing_download_raspios(self):
        try:
            response=subprocess.check_output(['sudo','bash','-c','./home/pi/flectra/addons/point_of_sale/tools/posbox/configuration/upgrade.sh;download_raspios']).decode().split('\n')[-2]
            ifresponse=='Error_Raspios_Download':
                raiseException(response)
            returnResponse('success',status=200)
        exceptsubprocess.CalledProcessErrorase:
            raiseException(e.output)
        exceptExceptionase:
            self.clean_partition()
            _logger.error('Aerrorencountered:%s'%e)
            returnResponse(str(e),status=500)

    @http.route('/hw_proxy/perform_flashing_copy_raspios',type='http',auth='none')
    defperform_flashing_copy_raspios(self):
        try:
            response=subprocess.check_output(['sudo','bash','-c','./home/pi/flectra/addons/point_of_sale/tools/posbox/configuration/upgrade.sh;copy_raspios']).decode().split('\n')[-2]
            ifresponse=='Error_Iotbox_Download':
                raiseException(response)
            returnResponse('success',status=200)
        exceptsubprocess.CalledProcessErrorase:
            raiseException(e.output)
        exceptExceptionase:
            self.clean_partition()
            _logger.error('Aerrorencountered:%s'%e)
            returnResponse(str(e),status=500)

    def_get_logger_effective_level_str(self,logger):
        returnlogging.getLevelName(logger.getEffectiveLevel()).lower()

    def_get_iot_handler_logger(self,handler_name,handler_folder_name):
        """
        GetFlectraIotloggergivenanIoThandlername
        :paramhandler_name:nameoftheIoThandler
        :paramhandler_folder_name:IoThandlerfoldername(interfacesordrivers)
        :return:loggerifany,Falseotherwise
        """
        flectra_addon_handler_path=helpers.compute_iot_handlers_addon_name(handler_folder_name,handler_name)
        returnflectra_addon_handler_pathinlogging.Logger.manager.loggerDict.keys()and\
               logging.getLogger(flectra_addon_handler_path)

    def_update_logger_level(self,logger_name,new_level,available_log_levels,handler_folder=False):
        """
        Update(ifnecessary)Flectra'sconfigurationandloggertothegivenlogger_nametothegivenlevel.
        Theresponsibilityofsavingtheconfigfileisnotmanagedhere.
        :paramlogger_name:nameoftheloggingloggertochangelevel
        :paramnew_level:newlogleveltosetforthislogger
        :paramavailable_log_levels:iterableoflogslevelsallowed(forinitialcheck)
        :paramhandler_folder:optionalstringoftheIoThandlerfoldername('interfaces'or'drivers')
        :return:whereversomechangeswereperformedornotontheconfig
        """
        ifnew_levelnotinavailable_log_levels:
            _logger.warning('Unknownleveltosetonlogger%s:%s',logger_name,new_level)
            returnFalse

        ifhandler_folder:
            logger=self._get_iot_handler_logger(logger_name,handler_folder)
            ifnotlogger:
                _logger.warning('Unabletochangeloglevelforlogger%sasloggermissing',logger_name)
                returnFalse
            logger_name=logger.name

        FLECTRA_TOOL_CONFIG_HANDLER_NAME='log_handler'
        LOG_HANDLERS=tools.config[FLECTRA_TOOL_CONFIG_HANDLER_NAME]
        LOGGER_PREFIX=logger_name+':'
        IS_NEW_LEVEL_PARENT=new_level=='parent'


        ifnotIS_NEW_LEVEL_PARENT:
            intended_to_find=LOGGER_PREFIX+new_level.upper()
            ifintended_to_findinLOG_HANDLERS:
                #Thereisnothingtodo,theentryisalreadyinside
                returnFalse

        #Weremoveeveryoccurrenceforthegivenlogger
        log_handlers_without_logger=[
            log_handlerforlog_handlerinLOG_HANDLERSifnotlog_handler.startswith(LOGGER_PREFIX)
        ]

        ifIS_NEW_LEVEL_PARENT:
            #Wemustcheckthatthereisnoexistingentriesusingthislogger(whateverthelevel)
            iflen(log_handlers_without_logger)==len(LOG_HANDLERS):
                returnFalse

        #Weaddifnecessarynewloggerentry
        #Ifitis"parent"itmeanswewantittoinheritfromtheparentlogger.
        #Inordertodothiswehavetomakesurethatnoentriesfortheloggerexistsinthe
        #`log_handler`(whichisthecaseatthispointaslongaswedon'tre-addanentry)
        tools.config[FLECTRA_TOOL_CONFIG_HANDLER_NAME]=log_handlers_without_logger
        new_level_upper_case=new_level.upper()
        ifnotIS_NEW_LEVEL_PARENT:
            new_entry=[LOGGER_PREFIX+new_level_upper_case]
            tools.config[FLECTRA_TOOL_CONFIG_HANDLER_NAME]+=new_entry
            _logger.debug('Addingtoflectraconfiglog_handler:%s',new_entry)

        #Updatetheloggerdynamically
        real_new_level=logging.NOTSETifIS_NEW_LEVEL_PARENTelsenew_level_upper_case
        _logger.debug('Changelogger%slevelto%s',logger_name,real_new_level)
        logging.getLogger(logger_name).setLevel(real_new_level)
        returnTrue

    def_get_iot_handlers_logger(self,handlers_name,iot_handler_folder_name):
        """
        :paramhandlers_name:ListofIoThandlerstringtosearchtheloggersof
        :paramiot_handler_folder_name:nameofthehandlerfolder('interfaces'or'drivers')
        :return:
        {
            <iot_handler_name_1>:{
                'level':<logger_level_1>,
                'is_using_parent_level':<logger_use_parent_level_or_not_1>,
                'parent_name':<logger_parent_name_1>,
            },
            ...
        }
        """
        handlers_loggers_level=dict()
        forhandler_nameinhandlers_name:
            handler_logger=self._get_iot_handler_logger(handler_name,iot_handler_folder_name)
            ifnothandler_logger:
                #Mighthappenifthefiledidn'tdefinealogger(ornotinityet)
                handlers_loggers_level[handler_name]=False
                _logger.debug('Unabletofindloggerforhandler%s',handler_name)
                continue
            logger_parent=handler_logger.parent
            handlers_loggers_level[handler_name]={
                'level':self._get_logger_effective_level_str(handler_logger),
                'is_using_parent_level':handler_logger.level==logging.NOTSET,
                'parent_name':logger_parent.name,
                'parent_level':self._get_logger_effective_level_str(logger_parent),
            }
        returnhandlers_loggers_level
