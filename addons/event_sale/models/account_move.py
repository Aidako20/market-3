#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classAccountMove(models.Model):
    _inherit='account.move'

    defaction_invoice_paid(self):
        """Whenaninvoicelinkedtoasalesordersellingregistrationsis
        paidconfirmattendees.Attendeesshouldindeednotbeconfirmedbefore
        fullpayment."""
        res=super(AccountMove,self).action_invoice_paid()
        self.mapped('line_ids.sale_line_ids')._update_registrations(confirm=True,mark_as_paid=True)
        returnres
