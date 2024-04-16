fromflectraimportmodels,fields,api,_
fromflectra.toolsimportformat_date


classStockInventory(models.Model):
    _inherit='stock.inventory'

    l10n_de_template_data=fields.Binary(compute='_compute_l10n_de_template_data')

    def_compute_l10n_de_template_data(self):
        forrecordinself:
            record.l10n_de_template_data=data=[]
            ifrecord.date:
                data.append((_("Date"),format_date(self.env,record.date)))
