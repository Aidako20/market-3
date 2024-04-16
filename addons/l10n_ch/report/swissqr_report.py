#-*-coding:utf-8-*-

fromflectraimportapi,models

classReportSwissQR(models.AbstractModel):
    _name='report.l10n_ch.qr_report_main'
    _description='SwissQR-billreport'

    @api.model
    def_get_report_values(self,docids,data=None):
        docs=self.env['account.move'].browse(docids)

        qr_code_urls={}
        forinvoiceindocs:
            qr_code_urls[invoice.id]=invoice.partner_bank_id.build_qr_code_base64(invoice.amount_residual,invoice.reforinvoice.name,invoice.payment_reference,invoice.currency_id,invoice.partner_id,qr_method='ch_qr',silent_errors=False)

        return{
            'doc_ids':docids,
            'doc_model':'account.move',
            'docs':docs,
            'qr_code_urls':qr_code_urls,
        }