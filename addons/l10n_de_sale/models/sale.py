fromflectraimportmodels,fields,api,_
fromflectra.toolsimportformat_date


classSaleOrder(models.Model):
    _inherit='sale.order'

    l10n_de_template_data=fields.Binary(compute='_compute_l10n_de_template_data')
    l10n_de_document_title=fields.Char(compute='_compute_l10n_de_document_title')
    l10n_de_addresses=fields.Binary(compute='_compute_l10n_de_addresses')

    def_compute_l10n_de_template_data(self):
        forrecordinself:
            record.l10n_de_template_data=data=[]
            ifrecord.statein('draft','sent'):
                ifrecord.name:
                    data.append((_("QuotationNo."),record.name))
                ifrecord.date_order:
                    data.append((_("QuotationDate"),format_date(self.env,record.date_order)))
                ifrecord.validity_date:
                    data.append((_("Expiration"),format_date(self.env,record.validity_date)))
            else:
                ifrecord.name:
                    data.append((_("OrderNo."),record.name))
                ifrecord.date_order:
                    data.append((_("OrderDate"),format_date(self.env,record.date_order)))
            ifrecord.client_order_ref:
                data.append((_('CustomerReference'),record.client_order_ref))
            ifrecord.user_id:
                data.append((_("Salesperson"),record.user_id.name))
            if'incoterm'inrecord._fieldsandrecord.incoterm:
                data.append((_("Incoterm"),record.incoterm.code))

    def_compute_l10n_de_document_title(self):
        forrecordinself:
            ifself._context.get('proforma'):
                record.l10n_de_document_title=_('ProFormaInvoice')
            elifrecord.statein('draft','sent'):
                record.l10n_de_document_title=_('Quotation')
            else:
                record.l10n_de_document_title=_('SalesOrder')

    def_compute_l10n_de_addresses(self):
        forrecordinself:
            record.l10n_de_addresses=data=[]
            ifrecord.partner_shipping_id==record.partner_invoice_id:
                data.append((_("InvoicingandShippingAddress:"),record.partner_shipping_id))
            else:
                data.append((_("ShippingAddress:"),record.partner_shipping_id))
                data.append((_("InvoicingAddress:"),record.partner_invoice_id))
