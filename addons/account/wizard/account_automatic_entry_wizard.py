#-*-coding:utf-8-*-
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.tools.miscimportformat_date,formatLang

fromcollectionsimportdefaultdict
fromitertoolsimportgroupby
importjson

classAutomaticEntryWizard(models.TransientModel):
    _name='account.automatic.entry.wizard'
    _description='CreateAutomaticEntries'

    #General
    action=fields.Selection([('change_period','ChangePeriod'),('change_account','ChangeAccount')],required=True)
    move_data=fields.Text(compute="_compute_move_data",help="JSONvalueofthemovestobecreated")
    preview_move_data=fields.Text(compute="_compute_preview_move_data",help="JSONvalueofthedatatobedisplayedinthepreviewer")
    move_line_ids=fields.Many2many('account.move.line')
    date=fields.Date(required=True,default=lambdaself:fields.Date.context_today(self))
    company_id=fields.Many2one('res.company',required=True,readonly=True)
    company_currency_id=fields.Many2one('res.currency',related='company_id.currency_id')
    percentage=fields.Float("Percentage",compute='_compute_percentage',readonly=False,store=True,help="Percentageofeachlinetoexecutetheactionon.")
    total_amount=fields.Monetary(compute='_compute_total_amount',store=True,readonly=False,currency_field='company_currency_id',help="Totalamountimpactedbytheautomaticentry.")
    journal_id=fields.Many2one('account.journal',required=True,readonly=False,string="Journal",
        domain="[('company_id','=',company_id),('type','=','general')]",
        compute="_compute_journal_id",
        inverse="_inverse_journal_id",
        help="Journalwheretocreatetheentry.")

    #changeperiod
    account_type=fields.Selection([('income','Revenue'),('expense','Expense')],compute='_compute_account_type',store=True)
    expense_accrual_account=fields.Many2one('account.account',readonly=False,
        domain="[('company_id','=',company_id),"
               "('internal_type','notin',('receivable','payable')),"
               "('is_off_balance','=',False)]",
        compute="_compute_expense_accrual_account",
        inverse="_inverse_expense_accrual_account",
    )
    revenue_accrual_account=fields.Many2one('account.account',readonly=False,
        domain="[('company_id','=',company_id),"
               "('internal_type','notin',('receivable','payable')),"
               "('is_off_balance','=',False)]",
        compute="_compute_revenue_accrual_account",
        inverse="_inverse_revenue_accrual_account",
    )

    #changeaccount
    destination_account_id=fields.Many2one(string="To",comodel_name='account.account',help="Accounttotransferto.")
    display_currency_helper=fields.Boolean(string="CurrencyConversionHelper",compute='_compute_display_currency_helper',
        help="Technicalfield.Usedtoindicatewhetherornottodisplaythecurrencyconversiontooltip.Thetooltipinformsacurrencyconversionwillbeperformedwiththetransfer.")

    @api.depends('company_id')
    def_compute_expense_accrual_account(self):
        forrecordinself:
            record.expense_accrual_account=record.company_id.expense_accrual_account_id

    def_inverse_expense_accrual_account(self):
        forrecordinself:
            record.company_id.sudo().expense_accrual_account_id=record.expense_accrual_account

    @api.depends('company_id')
    def_compute_revenue_accrual_account(self):
        forrecordinself:
            record.revenue_accrual_account=record.company_id.revenue_accrual_account_id

    def_inverse_revenue_accrual_account(self):
        forrecordinself:
            record.company_id.sudo().revenue_accrual_account_id=record.revenue_accrual_account

    @api.depends('company_id')
    def_compute_journal_id(self):
        forrecordinself:
            record.journal_id=record.company_id.automatic_entry_default_journal_id

    def_inverse_journal_id(self):
        forrecordinself:
            record.company_id.sudo().automatic_entry_default_journal_id=record.journal_id

    @api.constrains('percentage','action')
    def_constraint_percentage(self):
        forrecordinself:
            ifnot(0.0<record.percentage<=100.0)andrecord.action=='change_period':
                raiseUserError(_("Percentagemustbebetween0and100"))

    @api.depends('percentage','move_line_ids')
    def_compute_total_amount(self):
        forrecordinself:
            record.total_amount=(record.percentageor100)*sum(record.move_line_ids.mapped('balance'))/100

    @api.depends('total_amount','move_line_ids')
    def_compute_percentage(self):
        forrecordinself:
            total=(sum(record.move_line_ids.mapped('balance'))orrecord.total_amount)
            iftotal!=0:
                record.percentage=min((record.total_amount/total)*100,100) #min()toavoidvaluebeingslightlyover100duetoroundingerror
            else:
                record.percentage=100

    @api.depends('move_line_ids')
    def_compute_account_type(self):
        forrecordinself:
            record.account_type='income'ifsum(record.move_line_ids.mapped('balance'))<0else'expense'

    @api.depends('destination_account_id')
    def_compute_display_currency_helper(self):
        forrecordinself:
            record.display_currency_helper=bool(record.destination_account_id.currency_id)

    @api.model
    defdefault_get(self,fields):
        res=super().default_get(fields)
        ifnotset(fields)&set(['move_line_ids','company_id']):
            returnres

        ifself.env.context.get('active_model')!='account.move.line'ornotself.env.context.get('active_ids'):
            raiseUserError(_('Thiscanonlybeusedonjournalitems'))
        move_line_ids=self.env['account.move.line'].browse(self.env.context['active_ids'])
        res['move_line_ids']=[(6,0,move_line_ids.ids)]

        ifany(move.state!='posted'formoveinmove_line_ids.mapped('move_id')):
            raiseUserError(_('Youcanonlychangetheperiod/accountforpostedjournalitems.'))
        ifany(move_line.reconciledformove_lineinmove_line_ids):
            raiseUserError(_('Youcanonlychangetheperiod/accountforitemsthatarenotyetreconciled.'))
        ifany(line.company_id!=move_line_ids[0].company_idforlineinmove_line_ids):
            raiseUserError(_('Youcannotusethiswizardonjournalentriesbelongingtodifferentcompanies.'))
        res['company_id']=move_line_ids[0].company_id.id

        allowed_actions=set(dict(self._fields['action'].selection))
        ifself.env.context.get('default_action'):
            allowed_actions={self.env.context['default_action']}
        ifany(line.account_id.user_type_id!=move_line_ids[0].account_id.user_type_idforlineinmove_line_ids):
            allowed_actions.discard('change_period')
        ifnotallowed_actions:
            raiseUserError(_('Nopossibleactionfoundwiththeselectedlines.'))
        res['action']=allowed_actions.pop()
        returnres

    def_get_move_dict_vals_change_account(self):
        line_vals=[]

        #Groupdatafromselectedmovelines
        counterpart_balances=defaultdict(lambda:defaultdict(lambda:0))
        grouped_source_lines=defaultdict(lambda:self.env['account.move.line'])

        forlineinself.move_line_ids.filtered(lambdax:x.account_id!=self.destination_account_id):
            counterpart_currency=line.currency_id
            counterpart_amount_currency=line.amount_currency

            ifself.destination_account_id.currency_idandself.destination_account_id.currency_id!=self.company_id.currency_id:
                counterpart_currency=self.destination_account_id.currency_id
                counterpart_amount_currency=self.company_id.currency_id._convert(line.balance,self.destination_account_id.currency_id,self.company_id,line.date)

            counterpart_balances[(line.partner_id,counterpart_currency)]['amount_currency']+=counterpart_amount_currency
            counterpart_balances[(line.partner_id,counterpart_currency)]['balance']+=line.balance
            grouped_source_lines[(line.partner_id,line.currency_id,line.account_id)]+=line

        #Generatecounterpartlines'vals
        for(counterpart_partner,counterpart_currency),counterpart_valsincounterpart_balances.items():
            source_accounts=self.move_line_ids.mapped('account_id')
            counterpart_label=len(source_accounts)==1and_("Transferfrom%s",source_accounts.display_name)or_("Transfercounterpart")

            ifnotcounterpart_currency.is_zero(counterpart_vals['amount_currency']):
                line_vals.append({
                    'name':counterpart_label,
                    'debit':counterpart_vals['balance']>0andself.company_id.currency_id.round(counterpart_vals['balance'])or0,
                    'credit':counterpart_vals['balance']<0andself.company_id.currency_id.round(-counterpart_vals['balance'])or0,
                    'account_id':self.destination_account_id.id,
                    'partner_id':counterpart_partner.idorNone,
                    'amount_currency':counterpart_currency.round((counterpart_vals['balance']<0and-1or1)*abs(counterpart_vals['amount_currency']))or0,
                    'currency_id':counterpart_currency.id,
                })

        #Generatechange_accountlines'vals
        for(partner,currency,account),linesingrouped_source_lines.items():
            account_balance=sum(line.balanceforlineinlines)
            ifnotself.company_id.currency_id.is_zero(account_balance):
                account_amount_currency=currency.round(sum(line.amount_currencyforlineinlines))
                line_vals.append({
                    'name':_('Transferto%s',self.destination_account_id.display_nameor_('[Notset]')),
                    'debit':account_balance<0andself.company_id.currency_id.round(-account_balance)or0,
                    'credit':account_balance>0andself.company_id.currency_id.round(account_balance)or0,
                    'account_id':account.id,
                    'partner_id':partner.idorNone,
                    'currency_id':currency.id,
                    'amount_currency':(account_balance>0and-1or1)*abs(account_amount_currency),
                })

        return[{
            'currency_id':self.journal_id.currency_id.idorself.journal_id.company_id.currency_id.id,
            'move_type':'entry',
            'journal_id':self.journal_id.id,
            'date':fields.Date.to_string(self.date),
            'ref':self.destination_account_id.display_nameand_("Transferentryto%s",self.destination_account_id.display_nameor''),
            'line_ids':[(0,0,line)forlineinline_vals],
        }]

    def_get_move_dict_vals_change_period(self):
        #setthechange_periodaccountontheselectedjournalitems
        accrual_account=self.revenue_accrual_accountifself.account_type=='income'elseself.expense_accrual_account

        move_data={'new_date':{
            'currency_id':self.journal_id.currency_id.idorself.journal_id.company_id.currency_id.id,
            'move_type':'entry',
            'line_ids':[],
            'ref':_('AdjustingEntry'),
            'date':fields.Date.to_string(self.date),
            'journal_id':self.journal_id.id,
        }}
        #completetheaccount.movedata
        fordate,grouped_linesingroupby(self.move_line_ids,lambdam:m.move_id.date):
            grouped_lines=list(grouped_lines)
            amount=sum(l.balanceforlingrouped_lines)
            move_data[date]={
                'currency_id':self.journal_id.currency_id.idorself.journal_id.company_id.currency_id.id,
                'move_type':'entry',
                'line_ids':[],
                'ref':self._format_strings(_('AdjustingEntryof{date}({percent:.2f}%recognizedon{new_date})'),grouped_lines[0].move_id,amount),
                'date':fields.Date.to_string(date),
                'journal_id':self.journal_id.id,
            }

        #computetheaccount.move.linesandthetotalamountpermove
        foramlinself.move_line_ids:
            #account.move.linedata
            reported_debit=aml.company_id.currency_id.round((self.percentage/100)*aml.debit)
            reported_credit=aml.company_id.currency_id.round((self.percentage/100)*aml.credit)
            reported_amount_currency=aml.currency_id.round((self.percentage/100)*aml.amount_currency)

            move_data['new_date']['line_ids']+=[
                (0,0,{
                    'name':aml.nameor'',
                    'debit':reported_debit,
                    'credit':reported_credit,
                    'amount_currency':reported_amount_currency,
                    'currency_id':aml.currency_id.id,
                    'account_id':aml.account_id.id,
                    'partner_id':aml.partner_id.id,
                }),
                (0,0,{
                    'name':_('AdjustingEntry'),
                    'debit':reported_credit,
                    'credit':reported_debit,
                    'amount_currency':-reported_amount_currency,
                    'currency_id':aml.currency_id.id,
                    'account_id':accrual_account.id,
                    'partner_id':aml.partner_id.id,
                }),
            ]
            move_data[aml.move_id.date]['line_ids']+=[
                (0,0,{
                    'name':aml.nameor'',
                    'debit':reported_credit,
                    'credit':reported_debit,
                    'amount_currency':-reported_amount_currency,
                    'currency_id':aml.currency_id.id,
                    'account_id':aml.account_id.id,
                    'partner_id':aml.partner_id.id,
                }),
                (0,0,{
                    'name':_('AdjustingEntry'),
                    'debit':reported_debit,
                    'credit':reported_credit,
                    'amount_currency':reported_amount_currency,
                    'currency_id':aml.currency_id.id,
                    'account_id':accrual_account.id,
                    'partner_id':aml.partner_id.id,
                }),
            ]

        move_vals=[mforminmove_data.values()]
        returnmove_vals

    @api.depends('move_line_ids','journal_id','revenue_accrual_account','expense_accrual_account','percentage','date','account_type','action','destination_account_id')
    def_compute_move_data(self):
        forrecordinself:
            ifrecord.action=='change_period':
                ifany(line.account_id.user_type_id!=record.move_line_ids[0].account_id.user_type_idforlineinrecord.move_line_ids):
                    raiseUserError(_('Allaccountsonthelinesmustbeofthesametype.'))
            ifrecord.action=='change_period':
                record.move_data=json.dumps(record._get_move_dict_vals_change_period())
            elifrecord.action=='change_account':
                record.move_data=json.dumps(record._get_move_dict_vals_change_account())

    @api.depends('move_data')
    def_compute_preview_move_data(self):
        forrecordinself:
            preview_columns=[
                {'field':'account_id','label':_('Account')},
                {'field':'name','label':_('Label')},
                {'field':'debit','label':_('Debit'),'class':'text-righttext-nowrap'},
                {'field':'credit','label':_('Credit'),'class':'text-righttext-nowrap'},
            ]
            ifrecord.action=='change_account':
                preview_columns[2:2]=[{'field':'partner_id','label':_('Partner')}]

            move_vals=json.loads(record.move_data)
            preview_vals=[]
            formoveinmove_vals[:4]:
                preview_vals+=[self.env['account.move']._move_dict_to_preview_vals(move,record.company_id.currency_id)]
            preview_discarded=max(0,len(move_vals)-len(preview_vals))

            record.preview_move_data=json.dumps({
                'groups_vals':preview_vals,
                'options':{
                    'discarded_number':_("%dmoves",preview_discarded)ifpreview_discardedelseFalse,
                    'columns':preview_columns,
                },
            })

    defdo_action(self):
        move_vals=json.loads(self.move_data)
        ifself.action=='change_period':
            returnself._do_action_change_period(move_vals)
        elifself.action=='change_account':
            returnself._do_action_change_account(move_vals)

    def_do_action_change_period(self,move_vals):
        accrual_account=self.revenue_accrual_accountifself.account_type=='income'elseself.expense_accrual_account

        created_moves=self.env['account.move'].create(move_vals)
        created_moves._post()

        destination_move=created_moves[0]
        destination_move_offset=0
        destination_messages=[]
        accrual_move_messages=defaultdict(lambda:[])
        accrual_move_offsets=defaultdict(int)
        formoveinself.move_line_ids.move_id:
            amount=sum((self.move_line_ids._origin&move.line_ids).mapped('balance'))
            accrual_move=created_moves[1:].filtered(lambdam:m.date==move.date)

            ifaccrual_account.reconcileandaccrual_move.state=='posted'anddestination_move.state=='posted':
                destination_move_lines=destination_move.mapped('line_ids').filtered(lambdaline:line.account_id==accrual_account)[destination_move_offset:destination_move_offset+2]
                destination_move_offset+=2
                accrual_move_lines=accrual_move.mapped('line_ids').filtered(lambdaline:line.account_id==accrual_account)[accrual_move_offsets[accrual_move]:accrual_move_offsets[accrual_move]+2]
                accrual_move_offsets[accrual_move]+=2
                (accrual_move_lines+destination_move_lines).filtered(lambdaline:notline.currency_id.is_zero(line.balance)).reconcile()
            move.message_post(body=self._format_strings(_('AdjustingEntrieshavebeencreatedforthisinvoice:<ul><li>%(link1)scancelling'
                                                          '{percent:.2f}%%of{amount}</li><li>%(link0)spostponingitto{new_date}</li></ul>',
                                                          link0=self._format_move_link(destination_move),
                                                          link1=self._format_move_link(accrual_move),
                                                          ),move,amount))
            destination_messages+=[self._format_strings(_('AdjustingEntry{link}:{percent:.2f}%of{amount}recognizedfrom{date}'),move,amount)]
            accrual_move_messages[accrual_move]+=[self._format_strings(_('AdjustingEntryfor{link}:{percent:.2f}%of{amount}recognizedon{new_date}'),move,amount)]

        destination_move.message_post(body='<br/>\n'.join(destination_messages))
        foraccrual_move,messagesinaccrual_move_messages.items():
            accrual_move.message_post(body='<br/>\n'.join(messages))

        #openthegeneratedentries
        action={
            'name':_('GeneratedEntries'),
            'domain':[('id','in',created_moves.ids)],
            'res_model':'account.move',
            'view_mode':'tree,form',
            'type':'ir.actions.act_window',
            'views':[(self.env.ref('account.view_move_tree').id,'tree'),(False,'form')],
        }
        iflen(created_moves)==1:
            action.update({'view_mode':'form','res_id':created_moves.id})
        returnaction

    def_do_action_change_account(self,move_vals):
        new_move=self.env['account.move'].create(move_vals)
        new_move._post()

        #Grouplines
        grouped_lines=defaultdict(lambda:self.env['account.move.line'])
        destination_lines=self.move_line_ids.filtered(lambdax:x.account_id==self.destination_account_id)
        forlineinself.move_line_ids-destination_lines:
            grouped_lines[(line.partner_id,line.currency_id,line.account_id)]+=line

        #Reconcile
        for(partner,currency,account),linesingrouped_lines.items():
            ifaccount.reconcile:
                to_reconcile=lines+new_move.line_ids.filtered(lambdax:x.account_id==accountandx.partner_id==partnerandx.currency_id==currency)
                to_reconcile.reconcile()

            ifdestination_linesandself.destination_account_id.reconcile:
                to_reconcile=destination_lines+new_move.line_ids.filtered(lambdax:x.account_id==self.destination_account_idandx.partner_id==partnerandx.currency_id==currency)
                to_reconcile.reconcile()

        #Logtheoperationonsourcemoves
        acc_transfer_per_move=defaultdict(lambda:defaultdict(lambda:0)) #dict(move,dict(account,balance))
        forlineinself.move_line_ids:
            acc_transfer_per_move[line.move_id][line.account_id]+=line.balance

        formove,balances_per_accountinacc_transfer_per_move.items():
            message_to_log=self._format_transfer_source_log(balances_per_account,new_move)
            ifmessage_to_log:
                move.message_post(body=message_to_log)

        #Logontargetmoveaswell
        new_move.message_post(body=self._format_new_transfer_move_log(acc_transfer_per_move))

        return{
            'name':_("Transfer"),
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'account.move',
            'res_id':new_move.id,
        }

    #Transferutils
    def_format_new_transfer_move_log(self,acc_transfer_per_move):
        format=_("<li>{amount}({debit_credit})from{link},<strong>%(account_source_name)s</strong></li>")
        rslt=_("Thisentrytransfersthefollowingamountsto<strong>%(destination)s</strong><ul>",destination=self.destination_account_id.display_name)
        formove,balances_per_accountinacc_transfer_per_move.items():
            foraccount,balanceinbalances_per_account.items():
                ifaccount!=self.destination_account_id: #Otherwise,loggingithereisconfusingfortheuser
                    rslt+=self._format_strings(format,move,balance)%{'account_source_name':account.display_name}

        rslt+='</ul>'
        returnrslt

    def_format_transfer_source_log(self,balances_per_account,transfer_move):
        transfer_format=_("<li>{amount}({debit_credit})from<strong>%s</strong>weretransferredto<strong>{account_target_name}</strong>by{link}</li>")
        content=''
        foraccount,balanceinbalances_per_account.items():
            ifaccount!=self.destination_account_id:
                content+=self._format_strings(transfer_format,transfer_move,balance)%account.display_name
        returncontentand'<ul>'+content+'</ul>'orNone

    def_format_move_link(self,move):
        move_link_format="<ahref=#data-oe-model=account.movedata-oe-id={move_id}>{move_name}</a>"
        returnmove_link_format.format(move_id=move.id,move_name=move.name)

    def_format_strings(self,string,move,amount):
        returnstring.format(
            percent=self.percentage,
            name=move.name,
            id=move.id,
            amount=formatLang(self.env,abs(amount),currency_obj=self.company_id.currency_id),
            debit_credit=amount<0and_('C')or_('D'),
            link=self._format_move_link(move),
            date=format_date(self.env,move.date),
            new_date=self.dateandformat_date(self.env,self.date)or_('[Notset]'),
            account_target_name=self.destination_account_id.display_name,
        )
