#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importuuid
importwerkzeug.urls

fromflectraimportapi,fields,models
fromflectra.addons.iap.toolsimportiap_tools

_logger=logging.getLogger(__name__)

DEFAULT_ENDPOINT='https://iap.flectrahq.com'


classIapAccount(models.Model):
    _name='iap.account'
    _rec_name='service_name'
    _description='IAPAccount'

    service_name=fields.Char()
    account_token=fields.Char(default=lambdas:uuid.uuid4().hex)
    company_ids=fields.Many2many('res.company')

    @api.model
    defcreate(self,vals):
        account=super().create(vals)
        ifself.env['ir.config_parameter'].sudo().get_param('database.is_neutralized')andaccount.account_token:
            #Disablenewaccountsonaneutralizeddatabase
            account.account_token=f"{account.account_token.split('+')[0]}+disabled"
        returnaccount

    @api.model
    defget(self,service_name,force_create=True):
        domain=[
            ('service_name','=',service_name),
            '|',
                ('company_ids','in',self.env.companies.ids),
                ('company_ids','=',False)
        ]
        accounts=self.search(domain,order='iddesc')
        accounts_without_token=accounts.filtered(lambdaacc:notacc.account_token)
        ifaccounts_without_token:
            withself.pool.cursor()ascr:
                #Incaseofafurthererrorthatwillrollbackthedatabase,weshould
                #useadifferentSQLcursortoavoidundotheaccountsdeletion.

                #Flushthependingoperationstoavoidadeadlock.
                self.flush()
                IapAccount=self.with_env(self.env(cr=cr))
                #Needtousesudobecauseregularusersdonothavedeleteright
                IapAccount.search(domain+[('account_token','=',False)]).sudo().unlink()
                accounts=accounts-accounts_without_token
        ifnotaccounts:
            withself.pool.cursor()ascr:
                #Sincetheaccountdidnotexistyet,wewillencounteraNoCreditError,
                #whichisgoingtorollbackthedatabaseandundotheaccountcreation,
                #preventingtheprocesstocontinueanyfurther.

                #Flushthependingoperationstoavoidadeadlock.
                self.flush()
                IapAccount=self.with_env(self.env(cr=cr))
                account=IapAccount.search(domain,order='iddesc',limit=1)
                ifnotaccount:
                    ifnotforce_create:
                        returnaccount
                    account=IapAccount.create({'service_name':service_name})
                #fetch'account_token'intocachewiththiscursor,
                #asself'scursorcannotseethisaccount
                account_token=account.account_token
            account=self.browse(account.id)
            self.env.cache.set(account,IapAccount._fields['account_token'],account_token)
            returnaccount
        accounts_with_company=accounts.filtered(lambdaacc:acc.company_ids)
        ifaccounts_with_company:
            returnaccounts_with_company[0]
        returnaccounts[0]

    @api.model
    defget_credits_url(self,service_name,base_url='',credit=0,trial=False):
        """Callednotablybyajaxcrashmanager,buymorewidget,partner_autocomplete,sanilmail."""
        dbuuid=self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        ifnotbase_url:
            endpoint=iap_tools.iap_get_endpoint(self.env)
            route='/iap/1/credit'
            base_url=endpoint+route
        account_token=self.get(service_name).account_token
        d={
            'dbuuid':dbuuid,
            'service_name':service_name,
            'account_token':account_token,
            'credit':credit,
        }
        iftrial:
            d.update({'trial':trial})
        return'%s?%s'%(base_url,werkzeug.urls.url_encode(d))

    @api.model
    defget_account_url(self):
        """Calledonlybyressettings"""
        route='/iap/services'
        endpoint=iap_tools.iap_get_endpoint(self.env)
        all_accounts=self.search([
            '|',
            ('company_ids','=',self.env.company.id),
            ('company_ids','=',False),
        ])

        global_account_per_service={
            account.service_name:account.account_token
            foraccountinall_accounts.filtered(lambdaacc:notacc.company_ids)
        }
        company_account_per_service={
            account.service_name:account.account_token
            foraccountinall_accounts.filtered(lambdaacc:acc.company_ids)
        }

        #Prioritizecompanyspecificaccountsoverglobalaccounts
        account_per_service={**global_account_per_service,**company_account_per_service}

        parameters={'tokens':list(account_per_service.values())}

        return'%s?%s'%(endpoint+route,werkzeug.urls.url_encode(parameters))

    @api.model
    defget_config_account_url(self):
        """Callednotablybyajaxpartner_autocomplete."""
        account=self.env['iap.account'].get('partner_autocomplete')
        action=self.env.ref('iap.iap_account_action')
        menu=self.env.ref('iap.iap_account_menu')
        no_one=self.user_has_groups('base.group_no_one')
        ifaccount:
            url="/web#id=%s&action=%s&model=iap.account&view_type=form&menu_id=%s"%(account.id,action.id,menu.id)
        else:
            url="/web#action=%s&model=iap.account&view_type=form&menu_id=%s"%(action.id,menu.id)
        returnno_oneandurl

    @api.model
    defget_credits(self,service_name):
        account=self.get(service_name,force_create=False)
        credit=0

        ifaccount:
            route='/iap/1/balance'
            endpoint=iap_tools.iap_get_endpoint(self.env)
            url=endpoint+route
            params={
                'dbuuid':self.env['ir.config_parameter'].sudo().get_param('database.uuid'),
                'account_token':account.account_token,
                'service_name':service_name,
            }
            try:
                credit=iap_tools.iap_jsonrpc(url=url,params=params)
            exceptExceptionase:
                _logger.info('Getcrediterror:%s',str(e))
                credit=-1

        returncredit
