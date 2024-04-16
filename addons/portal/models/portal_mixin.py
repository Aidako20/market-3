#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importuuid
fromwerkzeug.urlsimporturl_encode
fromflectraimportapi,exceptions,fields,models,_


classPortalMixin(models.AbstractModel):
    _name="portal.mixin"
    _description='PortalMixin'

    access_url=fields.Char(
        'PortalAccessURL',compute='_compute_access_url',
        help='CustomerPortalURL')
    access_token=fields.Char('SecurityToken',copy=False)

    #todisplaythewarningfromspecificmodel
    access_warning=fields.Text("Accesswarning",compute="_compute_access_warning")

    def_compute_access_warning(self):
        formixininself:
            mixin.access_warning=''

    def_compute_access_url(self):
        forrecordinself:
            record.access_url='#'

    def_portal_ensure_token(self):
        """Getthecurrentrecordaccesstoken"""
        ifnotself.access_token:
            #weusea`write`toforcethecacheclearingotherwise`returnself.access_token`willreturnFalse
            self.sudo().write({'access_token':str(uuid.uuid4())})
        returnself.access_token

    def_get_share_url(self,redirect=False,signup_partner=False,pid=None,share_token=True):
        """
        Buildtheurloftherecord thatwillbesentbymailandaddsadditionalparameterssuchas
        access_tokentobypasstherecipient'srights,
        signup_partnertoallowstheusertocreateeasilyanaccount,
        hashtokentoallowtheusertobeauthenticatedinthechatteroftherecordportalview,ifapplicable
        :paramredirect:Sendtheredirecturlinsteadofthedirectportalshareurl
        :paramsignup_partner:allowstheusertocreateanaccountwithpre-filledfields.
        :parampid:=partner_id-whengiven,ahashisgeneratedtoallowtheusertobeauthenticated
            intheportalchatter,ifanyinthetargetpage,
            iftheuserisredirectedtotheportalinsteadofthebackend.
        :return:theurloftherecordwithaccessparameters,ifany.
        """
        self.ensure_one()
        params={
            'model':self._name,
            'res_id':self.id,
        }
        ifshare_tokenandhasattr(self,'access_token'):
            params['access_token']=self._portal_ensure_token()
        ifpid:
            params['pid']=pid
            params['hash']=self._sign_token(pid)
        ifsignup_partnerandhasattr(self,'partner_id')andself.partner_id:
            params.update(self.partner_id.signup_get_auth_param()[self.partner_id.id])

        return'%s?%s'%('/mail/view'ifredirectelseself.access_url,url_encode(params))

    def_notify_get_groups(self,msg_vals=None):
        access_token=self._portal_ensure_token()
        groups=super(PortalMixin,self)._notify_get_groups(msg_vals=msg_vals)
        local_msg_vals=dict(msg_valsor{})

        ifaccess_tokenand'partner_id'inself._fieldsandself['partner_id']:
            customer=self['partner_id']
            local_msg_vals['access_token']=self.access_token
            local_msg_vals.update(customer.signup_get_auth_param()[customer.id])
            access_link=self._notify_get_action_link('view',**local_msg_vals)

            new_group=[
                ('portal_customer',lambdapdata:pdata['id']==customer.id,{
                    'has_button_access':False,
                    'button_access':{
                        'url':access_link,
                    },
                    'notification_is_customer':True,
                })
            ]
        else:
            new_group=[]
        returnnew_group+groups

    defget_access_action(self,access_uid=None):
        """Insteadoftheclassicformview,redirecttotheonlinedocumentfor
        portalusersorifforce_website=Trueinthecontext."""
        self.ensure_one()

        user,record=self.env.user,self
        ifaccess_uid:
            try:
                record.check_access_rights('read')
                record.check_access_rule("read")
            exceptexceptions.AccessError:
                returnsuper(PortalMixin,self).get_access_action(access_uid)
            user=self.env['res.users'].sudo().browse(access_uid)
            record=self.with_user(user)
        ifuser.shareorself.env.context.get('force_website'):
            try:
                record.check_access_rights('read')
                record.check_access_rule('read')
            exceptexceptions.AccessError:
                ifself.env.context.get('force_website'):
                    return{
                        'type':'ir.actions.act_url',
                        'url':record.access_url,
                        'target':'self',
                        'res_id':record.id,
                    }
                else:
                    pass
            else:
                return{
                    'type':'ir.actions.act_url',
                    'url':record._get_share_url(),
                    'target':'self',
                    'res_id':record.id,
                }
        returnsuper(PortalMixin,self).get_access_action(access_uid)

    @api.model
    defaction_share(self):
        action=self.env["ir.actions.actions"]._for_xml_id("portal.portal_share_action")
        action['context']={'active_id':self.env.context['active_id'],
                             'active_model':self.env.context['active_model']}
        returnaction

    defget_portal_url(self,suffix=None,report_type=None,download=None,query_string=None,anchor=None):
        """
            Getaportalurlforthismodel,includingaccess_token.
            Theassociatedroutemusthandletheflagsforthemtohaveanyeffect.
            -suffix:stringtoappendtotheurl,beforethequerystring
            -report_type:report_typequerystring,oftenoneof:html,pdf,text
            -download:setthedownloadquerystringtotrue
            -query_string:additionalquerystring
            -anchor:stringtoappendaftertheanchor#
        """
        self.ensure_one()
        url=self.access_url+'%s?access_token=%s%s%s%s%s'%(
            suffixifsuffixelse'',
            self._portal_ensure_token(),
            '&report_type=%s'%report_typeifreport_typeelse'',
            '&download=true'ifdownloadelse'',
            query_stringifquery_stringelse'',
            '#%s'%anchorifanchorelse''
        )
        returnurl
