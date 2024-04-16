#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_
fromflectra.exceptionsimportAccessError


classDigest(models.Model):
    _inherit='digest.digest'

    kpi_pos_total=fields.Boolean('POSSales')
    kpi_pos_total_value=fields.Monetary(compute='_compute_kpi_pos_total_value')

    def_compute_kpi_pos_total_value(self):
        ifnotself.env.user.has_group('point_of_sale.group_pos_user'):
            raiseAccessError(_("Donothaveaccess,skipthisdataforuser'sdigestemail"))
        forrecordinself:
            start,end,company=record._get_kpi_compute_parameters()
            record.kpi_pos_total_value=sum(self.env['pos.order'].search([
                ('date_order','>=',start),
                ('date_order','<',end),
                ('state','notin',['draft','cancel','invoiced']),
                ('company_id','=',company.id)
            ]).mapped('amount_total'))

    def_compute_kpis_actions(self,company,user):
        res=super(Digest,self)._compute_kpis_actions(company,user)
        res['kpi_pos_total']='point_of_sale.action_pos_sale_graph&menu_id=%s'%self.env.ref('point_of_sale.menu_point_root').id
        returnres
