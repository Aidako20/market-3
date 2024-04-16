#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate,timedelta

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportValidationError


classFinancialYearOpeningWizard(models.TransientModel):
    _name='account.financial.year.op'
    _description='OpeningBalanceofFinancialYear'

    company_id=fields.Many2one(comodel_name='res.company',required=True)
    opening_move_posted=fields.Boolean(string='OpeningMovePosted',compute='_compute_opening_move_posted')
    opening_date=fields.Date(string='OpeningDate',required=True,related='company_id.account_opening_date',help="DatefromwhichtheaccountingismanagedinFlectra.Itisthedateoftheopeningentry.",readonly=False)
    fiscalyear_last_day=fields.Integer(related="company_id.fiscalyear_last_day",required=True,readonly=False,
                                         help="Thelastdayofthemonthwillbeusedifthechosendaydoesn'texist.")
    fiscalyear_last_month=fields.Selection(related="company_id.fiscalyear_last_month",readonly=False,
                                             required=True,
                                             help="Thelastdayofthemonthwillbeusedifthechosendaydoesn'texist.")

    @api.depends('company_id.account_opening_move_id')
    def_compute_opening_move_posted(self):
        forrecordinself:
            record.opening_move_posted=record.company_id.opening_move_posted()

    @api.constrains('fiscalyear_last_day','fiscalyear_last_month')
    def_check_fiscalyear(self):
        #Wetryifthedateexistsin2020,whichisaleapyear.
        #Wedonotdefinetheconstrainonres.company,sincetherecomputationoftherelated
        #fieldsisdoneonefieldatatime.
        forwizinself:
            try:
                date(2020,int(wiz.fiscalyear_last_month),wiz.fiscalyear_last_day)
            exceptValueError:
                raiseValidationError(
                    _('Incorrectfiscalyeardate:dayisoutofrangeformonth.Month:%s;Day:%s')%
                    (wiz.fiscalyear_last_month,wiz.fiscalyear_last_day)
                )

    defwrite(self,vals):
        #Amazingworkaround:non-storedrelatedfieldsoncompanyareaBADideasincethe3fields
        #mustfollowtheconstraint'_check_fiscalyear_last_day'.Thethingis,incaseofrelated
        #fields,theinversewriteisdoneonevalueatatime,andthustheconstraintisverified
        #onevalueatatime...soitislikelytofail.
        forwizinself:
            wiz.company_id.write({
                'fiscalyear_last_day':vals.get('fiscalyear_last_day')orwiz.company_id.fiscalyear_last_day,
                'fiscalyear_last_month':vals.get('fiscalyear_last_month')orwiz.company_id.fiscalyear_last_month,
                'account_opening_date':vals.get('opening_date')orwiz.company_id.account_opening_date,
            })
            wiz.company_id.account_opening_move_id.write({
                'date':fields.Date.from_string(vals.get('opening_date')orwiz.company_id.account_opening_date)-timedelta(days=1),
            })

        vals.pop('opening_date',None)
        vals.pop('fiscalyear_last_day',None)
        vals.pop('fiscalyear_last_month',None)
        returnsuper().write(vals)

    defaction_save_onboarding_fiscal_year(self):
        self.env.company.sudo().set_onboarding_step_done('account_setup_fy_data_state')


classSetupBarBankConfigWizard(models.TransientModel):
    _inherits={'res.partner.bank':'res_partner_bank_id'}
    _name='account.setup.bank.manual.config'
    _description='Banksetupmanualconfig'
    _check_company_auto=True

    res_partner_bank_id=fields.Many2one(comodel_name='res.partner.bank',ondelete='cascade',required=True)
    new_journal_name=fields.Char(default=lambdaself:self.linked_journal_id.name,inverse='set_linked_journal_id',required=True,help='WillbeusedtonametheJournalrelatedtothisbankaccount')
    linked_journal_id=fields.Many2one(string="Journal",
        comodel_name='account.journal',inverse='set_linked_journal_id',
        compute="_compute_linked_journal_id",check_company=True,
        domain="[('type','=','bank'),('bank_account_id','=',False),('company_id','=',company_id)]")
    bank_bic=fields.Char(related='bank_id.bic',readonly=False,string="Bic")
    num_journals_without_account=fields.Integer(default=lambdaself:self._number_unlinked_journal())

    def_number_unlinked_journal(self):
        returnself.env['account.journal'].search([('type','=','bank'),('bank_account_id','=',False),
                                                   ('id','!=',self.default_linked_journal_id())],count=True)

    @api.onchange('acc_number')
    def_onchange_acc_number(self):
        forrecordinself:
            record.new_journal_name=record.acc_number

    @api.model
    defcreate(self,vals):
        """Thiswizardisonlyusedtosetupanaccountforthecurrentactive
        company,sowealwaysinjectthecorrespondingpartnerwhencreating
        themodel.
        """
        vals['partner_id']=self.env.company.partner_id.id
        vals['new_journal_name']=vals['acc_number']

        #Ifnobankhasbeenselected,butwehaveabic,weareusingittofindorcreatethebank
        ifnotvals['bank_id']andvals['bank_bic']:
            vals['bank_id']=self.env['res.bank'].search([('bic','=',vals['bank_bic'])],limit=1).id\
                              orself.env['res.bank'].create({'name':vals['bank_bic'],'bic':vals['bank_bic']}).id

        returnsuper(SetupBarBankConfigWizard,self).create(vals)

    @api.onchange('linked_journal_id')
    def_onchange_new_journal_related_data(self):
        forrecordinself:
            ifrecord.linked_journal_id:
                record.new_journal_name=record.linked_journal_id.name

    @api.depends('journal_id') #Despiteitsname,journal_idisactuallyaOne2manyfield
    def_compute_linked_journal_id(self):
        forrecordinself:
            record.linked_journal_id=record.journal_idandrecord.journal_id[0]orrecord.default_linked_journal_id()

    defdefault_linked_journal_id(self):
        default=self.env['account.journal'].search([('type','=','bank'),('bank_account_id','=',False)],limit=1)
        returndefault[:1].id

    defset_linked_journal_id(self):
        """Calledwhensavingthewizard.
        """
        forrecordinself:
            selected_journal=record.linked_journal_id
            ifnotselected_journal:
                new_journal_code=self.env['account.journal'].get_next_bank_cash_default_code('bank',self.env.company)
                company=self.env.company
                selected_journal=self.env['account.journal'].create({
                    'name':record.new_journal_name,
                    'code':new_journal_code,
                    'type':'bank',
                    'company_id':company.id,
                    'bank_account_id':record.res_partner_bank_id.id,
                })
            else:
                selected_journal.bank_account_id=record.res_partner_bank_id.id
                selected_journal.name=record.new_journal_name

    defvalidate(self):
        """Calledbythevalidationbuttonofthiswizard.Servesasan
        extensionhookinaccount_bank_statement_import.
        """
        self.linked_journal_id.mark_bank_setup_as_done_action()
