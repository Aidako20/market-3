#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api
fromflectra.exceptionsimportAccessError


classPosConfig(models.Model):
    _inherit='pos.config'


    crm_team_id=fields.Many2one(
        'crm.team',string="SalesTeam",
        help="ThisPointofsale'ssaleswillberelatedtothisSalesTeam.")

    @api.onchange('company_id')
    def_get_default_pos_team(self):
        default_sale_team=self.env.ref('sales_team.pos_sales_team',raise_if_not_found=False)
        ifdefault_sale_teamand(notdefault_sale_team.company_idordefault_sale_team.company_id==self.company_id):
            self.crm_team_id=default_sale_team
        else:
            self.crm_team_id=self.env['crm.team'].search(['|',('company_id','=',self.company_id.id),('company_id','=',False)],limit=1)
