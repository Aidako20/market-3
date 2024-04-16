#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    security_lead=fields.Float(related='company_id.security_lead',string="SecurityLeadTime",readonly=False)
    group_display_incoterm=fields.Boolean("Incoterms",implied_group='sale_stock.group_display_incoterm')
    group_lot_on_invoice=fields.Boolean("DisplayLots&SerialNumbersonInvoices",
        implied_group='sale_stock.group_lot_on_invoice')
    use_security_lead=fields.Boolean(
        string="SecurityLeadTimeforSales",
        config_parameter='sale_stock.use_security_lead',
        help="Marginoferrorfordatespromisedtocustomers.Productswillbescheduledfordeliverythatmanydaysearlierthantheactualpromiseddate,tocopewithunexpecteddelaysinthesupplychain.")
    default_picking_policy=fields.Selection([
        ('direct','Shipproductsassoonasavailable,withbackorders'),
        ('one','Shipallproductsatonce')
        ],"PickingPolicy",default='direct',default_model="sale.order",required=True)

    @api.onchange('use_security_lead')
    def_onchange_use_security_lead(self):
        ifnotself.use_security_lead:
            self.security_lead=0.0
