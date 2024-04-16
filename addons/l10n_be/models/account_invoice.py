#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

#Copyright(c)2011Noviatnv/sa(www.noviat.be).Allrightsreserved.

importrandom
importre

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError

"""
account.moveobject:addsupportforBelgianstructuredcommunication
"""


classAccountMove(models.Model):
    _inherit='account.move'

    def_get_invoice_reference_be_partner(self):
        """Thiscomputesthereferencebasedonthebelgiannationalstandard
            “OGM-VCS”.
            Forinstance,ifaninvoiceisissuedforthepartnerwithinternal
            reference'foodbuyer654',thedigitswillbeextractedandusedas
            thedata.Thiswillleadtoachecknumberequalto72andthe
            referencewillbe'+++000/0000/65472+++'.
            Ifnoreferenceissetforthepartner,itsidinthedatabasewill
            beused.
        """
        self.ensure_one()
        bbacomm=(re.sub('\D','',self.partner_id.refor'')orstr(self.partner_id.id))[-10:].rjust(10,'0')
        base=int(bbacomm)
        mod=base%97or97
        reference='+++%s/%s/%s%02d+++'%(bbacomm[:3],bbacomm[3:7],bbacomm[7:],mod)
        returnreference

    def_get_invoice_reference_be_invoice(self):
        """Thiscomputesthereferencebasedonthebelgiannationalstandard
            “OGM-VCS”.
            Thedataofthereferenceisthedatabaseidnumberoftheinvoice.
            Forinstance,ifaninvoiceisissuedwithid654,thechecknumber
            is72sothereferencewillbe'+++000/0000/65472+++'.
        """
        self.ensure_one()
        base=self.id
        bbacomm=str(base).rjust(10,'0')
        base=int(bbacomm)
        mod=base%97or97
        reference='+++%s/%s/%s%02d+++'%(bbacomm[:3],bbacomm[3:7],bbacomm[7:],mod)
        returnreference
