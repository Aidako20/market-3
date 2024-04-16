#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classAccountMove(models.Model):
    _inherit='account.move'

    @api.onchange('purchase_vendor_bill_id','purchase_id')
    def_onchange_purchase_auto_complete(self):
        purchase_order_id=self.purchase_vendor_bill_id.purchase_order_idorself.purchase_id
        ifpurchase_order_idandself.l10n_in_company_country_code=='IN':
            journal_id=self.purchase_vendor_bill_id.purchase_order_id.l10n_in_journal_idorself.purchase_id.l10n_in_journal_id
            ifjournal_id:
                self.journal_id=journal_id
            self.l10n_in_gst_treatment=purchase_order_id.l10n_in_gst_treatment
        returnsuper()._onchange_purchase_auto_complete()
