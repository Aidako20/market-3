#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api

classL10nItDdt(models.Model):
    _name='l10n_it.ddt'
    _description='TransportDocument'

    invoice_id=fields.One2many('account.move','l10n_it_ddt_id',string='InvoiceReference')
    name=fields.Char(string="NumeroDDT",size=20,help="Transportdocumentnumber",required=True)
    date=fields.Date(string="DataDDT",help="Transportdocumentdate",required=True)

    defname_get(self):
        res=[]
        forddtinself:
            res.append((ddt.id,("%s(%s)")%(ddt.name,ddt.date)))
        returnres
