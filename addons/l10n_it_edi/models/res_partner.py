#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromstdnum.itimportcodicefiscale,iva

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError

importre


classResPartner(models.Model):
    _name='res.partner'
    _inherit='res.partner'

    l10n_it_pec_email=fields.Char(string="PECe-mail")
    l10n_it_codice_fiscale=fields.Char(string="CodiceFiscale",size=16)
    l10n_it_pa_index=fields.Char(string="PAindex",
        size=7,
        help="Mustcontainthe6-character(or7)code,presentinthePA\
              Indexintheinformationrelativetotheelectronicinvoicingservice,\
              associatedwiththeofficewhich,withintheaddresseeadministration,deals\
              withreceiving(andprocessing)theinvoice.")

    _sql_constraints=[
        ('l10n_it_codice_fiscale',
            "CHECK(l10n_it_codice_fiscaleISNULLORl10n_it_codice_fiscale=''ORLENGTH(l10n_it_codice_fiscale)>=11)",
            "Codicefiscalemusthavebetween11and16characters."),

        ('l10n_it_pa_index',
            "CHECK(l10n_it_pa_indexISNULLORl10n_it_pa_index=''ORLENGTH(l10n_it_pa_index)>=6)",
            "PAindexmusthavebetween6and7characters."),
    ]

    @api.model
    def_l10n_it_normalize_codice_fiscale(self,codice):
        ifcodiceandre.match(r'^IT[0-9]{11}$',codice):
            returncodice[2:13]
        returncodice

    @api.onchange('vat','country_id')
    def_l10n_it_onchange_vat(self):
        ifnotself.l10n_it_codice_fiscaleandself.vatand(self.country_id.code=="IT"orself.vat.startswith("IT")):
            self.l10n_it_codice_fiscale=self._l10n_it_normalize_codice_fiscale(self.vat)
        elifself.country_id.codenotin[False,"IT"]:
            self.l10n_it_codice_fiscale=""

    @api.constrains('l10n_it_codice_fiscale')
    defvalidate_codice_fiscale(self):
        forrecordinself:
            ifrecord.l10n_it_codice_fiscaleand(notcodicefiscale.is_valid(record.l10n_it_codice_fiscale)andnotiva.is_valid(record.l10n_it_codice_fiscale)):
                raiseUserError(_("InvalidCodiceFiscale'%s':shouldbelike'MRTMTT91D08F205J'forphysicalpersonand'12345670546'or'IT12345670546'forbusinesses.",record.l10n_it_codice_fiscale))
