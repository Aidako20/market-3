#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api,SUPERUSER_ID

classUtmCampaign(models.Model):
    _inherit='utm.campaign'

    use_leads=fields.Boolean('UseLeads',compute='_compute_use_leads')
    crm_lead_count=fields.Integer('Leads/Opportunitiescount',groups='sales_team.group_sale_salesman',compute="_compute_crm_lead_count")

    def_compute_use_leads(self):
        forcampaigninself:
            campaign.use_leads=self.env.user.has_group('crm.group_use_lead')

    def_compute_crm_lead_count(self):
        lead_data=self.env['crm.lead'].with_context(active_test=False).read_group([
            ('campaign_id','in',self.ids)],
            ['campaign_id'],['campaign_id'])
        mapped_data={datum['campaign_id'][0]:datum['campaign_id_count']fordatuminlead_data}
        forcampaigninself:
            campaign.crm_lead_count=mapped_data.get(campaign.id,0)

    defaction_redirect_to_leads_opportunities(self):
        view='crm.crm_lead_all_leads'ifself.use_leadselse'crm.crm_lead_opportunities'
        action=self.env['ir.actions.act_window']._for_xml_id(view)
        action['view_mode']='tree,kanban,graph,pivot,form,calendar'
        action['domain']=[('campaign_id','in',self.ids)]
        action['context']={'active_test':False,'create':False}
        returnaction
