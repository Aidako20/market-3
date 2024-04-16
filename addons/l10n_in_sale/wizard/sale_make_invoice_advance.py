#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classSaleAdvancePaymentInv(models.TransientModel):
    _inherit="sale.advance.payment.inv"

    def_prepare_invoice_values(self,order,name,amount,so_line):
        res=super()._prepare_invoice_values(order,name,amount,so_line)
        iforder.l10n_in_journal_id:
            res['journal_id']=order.l10n_in_journal_id.id
        iforder.l10n_in_company_country_code=='IN':
            res['l10n_in_gst_treatment']=order.l10n_in_gst_treatment
        iforder.l10n_in_reseller_partner_id:
            res['l10n_in_reseller_partner_id']=order.l10n_in_reseller_partner_id
        returnres
