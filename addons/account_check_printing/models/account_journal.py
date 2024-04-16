#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre
fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportValidationError

classAccountJournal(models.Model):
    _inherit="account.journal"

    check_manual_sequencing=fields.Boolean(
        string='ManualNumbering',
        default=False,
        help="Checkthisoptionifyourpre-printedchecksarenotnumbered.",
    )
    check_sequence_id=fields.Many2one(
        comodel_name='ir.sequence',
        string='CheckSequence',
        readonly=True,
        copy=False,
        help="Checksnumberingsequence.",
    )
    check_next_number=fields.Char(
        string='NextCheckNumber',
        compute='_compute_check_next_number',
        inverse='_inverse_check_next_number',
        help="Sequencenumberofthenextprintedcheck.",
    )
    check_printing_payment_method_selected=fields.Boolean(
        compute='_compute_check_printing_payment_method_selected',
        help="Technicalfeatureusedtoknowwhethercheckprintingwasenabledaspaymentmethod.",
    )

    @api.depends('check_manual_sequencing')
    def_compute_check_next_number(self):
        forjournalinself:
            sequence=journal.check_sequence_id
            ifsequence:
                journal.check_next_number=sequence.get_next_char(sequence.number_next_actual)
            else:
                journal.check_next_number=1

    def_inverse_check_next_number(self):
        forjournalinself:
            ifjournal.check_next_numberandnotre.match(r'^[0-9]+$',journal.check_next_number):
                raiseValidationError(_('NextCheckNumbershouldonlycontainsnumbers.'))
            ifint(journal.check_next_number)<journal.check_sequence_id.number_next_actual:
                raiseValidationError(_(
                    "Thelastchecknumberwas%s.Inordertoavoidacheckbeingrejected"
                    "bythebank,youcanonlyuseagreaternumber.",
                    journal.check_sequence_id.number_next_actual
                ))
            ifjournal.check_sequence_id:
                journal.check_sequence_id.sudo().number_next_actual=int(journal.check_next_number)
                journal.check_sequence_id.sudo().padding=len(journal.check_next_number)

    @api.depends('type')
    def_compute_outbound_payment_method_ids(self):
        super()._compute_outbound_payment_method_ids()
        forjournalinself:
            ifjournal.type=='cash':
                check_method=self.env.ref('account_check_printing.account_payment_method_check')
                journal.outbound_payment_method_ids-=check_method

    @api.depends('outbound_payment_method_ids')
    def_compute_check_printing_payment_method_selected(self):
        forjournalinself:
            journal.check_printing_payment_method_selected=any(
                pm.code=='check_printing'
                forpminjournal.outbound_payment_method_ids
            )

    @api.model
    defcreate(self,vals):
        rec=super(AccountJournal,self).create(vals)
        ifnotrec.check_sequence_id:
            rec._create_check_sequence()
        returnrec

    def_create_check_sequence(self):
        """Createachecksequenceforthejournal"""
        forjournalinself:
            journal.check_sequence_id=self.env['ir.sequence'].sudo().create({
                'name':journal.name+_(":CheckNumberSequence"),
                'implementation':'no_gap',
                'padding':5,
                'number_increment':1,
                'company_id':journal.company_id.id,
            })

    def_default_outbound_payment_methods(self):
        methods=super(AccountJournal,self)._default_outbound_payment_methods()
        returnmethods+self.env.ref('account_check_printing.account_payment_method_check')

    @api.model
    def_enable_check_printing_on_bank_journals(self):
        """Enablescheckprintingpaymentmethodandaddachecksequenceonbankjournals.
            Calleduponmoduleinstallationviadatafile.
        """
        check_method=self.env.ref('account_check_printing.account_payment_method_check')
        forbank_journalinself.search([('type','=','bank')]):
            bank_journal._create_check_sequence()
            bank_journal.outbound_payment_method_ids+=check_method

    defget_journal_dashboard_datas(self):
        domain_checks_to_print=[
            ('journal_id','=',self.id),
            ('payment_method_id.code','=','check_printing'),
            ('state','=','posted'),
            ('is_move_sent','=',False),
        ]
        returndict(
            super(AccountJournal,self).get_journal_dashboard_datas(),
            num_checks_to_print=self.env['account.payment'].search_count(domain_checks_to_print),
        )

    defaction_checks_to_print(self):
        check_method=self.env.ref('account_check_printing.account_payment_method_check')
        return{
            'name':_('CheckstoPrint'),
            'type':'ir.actions.act_window',
            'view_mode':'list,form,graph',
            'res_model':'account.payment',
            'context':dict(
                self.env.context,
                search_default_checks_to_send=1,
                journal_id=self.id,
                default_journal_id=self.id,
                default_payment_type='outbound',
                default_payment_method_id=check_method.id,
            ),
        }
