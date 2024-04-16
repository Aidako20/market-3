#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.exceptionsimportValidationError
fromflectraimportmodels,fields,api,_
fromflectra.osvimportexpression

SII_VAT='60805000-0'


classAccountMove(models.Model):
    _inherit="account.move"

    l10n_latam_document_type_id_code=fields.Char(related='l10n_latam_document_type_id.code',string='DocType')
    partner_id_vat=fields.Char(related='partner_id.vat',string='VATNo')
    l10n_latam_internal_type=fields.Selection(
        related='l10n_latam_document_type_id.internal_type',string='L10nLatamInternalType')

    def_get_l10n_latam_documents_domain(self):
        self.ensure_one()
        ifself.journal_id.company_id.country_id!=self.env.ref('base.cl')ornot\
                self.journal_id.l10n_latam_use_documents:
            returnsuper()._get_l10n_latam_documents_domain()
        ifself.journal_id.type=='sale':
            domain=[('country_id.code','=','CL')]
            ifself.move_typein['in_invoice','out_invoice']:
                domain+=[('internal_type','in',['invoice','debit_note','invoice_in'])]
            elifself.move_typein['in_refund','out_refund']:
                domain+=[('internal_type','=','credit_note')]
            ifself.company_id.partner_id.l10n_cl_sii_taxpayer_type=='1':
                domain+=[('code','!=','71')] #CompanieswithVATAffecteddoesn'thave"BoletadehonorariosElectrónica"
            returndomain
        ifself.move_type=='in_refund':
            internal_types_domain=('internal_type','=','credit_note')
        else:
            internal_types_domain=('internal_type','in',['invoice','debit_note','invoice_in'])
        domain=[
            ('country_id.code','=','CL'),
            internal_types_domain,
        ]
        ifself.partner_id.l10n_cl_sii_taxpayer_type=='1'andself.partner_id_vat!='60805000-0':
            domain+=[('code','notin',['39','70','71','914','911'])]
        elifself.partner_id.l10n_cl_sii_taxpayer_type=='1'andself.partner_id_vat=='60805000-0':
            domain+=[('code','notin',['39','70','71'])]
        elifself.partner_id.l10n_cl_sii_taxpayer_type=='2':
            domain+=[('code','in',['70','71','56','61'])]
        elifself.partner_id.l10n_cl_sii_taxpayer_type=='3':
            domain+=[('code','in',['35','38','39','41','56','61'])]
        elifself.partner_id.country_id.code!='CL'orself.partner_id.l10n_cl_sii_taxpayer_type=='4':
            domain+=[('code','=','46')]
        else:
            domain+=[('code','in',[])]
        returndomain

    def_check_document_types_post(self):
        forrecinself.filtered(
                lambdar:r.company_id.country_id.code=="CL"and
                          r.journal_id.typein['sale','purchase']):
            tax_payer_type=rec.partner_id.l10n_cl_sii_taxpayer_type
            vat=rec.partner_id.vat
            country_id=rec.partner_id.country_id
            latam_document_type_code=rec.l10n_latam_document_type_id.code
            if(nottax_payer_typeornotvat)and(country_id.code=="CL"andlatam_document_type_code
                                                  andlatam_document_type_codenotin['35','38','39','41']):
                raiseValidationError(_('Taxpayertypeandvatnumberaremandatoryforthistypeof'
                                        'document.Pleasesetthecurrenttaxpayertypeofthiscustomer'))
            ifrec.journal_id.type=='sale'andrec.journal_id.l10n_latam_use_documents:
                ifcountry_id.code!="CL":
                    ifnot((tax_payer_type=='4'andlatam_document_type_codein['110','111','112'])or(
                            tax_payer_type=='3'andlatam_document_type_codein['39','41','61','56'])):
                        raiseValidationError(_(
                            'Documenttypesforforeigncustomersmustbeexporttype(codes110,111or112)oryou\
                            shoulddefinethecustomerasanendconsumerandusereceipts(codes39or41)'))
            ifrec.journal_id.type=='purchase'andrec.journal_id.l10n_latam_use_documents:
                ifvat!=SII_VATandlatam_document_type_code=='914':
                    raiseValidationError(_('TheDINdocumentisintendedtobeusedonlywithRUT60805000-0'
                                            '(TesoreríaGeneraldeLaRepública)'))
                ifnottax_payer_typeornotvat:
                    ifcountry_id.code=="CL"andlatam_document_type_codenotin[
                            '35','38','39','41']:
                        raiseValidationError(_('Taxpayertypeandvatnumberaremandatoryforthistypeof'
                                                'document.Pleasesetthecurrenttaxpayertypeofthissupplier'))
                iftax_payer_type=='2'andlatam_document_type_codenotin['70','71','56','61']:
                    raiseValidationError(_('Thetaxpayertypeofthissupplierisincorrectfortheselectedtype'
                                            'ofdocument.'))
                iftax_payer_typein['1','3']:
                    iflatam_document_type_codein['70','71']:
                        raiseValidationError(_('Thetaxpayertypeofthissupplierisnotentitledtodeliver'
                                                'feesdocuments'))
                    iflatam_document_type_codein['110','111','112']:
                        raiseValidationError(_('Thetaxpayertypeofthissupplierisnotentitledtodeliver'
                                                'importsdocuments'))
                if(tax_payer_type=='4'orcountry_id.code!="CL")andlatam_document_type_code!='46':
                    raiseValidationError(_('Youneedajournalwithouttheuseofdocumentsforforeign'
                                            'suppliers'))

    @api.onchange('journal_id')
    def_l10n_cl_onchange_journal(self):
        self.l10n_latam_document_type_id=False

    def_post(self,soft=True):
        self._check_document_types_post()
        returnsuper()._post(soft)

    def_l10n_cl_get_formatted_sequence(self,number=0):
        return'%s%06d'%(self.l10n_latam_document_type_id.doc_code_prefix,number)

    def_get_starting_sequence(self):
        """Ifusedocumentsthenwillcreateanewstartingsequenceusingthedocumenttypecodeprefixandthe
        journaldocumentnumberwitha6paddingnumber"""
        ifself.journal_id.l10n_latam_use_documentsandself.company_id.country_id.code=="CL":
            ifself.l10n_latam_document_type_id:
                returnself._l10n_cl_get_formatted_sequence()
        returnsuper()._get_starting_sequence()

    def_get_last_sequence_domain(self,relaxed=False):
        where_string,param=super(AccountMove,self)._get_last_sequence_domain(relaxed)
        ifself.company_id.country_id.code=="CL"andself.l10n_latam_use_documents:
            where_string=where_string.replace('journal_id=%(journal_id)sAND','')
            where_string+='ANDl10n_latam_document_type_id=%(l10n_latam_document_type_id)sAND'\
                            'company_id=%(company_id)sANDmove_typeIN(\'out_invoice\',\'out_refund\')'
            param['company_id']=self.company_id.idorFalse
            param['l10n_latam_document_type_id']=self.l10n_latam_document_type_id.idor0
        returnwhere_string,param

    def_get_name_invoice_report(self):
        self.ensure_one()
        ifself.l10n_latam_use_documentsandself.company_id.country_id.code=='CL':
            return'l10n_cl.report_invoice_document'
        returnsuper()._get_name_invoice_report()
