#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime
fromenumimportEnum
fromimportlibimportutil
importio
importjson
importlogging
importnetifaces
fromOpenSSLimportcrypto
importos
frompathlibimportPath
importsubprocess
importurllib3
importzipfile
fromthreadingimportThread
importtime

fromflectraimport_,http
fromflectra.modules.moduleimportget_resource_path

_logger=logging.getLogger(__name__)

#----------------------------------------------------------
#Helper
#----------------------------------------------------------


classCertificateStatus(Enum):
    OK=1
    NEED_REFRESH=2
    ERROR=3


classIoTRestart(Thread):
    """
    ThreadtorestartflectraserverinIoTBoxwhenwemustreturnaanswerbefore
    """
    def__init__(self,delay):
        Thread.__init__(self)
        self.delay=delay

    defrun(self):
        time.sleep(self.delay)
        subprocess.check_call(["sudo","service","flectra","restart"])

defaccess_point():
    returnget_ip()=='10.11.12.1'

defadd_credential(db_uuid,enterprise_code):
    write_file('flectra-db-uuid.conf',db_uuid)
    write_file('flectra-enterprise-code.conf',enterprise_code)

defcheck_certificate():
    """
    Checkifthecurrentcertificateisuptodateornotauthenticated
    :returnCheckCertificateStatus
    """
    server=get_flectra_server_url()
    ifnotserver:
        return{"status":CertificateStatus.ERROR,
                "error_code":"ERR_IOT_HTTPS_CHECK_NO_SERVER"}

    path=Path('/etc/ssl/certs/nginx-cert.crt')
    ifnotpath.exists():
        return{"status":CertificateStatus.NEED_REFRESH}

    try:
        withpath.open('r')asf:
            cert=crypto.load_certificate(crypto.FILETYPE_PEM,f.read())
    exceptEnvironmentError:
        _logger.exception("Unabletoreadcertificatefile")
        return{"status":CertificateStatus.ERROR,
                "error_code":"ERR_IOT_HTTPS_CHECK_CERT_READ_EXCEPTION"}

    cert_end_date=datetime.datetime.strptime(cert.get_notAfter().decode('utf-8'),"%Y%m%d%H%M%SZ")-datetime.timedelta(days=10)
    forkeyincert.get_subject().get_components():
        ifkey[0]==b'CN':
            cn=key[1].decode('utf-8')
    ifcn=='FlectraTempIoTBoxCertificate'ordatetime.datetime.now()>cert_end_date:
        message=_('Yourcertificate%smustbeupdated')%(cn)
        _logger.info(message)
        return{"status":CertificateStatus.NEED_REFRESH}
    else:
        message=_('Yourcertificate%sisvaliduntil%s')%(cn,cert_end_date)
        _logger.info(message)
        return{"status":CertificateStatus.OK,"message":message}

defcheck_git_branch():
    """
    CheckifthelocalbranchisthesamethantheconnectedFlectraDBand
    checkouttomatchitifneeded.
    """
    server=get_flectra_server_url()
    ifserver:
        urllib3.disable_warnings()
        http=urllib3.PoolManager(cert_reqs='CERT_NONE')
        try:
            response=http.request(
                'POST',
                server+"/web/webclient/version_info",
                body='{}',
                headers={'Content-type':'application/json'}
            )

            ifresponse.status==200:
                git=['git','--work-tree=/home/pi/flectra/','--git-dir=/home/pi/flectra/.git']

                db_branch=json.loads(response.data)['result']['server_serie'].replace('~','-')
                ifnotsubprocess.check_output(git+['ls-remote','origin',db_branch]):
                    db_branch='master'

                local_branch=subprocess.check_output(git+['symbolic-ref','-q','--short','HEAD']).decode('utf-8').rstrip()

                ifdb_branch!=local_branch:
                    subprocess.call(["sudo","mount","-o","remount,rw","/"])
                    subprocess.check_call(["rm","-rf","/home/pi/flectra/addons/hw_drivers/iot_handlers/drivers/*"])
                    subprocess.check_call(["rm","-rf","/home/pi/flectra/addons/hw_drivers/iot_handlers/interfaces/*"])
                    subprocess.check_call(git+['branch','-m',db_branch])
                    subprocess.check_call(git+['remote','set-branches','origin',db_branch])
                    os.system('/home/pi/flectra/addons/point_of_sale/tools/posbox/configuration/posbox_update.sh')
                    subprocess.call(["sudo","mount","-o","remount,ro","/"])
                    subprocess.call(["sudo","mount","-o","remount,rw","/root_bypass_ramdisks/etc/cups"])

        exceptExceptionase:
            _logger.error('Couldnotreachconfiguredserver')
            _logger.error('Aerrorencountered:%s'%e)

