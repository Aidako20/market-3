#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
importbase64


classAccountInvoiceSend(models.TransientModel):
    _inherit='account.invoice.send'
    _description='AccountInvoiceSend'

    edi_format_ids=fields.Many2many(related='invoice_ids.journal_id.edi_format_ids',string="Electronicinvoicing")
