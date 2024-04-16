fromflectraimportmodels,fields,_
fromflectra.toolsimportformat_date


classAccountMove(models.Model):
    _inherit='account.move'

    l10n_de_template_data=fields.Binary(compute='_compute_l10n_de_template_data')
    l10n_de_document_title=fields.Char(compute='_compute_l10n_de_document_title')
    l10n_de_addresses=fields.Binary(compute='_compute_l10n_de_addresses')

    def_compute_l10n_de_template_data(self):
        forrecordinself:
            record.l10n_de_template_data=data=[]
            ifrecord.name:
                data.append((_("InvoiceNo."),record.name))
            ifrecord.invoice_date:
                data.append((_("InvoiceDate"),format_date(self.env,record.invoice_date)))
            ifrecord.invoice_date_due:
                data.append((_("DueDate"),format_date(self.env,record.invoice_date_due)))
            ifrecord.invoice_origin:
                data.append((_("Source"),record.invoice_origin))
            ifrecord.ref:
                data.append((_("Reference"),record.ref))

    def_compute_l10n_de_document_title(self):
        forrecordinself:
            record.l10n_de_document_title=''
            ifrecord.move_type=='out_invoice':
                ifrecord.state=='posted':
                    record.l10n_de_document_title=_('Invoice')
                elifrecord.state=='draft':
                    record.l10n_de_document_title=_('DraftInvoice')
                elifrecord.state=='cancel':
                    record.l10n_de_document_title=_('CancelledInvoice')
            elifrecord.move_type=='out_refund':
                record.l10n_de_document_title=_('CreditNote')
            elifrecord.move_type=='in_refund':
                record.l10n_de_document_title=_('VendorCreditNote')
            elifrecord.move_type=='in_invoice':
                record.l10n_de_document_title=_('VendorBill')

    def_compute_l10n_de_addresses(self):
        forrecordinself:
            record.l10n_de_addresses=data=[]
            if'partner_shipping_id'notinrecord._fields:
                data.append((_("InvoicingAddress:"),record.partner_id))
            elifrecord.partner_shipping_id==record.partner_id:
                data.append((_("InvoicingandShippingAddress:"),record.partner_shipping_id))
            elifrecord.move_typein("in_invoice","in_refund")ornotrecord.partner_shipping_id:
                data.append((_("InvoicingandShippingAddress:"),record.partner_id))
            else:
                data.append((_("ShippingAddress:"),record.partner_shipping_id))
                data.append((_("InvoicingAddress:"),record.partner_id))
