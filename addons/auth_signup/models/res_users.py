#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromastimportliteral_eval
fromcollectionsimportdefaultdict
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.osvimportexpression
fromflectra.tools.miscimportustr

fromflectra.addons.base.models.ir_mail_serverimportMailDeliveryException
fromflectra.addons.auth_signup.models.res_partnerimportSignupError,now

_logger=logging.getLogger(__name__)

classResUsers(models.Model):
    _inherit='res.users'

    state=fields.Selection(compute='_compute_state',search='_search_state',string='Status',
                 selection=[('new','NeverConnected'),('active','Confirmed')])

    def_search_state(self,operator,value):
        negative=operatorinexpression.NEGATIVE_TERM_OPERATORS

        #Incasewehavenovalue
        ifnotvalue:
            returnexpression.TRUE_DOMAINifnegativeelseexpression.FALSE_DOMAIN

        ifoperatorin['in','notin']:
            iflen(value)>1:
                returnexpression.FALSE_DOMAINifnegativeelseexpression.TRUE_DOMAIN
            ifvalue[0]=='new':
                comp='!='ifnegativeelse'='
            ifvalue[0]=='active':
                comp='='ifnegativeelse'!='
            return[('log_ids',comp,False)]

        ifoperatorin['=','!=']:
            #Incasewesearchagainstanythingelsethannew,wehavetoinverttheoperator
            ifvalue!='new':
                operator=expression.TERM_OPERATORS_NEGATION[operator]

            return[('log_ids',operator,False)]

        returnexpression.TRUE_DOMAIN

    def_compute_state(self):
        foruserinself:
            user.state='active'ifuser.login_dateelse'new'

    @api.model
    defsignup(self,values,token=None):
        """signupauser,toeither:
            -createanewuser(notoken),or
            -createauserforapartner(withtoken,butnouserforpartner),or
            -changethepasswordofauser(withtoken,andexistinguser).
            :paramvalues:adictionarywithfieldvaluesthatarewrittenonuser
            :paramtoken:signuptoken(optional)
            :return:(dbname,login,password)forthesignedupuser
        """
        iftoken:
            #signupwithatoken:findthecorrespondingpartnerid
            partner=self.env['res.partner']._signup_retrieve_partner(token,check_validity=True,raise_exception=True)
            #invalidatesignuptoken
            partner.write({'signup_token':False,'signup_type':False,'signup_expiration':False})

            partner_user=partner.user_idsandpartner.user_ids[0]orFalse

            #avoidoverwritingexisting(presumablycorrect)valueswithgeolocationdata
            ifpartner.country_idorpartner.ziporpartner.city:
                values.pop('city',None)
                values.pop('country_id',None)
            ifpartner.lang:
                values.pop('lang',None)

            ifpartner_user:
                #userexists,modifyitaccordingtovalues
                values.pop('login',None)
                values.pop('name',None)
                partner_user.write(values)
                ifnotpartner_user.login_date:
                    partner_user._notify_inviter()
                return(self.env.cr.dbname,partner_user.login,values.get('password'))
            else:
                #userdoesnotexist:signupinviteduser
                values.update({
                    'name':partner.name,
                    'partner_id':partner.id,
                    'email':values.get('email')orvalues.get('login'),
                })
                ifpartner.company_id:
                    values['company_id']=partner.company_id.id
                    values['company_ids']=[(6,0,[partner.company_id.id])]
                partner_user=self._signup_create_user(values)
                partner_user._notify_inviter()
        else:
            #notoken,signupanexternaluser
            values['email']=values.get('email')orvalues.get('login')
            self._signup_create_user(values)

        return(self.env.cr.dbname,values.get('login'),values.get('password'))

    @api.model
    def_get_signup_invitation_scope(self):
        returnself.env['ir.config_parameter'].sudo().get_param('auth_signup.invitation_scope','b2b')

    @api.model
    def_signup_create_user(self,values):
        """signupanewuserusingthetemplateuser"""

        #checkthatuninvitedusersmaysignup
        if'partner_id'notinvalues:
            ifself._get_signup_invitation_scope()!='b2c':
                raiseSignupError(_('Signupisnotallowedforuninvitedusers'))
        returnself._create_user_from_template(values)

    def_notify_inviter(self):
        foruserinself:
            invite_partner=user.create_uid.partner_id
            ifinvite_partner:
                #notifyinviteuserthatnewuserisconnected
                title=_("%sconnected",user.name)
                message=_("Thisishisfirstconnection.Wishhimwelcome")
                self.env['bus.bus'].sendone(
                    (self._cr.dbname,'res.partner',invite_partner.id),
                    {'type':'user_connection','title':title,
                     'message':message,'partner_id':user.partner_id.id}
                )

    def_create_user_from_template(self,values):
        template_user_id=literal_eval(self.env['ir.config_parameter'].sudo().get_param('base.template_portal_user_id','False'))
        template_user=self.browse(template_user_id)
        ifnottemplate_user.exists():
            raiseValueError(_('Signup:invalidtemplateuser'))

        ifnotvalues.get('login'):
            raiseValueError(_('Signup:nologingivenfornewuser'))
        ifnotvalues.get('partner_id')andnotvalues.get('name'):
            raiseValueError(_('Signup:nonameorpartnergivenfornewuser'))

        #createacopyofthetemplateuser(attachedtoaspecificpartner_idifgiven)
        values['active']=True
        try:
            withself.env.cr.savepoint():
                returntemplate_user.with_context(no_reset_password=True).copy(values)
        exceptExceptionase:
            #copymayfailedifaskedloginisnotavailable.
            raiseSignupError(ustr(e))

    defreset_password(self,login):
        """retrievetheusercorrespondingtologin(loginoremail),
            andresettheirpassword
        """
        users=self.search(self._get_login_domain(login))
        ifnotusers:
            users=self.search(self._get_email_domain(login))

        ifnotusers:
            raiseException(_('Resetpassword:invalidusernameoremail'))
        iflen(users)>1:
            raiseException(_('Multipleaccountsfoundforthisemail'))
        returnusers.action_reset_password()

    defaction_reset_password(self):
        """createsignuptokenforeachuser,andsendtheirsignupurlbyemail"""
        ifself.env.context.get('install_mode',False):
            return
        ifself.filtered(lambdauser:notuser.active):
            raiseUserError(_("Youcannotperformthisactiononanarchiveduser."))
        #prepareresetpasswordsignup
        create_mode=bool(self.env.context.get('create_user'))

        #notimelimitforinitialinvitation,onlyforresetpassword
        expiration=Falseifcreate_modeelsenow(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset",expiration=expiration)

        #sendemailtouserswiththeirsignupurl
        template=False
        ifcreate_mode:
            try:
                template=self.env.ref('auth_signup.set_password_email',raise_if_not_found=False)
            exceptValueError:
                pass
        ifnottemplate:
            template=self.env.ref('auth_signup.reset_password_email')
        asserttemplate._name=='mail.template'

        template_values={
            'email_to':'${object.email|safe}',
            'email_cc':False,
            'auto_delete':True,
            'partner_to':False,
            'scheduled_date':False,
        }
        template.write(template_values)

        foruserinself:
            ifnotuser.email:
                raiseUserError(_("Cannotsendemail:user%shasnoemailaddress.",user.name))
            #TDEFIXME:makethistemplatetechnical(qweb)
            withself.env.cr.savepoint():
                force_send=not(self.env.context.get('import_file',False))
                template.send_mail(user.id,force_send=force_send,raise_exception=True)
            _logger.info("Passwordresetemailsentforuser<%s>to<%s>",user.login,user.email)

    defsend_unregistered_user_reminder(self,after_days=5):
        datetime_min=fields.Datetime.today()-relativedelta(days=after_days)
        datetime_max=datetime_min+relativedelta(hours=23,minutes=59,seconds=59)

        res_users_with_details=self.env['res.users'].search_read([
            ('share','=',False),
            ('create_uid.email','!=',False),
            ('create_date','>=',datetime_min),
            ('create_date','<=',datetime_max),
            ('log_ids','=',False)],['create_uid','name','login'])

        #groupbyinvitedby
        invited_users=defaultdict(list)
        foruserinres_users_with_details:
            invited_users[user.get('create_uid')[0]].append("%s(%s)"%(user.get('name'),user.get('login')))

        #Forsendingmailtoalltheinvitorsabouttheirinvitedusers
        foruserininvited_users:
            template=self.env.ref('auth_signup.mail_template_data_unregistered_users').with_context(dbname=self._cr.dbname,invited_users=invited_users[user])
            template.send_mail(user,notif_layout='mail.mail_notification_light',force_send=False)

    @api.model
    defweb_create_users(self,emails):
        inactive_users=self.search([('state','=','new'),'|',('login','in',emails),('email','in',emails)])
        new_emails=set(emails)-set(inactive_users.mapped('email'))
        res=super(ResUsers,self).web_create_users(list(new_emails))
        ifinactive_users:
            inactive_users.with_context(create_user=True).action_reset_password()
        returnres

    @api.model_create_multi
    defcreate(self,vals_list):
        #overriddentoautomaticallyinviteusertosignup
        users=super(ResUsers,self).create(vals_list)
        ifnotself.env.context.get('no_reset_password'):
            users_with_email=users.filtered('email')
            ifusers_with_email:
                try:
                    users_with_email.with_context(create_user=True).action_reset_password()
                exceptMailDeliveryException:
                    users_with_email.partner_id.with_context(create_user=True).signup_cancel()
        returnusers

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        self.ensure_one()
        sup=super(ResUsers,self)
        ifnotdefaultornotdefault.get('email'):
            #avoidsendingemailtotheuserweareduplicating
            sup=super(ResUsers,self.with_context(no_reset_password=True))
        returnsup.copy(default=default)
