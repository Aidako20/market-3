#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classEvent(models.Model):
    _inherit='event.event'

    sale_order_lines_ids=fields.One2many(
        'sale.order.line','event_id',
        groups='sales_team.group_sale_salesman',
        string='Allsaleorderlinespointingtothisevent')
    sale_price_subtotal=fields.Monetary(
        string='Sales(TaxExcluded)',compute='_compute_sale_price_subtotal',
        groups='sales_team.group_sale_salesman')
    currency_id=fields.Many2one(
        'res.currency',string='Currency',
        related='company_id.currency_id',readonly=True)

    @api.depends('company_id.currency_id',
                 'sale_order_lines_ids.price_subtotal','sale_order_lines_ids.currency_id',
                 'sale_order_lines_ids.company_id','sale_order_lines_ids.order_id.date_order')
    def_compute_sale_price_subtotal(self):
        """Takesallthesale.order.linesrelatedtothiseventandconvertsamounts
        fromthecurrencyofthesaleordertothecurrencyoftheeventcompany.

        Toavoidextraoverhead,weuseconversionratesasof'today'.
        Meaningwehaveanumberthatcanchangeovertime,butusingtheconversionrates
        atthetimeoftherelatedsale.orderwouldmeanthousandsofextrarequestsaswewould
        havetodooneconversionpersale.order(andasale.orderiscreatedeverytime
        wesellasingleeventticket)."""
        date_now=fields.Datetime.now()
        sale_price_by_event={}
        ifself.ids:
            event_subtotals=self.env['sale.order.line'].read_group(
                [('event_id','in',self.ids),
                 ('price_subtotal','!=',0)],
                ['event_id','currency_id','price_subtotal:sum'],
                ['event_id','currency_id'],
                lazy=False
            )

            company_by_event={
                event._origin.idorevent.id:event.company_id
                foreventinself
            }

            currency_by_event={
                event._origin.idorevent.id:event.currency_id
                foreventinself
            }

            currency_by_id={
                currency.id:currency
                forcurrencyinself.env['res.currency'].browse(
                    [event_subtotal['currency_id'][0]forevent_subtotalinevent_subtotals]
                )
            }

            forevent_subtotalinevent_subtotals:
                price_subtotal=event_subtotal['price_subtotal']
                event_id=event_subtotal['event_id'][0]
                currency_id=event_subtotal['currency_id'][0]
                sale_price=currency_by_event[event_id]._convert(
                    price_subtotal,
                    currency_by_id[currency_id],
                    company_by_event[event_id],
                    date_now)
                ifevent_idinsale_price_by_event:
                    sale_price_by_event[event_id]+=sale_price
                else:
                    sale_price_by_event[event_id]=sale_price

        foreventinself:
            event.sale_price_subtotal=sale_price_by_event.get(event._origin.idorevent.id,0)

    defaction_view_linked_orders(self):
        """Redirectstotheorderslinkedtothecurrentevents"""
        sale_order_action=self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        sale_order_action.update({
            'domain':[('state','!=','cancel'),('order_line.event_id','in',self.ids)],
            'context':{'create':0},
        })
        returnsale_order_action
