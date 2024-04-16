#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResCountry(models.Model):

    _inherit='res.country'

    l10n_ar_afip_code=fields.Char('AFIPCode',size=3,help='Thiscodewillbeusedonelectronicinvoice')
    l10n_ar_natural_vat=fields.Char(
        'NaturalPersonVAT',size=11,help="GenericVATnumberdefinedbyAFIPinordertorecognizepartnersfrom"
        "thiscountrythatarenaturalpersons")
    l10n_ar_legal_entity_vat=fields.Char(
        'LegalEntityVAT',size=11,help="GenericVATnumberdefinedbyAFIPinordertorecognizepartnersfromthis"
        "countrythatarelegalentity")
    l10n_ar_other_vat=fields.Char(
        'OtherVAT',size=11,help="GenericVATnumberdefinedbyAFIPinordertorecognizepartnersfromthis"
        "countrythatarenotnaturalpersonsorlegalentities")
