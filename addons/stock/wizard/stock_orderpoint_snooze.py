#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.tools.date_utilsimportadd


classStockOrderpointSnooze(models.TransientModel):
    _name='stock.orderpoint.snooze'
    _description='SnoozeOrderpoint'

    orderpoint_ids=fields.Many2many('stock.warehouse.orderpoint')
    predefined_date=fields.Selection([
        ('day','1Day'),
        ('week','1Week'),
        ('month','1Month'),
        ('custom','Custom')
    ],string='Snoozefor',default='day')
    snoozed_until=fields.Date('SnoozeDate')

    @api.onchange('predefined_date')
    def_onchange_predefined_date(self):
        today=fields.Date.context_today(self)
        ifself.predefined_date=='day':
            self.snoozed_until=add(today,days=1)
        elifself.predefined_date=='week':
            self.snoozed_until=add(today,weeks=1)
        elifself.predefined_date=='month':
            self.snoozed_until=add(today,months=1)

    defaction_snooze(self):
        self.orderpoint_ids.write({
            'snoozed_until':self.snoozed_until
        })
