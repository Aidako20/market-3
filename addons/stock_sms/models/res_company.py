#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classCompany(models.Model):
    _inherit="res.company"

    def_default_confirmation_sms_picking_template(self):
        try:
            returnself.env.ref('stock_sms.sms_template_data_stock_delivery').id
        exceptValueError:
            returnFalse

    stock_move_sms_validation=fields.Boolean("SMSConfirmation",default=True)
    stock_sms_confirmation_template_id=fields.Many2one(
        'sms.template',string="SMSTemplate",
        domain="[('model','=','stock.picking')]",
        default=_default_confirmation_sms_picking_template,
        help="SMSsenttothecustomeroncetheorderisdone.")
    has_received_warning_stock_sms=fields.Boolean()
