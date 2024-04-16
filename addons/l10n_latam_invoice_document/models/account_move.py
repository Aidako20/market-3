#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportUserError,ValidationError
importre
fromflectra.tools.miscimportformatLang
fromflectra.tools.sqlimportcolumn_exists,create_column


classAccountMove(models.Model):

    _inherit="account.move"

    def_auto_init(self):
        #Skipthecomputationofthefield`l10n_latam_document_type_id`atthemoduleinstallation
        #Withoutthis,atthemoduleinstallation,
        #itwouldcall`_compute_l10n_latam_document_type`onallexistingrecords
        #whichcantakequiteawhileifyoualreadyhavealotofmoves.ItcanevenfailwithaMemoryError.
        #Inaddition,itsets`_compute_l10n_latam_document_type=False`onallrecords
        #becausethisfielddependsonthemany2many`l10n_latam_available_document_type_ids`,
        #whichreliesonhavingrecordsforthemodel`l10n_latam.document.type`
        #whichonlyhappensoncetheaccordinglocalizationmoduleisloaded.
        #Thelocalizationmoduleisloadedafterwards,becausethelocalizationmoduledependsonthismodule,
        #(e.g.`l10n_cl`dependson`l10n_latam_invoice_document`,andtherefore`l10n_cl`isloadedafter)
        #andthereforetherearenorecordsforthemodel`l10n_latam.document.type`atthetimethisfields
        #getscomputedoninstallation.Hence,allrecords'`_compute_l10n_latam_document_type`aresetto`False`.
        #Inaddition,multiplelocalizationmoduledependsonthismodule(e.g.`l10n_cl`,`l10n_ar`)
        #So,imagine`l10n_cl`getsinstalledfirst,andthen`l10n_ar`isinstallednext,
        #if`l10n_latam_document_type_id`neededtobecomputedoninstall,
        #theinstallof`l10n_cl`wouldcallthecomputemethod,
        #because`l10n_latam_invoice_document`wouldbeinstalledatthesametime,
        #butthen`l10n_ar`wouldmissit,because`l10n_latam_invoice_document`wouldalreadybeinstalled.
        #Besides,thisfieldiscomputedonlyfordraftsinvoices,asstatedinthecomputemethod:
        #`forrecinself.filtered(lambdax:x.state=='draft'):`
        #So,ifwewantthisfieldtobecomputedoninstall,itmustbedoneonlyondraftinvoices,andonlyonce
        #thelocalizationmodulesareloaded.
        #Itshouldbedoneinadedicatedpostinithook,
        #filteringcorrectlytheinvoicesforwhichitmustbecomputed.
        #ThoughIdon'tthinkthisisneeded.
        #Inpractical,it'sveryraretoalreadyhaveinvoices(draft,inaddition)
        #foraChilianorArgentiancompany(`res.company`)beforeinstalling`l10n_cl`or`l10n_ar`.
        ifnotcolumn_exists(self.env.cr,"account_move","l10n_latam_document_type_id"):
            create_column(self.env.cr,"account_move","l10n_latam_document_type_id","int4")
        returnsuper()._auto_init()

    l10n_latam_amount_untaxed=fields.Monetary(compute='_compute_l10n_latam_amount_and_taxes')
    l10n_latam_tax_ids=fields.One2many(compute="_compute_l10n_latam_amount_and_taxes",comodel_name='account.move.line')
    l10n_latam_available_document_type_ids=fields.Many2many('l10n_latam.document.type',compute='_compute_l10n_latam_available_document_types')
    l10n_latam_document_type_id=fields.Many2one(
        'l10n_latam.document.type',string='DocumentType',readonly=False,auto_join=True,index=True,
        states={'posted':[('readonly',True)]},compute='_compute_l10n_latam_document_type',store=True)
    l10n_latam_document_number=fields.Char(
        compute='_compute_l10n_latam_document_number',inverse='_inverse_l10n_latam_document_number',
        string='DocumentNumber',readonly=True,states={'draft':[('readonly',False)]})
    l10n_latam_use_documents=fields.Boolean(related='journal_id.l10n_latam_use_documents')
    l10n_latam_manual_document_number=fields.Boolean(compute='_compute_l10n_latam_manual_document_number',string='ManualNumber')

    @api.depends('l10n_latam_document_type_id')
    def_compute_name(self):
        """Changethewaythattheuse_documentmovesnameiscomputed:

        *Ifmoveusedocumentbutdoesnothavedocumenttypeselectedthenname='/'todonotshowthename.
        *Ifmoveusedocumentandarenumberedmanuallydonotcomputenameatall(willbesetmanually)
        *Ifmoveusedocumentandisindraftstateandhasnotbeenpostedbeforewerestartnameto'/'(thisis
           whenwechangethedocumenttype)"""
        without_doc_type=self.filtered(lambdax:x.journal_id.l10n_latam_use_documentsandnotx.l10n_latam_document_type_id)
        manual_documents=self.filtered(lambdax:x.journal_id.l10n_latam_use_documentsandx.l10n_latam_manual_document_number)
        (without_doc_type+manual_documents.filtered(lambdax:notx.nameorx.nameandx.state=='draft'andnotx.posted_before)).name='/'
        #ifwechangedocumentorjournalandweareindraftandnotposted,wecleannumbersothatisrecomputedinsuper
        self.filtered(
            lambdax:x.journal_id.l10n_latam_use_documentsandx.l10n_latam_document_type_id
            andnotx.l10n_latam_manual_document_numberandx.state=='draft'andnotx.posted_before).name='/'
        super(AccountMove,self-without_doc_type-manual_documents)._compute_name()

    @api.depends('l10n_latam_document_type_id','journal_id')
    def_compute_l10n_latam_manual_document_number(self):
        """Indicatesifthisdocumenttypeusesasequenceorifthenumberingismademanually"""
        recs_with_journal_id=self.filtered(lambdax:x.journal_idandx.journal_id.l10n_latam_use_documents)
        forrecinrecs_with_journal_id:
            rec.l10n_latam_manual_document_number=self._is_manual_document_number(rec.journal_id)
        remaining=self-recs_with_journal_id
        remaining.l10n_latam_manual_document_number=False

    def_is_manual_document_number(self,journal):
        returnTrueifjournal.type=='purchase'elseFalse

    @api.depends('name')
    def_compute_l10n_latam_document_number(self):
        recs_with_name=self.filtered(lambdax:x.name!='/')
        forrecinrecs_with_name:
            name=rec.name
            doc_code_prefix=rec.l10n_latam_document_type_id.doc_code_prefix
            ifdoc_code_prefixandname:
                name=name.split("",1)[-1]
            rec.l10n_latam_document_number=name
        remaining=self-recs_with_name
        remaining.l10n_latam_document_number=False

    @api.onchange('l10n_latam_document_type_id','l10n_latam_document_number')
    def_inverse_l10n_latam_document_number(self):
        forrecinself.filtered(lambdax:x.l10n_latam_document_type_id):
            ifnotrec.l10n_latam_document_number:
                rec.name='/'
            else:
                l10n_latam_document_number=rec.l10n_latam_document_type_id._format_document_number(rec.l10n_latam_document_number)
                ifrec.l10n_latam_document_number!=l10n_latam_document_number:
                    rec.l10n_latam_document_number=l10n_latam_document_number
                rec.name="%s%s"%(rec.l10n_latam_document_type_id.doc_code_prefix,l10n_latam_document_number)

    @api.depends('journal_id','l10n_latam_document_type_id')
    def_compute_highest_name(self):
        manual_records=self.filtered('l10n_latam_manual_document_number')
        manual_records.highest_name=''
        super(AccountMove,self-manual_records)._compute_highest_name()

    @api.model
    def_deduce_sequence_number_reset(self,name):
        ifself.l10n_latam_use_documents:
            return'never'
        returnsuper(AccountMove,self)._deduce_sequence_number_reset(name)

    def_get_starting_sequence(self):
        ifself.journal_id.l10n_latam_use_documents:
            ifself.l10n_latam_document_type_id:
                return"%s00000000"%(self.l10n_latam_document_type_id.doc_code_prefix)
            #Therewasnopatternfound,proposeone
            return""

        returnsuper(AccountMove,self)._get_starting_sequence()

    def_compute_l10n_latam_amount_and_taxes(self):
        recs_invoice=self.filtered(lambdax:x.is_invoice())
        forinvoiceinrecs_invoice:
            tax_lines=invoice.line_ids.filtered('tax_line_id')
            currencies=invoice.line_ids.filtered(lambdax:x.currency_id==invoice.currency_id).mapped('currency_id')
            included_taxes=invoice.l10n_latam_document_type_idand\
                invoice.l10n_latam_document_type_id._filter_taxes_included(tax_lines.mapped('tax_line_id'))
            ifnotincluded_taxes:
                l10n_latam_amount_untaxed=invoice.amount_untaxed
                not_included_invoice_taxes=tax_lines
            else:
                included_invoice_taxes=tax_lines.filtered(lambdax:x.tax_line_idinincluded_taxes)
                not_included_invoice_taxes=tax_lines-included_invoice_taxes
                ifinvoice.is_inbound():
                    sign=-1
                else:
                    sign=1
                amount='amount_currency'iflen(currencies)==1else'balance'
                l10n_latam_amount_untaxed=invoice.amount_untaxed+sign*sum(included_invoice_taxes.mapped(amount))
            invoice.l10n_latam_amount_untaxed=l10n_latam_amount_untaxed
            invoice.l10n_latam_tax_ids=not_included_invoice_taxes
        remaining=self-recs_invoice
        remaining.l10n_latam_amount_untaxed=False
        remaining.l10n_latam_tax_ids=[(5,0)]

    def_post(self,soft=True):
        forrecinself.filtered(lambdax:x.l10n_latam_use_documentsand(notx.nameorx.name=='/')):
            ifrec.move_typein('in_receipt','out_receipt'):
                raiseUserError(_('Wedonotaccepttheusageofdocumenttypesonreceiptsyet.'))
        returnsuper()._post(soft)

    @api.constrains('name','journal_id','state')
    def_check_unique_sequence_number(self):
        """Thisuniquenessverificationisonlyvalidforcustomerinvoices,andvendorbillsthatdoesnotuse
        documents.Anewconstraintmethod_check_unique_vendor_numberhasbeencreatedjustforvalidateforthispurpose"""
        vendor=self.filtered(lambdax:x.is_purchase_document()andx.l10n_latam_use_documents)
        returnsuper(AccountMove,self-vendor)._check_unique_sequence_number()

    @api.constrains('state','l10n_latam_document_type_id')
    def_check_l10n_latam_documents(self):
        """Thisconstraintchecksthatifainvoiceispostedanddoesnothaveadocumenttypeconfiguredwillraise
        anerror.Thisonlyappliestoinvoicesrelatedtojournalsthathasthe"UseDocuments"setasTrue.
        Andifthedocumenttypeissetthencheckiftheinvoicenumberhasbeenset,becauseapostedinvoice
        withoutadocumentnumberisnotvalidinthecasethattherelatedjournalshas"UseDocuemnts"setasTrue"""
        validated_invoices=self.filtered(lambdax:x.l10n_latam_use_documentsandx.state=='posted')
        without_doc_type=validated_invoices.filtered(lambdax:notx.l10n_latam_document_type_id)
        ifwithout_doc_type:
            raiseValidationError(_(
                'Thejournalrequireadocumenttypebutnotdocumenttypehasbeenselectedoninvoices%s.',
                without_doc_type.ids
            ))
        without_number=validated_invoices.filtered(
            lambdax:notx.l10n_latam_document_numberandx.l10n_latam_manual_document_number)
        ifwithout_number:
            raiseValidationError(_(
                'Pleasesetthedocumentnumberonthefollowinginvoices%s.',
                without_number.ids
            ))

    @api.constrains('move_type','l10n_latam_document_type_id')
    def_check_invoice_type_document_type(self):
        forrecinself.filtered('l10n_latam_document_type_id.internal_type'):
            internal_type=rec.l10n_latam_document_type_id.internal_type
            invoice_type=rec.move_type
            ifinternal_typein['debit_note','invoice']andinvoice_typein['out_refund','in_refund']:
                raiseValidationError(_('Youcannotusea%sdocumenttypewitharefundinvoice',internal_type))
            elifinternal_type=='credit_note'andinvoice_typein['out_invoice','in_invoice']:
                raiseValidationError(_('Youcannotusea%sdocumenttypewithainvoice',internal_type))

    def_get_l10n_latam_documents_domain(self):
        self.ensure_one()
        ifself.move_typein['out_refund','in_refund']:
            internal_types=['credit_note']
        else:
            internal_types=['invoice','debit_note']
        return[('internal_type','in',internal_types),('country_id','=',self.company_id.country_id.id)]

    @api.depends('journal_id','partner_id','company_id','move_type')
    def_compute_l10n_latam_available_document_types(self):
        self.l10n_latam_available_document_type_ids=False
        forrecinself.filtered(lambdax:x.journal_idandx.l10n_latam_use_documentsandx.partner_id):
            rec.l10n_latam_available_document_type_ids=self.env['l10n_latam.document.type'].search(rec._get_l10n_latam_documents_domain())

    @api.depends('l10n_latam_available_document_type_ids','debit_origin_id')
    def_compute_l10n_latam_document_type(self):
        debit_note=self.debit_origin_id
        forrecinself.filtered(lambdax:x.state=='draft'):
            document_types=rec.l10n_latam_available_document_type_ids._origin
            document_types=debit_noteanddocument_types.filtered(lambdax:x.internal_type=='debit_note')ordocument_types
            rec.l10n_latam_document_type_id=document_typesanddocument_types[0].id

    def_compute_invoice_taxes_by_group(self):
        report_or_portal_view='commit_assetsbundle'inself.env.contextor\
            notself.env.context.get('params',{}).get('view_type')=='form'
        ifnotreport_or_portal_view:
            returnsuper()._compute_invoice_taxes_by_group()

        move_with_doc_type=self.filtered('l10n_latam_document_type_id')
        formoveinmove_with_doc_type:
            lang_env=move.with_context(lang=move.partner_id.lang).env
            tax_lines=move.l10n_latam_tax_ids
            tax_balance_multiplicator=-1ifmove.is_inbound(True)else1
            res={}
            #Thereareasmanytaxlineastherearerepartitionlines
            done_taxes=set()
            forlineintax_lines:
                res.setdefault(line.tax_line_id.tax_group_id,{'base':0.0,'amount':0.0})
                res[line.tax_line_id.tax_group_id]['amount']+=tax_balance_multiplicator*(line.amount_currencyifline.currency_idelseline.balance)
                tax_key_add_base=tuple(move._get_tax_key_for_group_add_base(line))
                iftax_key_add_basenotindone_taxes:
                    ifline.currency_idandline.company_currency_idandline.currency_id!=line.company_currency_id:
                        amount=line.company_currency_id._convert(line.tax_base_amount,line.currency_id,line.company_id,line.dateorfields.Date.today())
                    else:
                        amount=line.tax_base_amount
                    res[line.tax_line_id.tax_group_id]['base']+=amount
                    #ThebaseshouldbeaddedONCE
                    done_taxes.add(tax_key_add_base)

            #Atthispointweonlywanttokeepthetaxeswithazeroamountsincetheydonot
            #generateataxline.
            zero_taxes=set()
            forlineinmove.line_ids:
                fortaxinline.l10n_latam_tax_ids.flatten_taxes_hierarchy():
                    iftax.tax_group_idnotinresortax.idinzero_taxes:
                        res.setdefault(tax.tax_group_id,{'base':0.0,'amount':0.0})
                        res[tax.tax_group_id]['base']+=tax_balance_multiplicator*(line.amount_currencyifline.currency_idelseline.balance)
                        zero_taxes.add(tax.id)

            res=sorted(res.items(),key=lambdal:l[0].sequence)
            move.amount_by_group=[(
                group.name,amounts['amount'],
                amounts['base'],
                formatLang(lang_env,amounts['amount'],currency_obj=move.currency_id),
                formatLang(lang_env,amounts['base'],currency_obj=move.currency_id),
                len(res),
                group.id
            )forgroup,amountsinres]
        super(AccountMove,self-move_with_doc_type)._compute_invoice_taxes_by_group()

    @api.constrains('name','partner_id','company_id','posted_before')
    def_check_unique_vendor_number(self):
        """Theconstraint_check_unique_sequence_numberisvalidforcustomerbillsbutnotvalidforusonvendor
        billsbecausetheuniquenessmustbeperpartner"""
        forrecinself.filtered(
                lambdax:x.nameandx.name!='/'andx.is_purchase_document()andx.l10n_latam_use_documents
                            andx.commercial_partner_id):
            domain=[
                ('move_type','=',rec.move_type),
                #byvalidatingnamewevalidatel10n_latam_document_type_id
                ('name','=',rec.name),
                ('company_id','=',rec.company_id.id),
                ('id','!=',rec.id),
                ('commercial_partner_id','=',rec.commercial_partner_id.id),
                #allowtohavetoequaliftheyarecancelled
                ('state','!=','cancel'),
            ]
            ifrec.search(domain):
                raiseValidationError(_('Vendorbillnumbermustbeuniquepervendorandcompany.'))
