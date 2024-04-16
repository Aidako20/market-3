#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api,_
fromflectra.exceptionsimportValidationError,RedirectWarning


classAccountJournal(models.Model):

    _inherit="account.journal"

    l10n_ar_afip_pos_system=fields.Selection(
        selection='_get_l10n_ar_afip_pos_types_selection',string='AFIPPOSSystem')
    l10n_ar_afip_pos_number=fields.Integer(
        'AFIPPOSNumber',help='ThisisthepointofsalenumberassignedbyAFIPinordertogenerateinvoices')
    company_partner=fields.Many2one('res.partner',related='company_id.partner_id')
    l10n_ar_afip_pos_partner_id=fields.Many2one(
        'res.partner','AFIPPOSAddress',help='ThisistheaddressusedforinvoicereportsofthisPOS',
        domain="['|',('id','=',company_partner),'&',('id','child_of',company_partner),('type','!=','contact')]"
    )
    l10n_ar_share_sequences=fields.Boolean(
        'UnifiedBook',help='Usesamesequencefordocumentswiththesameletter')

    def_get_l10n_ar_afip_pos_types_selection(self):
        """Returnthelistofvaluesoftheselectionfield."""
        return[
            ('II_IM',_('Pre-printedInvoice')),
            ('RLI_RLM',_('OnlineInvoice')),
            ('BFERCEL',_('ElectronicFiscalBond-OnlineInvoice')),
            ('FEERCELP',_('ExportVoucher-BillingPlus')),
            ('FEERCEL',_('ExportVoucher-OnlineInvoice')),
            ('CPERCEL',_('ProductCoding-OnlineVoucher')),
        ]

    def_get_journal_letter(self,counterpart_partner=False):
        """RegardingtheAFIPresponsibilityofthecompanyandthetypeofjournal(sale/purchase),gettheallowed
        letters.Optionally,receivethecounterpartpartner(customer/supplier)andgettheallowedletterstowork
        withhim.Thismethodisusedtopopulatedocumenttypesonjournalsandalsotofilterdocumenttypeson
        specificinvoicesto/fromcustomer/supplier
        """
        self.ensure_one()
        letters_data={
            'issued':{
                '1':['A','B','E','M'],
                '3':[],
                '4':['C'],
                '5':[],
                '6':['C','E'],
                '9':['I'],
                '10':[],
                '13':['C','E'],
                '99':[]
            },
            'received':{
                '1':['A','B','C','E','M','I'],
                '3':['B','C','I'],
                '4':['B','C','I'],
                '5':['B','C','I'],
                '6':['A','B','C','I'],
                '9':['E'],
                '10':['E'],
                '13':['A','B','C','I'],
                '99':['B','C','I']
            },
        }
        ifnotself.company_id.l10n_ar_afip_responsibility_type_id:
            action=self.env.ref('base.action_res_company_form')
            msg=_('CannotcreatechartofaccountuntilyouconfigureyourcompanyAFIPResponsibilityandVAT.')
            raiseRedirectWarning(msg,action.id,_('GotoCompanies'))

        letters=letters_data['issued'ifself.type=='sale'else'received'][
            self.company_id.l10n_ar_afip_responsibility_type_id.code]
        ifcounterpart_partner:
            counterpart_letters=letters_data['issued'ifself.type=='purchase'else'received'].get(
                counterpart_partner.l10n_ar_afip_responsibility_type_id.code,[])
            letters=list(set(letters)&set(counterpart_letters))
        returnletters

    def_get_journal_codes(self):
        self.ensure_one()
        usual_codes=['1','2','3','6','7','8','11','12','13']
        mipyme_codes=['201','202','203','206','207','208','211','212','213']
        invoice_m_code=['51','52','53']
        receipt_m_code=['54']
        receipt_codes=['4','9','15']
        expo_codes=['19','20','21']
        ifself.type!='sale':
            return[]
        elifself.l10n_ar_afip_pos_system=='II_IM':
            #pre-printedinvoice
            returnusual_codes+receipt_codes+expo_codes+invoice_m_code+receipt_m_code
        elifself.l10n_ar_afip_pos_systemin['RAW_MAW','RLI_RLM']:
            #electronic/onlineinvoice
            returnusual_codes+receipt_codes+invoice_m_code+receipt_m_code+mipyme_codes
        elifself.l10n_ar_afip_pos_systemin['CPERCEL','CPEWS']:
            #invoicewithdetail
            returnusual_codes+invoice_m_code
        elifself.l10n_ar_afip_pos_systemin['BFERCEL','BFEWS']:
            #Bondsinvoice
            returnusual_codes+mipyme_codes
        elifself.l10n_ar_afip_pos_systemin['FEERCEL','FEEWS','FEERCELP']:
            returnexpo_codes

    @api.constrains('type','l10n_ar_afip_pos_system','l10n_ar_afip_pos_number','l10n_ar_share_sequences',
                    'l10n_latam_use_documents')
    def_check_afip_configurations(self):
        """Donotlettheuserupdatethejournalifitalreadycontainsconfirmedinvoices"""
        journals=self.filtered(lambdax:x.company_id.country_id.code=="AR"andx.typein['sale','purchase'])
        invoices=self.env['account.move'].search([('journal_id','in',journals.ids),('posted_before','=',True)],limit=1)
        ifinvoices:
            raiseValidationError(
                _("Youcannotchangethejournal'sconfigurationifitalreadyhasvalidatedinvoices")+'('
                +','.join(invoices.mapped('journal_id').mapped('name'))+')')

    @api.constrains('l10n_ar_afip_pos_number')
    def_check_afip_pos_number(self):
        to_review=self.filtered(
            lambdax:x.type=='sale'andx.l10n_latam_use_documentsand
            x.company_id.country_id.code=="AR")

        ifto_review.filtered(lambdax:x.l10n_ar_afip_pos_number==0):
            raiseValidationError(_('PleasedefineanAFIPPOSnumber'))

        ifto_review.filtered(lambdax:x.l10n_ar_afip_pos_number>99999):
            raiseValidationError(_('PleasedefineavalidAFIPPOSnumber(5digitsmax)'))

    @api.onchange('l10n_ar_afip_pos_system')
    def_onchange_l10n_ar_afip_pos_system(self):
        """On'Pre-printedInvoice'theusualistosharesequences.Onothertypes,donotshare"""
        self.l10n_ar_share_sequences=bool(self.l10n_ar_afip_pos_system=='II_IM')

    @api.onchange('l10n_ar_afip_pos_number','type')
    def_onchange_set_short_name(self):
        """WilldefinetheAFIPPOSAddressfielddomaintakingintoaccountthecompanyconfiguredinthejournal
        Theshortcodeofthejournalonlyadmit5characters,sodependingonthesizeofthepos_number(alsomax5)
        weaddornotaprefixtoidentifysalesjournal.
        """
        ifself.type=='sale'andself.l10n_ar_afip_pos_number:
            self.code="%05i"%self.l10n_ar_afip_pos_number
