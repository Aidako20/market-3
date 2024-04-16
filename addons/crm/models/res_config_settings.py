#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    crm_alias_prefix=fields.Char(
        'DefaultAliasNameforLeads',
        compute="_compute_crm_alias_prefix",readonly=False,store=True)
    generate_lead_from_alias=fields.Boolean(
        'ManualAssignmentofEmails',config_parameter='crm.generate_lead_from_alias',
        compute="_compute_generate_lead_from_alias",readonly=False,store=True)
    group_use_lead=fields.Boolean(string="Leads",implied_group='crm.group_use_lead')
    group_use_recurring_revenues=fields.Boolean(string="RecurringRevenues",implied_group='crm.group_use_recurring_revenues')
    module_crm_iap_lead=fields.Boolean("Generatenewleadsbasedontheircountry,industries,size,etc.")
    module_crm_iap_lead_website=fields.Boolean("CreateLeads/Opportunitiesfromyourwebsite'straffic")
    module_crm_iap_lead_enrich=fields.Boolean("Enrichyourleadsautomaticallywithcompanydatabasedontheiremailaddress.")
    module_mail_client_extension=fields.Boolean("Seeandmanageusers,companies,andleadsfromourmailclientextensions.")
    lead_enrich_auto=fields.Selection([
        ('manual','Enrichleadsondemandonly'),
        ('auto','Enrichallleadsautomatically'),
    ],string='Enrichleadautomatically',default='manual',config_parameter='crm.iap.lead.enrich.setting')
    lead_mining_in_pipeline=fields.Boolean("Createaleadminingrequestdirectlyfromtheopportunitypipeline.",config_parameter='crm.lead_mining_in_pipeline')
    predictive_lead_scoring_start_date=fields.Date(string='LeadScoringStartingDate',compute="_compute_pls_start_date",inverse="_inverse_pls_start_date_str")
    predictive_lead_scoring_start_date_str=fields.Char(string='LeadScoringStartingDateinString',config_parameter='crm.pls_start_date')
    predictive_lead_scoring_fields=fields.Many2many('crm.lead.scoring.frequency.field',string='LeadScoringFrequencyFields',compute="_compute_pls_fields",inverse="_inverse_pls_fields_str")
    predictive_lead_scoring_fields_str=fields.Char(string='LeadScoringFrequencyFieldsinString',config_parameter='crm.pls_fields')

    def_find_default_lead_alias_id(self):
        alias=self.env.ref('crm.mail_alias_lead_info',False)
        ifnotalias:
            alias=self.env['mail.alias'].search([
                ('alias_model_id.model','=','crm.lead'),
                ('alias_force_thread_id','=',False),
                ('alias_parent_model_id.model','=','crm.team'),
                ('alias_parent_thread_id','=',False),
                ('alias_defaults','=','{}')
            ],limit=1)
        returnalias

    @api.depends('predictive_lead_scoring_fields_str')
    def_compute_pls_fields(self):
        """Asconfig_parametersdoesnotacceptm2mfield,
            wegetthefieldsbackfromtheCharconfigfield,toeasetheconfigurationinconfigpanel"""
        forsettinginself:
            ifsetting.predictive_lead_scoring_fields_str:
                names=setting.predictive_lead_scoring_fields_str.split(',')
                fields=self.env['ir.model.fields'].search([('name','in',names),('model','=','crm.lead')])
                setting.predictive_lead_scoring_fields=self.env['crm.lead.scoring.frequency.field'].search([('field_id','in',fields.ids)])
            else:
                setting.predictive_lead_scoring_fields=None

    def_inverse_pls_fields_str(self):
        """Asconfig_parametersdoesnotacceptm2mfield,
            westorethefieldswithacommaseparatedstringintoaCharconfigfield"""
        forsettinginself:
            ifsetting.predictive_lead_scoring_fields:
                setting.predictive_lead_scoring_fields_str=','.join(setting.predictive_lead_scoring_fields.mapped('field_id.name'))
            else:
                setting.predictive_lead_scoring_fields_str=''

    @api.depends('predictive_lead_scoring_start_date_str')
    def_compute_pls_start_date(self):
        """Asconfig_parametersdoesnotacceptDatefield,
            wegetthedatebackfromtheCharconfigfield,toeasetheconfigurationinconfigpanel"""
        forsettinginself:
            lead_scoring_start_date=setting.predictive_lead_scoring_start_date_str
            #ifconfigparamisdeleted/empty,setthedate8dayspriortocurrentdate
            ifnotlead_scoring_start_date:
                setting.predictive_lead_scoring_start_date=fields.Date.to_date(fields.Date.today()-timedelta(days=8))
            else:
                try:
                    setting.predictive_lead_scoring_start_date=fields.Date.to_date(lead_scoring_start_date)
                exceptValueError:
                    #theconfigparameterismalformed,sosetthedate8dayspriortocurrentdate
                    setting.predictive_lead_scoring_start_date=fields.Date.to_date(fields.Date.today()-timedelta(days=8))

    def_inverse_pls_start_date_str(self):
        """Asconfig_parametersdoesnotacceptDatefield,
            westorethedateformatedstringintoaCharconfigfield"""
        forsettinginself:
            ifsetting.predictive_lead_scoring_start_date:
                setting.predictive_lead_scoring_start_date_str=fields.Date.to_string(setting.predictive_lead_scoring_start_date)

    @api.depends('group_use_lead')
    def_compute_generate_lead_from_alias(self):
        """Resetalias/leadsconfigurationifleadsarenotused"""
        forsettinginself.filtered(lambdar:notr.group_use_lead):
            setting.generate_lead_from_alias=False

    @api.depends('generate_lead_from_alias')
    def_compute_crm_alias_prefix(self):
        forsettinginself:
            setting.crm_alias_prefix=(setting.crm_alias_prefixor'contact')ifsetting.generate_lead_from_aliaselseFalse

    @api.model
    defget_values(self):
        res=super(ResConfigSettings,self).get_values()
        alias=self._find_default_lead_alias_id()
        res.update(
            crm_alias_prefix=alias.alias_nameifaliaselseFalse,
        )
        returnres

    defset_values(self):
        super(ResConfigSettings,self).set_values()
        alias=self._find_default_lead_alias_id()
        ifalias:
            alias.write({'alias_name':self.crm_alias_prefix})
        else:
            self.env['mail.alias'].create({
                'alias_name':self.crm_alias_prefix,
                'alias_model_id':self.env['ir.model']._get('crm.lead').id,
                'alias_parent_model_id':self.env['ir.model']._get('crm.team').id,
            })
        forteaminself.env['crm.team'].search([]):
            team.alias_id.write(team._alias_get_creation_values())

    #ACTIONS
    defaction_reset_lead_probabilities(self):
        ifself.env.user._is_admin():
            self.env['crm.lead'].sudo()._cron_update_automated_probabilities()
