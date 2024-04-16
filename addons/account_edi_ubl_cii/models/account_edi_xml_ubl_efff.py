#-*-coding:utf-8-*-

fromflectraimportmodels

importre


classAccountEdiXmlUBLEFFF(models.AbstractModel):
    _inherit="account.edi.xml.ubl_20"
    _name='account.edi.xml.ubl_efff'
    _description="E-FFF(BE)"

    #-------------------------------------------------------------------------
    #EXPORT
    #-------------------------------------------------------------------------

    def_export_invoice_filename(self,invoice):
        #officialnamingconvention
        vat=invoice.company_id.partner_id.commercial_partner_id.vat
        return'efff_%s%s%s.xml'%(vator'','_'ifvatelse'',re.sub(r'[\W_]','',invoice.name))

    def_export_invoice_ecosio_schematrons(self):
        returnNone
