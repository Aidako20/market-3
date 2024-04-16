#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,fields


classL10nCoDocumentType(models.Model):
    _inherit="l10n_latam.identification.type"

    l10n_co_document_code=fields.Char("DocumentCode")
