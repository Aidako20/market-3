#coding:utf-8
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classPosPaymentMethod(models.Model):
    _inherit='pos.payment.method'

    def_get_payment_terminal_selection(self):
        returnsuper(PosPaymentMethod,self)._get_payment_terminal_selection()+[('six','SIX')]

    six_terminal_ip=fields.Char('SixTerminalIP')
