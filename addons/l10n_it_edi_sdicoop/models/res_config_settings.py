#-*-coding:utf-8-*-

fromflectraimportapi,models,fields,_
fromflectra.exceptionsimportUserError

classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    is_edi_proxy_active=fields.Boolean(compute='_compute_is_edi_proxy_active')
    l10n_it_edi_proxy_current_state=fields.Char(compute='_compute_l10n_it_edi_proxy_current_state')
    l10n_it_edi_sdicoop_register=fields.Boolean(compute='_compute_l10n_it_edi_sdicoop_register',inverse='_set_l10n_it_edi_sdicoop_register_demo_mode')
    l10n_it_edi_sdicoop_demo_mode=fields.Selection(
        [('demo','Demo'),
         ('test','Test(experimental)'),
         ('prod','Official')],
        compute='_compute_l10n_it_edi_sdicoop_demo_mode',
        inverse='_set_l10n_it_edi_sdicoop_register_demo_mode',
        readonly=False)

    def_create_proxy_user(self,company_id):
        fattura_pa=self.env.ref('l10n_it_edi.edi_fatturaPA')
        edi_identification=fattura_pa._get_proxy_identification(company_id)
        self.env['account_edi_proxy_client.user']._register_proxy_user(company_id,fattura_pa,edi_identification)

    @api.depends('company_id.account_edi_proxy_client_ids','company_id.account_edi_proxy_client_ids.active')
    def_compute_l10n_it_edi_sdicoop_demo_mode(self):
        forconfiginself:
            config.l10n_it_edi_sdicoop_demo_mode=self.env['account_edi_proxy_client.user']._get_demo_state()

    def_set_l10n_it_edi_sdicoop_demo_mode(self):
        forconfiginself:
            self.env['ir.config_parameter'].set_param('account_edi_proxy_client.demo',config.l10n_it_edi_sdicoop_demo_mode)

    @api.depends('company_id.account_edi_proxy_client_ids','company_id.account_edi_proxy_client_ids.active')
    def_compute_is_edi_proxy_active(self):
        forconfiginself:
            config.is_edi_proxy_active=config.company_id.account_edi_proxy_client_ids

    @api.depends('company_id.account_edi_proxy_client_ids','company_id.account_edi_proxy_client_ids.active')
    def_compute_l10n_it_edi_proxy_current_state(self):
        fattura_pa=self.env.ref('l10n_it_edi.edi_fatturaPA')
        forconfiginself:
            proxy_user=config.company_id.account_edi_proxy_client_ids.search([
                ('company_id','=',config.company_id.id),
                ('edi_format_id','=',fattura_pa.id),
            ],limit=1)

            config.l10n_it_edi_proxy_current_state='inactive'ifnotproxy_userelse'demo'ifproxy_user.id_client[:4]=='demo'else'active'

    @api.depends('company_id')
    def_compute_l10n_it_edi_sdicoop_register(self):
        """Neededbecauseitexpectsacompute"""
        self.l10n_it_edi_sdicoop_register=False

    defbutton_create_proxy_user(self):
        #Fornow,onlyfattura_pausestheproxy.
        #Touseitformore,wehavetoeithermaketheactivationoftheproxyonaformatbasis
        #orcreateauserperformathere(butalsowheninstallingnewformats)
        fattura_pa=self.env.ref('l10n_it_edi.edi_fatturaPA')
        edi_identification=fattura_pa._get_proxy_identification(self.company_id)
        ifnotedi_identification:
            return

        self.env['account_edi_proxy_client.user']._register_proxy_user(self.company_id,fattura_pa,edi_identification)

    def_set_l10n_it_edi_sdicoop_register_demo_mode(self):

        fattura_pa=self.env.ref('l10n_it_edi.edi_fatturaPA')
        forconfiginself:

            proxy_user=self.env['account_edi_proxy_client.user'].search([
                ('company_id','=',config.company_id.id),
                ('edi_format_id','=',fattura_pa.id)
            ],limit=1)

            real_proxy_users=self.env['account_edi_proxy_client.user'].sudo().search([
                ('id_client','notlike','demo'),
            ])

            #Updatetheconfigaspertheselectedradiobutton
            previous_demo_state=proxy_user._get_demo_state()
            self.env['ir.config_parameter'].set_param('account_edi_proxy_client.demo',config.l10n_it_edi_sdicoop_demo_mode)

            #Iftheuseristryingtochangefromastateinwhichtheyhavearegisteredofficialortestingproxyclient
            #toanotherstate,weshouldstopthem
            ifreal_proxy_usersandprevious_demo_state!=config.l10n_it_edi_sdicoop_demo_mode:
                raiseUserError(_("Thecompanyhasalreadyregisteredwiththeserviceas'Test'or'Official',itcannotchange."))


            ifconfig.l10n_it_edi_sdicoop_register:
                #Thereshouldonlybeoneuseratatime,iftherearenousers,registerone
                ifnotproxy_user:
                    self._create_proxy_user(config.company_id)
                    return

                #Ifthereisademouser,andwearetransitioningfromdemototestorproduction,weshould
                #deletealldemousersandthencreatethenewuser.
                elifproxy_user.id_client[:4]=='demo'andconfig.l10n_it_edi_sdicoop_demo_mode!='demo':
                    self.env['account_edi_proxy_client.user'].search([('id_client','=like','demo%')]).sudo().unlink()
                    self._create_proxy_user(config.company_id)

