#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64

fromflectraimportfields,api,models


classPOSOrder(models.Model):
    _inherit='pos.order'

    def_prepare_invoice_vals(self):
        vals=super()._prepare_invoice_vals()
        ifself.company_id.country_id.code=='SA':
            vals.update({'l10n_sa_confirmation_datetime':self.date_order})
        returnvals
