#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_
fromflectra.exceptionsimportAccessError


classDigest(models.Model):
    _inherit='digest.digest'

    kpi_all_sale_total=fields.Boolean('AllSales')
    kpi_all_sale_total_value=fields.Monetary(compute='_compute_kpi_sale_total_value')

    def_compute_kpi_sale_total_value(self):
        ifnotself.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            raiseAccessError(_("Donothaveaccess,skipthisdataforuser'sdigestemail"))
        forrecordinself:
            start,end,company=record._get_kpi_compute_parameters()
            all_channels_sales=self.env['sale.report'].read_group([
                ('date','>=',start),
                ('date','<',end),
                ('state','notin',['draft','cancel','sent']),
                ('company_id','=',company.id)],['price_total'],['company_id'])
            record.kpi_all_sale_total_value=sum([channel_sale['price_total']forchannel_saleinall_channels_sales])

    def_compute_kpis_actions(self,company,user):
        res=super(Digest,self)._compute_kpis_actions(company,user)
        res['kpi_all_sale_total']='sale.report_all_channels_sales_action&menu_id=%s'%self.env.ref('sale.sale_menu_root').id
        returnres
