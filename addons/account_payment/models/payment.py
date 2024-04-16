#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportfields,models,_
fromflectra.toolsimportfloat_compare

_logger=logging.getLogger(__name__)


classPaymentTransaction(models.Model):
    _inherit='payment.transaction'

    defrender_invoice_button(self,invoice,submit_txt=None,render_values=None):
        values={
            'partner_id':invoice.partner_id.id,
            'type':self.type,
        }
        ifrender_values:
            values.update(render_values)
        returnself.acquirer_id.with_context(submit_class='btnbtn-primary',submit_txt=submit_txtor_('PayNow')).sudo().render(
            self.reference,
            invoice.amount_residual,
            invoice.currency_id.id,
            values=values,
        )
