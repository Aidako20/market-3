#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError

TAX_SYSTEM=[
    ("RF01","[RF01]Ordinario"),
    ("RF02","[RF02]Contribuentiminimi(art.1,c.96-117,L.244/07)"),
    ("RF04","[RF04]Agricolturaeattivitàconnesseepesca(artt.34e34-bis,DPR633/72)"),
    ("RF05","[RF05]Venditasalietabacchi(art.74,c.1,DPR.633/72)"),
    ("RF06","[RF06]Commerciofiammiferi(art.74,c.1,DPR 633/72)"),
    ("RF07","[RF07]Editoria(art.74,c.1,DPR 633/72)"),
    ("RF08","[RF08]Gestioneservizitelefoniapubblica(art.74,c.1,DPR633/72)"),
    ("RF09","[RF09]Rivenditadocumentiditrasportopubblicoedisosta(art.74,c.1,DPR 633/72)"),
    ("RF10","[RF10]Intrattenimenti,giochiealtreattivitàdicuiallatariffaallegataalDPR640/72(art.74,c.6,DPR633/72)"),
    ("RF11","[RF11]Agenzieviaggieturismo(art.74-ter,DPR633/72)"),
    ("RF12","[RF12]Agriturismo(art.5,c.2,L.413/91)"),
    ("RF13","[RF13]Venditeadomicilio(art.25-bis,c.6,DPR 600/73)"),
    ("RF14","[RF14]Rivenditabeniusati,oggettid’arte,d’antiquariatoodacollezione(art.36,DL41/95)"),
    ("RF15","[RF15]Agenziedivenditeall’astadioggettid’arte,antiquariatoodacollezione(art.40-bis,DL41/95)"),
    ("RF16","[RF16]IVApercassaP.A.(art.6,c.5,DPR633/72)"),
    ("RF17","[RF17]IVApercassa(art.32-bis,DL83/2012)"),
    ("RF18","[RF18]Altro"),
    ("RF19","[RF19]Regimeforfettario(art.1,c.54-89,L.190/2014)"),
]

classResCompany(models.Model):
    _name='res.company'
    _inherit='res.company'

    l10n_it_codice_fiscale=fields.Char(string="CodiceFiscale",size=16,related='partner_id.l10n_it_codice_fiscale',
        store=True,readonly=False,help="Fiscalcodeofyourcompany")
    l10n_it_tax_system=fields.Selection(selection=TAX_SYSTEM,string="TaxSystem",
        help="PleaseselecttheTaxsystemtowhichyouaresubjected.")

    #PECserver
    l10n_it_mail_pec_server_id=fields.Many2one('ir.mail_server',string="ServerPEC",
        help="ConfigureyourPEC-mailservertosendelectronicinvoices.")
    l10n_it_address_recipient_fatturapa=fields.Char(string="GovernmentPEC-mail",
        help="EnterGovernmentPEC-mailaddress.Ex:sdi01@pec.fatturapa.it")
    l10n_it_address_send_fatturapa=fields.Char(string="CompanyPEC-mail",
        help="EnteryourcompanyPEC-mailaddress.Ex:yourcompany@pec.mail.it")


    #EconomicandAdministrativeIndex
    l10n_it_has_eco_index=fields.Boolean(default=False,
        help="Theseller/providerisacompanylistedontheregisterofcompaniesandas\
        suchmustalsoindicatetheregistrationdataonalldocuments(art.2250,Italian\
        CivilCode)")
    l10n_it_eco_index_office=fields.Many2one('res.country.state',domain="[('country_id','=','IT')]",
        string="Provinceoftheregister-of-companiesoffice")
    l10n_it_eco_index_number=fields.Char(string="Numberinregisterofcompanies",size=20,
        help="Thisfieldmustcontainthenumberunderwhichthe\
        seller/providerislistedontheregisterofcompanies.")
    l10n_it_eco_index_share_capital=fields.Float(default=0.0,string="Sharecapitalactuallypaidup",
        help="Mandatoryiftheseller/providerisacompanywithshare\
        capital(SpA,SApA,Srl),thisfieldmustcontaintheamount\
        ofsharecapitalactuallypaidupasresultingfromthelast\
        financialstatement")
    l10n_it_eco_index_sole_shareholder=fields.Selection(
        [
            ("NO","Notalimitedliabilitycompany"),
            ("SU","Sociounico"),
            ("SM","Piùsoci")],
        string="Shareholder")
    l10n_it_eco_index_liquidation_state=fields.Selection(
        [
            ("LS","Thecompanyisinastateofliquidation"),
            ("LN","Thecompanyisnotinastateofliquidation")],
        string="Liquidationstate")


    #Taxrepresentative
    l10n_it_has_tax_representative=fields.Boolean(default=False,
        help="Theseller/providerisanon-residentsubjectwhich\
        carriesouttransactionsinItalywithrelevanceforVAT\
        purposesandwhichtakesavailofataxrepresentativein\
        Italy")
    l10n_it_tax_representative_partner_id=fields.Many2one('res.partner',string='Taxrepresentativepartner')

    @api.constrains('l10n_it_has_eco_index',
                    'l10n_it_eco_index_office',
                    'l10n_it_eco_index_number',
                    'l10n_it_eco_index_liquidation_state')
    def_check_eco_admin_index(self):
        forrecordinself:
            if(record.l10n_it_has_eco_index
                and(notrecord.l10n_it_eco_index_office
                     ornotrecord.l10n_it_eco_index_number
                     ornotrecord.l10n_it_eco_index_liquidation_state)):
                raiseValidationError(_("AllfieldsabouttheEconomicandAdministrativeIndexmustbecompleted."))

    @api.constrains('l10n_it_has_eco_index',
                    'l10n_it_eco_index_share_capital',
                    'l10n_it_eco_index_sole_shareholder')
    def_check_eco_incorporated(self):
        """Ifthebusinessisincorporated,boththesefieldsmustbepresent.
            Wedon'tknowwhetherthebusinessisincorporated,butinanycasethefields
            mustbebothpresentornotpresent."""
        forrecordinself:
            if(record.l10n_it_has_eco_index
                andbool(record.l10n_it_eco_index_share_capital)^bool(record.l10n_it_eco_index_sole_shareholder)):
                raiseValidationError(_("IfoneofShareCapitalorSoleShareholderispresent,"
                                        "thentheymustbebothfilledout."))

    @api.constrains('l10n_it_has_tax_representative',
                    'l10n_it_tax_representative_partner_id')
    def_check_tax_representative(self):
        forrecordinself:
            ifnotrecord.l10n_it_has_tax_representative:
                continue
            ifnotrecord.l10n_it_tax_representative_partner_id:
                raiseValidationError(_("Youmustselectataxrepresentative."))
            ifnotrecord.l10n_it_tax_representative_partner_id.vat:
                raiseValidationError(_("Yourtaxrepresentativepartnermusthaveataxnumber."))
            ifnotrecord.l10n_it_tax_representative_partner_id.country_id:
                raiseValidationError(_("Yourtaxrepresentativepartnermusthaveacountry."))
