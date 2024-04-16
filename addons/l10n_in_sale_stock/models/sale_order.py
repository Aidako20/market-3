#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api


classSaleOrder(models.Model):
    _inherit="sale.order"

    @api.depends('company_id','warehouse_id')
    def_compute_l10n_in_journal_id(self):
        super()._compute_l10n_in_journal_id()
        fororderinself:
            iforder.l10n_in_company_country_code=='IN':
                iforder.warehouse_id.l10n_in_sale_journal_id:
                    order.l10n_in_journal_id=order.warehouse_id.l10n_in_sale_journal_id.id
