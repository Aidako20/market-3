#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importpoplib
importsocket

fromimaplibimportIMAP4,IMAP4_SSL
frompoplibimportPOP3,POP3_SSL
fromsocketimportgaierror,timeout
fromsslimportSSLError

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportUserError


_logger=logging.getLogger(__name__)
MAX_POP_MESSAGES=50
MAIL_TIMEOUT=60

#WorkaroundforPython2.7.8bughttps://bugs.python.org/issue23906
poplib._MAXLINE=65536

#AddtimeouttoIMAPconnections
#HACKhttps://bugs.python.org/issue38615
#TODO:cleaninPython3.9
IMAP4._create_socket=lambdaself,timeout=MAIL_TIMEOUT:socket.create_connection((self.hostorNone,self.port),timeout)


classFetchmailServer(models.Model):
    """IncomingPOP/IMAPmailserveraccount"""

    _name='fetchmail.server'
    _description='IncomingMailServer'
    _order='priority'

    name=fields.Char('Name',required=True)
    active=fields.Boolean('Active',default=True)
    state=fields.Selection([
        ('draft','NotConfirmed'),
        ('done','Confirmed'),
    ],string='Status',index=True,readonly=True,copy=False,default='draft')
    server=fields.Char(string='ServerName',readonly=True,help="HostnameorIPofthemailserver",states={'draft':[('readonly',False)]})
    port=fields.Integer(readonly=True,states={'draft':[('readonly',False)]})
    server_type=fields.Selection([
        ('pop','POPServer'),
        ('imap','IMAPServer'),
        ('local','LocalServer'),
    ],string='ServerType',index=True,required=True,default='pop')
    is_ssl=fields.Boolean('SSL/TLS',help="ConnectionsareencryptedwithSSL/TLSthroughadedicatedport(default:IMAPS=993,POP3S=995)")
    attach=fields.Boolean('KeepAttachments',help="Whetherattachmentsshouldbedownloaded."
                                                     "Ifnotenabled,incomingemailswillbestrippedofanyattachmentsbeforebeingprocessed",default=True)
    original=fields.Boolean('KeepOriginal',help="Whetherafulloriginalcopyofeachemailshouldbekeptforreference"
                                                    "andattachedtoeachprocessedmessage.Thiswillusuallydoublethesizeofyourmessagedatabase.")
    date=fields.Datetime(string='LastFetchDate',readonly=True)
    user=fields.Char(string='Username',readonly=True,states={'draft':[('readonly',False)]})
    password=fields.Char(readonly=True,states={'draft':[('readonly',False)]})
    object_id=fields.Many2one('ir.model',string="CreateaNewRecord",help="Processeachincomingmailaspartofaconversation"
                                                                                "correspondingtothisdocumenttype.Thiswillcreate"
                                                                                "newdocumentsfornewconversations,orattachfollow-up"
                                                                                "emailstotheexistingconversations(documents).")
    priority=fields.Integer(string='ServerPriority',readonly=True,states={'draft':[('readonly',False)]},help="Definestheorderofprocessing,lowervaluesmeanhigherpriority",default=5)
    message_ids=fields.One2many('mail.mail','fetchmail_server_id',string='Messages',readonly=True)
    configuration=fields.Text('Configuration',readonly=True)
    script=fields.Char(readonly=True,default='/mail/static/scripts/flectra-mailgate.py')

    @api.onchange('server_type','is_ssl','object_id')
    defonchange_server_type(self):
        self.port=0
        ifself.server_type=='pop':
            self.port=self.is_ssland995or110
        elifself.server_type=='imap':
            self.port=self.is_ssland993or143

        conf={
            'dbname':self.env.cr.dbname,
            'uid':self.env.uid,
            'model':self.object_id.modelifself.object_idelse'MODELNAME'
        }
        self.configuration="""UsethebelowscriptwiththefollowingcommandlineoptionswithyourMailTransportAgent(MTA)
flectra-mailgate.py--host=HOSTNAME--port=PORT-u%(uid)d-pPASSWORD-d%(dbname)s
Exampleconfigurationforthepostfixmtarunninglocally:
/etc/postfix/virtual_aliases:@youdomainflectra_mailgate@localhost
/etc/aliases:
flectra_mailgate:"|/path/to/flectra-mailgate.py--host=localhost-u%(uid)d-pPASSWORD-d%(dbname)s"
        """%conf

    @api.model
    defcreate(self,values):
        res=super(FetchmailServer,self).create(values)
        self._update_cron()
        returnres

    defwrite(self,values):
        res=super(FetchmailServer,self).write(values)
        self._update_cron()
        returnres

    defunlink(self):
        res=super(FetchmailServer,self).unlink()
        self._update_cron()
        returnres

    defset_draft(self):
        self.write({'state':'draft'})
        returnTrue

    defconnect(self):
        self.ensure_one()
        ifself.server_type=='imap':
            ifself.is_ssl:
                connection=IMAP4_SSL(self.server,int(self.port))
            else:
                connection=IMAP4(self.server,int(self.port))
            self._imap_login(connection)
        elifself.server_type=='pop':
            ifself.is_ssl:
                connection=POP3_SSL(self.server,int(self.port),timeout=MAIL_TIMEOUT)
            else:
                connection=POP3(self.server,int(self.port),timeout=MAIL_TIMEOUT)
            #TODO:usethistoremoveonlyunreadmessages
            #connection.user("recent:"+server.user)
            connection.user(self.user)
            connection.pass_(self.password)
        returnconnection

    def_imap_login(self,connection):
        """AuthenticatetheIMAPconnection.

        Canbeoverriddeninothermodulefordifferentauthenticationmethods.

        :paramconnection:TheIMAPconnectiontoauthenticate
        """
        self.ensure_one()
        connection.login(self.user,self.password)

    defbutton_confirm_login(self):
        forserverinself:
            try:
                connection=server.connect()
                server.write({'state':'done'})
            exceptUnicodeErrorase:
                raiseUserError(_("Invalidservername!\n%s",tools.ustr(e)))
            except(gaierror,timeout,IMAP4.abort)ase:
                raiseUserError(_("Noresponsereceived.Checkserverinformation.\n%s",tools.ustr(e)))
            except(IMAP4.error,poplib.error_proto)aserr:
                raiseUserError(_("Serverrepliedwithfollowingexception:\n%s",tools.ustr(err)))
            exceptSSLErrorase:
                raiseUserError(_("AnSSLexceptionoccurred.CheckSSL/TLSconfigurationonserverport.\n%s",tools.ustr(e)))
            except(OSError,Exception)aserr:
                _logger.info("Failedtoconnectto%sserver%s.",server.server_type,server.name,exc_info=True)
                raiseUserError(_("Connectiontestfailed:%s",tools.ustr(err)))
            finally:
                try:
                    ifconnection:
                        ifserver.server_type=='imap':
                            connection.close()
                        elifserver.server_type=='pop':
                            connection.quit()
                exceptException:
                    #ignored,justaconsequenceofthepreviousexception
                    pass
        returnTrue

    @api.model
    def_fetch_mails(self):
        """Methodcalledbycrontofetchmailsfromservers"""
        returnself.search([('state','=','done'),('server_type','in',['pop','imap'])]).fetch_mail()

    deffetch_mail(self):
        """WARNING:meantforcronusageonly-willcommit()aftereachemail!"""
        additionnal_context={
            'fetchmail_cron_running':True
        }
        MailThread=self.env['mail.thread']
        forserverinself:
            _logger.info('startcheckingfornewemailson%sserver%s',server.server_type,server.name)
            additionnal_context['default_fetchmail_server_id']=server.id
            count,failed=0,0
            imap_server=None
            pop_server=None
            ifserver.server_type=='imap':
                try:
                    imap_server=server.connect()
                    imap_server.select()
                    result,data=imap_server.search(None,'(UNSEEN)')
                    fornumindata[0].split():
                        res_id=None
                        result,data=imap_server.fetch(num,'(RFC822)')
                        imap_server.store(num,'-FLAGS','\\Seen')
                        try:
                            res_id=MailThread.with_context(**additionnal_context).message_process(server.object_id.model,data[0][1],save_original=server.original,strip_attachments=(notserver.attach))
                        exceptException:
                            _logger.info('Failedtoprocessmailfrom%sserver%s.',server.server_type,server.name,exc_info=True)
                            failed+=1
                        imap_server.store(num,'+FLAGS','\\Seen')
                        self._cr.commit()
                        count+=1
                    _logger.info("Fetched%demail(s)on%sserver%s;%dsucceeded,%dfailed.",count,server.server_type,server.name,(count-failed),failed)
                exceptException:
                    _logger.info("Generalfailurewhentryingtofetchmailfrom%sserver%s.",server.server_type,server.name,exc_info=True)
                finally:
                    ifimap_server:
                        imap_server.close()
                        imap_server.logout()
            elifserver.server_type=='pop':
                try:
                    whileTrue:
                        failed_in_loop=0
                        num=0
                        pop_server=server.connect()
                        (num_messages,total_size)=pop_server.stat()
                        pop_server.list()
                        fornuminrange(1,min(MAX_POP_MESSAGES,num_messages)+1):
                            (header,messages,octets)=pop_server.retr(num)
                            message=(b'\n').join(messages)
                            res_id=None
                            try:
                                res_id=MailThread.with_context(**additionnal_context).message_process(server.object_id.model,message,save_original=server.original,strip_attachments=(notserver.attach))
                                pop_server.dele(num)
                            exceptException:
                                _logger.info('Failedtoprocessmailfrom%sserver%s.',server.server_type,server.name,exc_info=True)
                                failed+=1
                                failed_in_loop+=1
                            self.env.cr.commit()
                        _logger.info("Fetched%demail(s)on%sserver%s;%dsucceeded,%dfailed.",num,server.server_type,server.name,(num-failed_in_loop),failed_in_loop)
                        #Stopif(1)nomoremessageleftor(2)allmessageshavefailed
                        ifnum_messages<MAX_POP_MESSAGESorfailed_in_loop==num:
                            break
                        pop_server.quit()
                exceptException:
                    _logger.info("Generalfailurewhentryingtofetchmailfrom%sserver%s.",server.server_type,server.name,exc_info=True)
                finally:
                    ifpop_server:
                        pop_server.quit()
            server.write({'date':fields.Datetime.now()})
        returnTrue

    @api.model
    def_update_cron(self):
        ifself.env.context.get('fetchmail_cron_running'):
            return
        try:
            #Enabled/Disablecronbasedonthenumberof'done'serveroftypepoporimap
            cron=self.env.ref('fetchmail.ir_cron_mail_gateway_action')
            cron.toggle(model=self._name,domain=[('state','=','done'),('server_type','in',['pop','imap'])])
        exceptValueError:
            pass
