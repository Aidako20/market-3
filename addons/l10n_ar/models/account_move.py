#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportUserError,RedirectWarning,ValidationError
fromdateutil.relativedeltaimportrelativedelta
fromlxmlimportetree
importlogging
_logger=logging.getLogger(__name__)


classAccountMove(models.Model):

    _inherit='account.move'

    @api.model
    def_l10n_ar_get_document_number_parts(self,document_number,document_type_code):
        #importshipments
        ifdocument_type_codein['66','67']:
            pos=invoice_number='0'
        else:
            pos,invoice_number=document_number.split('-')
        return{'invoice_number':int(invoice_number),'point_of_sale':int(pos)}

    l10n_ar_afip_responsibility_type_id=fields.Many2one(
        'l10n_ar.afip.responsibility.type',string='AFIPResponsibilityType',help='DefinedbyAFIPto'
        'identifythetypeofresponsibilitiesthatapersonoralegalentitycouldhaveandthatimpactsinthe'
        'typeofoperationsandrequirementstheyneed.')

    l10n_ar_currency_rate=fields.Float(copy=False,digits=(16,6),readonly=True,string="CurrencyRate")

    #Mostlyusedonreports
    l10n_ar_afip_concept=fields.Selection(
        compute='_compute_l10n_ar_afip_concept',selection='_get_afip_invoice_concepts',string="AFIPConcept",
        help="Aconceptissuggestedregardingthetypeoftheproductsontheinvoicebutitisallowedtoforcea"
        "differenttypeifrequired.")
    l10n_ar_afip_service_start=fields.Date(string='AFIPServiceStartDate',readonly=True,states={'draft':[('readonly',False)]})
    l10n_ar_afip_service_end=fields.Date(string='AFIPServiceEndDate',readonly=True,states={'draft':[('readonly',False)]})

    @api.constrains('move_type','journal_id')
    def_check_moves_use_documents(self):
        """Donotlettocreatenotinvoicesentriesinjournalsthatusedocuments"""
        not_invoices=self.filtered(lambdax:x.company_id.country_id.code=="AR"andx.journal_id.typein['sale','purchase']andx.l10n_latam_use_documentsandnotx.is_invoice())
        ifnot_invoices:
            raiseValidationError(_("TheselectedJournalcan'tbeusedinthistransaction,pleaseselectonethatdoesn'tusedocumentsasthesearejustforInvoices."))

    @api.constrains('move_type','l10n_latam_document_type_id')
    def_check_invoice_type_document_type(self):
        """LATAMmoduledefinethatwearenotabletousedebit_noteorinvoicedocumenttypesinaninvoicerefunds,
        HoweverforArgentinianDocumentType's99(internaltype=invoice)weareabletousedinarefundinvoices.

        Inthismethodweexcludetheargentiniandocumentsthatcanbeusedasinvoiceandrefundfromthegeneric
        constraint"""
        docs_used_for_inv_and_ref=self.filtered(
            lambdax:x.country_code=='AR'and
            x.l10n_latam_document_type_id.codeinself._get_l10n_ar_codes_used_for_inv_and_ref()and
            x.move_typein['out_refund','in_refund'])

        super(AccountMove,self-docs_used_for_inv_and_ref)._check_invoice_type_document_type()

    def_get_afip_invoice_concepts(self):
        """Returnthelistofvaluesoftheselectionfield."""
        return[('1','Products/Definitiveexportofgoods'),('2','Services'),('3','ProductsandServices'),
                ('4','4-Other(export)')]

    @api.depends('invoice_line_ids','invoice_line_ids.product_id','invoice_line_ids.product_id.type','journal_id')
    def_compute_l10n_ar_afip_concept(self):
        recs_afip=self.filtered(lambdax:x.company_id.country_id.code=="AR"andx.l10n_latam_use_documents)
        forrecinrecs_afip:
            rec.l10n_ar_afip_concept=rec._get_concept()
        remaining=self-recs_afip
        remaining.l10n_ar_afip_concept=''

    def_get_concept(self):
        """Methodtogettheconceptoftheinvoiceconsideringthetypeoftheproductsontheinvoice"""
        self.ensure_one()
        invoice_lines=self.invoice_line_ids.filtered(lambdax:notx.display_type)
        product_types=set([x.product_id.typeforxininvoice_linesifx.product_id])
        consumable=set(['consu','product'])
        service=set(['service'])
        mixed=set(['consu','service','product'])
        #onexpoinvoiceyoucanmixservicesandproducts
        expo_invoice=self.l10n_latam_document_type_id.codein['19','20','21']

        #Defaultvalue"product"
        afip_concept='1'
        ifproduct_types==service:
            afip_concept='2'
        elifproduct_types-consumableandproduct_types-serviceandnotexpo_invoice:
            afip_concept='3'
        returnafip_concept

    @api.model
    def_get_l10n_ar_codes_used_for_inv_and_ref(self):
        """Listofdocumenttypesthatcanbeusedasaninvoiceandrefund.Thislistcanbeincreasedonceneeded
        anddemonstrated.Asfaraswe'vecheckeddocumenttypesofwsfev1don'tallownegativeamountsso,forexample
        document60and61couldnotbeusedasrefunds."""
        return['99','186','188','189']

    def_get_l10n_latam_documents_domain(self):
        self.ensure_one()
        domain=super()._get_l10n_latam_documents_domain()
        ifself.journal_id.company_id.country_id.code=="AR":
            letters=self.journal_id._get_journal_letter(counterpart_partner=self.partner_id.commercial_partner_id)
            domain+=['|',('l10n_ar_letter','=',False),('l10n_ar_letter','in',letters)]
            codes=self.journal_id._get_journal_codes()
            ifcodes:
                domain.append(('code','in',codes))
            ifself.move_type=='in_refund':
                domain=['|',('code','in',self._get_l10n_ar_codes_used_for_inv_and_ref())]+domain
        returndomain

    def_check_argentinian_invoice_taxes(self):

        #checkvatoncompaniesthatshasit(Responsableinscripto)
        forinvinself.filtered(lambdax:x.company_id.l10n_ar_company_requires_vat):
            purchase_aliquots='not_zero'
            #werequireasinglevatoneachinvoicelineexceptfromsomepurchasedocuments
            ifinv.move_typein['in_invoice','in_refund']andinv.l10n_latam_document_type_id.purchase_aliquots=='zero':
                purchase_aliquots='zero'
            forlineininv.mapped('invoice_line_ids').filtered(lambdax:x.display_typenotin('line_section','line_note')):
                vat_taxes=line.tax_ids.filtered(lambdax:x.tax_group_id.l10n_ar_vat_afip_code)
                iflen(vat_taxes)!=1:
                    raiseUserError(_('Thereshouldbeasingletaxfromthe"VAT"taxgroupperline,additto"%s".Ifyoualreadyhaveit,pleasecheckthetaxconfiguration,inadvancedoptions,inthecorrespondingfield"TaxGroup".')%line.name)

                elifpurchase_aliquots=='zero'andvat_taxes.tax_group_id.l10n_ar_vat_afip_code!='0':
                    raiseUserError(_('Oninvoiceid"%s"youmustuseVATNotApplicableoneveryline.') %inv.id)
                elifpurchase_aliquots=='not_zero'andvat_taxes.tax_group_id.l10n_ar_vat_afip_code=='0':
                    raiseUserError(_('Oninvoiceid"%s"youmustuseVATtaxesdifferentthanVATNotApplicable.') %inv.id)

    def_set_afip_service_dates(self):
        forrecinself.filtered(lambdam:m.invoice_dateandm.l10n_ar_afip_conceptin['2','3','4']):
            ifnotrec.l10n_ar_afip_service_start:
                rec.l10n_ar_afip_service_start=rec.invoice_date+relativedelta(day=1)
            ifnotrec.l10n_ar_afip_service_end:
                rec.l10n_ar_afip_service_end=rec.invoice_date+relativedelta(day=1,days=-1,months=+1)

    def_set_afip_responsibility(self):
        """Wesavetheinformationaboutthereceptorresponsabilityatthetimewevalidatetheinvoice,thisis
        necessarybecausetheusercanchangetheresponsabilityafterthatanytime"""
        forrecinself:
            rec.l10n_ar_afip_responsibility_type_id=rec.commercial_partner_id.l10n_ar_afip_responsibility_type_id.id

    def_set_afip_rate(self):
        """Wesetthel10n_ar_currency_ratevaluewiththeaccountingdate.Thisshouldbedone
        afterinvoicehasbeenpostedinordertohavetheproperaccountingdate"""
        forrecinself:
            ifrec.company_id.currency_id==rec.currency_id:
                rec.l10n_ar_currency_rate=1.0
            elifnotrec.l10n_ar_currency_rate:
                rec.l10n_ar_currency_rate=rec.currency_id._convert(
                    1.0,rec.company_id.currency_id,rec.company_id,rec.date,round=False)

    @api.onchange('partner_id')
    def_onchange_afip_responsibility(self):
        ifself.company_id.country_id.code=='AR'andself.l10n_latam_use_documentsandself.partner_id\
           andnotself.partner_id.l10n_ar_afip_responsibility_type_id:
            return{'warning':{
                'title':_('MissingPartnerConfiguration'),
                'message':_('PleaseconfiguretheAFIPResponsibilityfor"%s"inordertocontinue')%(
                    self.partner_id.name)}}

    @api.onchange('partner_id')
    def_onchange_partner_journal(self):
        """Thismethodisusedwhentheinvoiceiscreatedfromthesaleorsubscription"""
        expo_journals=['FEERCEL','FEEWS','FEERCELP']
        forrecinself.filtered(lambdax:x.company_id.country_id.code=="AR"andx.journal_id.type=='sale'
                                 andx.l10n_latam_use_documentsandx.partner_id.l10n_ar_afip_responsibility_type_id):
            res_code=rec.partner_id.l10n_ar_afip_responsibility_type_id.code
            domain=[('company_id','=',rec.company_id.id),('l10n_latam_use_documents','=',True),('type','=','sale')]
            journal=self.env['account.journal']
            msg=False
            ifres_codein['9','10']andrec.journal_id.l10n_ar_afip_pos_systemnotinexpo_journals:
                #ifpartnerisforeginandjournalisnotofexpo,wetrytochangetoexpojournal
                journal=journal.search(domain+[('l10n_ar_afip_pos_system','in',expo_journals)],limit=1)
                msg=_('Youaretryingtocreateaninvoiceforforeignpartnerbutyoudon\'thaveanexportationjournal')
            elifres_codenotin['9','10']andrec.journal_id.l10n_ar_afip_pos_systeminexpo_journals:
                #ifpartnerisNOTforeginandjournalisforexpo,wetrytochangetolocaljournal
                journal=journal.search(domain+[('l10n_ar_afip_pos_system','notin',expo_journals)],limit=1)
                msg=_('Youaretryingtocreateaninvoicefordomesticpartnerbutyoudon\'thaveadomesticmarketjournal')
            ifjournal:
                rec.journal_id=journal.id
            elifmsg:
                #Throwanerrortouserinordertoproperconfigurethejournalforthetypeofoperation
                action=self.env.ref('account.action_account_journal_form')
                raiseRedirectWarning(msg,action.id,_('GotoJournals'))

    def_post(self,soft=True):
        ar_invoices=self.filtered(lambdax:x.company_id.country_id.code=="AR"andx.l10n_latam_use_documents)
        #Wemakevalidationshereandnotwithaconstraintbecausewewantvalidationbeforesendingelectronic
        #dataonl10n_ar_edi
        ar_invoices._check_argentinian_invoice_taxes()
        posted=super()._post(soft=soft)

        posted_ar_invoices=posted&ar_invoices
        posted_ar_invoices._set_afip_responsibility()
        posted_ar_invoices._set_afip_rate()
        posted_ar_invoices._set_afip_service_dates()
        returnposted

    def_reverse_moves(self,default_values_list=None,cancel=False):
        ifnotdefault_values_list:
            default_values_list=[{}formoveinself]
        formove,default_valuesinzip(self,default_values_list):
            default_values.update({
                'l10n_ar_afip_service_start':move.l10n_ar_afip_service_start,
                'l10n_ar_afip_service_end':move.l10n_ar_afip_service_end,
            })
        returnsuper()._reverse_moves(default_values_list=default_values_list,cancel=cancel)

    @api.onchange('l10n_latam_document_type_id','l10n_latam_document_number')
    def_inverse_l10n_latam_document_number(self):
        super()._inverse_l10n_latam_document_number()

        to_review=self.filtered(
            lambdax:x.journal_id.type=='sale'andx.l10n_latam_document_type_idandx.l10n_latam_document_numberand
            (x.l10n_latam_manual_document_numberornotx.highest_name)
            andx.l10n_latam_document_type_id.country_id.code=='AR')
        forrecinto_review:
            number=rec.l10n_latam_document_type_id._format_document_number(rec.l10n_latam_document_number)
            current_pos=int(number.split("-")[0])
            ifcurrent_pos!=rec.journal_id.l10n_ar_afip_pos_number:
                invoices=self.search([('journal_id','=',rec.journal_id.id),('posted_before','=',True)],limit=1)
                #IfthereisnopostedbeforeinvoicestheusercanchangethePOSnumber(x.l10n_latam_document_number)
                if(notinvoices):
                    rec.journal_id.l10n_ar_afip_pos_number=current_pos
                    rec.journal_id._onchange_set_short_name()
                #Ifnot,avoidthattheuserchangethePOSnumber
                else:
                    raiseUserError(_('Thedocumentnumbercannotbechangedforthisjournal,youcanonlymodify'
                                      'thePOSnumberifthereisnotposted(orpostedbefore)invoices'))

    def_get_formatted_sequence(self,number=0):
        return"%s%05d-%08d"%(self.l10n_latam_document_type_id.doc_code_prefix,
                                 self.journal_id.l10n_ar_afip_pos_number,number)

    def_get_starting_sequence(self):
        """Ifusedocumentsthenwillcreateanewstartingsequenceusingthedocumenttypecodeprefixandthe
        journaldocumentnumberwitha8paddingnumber"""
        ifself.journal_id.l10n_latam_use_documentsandself.company_id.country_id.code=="AR":
            ifself.l10n_latam_document_type_id:
                returnself._get_formatted_sequence()
        returnsuper()._get_starting_sequence()

    def_get_last_sequence(self,relaxed=False,lock=True):
        """Ifusesharesequencesweneedtorecomputethesequencetoaddtheproperdocumentcodeprefix"""
        res=super()._get_last_sequence(relaxed=relaxed,lock=lock)
        ifresandself.journal_id.l10n_ar_share_sequencesandself.l10n_latam_document_type_id.doc_code_prefixnotinres:
            res=self._get_formatted_sequence(number=self._l10n_ar_get_document_number_parts(
                res.split()[-1],self.l10n_latam_document_type_id.code)['invoice_number'])
        returnres

    def_get_last_sequence_domain(self,relaxed=False):
        where_string,param=super(AccountMove,self)._get_last_sequence_domain(relaxed)
        ifself.company_id.country_id.code=="AR"andself.l10n_latam_use_documents:
            ifnotself.journal_id.l10n_ar_share_sequences:
                where_string+="ANDl10n_latam_document_type_id=%(l10n_latam_document_type_id)s"
                param['l10n_latam_document_type_id']=self.l10n_latam_document_type_id.idor0
            elifself.journal_id.l10n_ar_share_sequences:
                where_string+="ANDl10n_latam_document_type_idin%(l10n_latam_document_type_ids)s"
                param['l10n_latam_document_type_ids']=tuple(self.l10n_latam_document_type_id.search(
                    [('l10n_ar_letter','=',self.l10n_latam_document_type_id.l10n_ar_letter)]).ids)
        returnwhere_string,param

    def_l10n_ar_get_amounts(self,company_currency=False):
        """Methodusedtopreparedatatopresentamountsandtaxesrelatedamountswhencreatingan
        electronicinvoiceforargentinianandthetxtfilesfordigitalVATbooks.Onlytakeintoaccounttheargentiniantaxes"""
        self.ensure_one()
        amount_field=company_currencyand'balance'or'price_subtotal'
        #ifweusebalanceweneedtocorrectsign(onprice_subtotalispositiveforrefundsandinvoices)
        sign=-1if(company_currencyandself.is_inbound())else1

        #ifweareonadocumentthatworksinvoiceandrefundandit'sarefund,weneedtoexportitasnegative
        sign=-signifself.move_typein('out_refund','in_refund')and\
            self.l10n_latam_document_type_id.codeinself._get_l10n_ar_codes_used_for_inv_and_ref()elsesign

        tax_lines=self.line_ids.filtered('tax_line_id')
        vat_taxes=tax_lines.filtered(lambdar:r.tax_line_id.tax_group_id.l10n_ar_vat_afip_code)

        vat_taxable=self.env['account.move.line']
        forlineinself.invoice_line_ids:
            ifany(tax.tax_group_id.l10n_ar_vat_afip_codeandtax.tax_group_id.l10n_ar_vat_afip_codenotin['0','1','2']fortaxinline.tax_ids):
                vat_taxable|=line

        profits_tax_group=self.env.ref('l10n_ar.tax_group_percepcion_ganancias')
        return{'vat_amount':sign*sum(vat_taxes.mapped(amount_field)),
                #ForinvoicesofletterCshouldnotpassVAT
                'vat_taxable_amount':sign*sum(vat_taxable.mapped(amount_field))ifself.l10n_latam_document_type_id.l10n_ar_letter!='C'elseself.amount_untaxed,
                'vat_exempt_base_amount':sign*sum(self.invoice_line_ids.filtered(lambdax:x.tax_ids.filtered(lambday:y.tax_group_id.l10n_ar_vat_afip_code=='2')).mapped(amount_field)),
                'vat_untaxed_base_amount':sign*sum(self.invoice_line_ids.filtered(lambdax:x.tax_ids.filtered(lambday:y.tax_group_id.l10n_ar_vat_afip_code=='1')).mapped(amount_field)),
                #usedonFE
                'not_vat_taxes_amount':sign*sum((tax_lines-vat_taxes).mapped(amount_field)),
                #usedonBFE+TXT
                'iibb_perc_amount':sign*sum(tax_lines.filtered(lambdar:r.tax_line_id.tax_group_id.l10n_ar_tribute_afip_code=='07').mapped(amount_field)),
                'mun_perc_amount':sign*sum(tax_lines.filtered(lambdar:r.tax_line_id.tax_group_id.l10n_ar_tribute_afip_code=='08').mapped(amount_field)),
                'intern_tax_amount':sign*sum(tax_lines.filtered(lambdar:r.tax_line_id.tax_group_id.l10n_ar_tribute_afip_code=='04').mapped(amount_field)),
                'other_taxes_amount':sign*sum(tax_lines.filtered(lambdar:r.tax_line_id.tax_group_id.l10n_ar_tribute_afip_code=='99').mapped(amount_field)),
                'profits_perc_amount':sign*sum(tax_lines.filtered(lambdar:r.tax_line_id.tax_group_id==profits_tax_group).mapped(amount_field)),
                'vat_perc_amount':sign*sum(tax_lines.filtered(lambdar:r.tax_line_id.tax_group_id.l10n_ar_tribute_afip_code=='06').mapped(amount_field)),
                'other_perc_amount':sign*sum(tax_lines.filtered(lambdar:r.tax_line_id.tax_group_id.l10n_ar_tribute_afip_code=='09'andr.tax_line_id.tax_group_id!=profits_tax_group).mapped(amount_field)),
                }

    def_get_vat(self,company_currency=False):
        """AppliesonwsfewebserviceandintheVATdigitalbooks"""
        amount_field=company_currencyand'balance'or'price_subtotal'
        #ifweusebalanceweneedtocorrectsign(onprice_subtotalispositiveforrefundsandinvoices)
        sign=-1if(company_currencyandself.is_inbound())else1

        #ifweareonadocumentthatworksinvoiceandrefundandit'sarefund,weneedtoexportitasnegative
        sign=-signifself.move_typein('out_refund','in_refund')and\
            self.l10n_latam_document_type_id.codeinself._get_l10n_ar_codes_used_for_inv_and_ref()elsesign

        res=[]
        vat_taxable=self.env['account.move.line']
        #getallinvoicelinesthatarevattaxable
        forlineinself.line_ids:
            ifany(tax.tax_group_id.l10n_ar_vat_afip_codeandtax.tax_group_id.l10n_ar_vat_afip_codenotin['0','1','2']fortaxinline.tax_line_id)andline[amount_field]:
                vat_taxable|=line
        fortax_groupinvat_taxable.mapped('tax_group_id'):
            base_imp=sum(self.invoice_line_ids.filtered(lambdax:x.tax_ids.filtered(lambday:y.tax_group_id.l10n_ar_vat_afip_code==tax_group.l10n_ar_vat_afip_code)).mapped(amount_field))
            imp=sum(vat_taxable.filtered(lambdax:x.tax_group_id.l10n_ar_vat_afip_code==tax_group.l10n_ar_vat_afip_code).mapped(amount_field))
            res+=[{'Id':tax_group.l10n_ar_vat_afip_code,
                     'BaseImp':sign*base_imp,
                     'Importe':sign*imp}]

        #Reportvat0%
        vat_base_0=sign*sum(self.invoice_line_ids.filtered(lambdax:x.tax_ids.filtered(lambday:y.tax_group_id.l10n_ar_vat_afip_code=='3')).mapped(amount_field))
        ifvat_base_0:
            res+=[{'Id':'3','BaseImp':vat_base_0,'Importe':0.0}]

        returnresifreselse[]

    def_get_name_invoice_report(self):
        self.ensure_one()
        ifself.l10n_latam_use_documentsandself.company_id.country_id.code=='AR':
            return'l10n_ar.report_invoice_document'
        returnsuper()._get_name_invoice_report()
