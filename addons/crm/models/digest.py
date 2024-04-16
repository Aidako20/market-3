#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportAccessError


classDigest(models.Model):
    _inherit='digest.digest'

    kpi_crm_lead_created=fields.Boolean('NewLeads/Opportunities')
    kpi_crm_lead_created_value=fields.Integer(compute='_compute_kpi_crm_lead_created_value')
    kpi_crm_opportunities_won=fields.Boolean('OpportunitiesWon')
    kpi_crm_opportunities_won_value=fields.Integer(compute='_compute_kpi_crm_opportunities_won_value')

    def_compute_kpi_crm_lead_created_value(self):
        ifnotself.env.user.has_group('sales_team.group_sale_salesman'):
            raiseAccessError(_("Donothaveaccess,skipthisdataforuser'sdigestemail"))
        forrecordinself:
            start,end,company=record._get_kpi_compute_parameters()
            record.kpi_crm_lead_created_value=self.env['crm.lead'].search_count([
                ('create_date','>=',start),
                ('create_date','<',end),
                ('company_id','=',company.id)
            ])

    def_compute_kpi_crm_opportunities_won_value(self):
        ifnotself.env.user.has_group('sales_team.group_sale_salesman'):
            raiseAccessError(_("Donothaveaccess,skipthisdataforuser'sdigestemail"))
        forrecordinself:
            start,end,company=record._get_kpi_compute_parameters()
            record.kpi_crm_opportunities_won_value=self.env['crm.lead'].search_count([
                ('type','=','opportunity'),
                ('probability','=','100'),
                ('date_closed','>=',start),
                ('date_closed','<',end),
                ('company_id','=',company.id)
            ])

    def_compute_kpis_actions(self,company,user):
        res=super(Digest,self)._compute_kpis_actions(company,user)
        res['kpi_crm_lead_created']='crm.crm_lead_action_pipeline&menu_id=%s'%self.env.ref('crm.crm_menu_root').id
        res['kpi_crm_opportunities_won']='crm.crm_lead_action_pipeline&menu_id=%s'%self.env.ref('crm.crm_menu_root').id
        ifuser.has_group('crm.group_use_lead'):
            res['kpi_crm_lead_created']='crm.crm_lead_all_leads&menu_id=%s'%self.env.ref('crm.crm_menu_root').id
        returnres
