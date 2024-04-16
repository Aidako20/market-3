#-*-coding:utf-8-*-
fromflectraimportmodels


classAccountEdiXmlUBL21(models.AbstractModel):
    _name="account.edi.xml.ubl_21"
    _inherit='account.edi.xml.ubl_20'
    _description="UBL2.1"

    #-------------------------------------------------------------------------
    #EXPORT
    #-------------------------------------------------------------------------

    def_export_invoice_filename(self,invoice):
        returnf"{invoice.name.replace('/','_')}_ubl_21.xml"

    def_export_invoice_ecosio_schematrons(self):
        return{
            'invoice':'org.oasis-open:invoice:2.1',
            'credit_note':'org.oasis-open:creditnote:2.1',
        }

    def_export_invoice_vals(self,invoice):
        #EXTENDSaccount.edi.xml.ubl_20
        vals=super()._export_invoice_vals(invoice)

        vals.update({
            'InvoiceType_template':'account_edi_ubl_cii.ubl_21_InvoiceType',
            'InvoiceLineType_template':'account_edi_ubl_cii.ubl_21_InvoiceLineType',
        })

        vals['vals'].update({
            'ubl_version_id':2.1,
            'buyer_reference':invoice.commercial_partner_id.ref,
        })

        returnvals
