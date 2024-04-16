fromflectraimportmodels,fields,api,_
fromflectra.toolsimportformat_date


classPurchaseOrder(models.Model):
    _inherit='purchase.order'

    l10n_de_template_data=fields.Binary(compute='_compute_l10n_de_template_data')
    l10n_de_document_title=fields.Char(compute='_compute_l10n_de_document_title')
    l10n_de_addresses=fields.Binary(compute='_compute_l10n_de_addresses')

    def_compute_l10n_de_template_data(self):
        forrecordinself:
            record.l10n_de_template_data=data=[]
            ifrecord.state=='draft':
                data.append((_("RequestforQuotationNo."),record.name))
            elifrecord.statein['sent','toapprove','purchase','done']:
                data.append((_("PurchaseOrderNo."),record.name))
            elifrecord.state=='cancel':
                data.append((_("CancelledPurchaseOrderNo."),record.name))

            ifrecord.user_id:
                data.append((_("PurchaseRepresentative"),record.user_id.name))
            ifrecord.partner_ref:
                data.append((_("OrderReference"),record.partner_ref))
            ifrecord.date_order:
                data.append((_("OrderDate"),format_date(self.env,record.date_order)))
            ifrecord.incoterm_id:
                data.append((_("Incoterm"),record.incoterm_id.code))



    def_compute_l10n_de_document_title(self):
        forrecordinself:
            ifrecord.state=='draft':
                record.l10n_de_document_title=_("RequestforQuotation")
            elifrecord.statein['sent','toapprove','purchase','done']:
                record.l10n_de_document_title=_("PurchaseOrder")
            elifrecord.state=='cancel':
                record.l10n_de_document_title=_("CancelledPurchaseOrder")

    def_compute_l10n_de_addresses(self):
        forrecordinself:
            record.l10n_de_addresses=data=[]
            ifrecord.dest_address_id:
                data.append((_("ShippingAddress:"),record.dest_address_id))
            elif'picking_type_id'inrecord._fieldsandrecord.picking_type_id.warehouse_id:
                data.append((_("ShippingAddress:"),record.picking_type_id.warehouse_id.partner_id))
