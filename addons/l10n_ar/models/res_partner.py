#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models,api,_
fromflectra.exceptionsimportUserError,ValidationError
importstdnum.ar
importre
importlogging

_logger=logging.getLogger(__name__)


classResPartner(models.Model):

    _inherit='res.partner'

    l10n_ar_vat=fields.Char(
        compute='_compute_l10n_ar_vat',string="VAT",help='ComputedfieldthatreturnsVATornothingifthisone'
        'isnotsetforthepartner')
    l10n_ar_formatted_vat=fields.Char(
        compute='_compute_l10n_ar_formatted_vat',string="FormattedVAT",help='Computedfieldthatwillconvertthe'
        'givenVATnumbertotheformat{person_category:2}-{number:10}-{validation_number:1}')

    l10n_ar_gross_income_number=fields.Char('GrossIncomeNumber')
    l10n_ar_gross_income_type=fields.Selection(
        [('multilateral','Multilateral'),('local','Local'),('exempt','Exempt')],
        'GrossIncomeType',help='Typeofgrossincome:exempt,local,multilateral')
    l10n_ar_afip_responsibility_type_id=fields.Many2one(
        'l10n_ar.afip.responsibility.type',string='AFIPResponsibilityType',index=True,help='DefinedbyAFIPto'
        'identifythetypeofresponsibilitiesthatapersonoralegalentitycouldhaveandthatimpactsinthe'
        'typeofoperationsandrequirementstheyneed.')
    l10n_ar_special_purchase_document_type_ids=fields.Many2many(
        'l10n_latam.document.type','res_partner_document_type_rel','partner_id','document_type_id',
        string='OtherPurchaseDocuments',help='Sethereifthispartnercanissueotherdocumentsfurtherthan'
        'invoices,creditnotesanddebitnotes')

    @api.depends('l10n_ar_vat')
    def_compute_l10n_ar_formatted_vat(self):
        """ThiswilladdsomedashtotheCUITnumber(VATAR)inordertoshowinhisnaturalformat:
        {person_category}-{number}-{validation_number}"""
        recs_ar_vat=self.filtered('l10n_ar_vat')
        forrecinrecs_ar_vat:
            try:
                rec.l10n_ar_formatted_vat=stdnum.ar.cuit.format(rec.l10n_ar_vat)
            exceptExceptionaserror:
                rec.l10n_ar_formatted_vat=rec.l10n_ar_vat
                _logger.runbot("ArgentinianVATwasnotformatted:%s",repr(error))
        remaining=self-recs_ar_vat
        remaining.l10n_ar_formatted_vat=False

    @api.depends('vat','l10n_latam_identification_type_id')
    def_compute_l10n_ar_vat(self):
        """Weaddthiscomputedfieldthatreturnscuit(VATAR)ornothingifthisoneisnotsetforthepartner.
        ThisValidationcanbealsodonebycallingensure_vat()methodthatreturnsthecuit(VATAR)orerrorifthis
        oneisnotfound"""
        recs_ar_vat=self.filtered(lambdax:x.l10n_latam_identification_type_id.l10n_ar_afip_code=='80'andx.vat)
        forrecinrecs_ar_vat:
            rec.l10n_ar_vat=stdnum.ar.cuit.compact(rec.vat)
        remaining=self-recs_ar_vat
        remaining.l10n_ar_vat=False

    @api.constrains('vat','l10n_latam_identification_type_id')
    defcheck_vat(self):
        """SincewevalidatemoredocumentsthanthevatforArgentinianpartners(CUIT-VATAR,CUIL,DNI)we
        extendthismethodinordertoprocessit."""
        #NOTEbythemomentweincludetheCUIT(VATAR)validationalsoherebecauseweextendthemessages
        #errorstobemorefriendlytotheuser.InafuturewhenFlectraimprovethebase_vatmessageerrors
        #wecanchangethismethodandusethebase_vat.check_vat_armethod.s
        l10n_ar_partners=self.filtered(lambdax:x.l10n_latam_identification_type_id.l10n_ar_afip_code)
        l10n_ar_partners.l10n_ar_identification_validation()
        returnsuper(ResPartner,self-l10n_ar_partners).check_vat()

    @api.model
    def_commercial_fields(self):
        returnsuper()._commercial_fields()+['l10n_ar_afip_responsibility_type_id']

    defensure_vat(self):
        """ThismethodisahelperthatreturnstheVATnumberisthisoneisdefinedifnotraiseanUserError.

        VATisnotmandatoryfieldbutforsomeArgentinianoperationstheVATisrequired,foreg validatean
        electronicinvoice,buildareport,etc.

        ThismethodcanbeusedtovalidateistheVATisproperdefinedinthepartner"""
        self.ensure_one()
        ifnotself.l10n_ar_vat:
            raiseUserError(_('NoVATconfiguredforpartner[%i]%s')%(self.id,self.name))
        returnself.l10n_ar_vat

    def_get_validation_module(self):
        self.ensure_one()
        ifself.l10n_latam_identification_type_id.l10n_ar_afip_codein['80','86']:
            returnstdnum.ar.cuit
        elifself.l10n_latam_identification_type_id.l10n_ar_afip_code=='96':
            returnstdnum.ar.dni

    defl10n_ar_identification_validation(self):
        forrecinself.filtered('vat'):
            try:
                module=rec._get_validation_module()
            exceptExceptionaserror:
                module=False
                _logger.runbot("Argentiniandocumentwasnotvalidated:%s",repr(error))

            ifnotmodule:
                continue
            try:
                module.validate(rec.vat)
            exceptmodule.InvalidChecksum:
                raiseValidationError(_('Thevalidationdigitisnotvalidfor"%s"',rec.l10n_latam_identification_type_id.name))
            exceptmodule.InvalidLength:
                raiseValidationError(_('Invalidlengthfor"%s"',rec.l10n_latam_identification_type_id.name))
            exceptmodule.InvalidFormat:
                raiseValidationError(_('Onlynumbersallowedfor"%s"',rec.l10n_latam_identification_type_id.name))
            exceptExceptionaserror:
                raiseValidationError(repr(error))

    def_get_id_number_sanitize(self):
        """Sanitizetheidentificationnumber.Returnthedigits/integervalueoftheidentificationnumber
        Ifnotvatnumberdefinedreturn0"""
        self.ensure_one()
        ifnotself.vat:
            return0
        ifself.l10n_latam_identification_type_id.l10n_ar_afip_codein['80','86']:
            #Compactisthenumbercleanup,removeallseparatorsleaveonlydigits
            res=int(stdnum.ar.cuit.compact(self.vat))
        else:
            id_number=re.sub('[^0-9]','',self.vat)
            res=int(id_number)
        returnres
