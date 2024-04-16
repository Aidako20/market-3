fromflectraimportmodels,fields,api,_
fromflectra.toolsimportformat_date


classRepairOrder(models.Model):
    _inherit='repair.order'

    l10n_de_template_data=fields.Binary(compute='_compute_l10n_de_template_data')
    l10n_de_document_title=fields.Char(compute='_compute_l10n_de_document_title')

    def_compute_l10n_de_template_data(self):
        forrecordinself:
            record.l10n_de_template_data=data=[]
            ifrecord.product_id:
                data.append((_("ProducttoRepair"),record.product_id.name))
            ifrecord.lot_id:
                data.append((_("Lot/SerialNumber"),record.lot_id.name))
            ifrecord.guarantee_limit:
                data.append((_("Warranty"),format_date(self.env,record.guarantee_limit)))
            data.append((_("PrintingDate"),format_date(self.env,fields.Date.today())))

    def_compute_l10n_de_document_title(self):
        forrecordinself:
            ifrecord.state=='draft':
                record.l10n_de_document_title=_("RepairQuotation")
            else:
                record.l10n_de_document_title=_("RepairOrder")
