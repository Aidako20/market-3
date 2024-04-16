#coding:utf-8
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classBank(models.Model):
    _inherit="res.bank"

    l10n_mx_edi_code=fields.Char(
        "ABMCode",
        help="Three-digitnumberassignedbytheABMtoidentifybanking"
        "institutions(ABMisanacronymforAsociacióndeBancosdeMéxico)")


classResPartnerBank(models.Model):
    _inherit="res.partner.bank"

    l10n_mx_edi_clabe=fields.Char(
        "CLABE",help="StandardizedbankingcipherforMexico.Moreinfo"
        "wikipedia.org/wiki/CLABE")
