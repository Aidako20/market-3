#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.


fromflectraimportapi,fields,models,_,tools
fromflectra.osvimportexpression


classMassMailing(models.Model):
    _name='mailing.mailing'
    _inherit='mailing.mailing'

    use_leads=fields.Boolean('UseLeads',compute='_compute_use_leads')
    crm_lead_count=fields.Integer('Leads/OpportunitiesCount',groups='sales_team.group_sale_salesman',compute='_compute_crm_lead_count')

    def_compute_use_leads(self):
        formass_mailinginself:
            mass_mailing.use_leads=self.env.user.has_group('crm.group_use_lead')

    def_compute_crm_lead_count(self):
        lead_data=self.env['crm.lead'].with_context(active_test=False).read_group(
            [('source_id','in',self.source_id.ids)],
            ['source_id'],['source_id']
        )
        mapped_data={datum['source_id'][0]:datum['source_id_count']fordatuminlead_data}
        formass_mailinginself:
            mass_mailing.crm_lead_count=mapped_data.get(mass_mailing.source_id.id,0)

    defaction_redirect_to_leads_and_opportunities(self):
        view='crm.crm_lead_all_leads'ifself.use_leadselse'crm.crm_lead_opportunities'
        action=self.env.ref(view).sudo().read()[0]
        action['view_mode']='tree,kanban,graph,pivot,form,calendar'
        action['domain']=[('source_id','in',self.source_id.ids)]
        action['context']={'active_test':False,'create':False}
        returnaction

    def_prepare_statistics_email_values(self):
        self.ensure_one()
        values=super(MassMailing,self)._prepare_statistics_email_values()
        ifnotself.user_id:
            returnvalues
        values['kpi_data'][1]['kpi_col1']={
            'value':tools.format_decimalized_number(self.crm_lead_count,decimal=0),
            'col_subtitle':_('LEADS'),
        }
        returnvalues