defcheck_image():
    """
    CheckifthecurrentimageofIoTBoxisuptodate
    """
    url='https://nightly.flectrahq.com/master/iotbox/SHA1SUMS.txt'
    urllib3.disable_warnings()
    http=urllib3.PoolManager(cert_reqs='CERT_NONE')
    response=http.request('GET',url)
    checkFile={}
    valueActual=''
    forlineinresponse.data.decode().split('\n'):
        ifline:
            value,name=line.split(' ')
            checkFile.update({value:name})
            ifname=='iotbox-latest.zip':
                valueLastest=value
            elifname==get_img_name():
                valueActual=value
    ifvalueActual==valueLastest:
        returnFalse
    version=checkFile.get(valueLastest,'Error').replace('iotboxv','').replace('.zip','').split('_')
    return{'major':version[0],'minor':version[1]}

defget_certificate_status(is_first=True):
    """
    WillgettheHTTPScertificatedetailsifpresent.Willloadthecertificateifmissing.

    :paramis_first:Usetomakesurethattherecursionhappensonlyonce
    :return:(bool,str)
    """
    check_certificate_result=check_certificate()
    certificateStatus=check_certificate_result["status"]

    ifcertificateStatus==CertificateStatus.ERROR:
        returnFalse,check_certificate_result["error_code"]

    ifcertificateStatus==CertificateStatus.NEED_REFRESHandis_first:
        certificate_process=load_certificate()
        ifcertificate_processisnotTrue:
            returnFalse,certificate_process
        returnget_certificate_status(is_first=False) #recursivecalltoattemptcertificateread
    returnTrue,check_certificate_result.get("message",
                                              "TheHTTPScertificatewasgeneratedcorrectly")

defget_img_name():
    major,minor=get_version().split('.')
    return'iotboxv%s_%s.zip'%(major,minor)

defget_ip():
    whileTrue:
        try:
            returnnetifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
        exceptKeyError:
            pass

        try:
            returnnetifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
        exceptKeyError:
            pass

        _logger.warning("Couldn'tgetIP,sleepingandretrying.")
        time.sleep(5)

defget_mac_address():
    whileTrue:
        try:
            returnnetifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr']
        exceptKeyError:
            pass

        try:
            returnnetifaces.ifaddresses('wlan0')[netifaces.AF_LINK][0]['addr']
        exceptKeyError:
            pass

        _logger.warning("Couldn'tgetMACaddress,sleepingandretrying.")
        time.sleep(5)

