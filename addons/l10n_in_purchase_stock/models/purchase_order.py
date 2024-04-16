#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api


classPurchaseOrder(models.Model):
    _inherit="purchase.order"

    @api.onchange('company_id','picking_type_id')
    defl10n_in_onchange_company_id(self):
        ifself.picking_type_id.warehouse_idandself.picking_type_id.warehouse_id.l10n_in_purchase_journal_id:
            self.l10n_in_journal_id=self.picking_type_id.warehouse_id.l10n_in_purchase_journal_id.id
        else:
            super().l10n_in_onchange_company_id()
