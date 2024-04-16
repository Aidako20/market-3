#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classSnailmailConfirmInvoiceSend(models.TransientModel):
    _name='snailmail.confirm.invoice'
    _inherit=['snailmail.confirm']
    _description='SnailmailConfirmInvoice'

    invoice_send_id=fields.Many2one('account.invoice.send')

    def_confirm(self):
        self.ensure_one()
        self.invoice_send_id._print_action()

    def_continue(self):
        self.ensure_one()
        returnself.invoice_send_id.send_and_print()