defget_ssid():
    ap=subprocess.call(['systemctl','is-active','--quiet','hostapd'])#ifserviceisactivereturn0elseinactive
    ifnotap:
        returnsubprocess.check_output(['grep','-oP','(?<=ssid=).*','/etc/hostapd/hostapd.conf']).decode('utf-8').rstrip()
    process_iwconfig=subprocess.Popen(['iwconfig'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    process_grep=subprocess.Popen(['grep','ESSID:"'],stdin=process_iwconfig.stdout,stdout=subprocess.PIPE)
    returnsubprocess.check_output(['sed','s/.*"\\(.*\\)"/\\1/'],stdin=process_grep.stdout).decode('utf-8').rstrip()

defget_flectra_server_url():
    ap=subprocess.call(['systemctl','is-active','--quiet','hostapd'])#ifserviceisactivereturn0elseinactive
    ifnotap:
        returnFalse
    returnread_file_first_line('flectra-remote-server.conf')

defget_token():
    returnread_file_first_line('token')

defget_version():
    returnsubprocess.check_output(['cat','/var/flectra/iotbox_version']).decode().rstrip()

defget_wifi_essid():
    wifi_options=[]
    process_iwlist=subprocess.Popen(['sudo','iwlist','wlan0','scan'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    process_grep=subprocess.Popen(['grep','ESSID:"'],stdin=process_iwlist.stdout,stdout=subprocess.PIPE).stdout.readlines()
    forssidinprocess_grep:
        essid=ssid.decode('utf-8').split('"')[1]
        ifessidnotinwifi_options:
            wifi_options.append(essid)
    returnwifi_options

defload_certificate():
    """
    SendarequesttoFlectrawithcustomerdb_uuidandenterprise_codetogetatruecertificate
    """
    db_uuid=read_file_first_line('flectra-db-uuid.conf')
    enterprise_code=read_file_first_line('flectra-enterprise-code.conf')
    ifnot(db_uuidandenterprise_code):
        return"ERR_IOT_HTTPS_LOAD_NO_CREDENTIAL"

    url='https://www.flectrahq.com/flectra-enterprise/iot/x509'
    data={
        'params':{
            'db_uuid':db_uuid,
            'enterprise_code':enterprise_code
        }
    }
    urllib3.disable_warnings()
    http=urllib3.PoolManager(cert_reqs='CERT_NONE',retries=urllib3.Retry(4))
    try:
        response=http.request(
            'POST',
            url,
            body=json.dumps(data).encode('utf8'),
            headers={'Content-type':'application/json','Accept':'text/plain'}
        )
    exceptExceptionase:
        _logger.exception("Anerroroccurredwhiletryingtoreachflectrahq.comservers.")
        return"ERR_IOT_HTTPS_LOAD_REQUEST_EXCEPTION\n\n%s"%e

    ifresponse.status!=200:
        return"ERR_IOT_HTTPS_LOAD_REQUEST_STATUS%s\n\n%s"%(response.status,response.reason)

    result=json.loads(response.data.decode('utf8'))['result']
    ifnotresult:
        return"ERR_IOT_HTTPS_LOAD_REQUEST_NO_RESULT"

    write_file('flectra-subject.conf',result['subject_cn'])
    subprocess.call(["sudo","mount","-o","remount,rw","/"])
    subprocess.call(["sudo","mount","-o","remount,rw","/root_bypass_ramdisks/"])
    Path('/etc/ssl/certs/nginx-cert.crt').write_text(result['x509_pem'])
    Path('/root_bypass_ramdisks/etc/ssl/certs/nginx-cert.crt').write_text(result['x509_pem'])
    Path('/etc/ssl/private/nginx-cert.key').write_text(result['private_key_pem'])
    Path('/root_bypass_ramdisks/etc/ssl/private/nginx-cert.key').write_text(result['private_key_pem'])
    subprocess.call(["sudo","mount","-o","remount,ro","/"])
    subprocess.call(["sudo","mount","-o","remount,ro","/root_bypass_ramdisks/"])
    subprocess.call(["sudo","mount","-o","remount,rw","/root_bypass_ramdisks/etc/cups"])
    subprocess.check_call(["sudo","service","nginx","restart"])
    returnTrue

defdownload_iot_handlers(auto=True):
    """
    GetthedriversfromtheconfiguredFlectraserver
    """
    server=get_flectra_server_url()
    ifserver:
        urllib3.disable_warnings()
        pm=urllib3.PoolManager(cert_reqs='CERT_NONE')
        server=server+'/iot/get_handlers'
        try:
            resp=pm.request('POST',server,fields={'mac':get_mac_address(),'auto':auto})
            ifresp.data:
                subprocess.call(["sudo","mount","-o","remount,rw","/"])
                drivers_path=Path.home()/'flectra/addons/hw_drivers/iot_handlers'
                zip_file=zipfile.ZipFile(io.BytesIO(resp.data))
                zip_file.extractall(drivers_path)
                subprocess.call(["sudo","mount","-o","remount,ro","/"])
                subprocess.call(["sudo","mount","-o","remount,rw","/root_bypass_ramdisks/etc/cups"])
        exceptExceptionase:
            _logger.error('Couldnotreachconfiguredserver')
            _logger.error('Aerrorencountered:%s'%e)

defcompute_iot_handlers_addon_name(handler_kind,handler_file_name):
    #TODO:replacewith`removesuffix`(forFlectraversionusinganIoTimagethatusePython>=3.9)
    return"flectra.addons.hw_drivers.iot_handlers.{handler_kind}.{handler_name}".\
        format(handler_kind=handler_kind,handler_name=handler_file_name.replace('.py',''))

defload_iot_handlers():
    """
    Thismethodloadslocalfiles:'flectra/addons/hw_drivers/iot_handlers/drivers'and
    'flectra/addons/hw_drivers/iot_handlers/interfaces'
    Andexecutethesepythondriversandinterfaces
    """
    fordirectoryin['interfaces','drivers']:
        path=get_resource_path('hw_drivers','iot_handlers',directory)
        filesList=os.listdir(path)
        forfileinfilesList:
            path_file=os.path.join(path,file)
            spec=util.spec_from_file_location(compute_iot_handlers_addon_name(directory,file),path_file)
            ifspec:
                module=util.module_from_spec(spec)
                spec.loader.exec_module(module)
    http.addons_manifest={}
    http.root=http.Root()

defflectra_restart(delay):
    IR=IoTRestart(delay)
    IR.start()

defread_file_first_line(filename):
    path=Path.home()/filename
    path=Path('/home/pi/'+filename)
    ifpath.exists():
        withpath.open('r')asf:
            returnf.readline().strip('\n')
    return''

defunlink_file(filename):
    subprocess.call(["sudo","mount","-o","remount,rw","/"])
    path=Path.home()/filename
    ifpath.exists():
        path.unlink()
    subprocess.call(["sudo","mount","-o","remount,ro","/"])
    subprocess.call(["sudo","mount","-o","remount,rw","/root_bypass_ramdisks/etc/cups"])

defwrite_file(filename,text):
    subprocess.call(["sudo","mount","-o","remount,rw","/"])
    path=Path.home()/filename
    path.write_text(text)
    subprocess.call(["sudo","mount","-o","remount,ro","/"])
    subprocess.call(["sudo","mount","-o","remount,rw","/root_bypass_ramdisks/etc/cups"])
