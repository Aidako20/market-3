#-*-coding:utf-8-*-
fromlxmlimportetree

fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportUserError


classAccountPaymentRegister(models.TransientModel):
    _name='account.payment.register'
    _description='RegisterPayment'

    #==Businessfields==
    payment_date=fields.Date(string="PaymentDate",required=True,
        default=fields.Date.context_today)
    amount=fields.Monetary(currency_field='currency_id',store=True,readonly=False,
        compute='_compute_amount')
    communication=fields.Char(string="Memo",store=True,readonly=False,
        compute='_compute_communication')
    group_payment=fields.Boolean(string="GroupPayments",store=True,readonly=False,
        compute='_compute_group_payment',
        help="Onlyonepaymentwillbecreatedbypartner(bank)/currency.")
    currency_id=fields.Many2one('res.currency',string='Currency',store=True,readonly=False,
        compute='_compute_currency_id',
        help="Thepayment'scurrency.")
    journal_id=fields.Many2one('account.journal',store=True,readonly=False,
        compute='_compute_journal_id',
        domain="[('company_id','=',company_id),('type','in',('bank','cash'))]")
    available_partner_bank_ids=fields.Many2many(
        comodel_name='res.partner.bank',
        compute='_compute_available_partner_bank_ids',
    )
    partner_bank_id=fields.Many2one(
        comodel_name='res.partner.bank',
        string="RecipientBankAccount",
        readonly=False,
        store=True,
        compute='_compute_partner_bank_id',
        domain="[('id','in',available_partner_bank_ids)]",
    )
    company_currency_id=fields.Many2one('res.currency',string="CompanyCurrency",
        related='company_id.currency_id')

    #==Fieldsgiventhroughthecontext==
    line_ids=fields.Many2many('account.move.line','account_payment_register_move_line_rel','wizard_id','line_id',
        string="Journalitems",readonly=True,copy=False,)
    payment_type=fields.Selection([
        ('outbound','SendMoney'),
        ('inbound','ReceiveMoney'),
    ],string='PaymentType',store=True,copy=False,
        compute='_compute_from_lines')
    partner_type=fields.Selection([
        ('customer','Customer'),
        ('supplier','Vendor'),
    ],store=True,copy=False,
        compute='_compute_from_lines')
    source_amount=fields.Monetary(
        string="AmounttoPay(companycurrency)",store=True,copy=False,
        currency_field='company_currency_id',
        compute='_compute_from_lines')
    source_amount_currency=fields.Monetary(
        string="AmounttoPay(foreigncurrency)",store=True,copy=False,
        currency_field='source_currency_id',
        compute='_compute_from_lines')
    source_currency_id=fields.Many2one('res.currency',
        string='SourceCurrency',store=True,copy=False,
        compute='_compute_from_lines',
        help="Thepayment'scurrency.")
    can_edit_wizard=fields.Boolean(store=True,copy=False,
        compute='_compute_from_lines',
        help="Technicalfieldusedtoindicatetheusercaneditthewizardcontentsuchastheamount.")
    can_group_payments=fields.Boolean(store=True,copy=False,
        compute='_compute_from_lines',
        help="Technicalfieldusedtoindicatetheusercanseethe'group_payments'box.")
    company_id=fields.Many2one('res.company',store=True,copy=False,
        compute='_compute_from_lines')
    partner_id=fields.Many2one('res.partner',
        string="Customer/Vendor",store=True,copy=False,ondelete='restrict',
        compute='_compute_from_lines')

    #==Paymentmethodsfields==
    payment_method_id=fields.Many2one('account.payment.method',string='PaymentMethod',
        readonly=False,store=True,
        compute='_compute_payment_method_id',
        domain="[('id','in',available_payment_method_ids)]",
        help="Manual:Getpaidbycash,checkoranyothermethodoutsideofFlectra.\n"\
        "Electronic:Getpaidautomaticallythroughapaymentacquirerbyrequestingatransactiononacardsavedbythecustomerwhenbuyingorsubscribingonline(paymenttoken).\n"\
        "Check:PaybillbycheckandprintitfromFlectra.\n"\
        "BatchDeposit:Encaseseveralcustomerchecksatoncebygeneratingabatchdeposittosubmittoyourbank.WhenencodingthebankstatementinFlectra,youaresuggestedtoreconcilethetransactionwiththebatchdeposit.Toenablebatchdeposit,moduleaccount_batch_paymentmustbeinstalled.\n"\
        "SEPACreditTransfer:PaybillfromaSEPACreditTransferfileyousubmittoyourbank.Toenablesepacredittransfer,moduleaccount_sepamustbeinstalled")
    available_payment_method_ids=fields.Many2many('account.payment.method',
        compute='_compute_payment_method_fields')
    hide_payment_method=fields.Boolean(
        compute='_compute_payment_method_fields',
        help="Technicalfieldusedtohidethepaymentmethodiftheselectedjournalhasonlyoneavailablewhichis'manual'")

    #==Paymentdifferencefields==
    payment_difference=fields.Monetary(
        compute='_compute_payment_difference')
    payment_difference_handling=fields.Selection([
        ('open','Keepopen'),
        ('reconcile','Markasfullypaid'),
    ],default='open',string="PaymentDifferenceHandling")
    writeoff_account_id=fields.Many2one('account.account',string="DifferenceAccount",copy=False,
        domain="[('deprecated','=',False),('company_id','=',company_id)]")
    writeoff_label=fields.Char(string='JournalItemLabel',default='Write-Off',
        help='Changelabelofthecounterpartthatwillholdthepaymentdifference')

    #==Displaypurposefields==
    show_partner_bank_account=fields.Boolean(
        compute='_compute_show_require_partner_bank',
        help="Technicalfieldusedtoknowwhetherthefield`partner_bank_id`needstobedisplayedornotinthepaymentsformviews")
    require_partner_bank_account=fields.Boolean(
        compute='_compute_show_require_partner_bank',
        help="Technicalfieldusedtoknowwhetherthefield`partner_bank_id`needstoberequiredornotinthepaymentsformviews")
    country_code=fields.Char(related='company_id.country_id.code',readonly=True)

    #-------------------------------------------------------------------------
    #HELPERS
    #-------------------------------------------------------------------------

    @api.model
    def_get_batch_communication(self,batch_result):
        '''Helpertocomputethecommunicationbasedonthebatch.
        :parambatch_result:   Abatchreturnedby'_get_batches'.
        :return:               Astringrepresentingacommunicationtobesetonpayment.
        '''
        labels=set(line.nameorline.move_id.reforline.move_id.nameforlineinbatch_result['lines'])
        return''.join(sorted(labels))

    @api.model
    def_get_batch_journal(self,batch_result):
        """Helpertocomputethejournalbasedonthebatch.

        :parambatch_result:   Abatchreturnedby'_get_batches'.
        :return:               Anaccount.journalrecord.
        """
        key_values=batch_result['key_values']
        foreign_currency_id=key_values['currency_id']
        partner_bank_id=key_values['partner_bank_id']

        currency_domain=[('currency_id','=',foreign_currency_id)]
        partner_bank_domain=[('bank_account_id','=',partner_bank_id)]

        default_domain=[
            ('type','in',('bank','cash')),
            ('company_id','=',batch_result['lines'].company_id.id),
        ]

        ifpartner_bank_id:
            extra_domains=(
                currency_domain+partner_bank_domain,
                partner_bank_domain,
                currency_domain,
                [],
            )
        else:
            extra_domains=(
                currency_domain,
                [],
            )

        forextra_domaininextra_domains:
            journal=self.env['account.journal'].search(default_domain+extra_domain,limit=1)
            ifjournal:
                returnjournal

        returnself.env['account.journal']

    @api.model
    def_get_batch_available_partner_banks(self,batch_result,journal):
        key_values=batch_result['key_values']
        company=batch_result['lines'].company_id

        #Aspecificbankaccountissetonthejournal.Theusermustusethisone.
        ifkey_values['payment_type']=='inbound':
            #Receivingmoneyonabankaccountlinkedtothejournal.
            returnjournal.bank_account_id
        else:
            #Sendingmoneytoabankaccountownedbyapartner.
            returnbatch_result['lines'].partner_id.bank_ids.filtered(lambdax:x.company_id.idin(False,company.id))._origin

    @api.model
    def_get_batch_available_payment_methods(self,journal,payment_type):
        ifpayment_type=='inbound':
            returnjournal.inbound_payment_method_ids._origin
        else:
            returnjournal.outbound_payment_method_ids._origin

    @api.model
    def_get_line_batch_key(self,line):
        '''Turnthelinepassedasparametertoadictionarydefiningonwhichwaythelines
        willbegroupedtogether.
        :return:Apythondictionary.
        '''
        move=line.move_id

        partner_bank_account=self.env['res.partner.bank']
        ifmove.is_invoice(include_receipts=True):
            partner_bank_account=move.partner_bank_id._origin

        return{
            'partner_id':line.partner_id.id,
            'account_id':line.account_id.id,
            'currency_id':line.currency_id.id,
            'partner_bank_id':partner_bank_account.id,
            'partner_type':'customer'ifline.account_internal_type=='receivable'else'supplier',
            'payment_type':'inbound'ifline.balance>0.0else'outbound',
        }

    def_get_batches(self):
        '''Grouptheaccount.move.linelinkedtothewizardtogether.
        :return:Alistofbatches,eachonecontaining:
            *key_values:  Thekeyasadictionaryusedtogroupthejournalitemstogether.
            *moves:       Anaccount.moverecordset.
        '''
        self.ensure_one()

        lines=self.line_ids._origin

        iflen(lines.company_id)>1:
            raiseUserError(_("Youcan'tcreatepaymentsforentriesbelongingtodifferentcompanies."))
        ifnotlines:
            raiseUserError(_("Youcan'topentheregisterpaymentwizardwithoutatleastonereceivable/payableline."))

        batches={}
        forlineinlines:
            batch_key=self._get_line_batch_key(line)

            serialized_key='-'.join(str(v)forvinbatch_key.values())
            batches.setdefault(serialized_key,{
                'key_values':batch_key,
                'lines':self.env['account.move.line'],
            })
            batches[serialized_key]['lines']+=line

        returnlist(batches.values())

    @api.model
    def_get_wizard_values_from_batch(self,batch_result):
        '''Extractvaluesfromthebatchpassedasparameter(see'_get_batches')
        tobemountedinthewizardview.
        :parambatch_result:   Abatchreturnedby'_get_batches'.
        :return:               Adictionarycontainingvalidfields
        '''
        key_values=batch_result['key_values']
        lines=batch_result['lines']
        company=lines[0].company_id

        source_amount=abs(sum(lines.mapped('amount_residual')))
        ifkey_values['currency_id']==company.currency_id.id:
            source_amount_currency=source_amount
        else:
            source_amount_currency=abs(sum(lines.mapped('amount_residual_currency')))

        return{
            'company_id':company.id,
            'partner_id':key_values['partner_id'],
            'partner_type':key_values['partner_type'],
            'payment_type':key_values['payment_type'],
            'source_currency_id':key_values['currency_id'],
            'source_amount':source_amount,
            'source_amount_currency':source_amount_currency,
        }

    #-------------------------------------------------------------------------
    #COMPUTEMETHODS
    #-------------------------------------------------------------------------

    @api.depends('line_ids')
    def_compute_from_lines(self):
        '''Loadinitialvaluesfromtheaccount.movespassedthroughthecontext.'''
        forwizardinself:
            batches=wizard._get_batches()
            batch_result=batches[0]
            wizard_values_from_batch=wizard._get_wizard_values_from_batch(batch_result)

            iflen(batches)==1:
                #==Singlebatchtobemountedontheview==
                wizard.update(wizard_values_from_batch)

                wizard.can_edit_wizard=True
                wizard.can_group_payments=len(batch_result['lines'])!=1
            else:
                #==Multiplebatches:Thewizardisnoteditable ==
                wizard.update({
                    'company_id':batches[0]['lines'][0].company_id.id,
                    'partner_id':False,
                    'partner_type':False,
                    'payment_type':wizard_values_from_batch['payment_type'],
                    'source_currency_id':False,
                    'source_amount':False,
                    'source_amount_currency':False,
                })

                wizard.can_edit_wizard=False
                wizard.can_group_payments=any(len(batch_result['lines'])!=1forbatch_resultinbatches)

    @api.depends('can_edit_wizard')
    def_compute_communication(self):
        #Thecommunicationcan'tbecomputedin'_compute_from_lines'because
        #it'sacomputeeditablefieldandthen,shouldbecomputedinaseparatedmethod.
        forwizardinself:
            ifwizard.can_edit_wizard:
                batches=wizard._get_batches()
                wizard.communication=wizard._get_batch_communication(batches[0])
            else:
                wizard.communication=False

    @api.depends('can_edit_wizard')
    def_compute_group_payment(self):
        forwizardinself:
            ifwizard.can_edit_wizard:
                batches=wizard._get_batches()
                wizard.group_payment=len(batches[0]['lines'].move_id)==1
            else:
                wizard.group_payment=False

    @api.depends('can_edit_wizard','company_id')
    def_compute_journal_id(self):
        forwizardinself:
            ifwizard.can_edit_wizard:
                batch=wizard._get_batches()[0]
                wizard.journal_id=wizard._get_batch_journal(batch)
            else:
                wizard.journal_id=self.env['account.journal'].search([
                    ('type','in',('bank','cash')),
                    ('company_id','=',wizard.company_id.id),
                ],limit=1)

    @api.depends('can_edit_wizard','journal_id')
    def_compute_available_partner_bank_ids(self):
        forwizardinself:
            ifwizard.can_edit_wizard:
                batch=wizard._get_batches()[0]
                wizard.available_partner_bank_ids=wizard._get_batch_available_partner_banks(batch,wizard.journal_id)
            else:
                wizard.available_partner_bank_ids=None

    @api.depends('journal_id','available_partner_bank_ids')
    def_compute_partner_bank_id(self):
        forwizardinself:
            ifwizard.can_edit_wizard:
                batch=wizard._get_batches()[0]
                partner_bank_id=batch['key_values']['partner_bank_id']
                available_partner_banks=wizard.available_partner_bank_ids._origin
                ifpartner_bank_idandpartner_bank_idinavailable_partner_banks.ids:
                    wizard.partner_bank_id=self.env['res.partner.bank'].browse(partner_bank_id)
                else:
                    wizard.partner_bank_id=available_partner_banks[:1]
            else:
                wizard.partner_bank_id=None

    @api.depends('journal_id')
    def_compute_currency_id(self):
        forwizardinself:
            wizard.currency_id=wizard.journal_id.currency_idorwizard.source_currency_idorwizard.company_id.currency_id

    @api.depends('payment_type',
                 'journal_id.inbound_payment_method_ids',
                 'journal_id.outbound_payment_method_ids')
    def_compute_payment_method_fields(self):
        forwizardinself:
            wizard.available_payment_method_ids=wizard._get_batch_available_payment_methods(wizard.journal_id,wizard.payment_type)
            wizard.hide_payment_method=len(wizard.available_payment_method_ids)==1andwizard.available_payment_method_ids.code=='manual'

    @api.depends('payment_type',
                 'journal_id.inbound_payment_method_ids',
                 'journal_id.outbound_payment_method_ids')
    def_compute_payment_method_id(self):
        forwizardinself:
            available_payment_methods=wizard._get_batch_available_payment_methods(wizard.journal_id,wizard.payment_type)
            ifavailable_payment_methods:
                wizard.payment_method_id=available_payment_methods[:1]
            else:
                wizard.payment_method_id=False

    @api.depends('payment_method_id')
    def_compute_show_require_partner_bank(self):
        """Computesifthedestinationbankaccountmustbedisplayedinthepaymentformview.Bydefault,it
        won'tbedisplayedbutsomemodulesmightchangethat,dependingonthepaymenttype."""
        forwizardinself:
            wizard.show_partner_bank_account=wizard.payment_method_id.codeinself.env['account.payment']._get_method_codes_using_bank_account()
            wizard.require_partner_bank_account=wizard.payment_method_id.codeinself.env['account.payment']._get_method_codes_needing_bank_account()

    @api.depends('source_amount','source_amount_currency','source_currency_id','company_id','currency_id','payment_date')
    def_compute_amount(self):
        forwizardinself:
            ifwizard.source_currency_id==wizard.currency_id:
                #Samecurrency.
                wizard.amount=wizard.source_amount_currency
            elifwizard.currency_id==wizard.company_id.currency_id:
                #Paymentexpressedonthecompany'scurrency.
                wizard.amount=wizard.source_amount
            else:
                #Foreigncurrencyonpaymentdifferentthantheonesetonthejournalentries.
                amount_payment_currency=wizard.company_id.currency_id._convert(wizard.source_amount,wizard.currency_id,wizard.company_id,wizard.payment_dateorfields.Date.today())
                wizard.amount=amount_payment_currency

    @api.depends('amount')
    def_compute_payment_difference(self):
        forwizardinself:
            ifwizard.source_currency_id==wizard.currency_id:
                #Samecurrency.
                wizard.payment_difference=wizard.source_amount_currency-wizard.amount
            elifwizard.currency_id==wizard.company_id.currency_id:
                #Paymentexpressedonthecompany'scurrency.
                wizard.payment_difference=wizard.source_amount-wizard.amount
            else:
                #Foreigncurrencyonpaymentdifferentthantheonesetonthejournalentries.
                amount_payment_currency=wizard.company_id.currency_id._convert(wizard.source_amount,wizard.currency_id,wizard.company_id,wizard.payment_dateorfields.Date.today())
                wizard.payment_difference=amount_payment_currency-wizard.amount

    #-------------------------------------------------------------------------
    #LOW-LEVELMETHODS
    #-------------------------------------------------------------------------

    @api.model
    deffields_view_get(self,view_id=None,view_type='form',toolbar=False,submenu=False):
        #OVERRIDEtoaddthe'available_partner_bank_ids'fielddynamicallyinsidetheview.
        #TOBEREMOVEDINMASTER
        res=super().fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)
        ifview_type=='form':
            form_view=self.env.ref('account.view_account_payment_register_form')
            tree=etree.fromstring(res['arch'])
            ifres.get('view_id')==form_view.idandlen(tree.xpath("//field[@name='available_partner_bank_ids']"))==0:
                #Don'tforcepeopletoupdatetheaccountmodule.
                arch_tree=etree.fromstring(form_view.arch)
                ifarch_tree.tag=='form':
                    arch_tree.insert(0,etree.Element('field',attrib={
                        'name':'available_partner_bank_ids',
                        'invisible':'1',
                    }))
                    form_view.sudo().write({'arch':etree.tostring(arch_tree,encoding='unicode')})
                    returnsuper().fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)

        returnres

    @api.model
    defdefault_get(self,fields_list):
        #OVERRIDE
        res=super().default_get(fields_list)

        if'line_ids'infields_listand'line_ids'notinres:

            #Retrievemovestopayfromthecontext.

            ifself._context.get('active_model')=='account.move':
                lines=self.env['account.move'].browse(self._context.get('active_ids',[])).line_ids
            elifself._context.get('active_model')=='account.move.line':
                lines=self.env['account.move.line'].browse(self._context.get('active_ids',[]))
            else:
                raiseUserError(_(
                    "Theregisterpaymentwizardshouldonlybecalledonaccount.moveoraccount.move.linerecords."
                ))

            if'journal_id'inresandnotself.env['account.journal'].browse(res['journal_id'])\
                    .filtered_domain([('company_id','=',lines.company_id.id),('type','in',('bank','cash'))]):
                #defaultcanbeinheritedfromthelistview,shouldbecomputedinstead
                delres['journal_id']

            #Keeplineshavingaresidualamounttopay.
            available_lines=self.env['account.move.line']
            forlineinlines:
                ifline.move_id.state!='posted':
                    raiseUserError(_("Youcanonlyregisterpaymentforpostedjournalentries."))

                ifline.account_internal_typenotin('receivable','payable'):
                    continue
                ifline.currency_id:
                    ifline.currency_id.is_zero(line.amount_residual_currency):
                        continue
                else:
                    ifline.company_currency_id.is_zero(line.amount_residual):
                        continue
                available_lines|=line

            #Check.
            ifnotavailable_lines:
                raiseUserError(_("Youcan'tregisterapaymentbecausethereisnothinglefttopayontheselectedjournalitems."))
            iflen(lines.company_id)>1:
                raiseUserError(_("Youcan'tcreatepaymentsforentriesbelongingtodifferentcompanies."))
            iflen(set(available_lines.mapped('account_internal_type')))>1:
                raiseUserError(_("Youcan'tregisterpaymentsforjournalitemsbeingeitherallinbound,eitheralloutbound."))

            res['line_ids']=[(6,0,available_lines.ids)]

        returnres

    #-------------------------------------------------------------------------
    #BUSINESSMETHODS
    #-------------------------------------------------------------------------

    def_create_payment_vals_from_wizard(self):
        payment_vals={
            'date':self.payment_date,
            'amount':self.amount,
            'payment_type':self.payment_type,
            'partner_type':self.partner_type,
            'ref':self.communication,
            'journal_id':self.journal_id.id,
            'currency_id':self.currency_id.id,
            'partner_id':self.partner_id.id,
            'partner_bank_id':self.partner_bank_id.id,
            'payment_method_id':self.payment_method_id.id,
            'destination_account_id':self.line_ids[0].account_id.id
        }

        ifnotself.currency_id.is_zero(self.payment_difference)andself.payment_difference_handling=='reconcile':
            payment_vals['write_off_line_vals']={
                'name':self.writeoff_label,
                'amount':self.payment_difference,
                'account_id':self.writeoff_account_id.id,
            }
        returnpayment_vals

    def_create_payment_vals_from_batch(self,batch_result):
        batch_values=self._get_wizard_values_from_batch(batch_result)

        ifbatch_values['payment_type']=='inbound':
            partner_bank_id=self.journal_id.bank_account_id.id
        else:
            partner_bank_id=batch_result['key_values']['partner_bank_id']

        payment_method=self.payment_method_id

        ifbatch_values['payment_type']!=payment_method.payment_type:
            payment_method=self._get_batch_available_payment_methods(self.journal_id,batch_values['payment_type'])[:1]

        return{
            'date':self.payment_date,
            'amount':batch_values['source_amount_currency'],
            'payment_type':batch_values['payment_type'],
            'partner_type':batch_values['partner_type'],
            'ref':self._get_batch_communication(batch_result),
            'journal_id':self.journal_id.id,
            'currency_id':batch_values['source_currency_id'],
            'partner_id':batch_values['partner_id'],
            'partner_bank_id':partner_bank_id,
            'payment_method_id':payment_method.id,
            'destination_account_id':batch_result['lines'][0].account_id.id
        }

    def_init_payments(self,to_process,edit_mode=False):
        """Createthepayments.

        :paramto_process: Alistofpythondictionary,oneforeachpaymenttocreate,containing:
                            *create_vals: Thevaluesusedforthe'create'method.
                            *to_reconcile:Thejournalitemstoperformthereconciliation.
                            *batch:       Apythondictcontainingeverythingyouwantaboutthesourcejournalitems
                                            towhichapaymentwillbecreated(see'_get_batches').
        :paramedit_mode:  Isthewizardineditionmode.
        """

        payments=self.env['account.payment'].create([x['create_vals']forxinto_process])

        forpayment,valsinzip(payments,to_process):
            vals['payment']=payment

            #Ifpaymentsaremadeusingacurrencydifferentthanthesourceone,ensurethebalancematchexactlyin
            #ordertofullypaidthesourcejournalitems.
            #Forexample,supposeanewcurrencyBhavingarate100:1regardingthecompanycurrencyA.
            #Ifyoutrytopay12.15Ausing0.12B,thecomputedbalancewillbe12.00Aforthepaymentinsteadof12.15A.
            ifedit_mode:
                lines=vals['to_reconcile']

                #Batchesaremadeusingthesamecurrencysomaking'lines.currency_id'isok.
                ifpayment.currency_id!=lines.currency_id:
                    liquidity_lines,counterpart_lines,writeoff_lines=payment._seek_for_lines()
                    source_balance=abs(sum(lines.mapped('amount_residual')))
                    ifliquidity_lines[0].balance:
                        payment_rate=liquidity_lines[0].amount_currency/liquidity_lines[0].balance
                    else:
                        payment_rate=0.0
                    source_balance_converted=abs(source_balance)*payment_rate

                    #Translatethebalanceintothepaymentcurrencyisordertobeabletocomparethem.
                    #Incaseinbothhavethesamevalue(12.15*0.01~=0.12inourexample),itmeanstheuser
                    #attempttofullypaidthesourcelinesandthen,weneedtomanuallyfixthemtogetaperfect
                    #match.
                    payment_balance=abs(sum(counterpart_lines.mapped('balance')))
                    payment_amount_currency=abs(sum(counterpart_lines.mapped('amount_currency')))
                    ifnotpayment.currency_id.is_zero(source_balance_converted-payment_amount_currency):
                        continue

                    delta_balance=source_balance-payment_balance

                    #Balancearealreadythesame.
                    ifself.company_currency_id.is_zero(delta_balance):
                        continue

                    #Fixthebalancebutmakesuretopeektheliquidityandcounterpartlinesfirst.
                    debit_lines=(liquidity_lines+counterpart_lines).filtered('debit')
                    credit_lines=(liquidity_lines+counterpart_lines).filtered('credit')

                    ifdebit_linesandcredit_lines:
                        payment.move_id.write({'line_ids':[
                            (1,debit_lines[0].id,{'debit':debit_lines[0].debit+delta_balance}),
                            (1,credit_lines[0].id,{'credit':credit_lines[0].credit+delta_balance}),
                        ]})
        returnpayments

    def_post_payments(self,to_process,edit_mode=False):
        """Postthenewlycreatedpayments.

        :paramto_process: Alistofpythondictionary,oneforeachpaymenttocreate,containing:
                            *create_vals: Thevaluesusedforthe'create'method.
                            *to_reconcile:Thejournalitemstoperformthereconciliation.
                            *batch:       Apythondictcontainingeverythingyouwantaboutthesourcejournalitems
                                            towhichapaymentwillbecreated(see'_get_batches').
        :paramedit_mode:  Isthewizardineditionmode.
        """
        payments=self.env['account.payment']
        forvalsinto_process:
            payments|=vals['payment']
        payments.action_post()

    def_reconcile_payments(self,to_process,edit_mode=False):
        """Reconcilethepayments.

        :paramto_process: Alistofpythondictionary,oneforeachpaymenttocreate,containing:
                            *create_vals: Thevaluesusedforthe'create'method.
                            *to_reconcile:Thejournalitemstoperformthereconciliation.
                            *batch:       Apythondictcontainingeverythingyouwantaboutthesourcejournalitems
                                            towhichapaymentwillbecreated(see'_get_batches').
        :paramedit_mode:  Isthewizardineditionmode.
        """
        domain=[
            ('parent_state','=','posted'),
            ('account_internal_type','in',('receivable','payable')),
            ('reconciled','=',False),
        ]
        forvalsinto_process:
            payment_lines=vals['payment'].line_ids.filtered_domain(domain)
            lines=vals['to_reconcile']

            foraccountinpayment_lines.account_id:
                (payment_lines+lines)\
                    .filtered_domain([('account_id','=',account.id),('reconciled','=',False)])\
                    .reconcile()

    def_create_payments(self):
        self.ensure_one()
        batches=self._get_batches()
        edit_mode=self.can_edit_wizardand(len(batches[0]['lines'])==1orself.group_payment)
        to_process=[]

        ifedit_mode:
            payment_vals=self._create_payment_vals_from_wizard()
            to_process.append({
                'create_vals':payment_vals,
                'to_reconcile':batches[0]['lines'],
                'batch':batches[0],
            })
        else:
            #Don'tgrouppayments:Createonebatchpermove.
            ifnotself.group_payment:
                new_batches=[]
                forbatch_resultinbatches:
                    forlineinbatch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'lines':line,
                        })
                batches=new_batches

            forbatch_resultinbatches:
                to_process.append({
                    'create_vals':self._create_payment_vals_from_batch(batch_result),
                    'to_reconcile':batch_result['lines'],
                    'batch':batch_result,
                })

        payments=self._init_payments(to_process,edit_mode=edit_mode)
        self._post_payments(to_process,edit_mode=edit_mode)
        self._reconcile_payments(to_process,edit_mode=edit_mode)
        returnpayments

    defaction_create_payments(self):
        payments=self._create_payments()

        ifself._context.get('dont_redirect_to_payments'):
            returnTrue

        action={
            'name':_('Payments'),
            'type':'ir.actions.act_window',
            'res_model':'account.payment',
            'context':{'create':False},
        }
        iflen(payments)==1:
            action.update({
                'view_mode':'form',
                'res_id':payments.id,
            })
        else:
            action.update({
                'view_mode':'tree,form',
                'domain':[('id','in',payments.ids)],
            })
        returnaction
