#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_
fromflectra.exceptionsimportAccessError


classDigest(models.Model):
    _inherit='digest.digest'

    kpi_website_sale_total=fields.Boolean('eCommerceSales')
    kpi_website_sale_total_value=fields.Monetary(compute='_compute_kpi_website_sale_total_value')

    def_compute_kpi_website_sale_total_value(self):
        ifnotself.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            raiseAccessError(_("Donothaveaccess,skipthisdataforuser'sdigestemail"))
        forrecordinself:
            start,end,company=record._get_kpi_compute_parameters()
            confirmed_website_sales=self.env['sale.order'].search([
                ('date_order','>=',start),
                ('date_order','<',end),
                ('state','notin',['draft','cancel','sent']),
                ('website_id','!=',False),
                ('company_id','=',company.id)
            ])
            record.kpi_website_sale_total_value=sum(confirmed_website_sales.mapped('amount_total'))

    def_compute_kpis_actions(self,company,user):
        res=super(Digest,self)._compute_kpis_actions(company,user)
        res['kpi_website_sale_total']='website.backend_dashboard&menu_id=%s'%self.env.ref('website.menu_website_configuration').id
        returnres
