#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classUoM(models.Model):
    _inherit="uom.uom"

    #AsperGSTRulesyouneedtoSpecifyUQCgivenbyGST.
    l10n_in_code=fields.Char("IndianGSTUQC",help="UniqueQuantityCode(UQC)underGST")
