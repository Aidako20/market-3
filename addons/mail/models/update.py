#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime
importlogging

importrequests
importwerkzeug.urls

fromastimportliteral_eval

fromflectraimportapi,release,SUPERUSER_ID
fromflectra.exceptionsimportUserError
fromflectra.modelsimportAbstractModel
fromflectra.tools.translateimport_
fromflectra.toolsimportconfig,misc,ustr

_logger=logging.getLogger(__name__)


classPublisherWarrantyContract(AbstractModel):
    _name="publisher_warranty.contract"
    _description='PublisherWarrantyContract'

    @api.model
    def_get_message(self):
        Users=self.env['res.users']
        IrParamSudo=self.env['ir.config_parameter'].sudo()

        dbuuid=IrParamSudo.get_param('database.uuid')
        db_create_date=IrParamSudo.get_param('database.create_date')
        limit_date=datetime.datetime.now()
        limit_date=limit_date-datetime.timedelta(15)
        limit_date_str=limit_date.strftime(misc.DEFAULT_SERVER_DATETIME_FORMAT)
        nbr_users=Users.search_count([('active','=',True)])
        nbr_active_users=Users.search_count([("login_date",">=",limit_date_str),('active','=',True)])
        nbr_share_users=0
        nbr_active_share_users=0
        if"share"inUsers._fields:
            nbr_share_users=Users.search_count([("share","=",True),('active','=',True)])
            nbr_active_share_users=Users.search_count([("share","=",True),("login_date",">=",limit_date_str),('active','=',True)])
        user=self.env.user
        domain=[('application','=',True),('state','in',['installed','toupgrade','toremove'])]
        apps=self.env['ir.module.module'].sudo().search_read(domain,['name'])

        enterprise_code=IrParamSudo.get_param('database.enterprise_code')

        web_base_url=IrParamSudo.get_param('web.base.url')
        msg={
            "dbuuid":dbuuid,
            "nbr_users":nbr_users,
            "nbr_active_users":nbr_active_users,
            "nbr_share_users":nbr_share_users,
            "nbr_active_share_users":nbr_active_share_users,
            "dbname":self._cr.dbname,
            "db_create_date":db_create_date,
            "version":release.version,
            "language":user.lang,
            "web_base_url":web_base_url,
            "apps":[app['name']forappinapps],
            "enterprise_code":enterprise_code,
        }
        ifuser.partner_id.company_id:
            company_id=user.partner_id.company_id
            msg.update(company_id.read(["name","email","phone"])[0])
        returnmsg

    @api.model
    def_get_sys_logs(self):
        """
        Utilitymethodtosendapublisherwarrantygetlogsmessages.
        """
        msg=self._get_message()
        arguments={'arg0':ustr(msg),"action":"update"}

        url=config.get("publisher_warranty_url")

        r=requests.post(url,data=arguments,timeout=30)
        r.raise_for_status()
        returnliteral_eval(r.text)

    defupdate_notification(self,cron_mode=True):
        """
        SendamessagetoFlectra'spublisherwarrantyservertocheckthe
        validityofthecontracts,getnotifications,etc...

        @paramcron_mode:Iftrue,catchallexceptions(appropriateforusageinacron).
        @typecron_mode:boolean
        """
        try:
            try:
                result=self._get_sys_logs()
            exceptException:
                ifcron_mode:  #wedon'twanttoseeanystacktraceincron
                    returnFalse
                _logger.debug("Exceptionwhilesendingagetlogsmessages",exc_info=1)
                raiseUserError(_("Errorduringcommunicationwiththepublisherwarrantyserver."))
            #oldbehaviorbasedonres.log;nowonmail.message,thatisnotnecessarilyinstalled
            user=self.env['res.users'].sudo().browse(SUPERUSER_ID)
            poster=self.sudo().env.ref('mail.channel_all_employees')
            ifnot(posterandposter.exists()):
                ifnotuser.exists():
                    returnTrue
                poster=user
            formessageinresult["messages"]:
                try:
                    poster.message_post(body=message,subtype_xmlid='mail.mt_comment',partner_ids=[user.partner_id.id])
                exceptException:
                    pass
            ifresult.get('enterprise_info'):
                #Updateexpirationdate
                set_param=self.env['ir.config_parameter'].sudo().set_param
                set_param('database.expiration_date',result['enterprise_info'].get('expiration_date'))
                set_param('database.expiration_reason',result['enterprise_info'].get('expiration_reason','trial'))
                set_param('database.enterprise_code',result['enterprise_info'].get('enterprise_code'))
                set_param('database.already_linked_subscription_url',result['enterprise_info'].get('database_already_linked_subscription_url'))
                set_param('database.already_linked_email',result['enterprise_info'].get('database_already_linked_email'))
                set_param('database.already_linked_send_mail_url',result['enterprise_info'].get('database_already_linked_send_mail_url'))

        exceptException:
            ifcron_mode:
                returnFalse   #wedon'twanttoseeanystacktraceincron
            else:
                raise
        returnTrue
