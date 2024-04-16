#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta,datetime,time
fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models


classResPartner(models.Model):
    _inherit='res.partner'

    purchase_line_ids=fields.One2many('purchase.order.line','partner_id',string="PurchaseLines")
    on_time_rate=fields.Float(
        "On-TimeDeliveryRate",compute='_compute_on_time_rate',
        help="Overthepastxdays;thenumberofproductsreceivedontimedividedbythenumberoforderedproducts."\
            "xiseithertheSystemParameterpurchase_stock.on_time_delivery_daysorthedefault365")

    @api.depends('purchase_line_ids')
    def_compute_on_time_rate(self):
        date_order_days_delta=int(self.env['ir.config_parameter'].sudo().get_param('purchase_stock.on_time_delivery_days',default='365'))
        order_lines=self.env['purchase.order.line'].search([
            ('partner_id','in',self.ids),
            ('date_order','>',fields.Date.today()-timedelta(date_order_days_delta)),
            ('qty_received','!=',0),
            ('order_id.state','in',['done','purchase']),
            ('product_id','in',self.env['product.product'].sudo()._search([('type','!=','service')]))
        ])
        lines_qty_done=defaultdict(lambda:0)
        moves=self.env['stock.move'].search([
            ('purchase_line_id','in',order_lines.ids),
            ('state','=','done')])
        #Fetchfieldsfromdbandputthemincache.
        order_lines.read(['date_planned','partner_id','product_uom_qty'],load='')
        moves.read(['purchase_line_id','date'],load='')
        moves=moves.filtered(lambdam:m.date.date()<=m.purchase_line_id.date_planned.date())
        formove,qty_doneinzip(moves,moves.mapped('quantity_done')):
            lines_qty_done[move.purchase_line_id.id]+=qty_done
        partner_dict={}
        forlineinorder_lines:
            on_time,ordered=partner_dict.get(line.partner_id,(0,0))
            ordered+=line.product_uom_qty
            on_time+=lines_qty_done[line.id]
            partner_dict[line.partner_id]=(on_time,ordered)
        seen_partner=self.env['res.partner']
        forpartner,numbersinpartner_dict.items():
            seen_partner|=partner
            on_time,ordered=numbers
            partner.on_time_rate=on_time/ordered*100iforderedelse-1  #usenegativenumbertoindicatenodata
        (self-seen_partner).on_time_rate=-1
