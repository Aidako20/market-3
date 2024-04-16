fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classPosPaymentMethod(models.Model):
    """Usedtoclassifypos.payment.

    Genericcharacteristicsofapos.paymentisdescribedinthismodel.
    E.g.Acashpaymentcanbedescribedbyapos.payment.methodwith
    fields:is_cash_count=Trueandacash_journal_idsettoan
    `account.journal`(type='cash')record.

    Whenapos.payment.methodiscash,cash_journal_idisrequiredas
    itwillbethejournalwheretheaccount.bank.statement.linerecords
    willbecreated.
    """

    _name="pos.payment.method"
    _description="PointofSalePaymentMethods"
    _order="idasc"

    def_get_payment_terminal_selection(self):
        return[]

    name=fields.Char(string="PaymentMethod",required=True,translate=True)
    receivable_account_id=fields.Many2one('account.account',
        string='IntermediaryAccount',
        required=True,
        domain=[('reconcile','=',True),('user_type_id.type','=','receivable')],
        default=lambdaself:self.env.company.account_default_pos_receivable_account_id,
        ondelete='restrict',
        help='Accountusedascounterpartoftheincomeaccountintheaccountingentryrepresentingthepossales.')
    is_cash_count=fields.Boolean(string='Cash')
    cash_journal_id=fields.Many2one('account.journal',
        string='CashJournal',
        domain=[('type','=','cash')],
        ondelete='restrict',
        help='Thepaymentmethodisoftypecash.Acashstatementwillbeautomaticallygenerated.')
    split_transactions=fields.Boolean(
        string='SplitTransactions',
        default=False,
        help='Ifticked,eachpaymentwillgenerateaseparatedjournalitem.TickingthatoptionwillslowtheclosingofthePoS.')
    open_session_ids=fields.Many2many('pos.session',string='PosSessions',compute='_compute_open_session_ids',help='OpenPoSsessionsthatareusingthispaymentmethod.')
    config_ids=fields.Many2many('pos.config',string='PointofSaleConfigurations')
    company_id=fields.Many2one('res.company',string='Company',default=lambdaself:self.env.company)
    use_payment_terminal=fields.Selection(selection=lambdaself:self._get_payment_terminal_selection(),string='UseaPaymentTerminal',help='Recordpaymentswithaterminalonthisjournal.')
    hide_use_payment_terminal=fields.Boolean(compute='_compute_hide_use_payment_terminal',help='Technicalfieldwhichisusedto'
                                               'hideuse_payment_terminalwhennopaymentinterfacesareinstalled.')
    active=fields.Boolean(default=True)

    @api.depends('is_cash_count')
    def_compute_hide_use_payment_terminal(self):
        no_terminals=notbool(self._fields['use_payment_terminal'].selection(self))
        forpayment_methodinself:
            payment_method.hide_use_payment_terminal=no_terminalsorpayment_method.is_cash_count

    @api.onchange('use_payment_terminal')
    def_onchange_use_payment_terminal(self):
        """Usedbyinheritingmodeltounsetthevalueofthefieldrelatedtotheunselectedpaymentterminal."""
        pass

    @api.depends('config_ids')
    def_compute_open_session_ids(self):
        forpayment_methodinself:
            payment_method.open_session_ids=self.env['pos.session'].search([('config_id','in',payment_method.config_ids.ids),('state','!=','closed')])

    @api.onchange('is_cash_count')
    def_onchange_is_cash_count(self):
        ifnotself.is_cash_count:
            self.cash_journal_id=False
        else:
            self.use_payment_terminal=False

    def_is_write_forbidden(self,fields):
        returnbool(fieldsandself.open_session_ids)

    defwrite(self,vals):
        ifself._is_write_forbidden(set(vals.keys())):
            raiseUserError('PleasecloseandvalidatethefollowingopenPoSSessionsbeforemodifyingthispaymentmethod.\n'
                            'Opensessions:%s'%(''.join(self.open_session_ids.mapped('name')),))
        returnsuper(PosPaymentMethod,self).write(vals)
