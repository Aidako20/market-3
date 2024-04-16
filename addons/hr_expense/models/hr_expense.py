#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.toolsimportemail_split,float_is_zero


classHrExpense(models.Model):

    _name="hr.expense"
    _inherit=['mail.thread','mail.activity.mixin']
    _description="Expense"
    _order="datedesc,iddesc"
    _check_company_auto=True

    @api.model
    def_default_employee_id(self):
        employee=self.env.user.employee_id
        ifnotemployeeandnotself.env.user.has_group('hr_expense.group_hr_expense_team_approver'):
            raiseValidationError(_('Thecurrentuserhasnorelatedemployee.Please,createone.'))
        returnemployee

    @api.model
    def_default_product_uom_id(self):
        returnself.env['uom.uom'].search([],limit=1,order='id')

    @api.model
    def_default_account_id(self):
        returnself.env['ir.property']._get('property_account_expense_categ_id','product.category')

    @api.model
    def_get_employee_id_domain(self):
        res=[('id','=',0)]#Nothingacceptedbydomain,bydefault
        ifself.user_has_groups('hr_expense.group_hr_expense_user')orself.user_has_groups('account.group_account_user'):
            res="['|',('company_id','=',False),('company_id','=',company_id)]" #Then,domainacceptseverything
        elifself.user_has_groups('hr_expense.group_hr_expense_team_approver')andself.env.user.employee_ids:
            user=self.env.user
            employee=self.env.user.employee_id
            res=[
                '|','|','|',
                ('department_id.manager_id','=',employee.id),
                ('parent_id','=',employee.id),
                ('id','=',employee.id),
                ('expense_manager_id','=',user.id),
                '|',('company_id','=',False),('company_id','=',employee.company_id.id),
            ]
        elifself.env.user.employee_id:
            employee=self.env.user.employee_id
            res=[('id','=',employee.id),'|',('company_id','=',False),('company_id','=',employee.company_id.id)]
        returnres

    name=fields.Char('Description',compute='_compute_from_product_id_company_id',store=True,required=True,copy=True,
        states={'draft':[('readonly',False)],'reported':[('readonly',False)],'refused':[('readonly',False)]})
    date=fields.Date(readonly=True,states={'draft':[('readonly',False)],'reported':[('readonly',False)],'refused':[('readonly',False)]},default=fields.Date.context_today,string="ExpenseDate")
    accounting_date=fields.Date(string="AccountingDate",related='sheet_id.accounting_date',store=True,groups='account.group_account_invoice,account.group_account_readonly')
    employee_id=fields.Many2one('hr.employee',compute='_compute_employee_id',string="Employee",
        store=True,required=True,readonly=False,tracking=True,
        states={'approved':[('readonly',True)],'done':[('readonly',True)]},
        default=_default_employee_id,domain=lambdaself:self._get_employee_id_domain(),check_company=True)
    #product_idnotrequiredtoallowcreateanexpensewithoutproductviamailalias,butshouldberequiredontheview.
    product_id=fields.Many2one('product.product',string='Product',readonly=True,tracking=True,states={'draft':[('readonly',False)],'reported':[('readonly',False)],'refused':[('readonly',False)]},domain="[('can_be_expensed','=',True),'|',('company_id','=',False),('company_id','=',company_id)]",ondelete='restrict')
    product_uom_id=fields.Many2one('uom.uom',string='UnitofMeasure',compute='_compute_from_product_id_company_id',
        store=True,copy=True,states={'draft':[('readonly',False)],'refused':[('readonly',False)]},
        default=_default_product_uom_id,domain="[('category_id','=',product_uom_category_id)]")
    product_uom_category_id=fields.Many2one(related='product_id.uom_id.category_id',readonly=True)
    unit_amount=fields.Float("UnitPrice",compute='_compute_from_product_id_company_id',store=True,required=True,copy=True,
        states={'draft':[('readonly',False)],'reported':[('readonly',False)],'refused':[('readonly',False)]},digits='ProductPrice')
    quantity=fields.Float(required=True,readonly=True,states={'draft':[('readonly',False)],'reported':[('readonly',False)],'refused':[('readonly',False)]},digits='ProductUnitofMeasure',default=1)
    tax_ids=fields.Many2many('account.tax','expense_tax','expense_id','tax_id',
        compute='_compute_from_product_id_company_id',store=True,readonly=False,
        domain="[('company_id','=',company_id),('type_tax_use','=','purchase')]",string='Taxes')
    untaxed_amount=fields.Float("Subtotal",store=True,compute='_compute_amount',digits='Account')
    total_amount=fields.Monetary("Total",compute='_compute_amount',store=True,currency_field='currency_id',tracking=True)
    amount_residual=fields.Monetary(string='AmountDue',compute='_compute_amount_residual',compute_sudo=True)
    company_currency_id=fields.Many2one('res.currency',string="ReportCompanyCurrency",related='sheet_id.currency_id',store=True,readonly=False)
    total_amount_company=fields.Monetary("Total(CompanyCurrency)",compute='_compute_total_amount_company',store=True,currency_field='company_currency_id')
    company_id=fields.Many2one('res.company',string='Company',required=True,readonly=True,states={'draft':[('readonly',False)],'refused':[('readonly',False)]},default=lambdaself:self.env.company)
    #TODOmakerequiredinmaster(sgv)
    currency_id=fields.Many2one('res.currency',string='Currency',readonly=True,states={'draft':[('readonly',False)],'refused':[('readonly',False)]},default=lambdaself:self.env.company.currency_id)
    analytic_account_id=fields.Many2one('account.analytic.account',string='AnalyticAccount',check_company=True)
    analytic_tag_ids=fields.Many2many('account.analytic.tag',string='AnalyticTags',states={'post':[('readonly',True)],'done':[('readonly',True)]},domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    account_id=fields.Many2one('account.account',compute='_compute_from_product_id_company_id',store=True,readonly=False,string='Account',
        default=_default_account_id,domain="[('internal_type','=','other'),('company_id','=',company_id)]",help="Anexpenseaccountisexpected")
    description=fields.Text('Notes...',readonly=True,states={'draft':[('readonly',False)],'reported':[('readonly',False)],'refused':[('readonly',False)]})
    payment_mode=fields.Selection([
        ("own_account","Employee(toreimburse)"),
        ("company_account","Company")
    ],default='own_account',tracking=True,states={'done':[('readonly',True)],'approved':[('readonly',True)],'reported':[('readonly',True)]},string="PaidBy")
    attachment_number=fields.Integer('NumberofAttachments',compute='_compute_attachment_number')
    state=fields.Selection([
        ('draft','ToSubmit'),
        ('reported','Submitted'),
        ('approved','Approved'),
        ('done','Paid'),
        ('refused','Refused')
    ],compute='_compute_state',string='Status',copy=False,index=True,readonly=True,store=True,default='draft',help="Statusoftheexpense.")
    sheet_id=fields.Many2one('hr.expense.sheet',string="ExpenseReport",domain="[('employee_id','=',employee_id),('company_id','=',company_id)]",readonly=True,copy=False)
    reference=fields.Char("BillReference")
    is_refused=fields.Boolean("ExplicitlyRefusedbymanageroraccountant",readonly=True,copy=False)

    is_editable=fields.Boolean("IsEditableByCurrentUser",compute='_compute_is_editable')
    is_ref_editable=fields.Boolean("ReferenceIsEditableByCurrentUser",compute='_compute_is_ref_editable')

    sample=fields.Boolean()

    @api.depends('sheet_id','sheet_id.account_move_id','sheet_id.state')
    def_compute_state(self):
        forexpenseinself:
            ifnotexpense.sheet_idorexpense.sheet_id.state=='draft':
                expense.state="draft"
            elifexpense.sheet_id.state=="cancel":
                expense.state="refused"
            elifexpense.sheet_id.state=="approve"orexpense.sheet_id.state=="post":
                expense.state="approved"
            elifnotexpense.sheet_id.account_move_id:
                expense.state="reported"
            else:
                expense.state="done"

    @api.depends('quantity','unit_amount','tax_ids','currency_id')
    def_compute_amount(self):
        forexpenseinself:
            expense.untaxed_amount=expense.unit_amount*expense.quantity
            taxes=expense.tax_ids.compute_all(expense.unit_amount,expense.currency_id,expense.quantity,expense.product_id,expense.employee_id.user_id.partner_id)
            expense.total_amount=taxes.get('total_included')

    @api.depends("sheet_id.account_move_id.line_ids")
    def_compute_amount_residual(self):
        forexpenseinself:
            ifnotexpense.sheet_id:
                expense.amount_residual=expense.total_amount
                continue
            ifnotexpense.currency_idorexpense.currency_id==expense.company_id.currency_id:
                residual_field='amount_residual'
            else:
                residual_field='amount_residual_currency'
            payment_term_lines=expense.sheet_id.account_move_id.line_ids\
                .filtered(lambdaline:line.expense_id==expenseandline.account_internal_typein('receivable','payable'))
            expense.amount_residual=-sum(payment_term_lines.mapped(residual_field))

    @api.depends('date','total_amount','company_currency_id')
    def_compute_total_amount_company(self):
        forexpenseinself:
            amount=0
            ifexpense.company_currency_id:
                date_expense=expense.date
                amount=expense.currency_id._convert(
                    expense.total_amount,expense.company_currency_id,
                    expense.company_id,date_expenseorfields.Date.today())
            expense.total_amount_company=amount

    def_compute_attachment_number(self):
        attachment_data=self.env['ir.attachment'].read_group([('res_model','=','hr.expense'),('res_id','in',self.ids)],['res_id'],['res_id'])
        attachment=dict((data['res_id'],data['res_id_count'])fordatainattachment_data)
        forexpenseinself:
            expense.attachment_number=attachment.get(expense.id,0)

    @api.depends('employee_id')
    def_compute_is_editable(self):
        is_account_manager=self.env.user.has_group('account.group_account_user')orself.env.user.has_group('account.group_account_manager')
        forexpenseinself:
            ifexpense.state=='draft'orexpense.sheet_id.statein['draft','submit']:
                expense.is_editable=True
            elifexpense.sheet_id.state=='approve':
                expense.is_editable=is_account_manager
            else:
                expense.is_editable=False

    @api.depends('employee_id')
    def_compute_is_ref_editable(self):
        is_account_manager=self.env.user.has_group('account.group_account_user')orself.env.user.has_group('account.group_account_manager')
        forexpenseinself:
            ifexpense.state=='draft'orexpense.sheet_id.statein['draft','submit']:
                expense.is_ref_editable=True
            else:
                expense.is_ref_editable=is_account_manager

    @api.depends('product_id','company_id')
    def_compute_from_product_id_company_id(self):
        forexpenseinself.filtered('product_id'):
            expense=expense.with_company(expense.company_id)
            expense.name=expense.nameorexpense.product_id.display_name
            ifnotexpense.attachment_numberor(expense.attachment_numberandnotexpense.unit_amount):
                expense.unit_amount=expense.product_id.price_compute('standard_price')[expense.product_id.id]
            expense.product_uom_id=expense.product_id.uom_id
            expense.tax_ids=expense.product_id.supplier_taxes_id.filtered(lambdatax:tax.company_id==expense.company_id) #taxesonlyfromthesamecompany
            account=expense.product_id.product_tmpl_id._get_product_accounts()['expense']
            ifaccount:
                expense.account_id=account

    @api.depends('company_id')
    def_compute_employee_id(self):
        ifnotself.env.context.get('default_employee_id'):
            forexpenseinself:
                expense.employee_id=self.env.user.with_company(expense.company_id).employee_id

    @api.onchange('product_id','date','account_id')
    def_onchange_product_id_date_account_id(self):
        rec=self.env['account.analytic.default'].sudo().account_get(
            product_id=self.product_id.id,
            account_id=self.account_id.id,
            company_id=self.company_id.id,
            date=self.date
        )
        self.analytic_account_id=self.analytic_account_idorrec.analytic_id.id
        self.analytic_tag_ids=self.analytic_tag_idsorrec.analytic_tag_ids.ids

    @api.constrains('payment_mode')
    def_check_payment_mode(self):
        self.sheet_id._check_payment_mode()

    @api.constrains('product_id','product_uom_id')
    def_check_product_uom_category(self):
        ifself.product_idandself.product_uom_id.category_id!=self.product_id.uom_id.category_id:
            raiseUserError(_('SelectedUnitofMeasuredoesnotbelongtothesamecategoryastheproductUnitofMeasure.'))

    defcreate_expense_from_attachments(self,attachment_ids=None,view_type='tree'):
        '''Createtheexpensesfromfiles.
         :return:Anactionredirectingtohr.expensetree/formview.
        '''
        ifattachment_idsisNone:
            attachment_ids=[]
        attachments=self.env['ir.attachment'].browse(attachment_ids)
        ifnotattachments:
            raiseUserError(_("Noattachmentwasprovided"))
        expenses=self.env['hr.expense']

        ifany(attachment.res_idorattachment.res_model!='hr.expense'forattachmentinattachments):
            raiseUserError(_("Invalidattachments!"))

        product=self.env['product.product'].search([('can_be_expensed','=',True)])
        ifproduct:
            product=product.filtered(lambdap:p.default_code=="EXP_GEN")orproduct[0]
        else:
            raiseUserError(_("Youneedtohaveatleastoneproductthatcanbeexpensedinyourdatabasetoproceed!"))

        forattachmentinattachments:
            vals={
                'name':attachment.name.split('.')[0],
                'unit_amount':0,
                'product_id':product.id
            }
            ifproduct.property_account_expense_id:
                vals['account_id']=product.property_account_expense_id.id

            expense=self.env['hr.expense'].create(vals)
            expense.message_post(body=_('UploadedAttachment'))
            attachment.write({
                'res_model':'hr.expense',
                'res_id':expense.id,
            })
            attachment.register_as_main_attachment()
            expenses+=expense
        iflen(expenses)==1:
            return{
                'name':_('GeneratedExpense'),
                'view_mode':'form',
                'res_model':'hr.expense',
                'type':'ir.actions.act_window',
                'views':[[False,'form']],
                'res_id':expenses[0].id,
            }
        return{
            'name':_('GeneratedExpenses'),
            'domain':[('id','in',expenses.ids)],
            'res_model':'hr.expense',
            'type':'ir.actions.act_window',
            'views':[[False,view_type],[False,"form"]],
        }

    #----------------------------------------
    #ORMOverrides
    #----------------------------------------

    defunlink(self):
        forexpenseinself:
            ifexpense.statein['done','approved']:
                raiseUserError(_('Youcannotdeleteapostedorapprovedexpense.'))
        returnsuper(HrExpense,self).unlink()

    defwrite(self,vals):
        if'sheet_id'invals:
            self.env['hr.expense.sheet'].browse(vals['sheet_id']).check_access_rule('write')
        if'tax_ids'invalsor'analytic_account_id'invalsor'account_id'invals:
            ifany(notexpense.is_editableforexpenseinself):
                raiseUserError(_('Youarenotauthorizedtoeditthisexpensereport.'))
        if'reference'invals:
            ifany(notexpense.is_ref_editableforexpenseinself):
                raiseUserError(_('Youarenotauthorizedtoeditthereferenceofthisexpensereport.'))
        returnsuper(HrExpense,self).write(vals)

    @api.model
    defget_empty_list_help(self,help_message):
        returnsuper(HrExpense,self).get_empty_list_help(help_messageor''+self._get_empty_list_mail_alias())

    @api.model
    def_get_empty_list_mail_alias(self):
        use_mailgateway=self.env['ir.config_parameter'].sudo().get_param('hr_expense.use_mailgateway')
        alias_record=use_mailgatewayandself.env.ref('hr_expense.mail_alias_expense')orFalse
        ifalias_recordandalias_record.alias_domainandalias_record.alias_name:
            return"""
<p>
Orsendyourreceiptsat<ahref="mailto:%(email)s?subject=Lunch%%20with%%20customer%%3A%%20%%2412.32">%(email)s</a>.
</p>"""%{'email':'%s@%s'%(alias_record.alias_name,alias_record.alias_domain)}
        return""

    #----------------------------------------
    #Actions
    #----------------------------------------

    defaction_view_sheet(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'hr.expense.sheet',
            'target':'current',
            'res_id':self.sheet_id.id
        }

    def_create_sheet_from_expenses(self):
        ifany(expense.state!='draft'orexpense.sheet_idforexpenseinself):
            raiseUserError(_("Youcannotreporttwicethesameline!"))
        iflen(self.mapped('employee_id'))!=1:
            raiseUserError(_("Youcannotreportexpensesfordifferentemployeesinthesamereport."))
        ifany(notexpense.product_idforexpenseinself):
            raiseUserError(_("Youcannotcreatereportwithoutproduct."))
        iflen(self.company_id)!=1:
            raiseUserError(_("Youcannotreportexpensesfordifferentcompaniesinthesamereport."))

        todo=self.filtered(lambdax:x.payment_mode=='own_account')orself.filtered(lambdax:x.payment_mode=='company_account')
        sheet=self.env['hr.expense.sheet'].create({
            'company_id':self.company_id.id,
            'employee_id':self[0].employee_id.id,
            'name':todo[0].nameiflen(todo)==1else'',
            'expense_line_ids':[(6,0,todo.ids)]
        })
        returnsheet

    defaction_submit_expenses(self):
        sheet=self._create_sheet_from_expenses()
        return{
            'name':_('NewExpenseReport'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'hr.expense.sheet',
            'target':'current',
            'res_id':sheet.id,
        }

    defaction_get_attachment_view(self):
        self.ensure_one()
        res=self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain']=[('res_model','=','hr.expense'),('res_id','in',self.ids)]
        res['context']={'default_res_model':'hr.expense','default_res_id':self.id}
        returnres

    #----------------------------------------
    #Business
    #----------------------------------------

    def_prepare_move_values(self):
        """
        Thisfunctionpreparesmovevaluesrelatedtoanexpense
        """
        self.ensure_one()
        journal=self.sheet_id.bank_journal_idifself.payment_mode=='company_account'elseself.sheet_id.journal_id
        account_date=self.sheet_id.accounting_dateorself.date
        move_values={
            'journal_id':journal.id,
            'company_id':self.sheet_id.company_id.id,
            'date':account_date,
            'ref':self.sheet_id.name,
            #forcethenametothedefaultvalue,toavoidaneventual'default_name'inthecontext
            #tosetitto''whichcausenonumbertobegiventotheaccount.movewhenposted.
            'name':'/',
        }
        returnmove_values

    def_get_account_move_by_sheet(self):
        """Returnamappingbetweentheexpensesheetofcurrentexpenseanditsaccountmove
            :returnsdictwherekeyisasheetid,andvalueisanaccountmoverecord
        """
        move_grouped_by_sheet={}
        forexpenseinself:
            #createthemovethatwillcontaintheaccountingentries
            ifexpense.sheet_id.idnotinmove_grouped_by_sheet:
                move_vals=expense._prepare_move_values()
                move=self.env['account.move'].with_context(default_journal_id=move_vals['journal_id']).create(move_vals)
                move_grouped_by_sheet[expense.sheet_id.id]=move
            else:
                move=move_grouped_by_sheet[expense.sheet_id.id]
        returnmove_grouped_by_sheet

    def_get_expense_account_source(self):
        self.ensure_one()
        ifself.account_id:
            account=self.account_id
        elifself.product_id:
            account=self.product_id.product_tmpl_id.with_company(self.company_id)._get_product_accounts()['expense']
            ifnotaccount:
                raiseUserError(
                    _("NoExpenseaccountfoundfortheproduct%s(orforitscategory),pleaseconfigureone.")%(self.product_id.name))
        else:
            account=self.env['ir.property'].with_company(self.company_id)._get('property_account_expense_categ_id','product.category')
            ifnotaccount:
                raiseUserError(_('PleaseconfigureDefaultExpenseaccountforProductexpense:`property_account_expense_categ_id`.'))
        returnaccount

    def_get_expense_account_destination(self):
        self.ensure_one()
        account_dest=self.env['account.account']
        ifself.payment_mode=='company_account':
            ifnotself.sheet_id.bank_journal_id.payment_credit_account_id:
                raiseUserError(_("NoOutstandingPaymentsAccountfoundforthe%sjournal,pleaseconfigureone.")%(self.sheet_id.bank_journal_id.name))
            account_dest=self.sheet_id.bank_journal_id.payment_credit_account_id.id
        else:
            ifnotself.employee_id.sudo().address_home_id:
                raiseUserError(_("NoHomeAddressfoundfortheemployee%s,pleaseconfigureone.")%(self.employee_id.name))
            partner=self.employee_id.sudo().address_home_id.with_company(self.company_id)
            account_dest=partner.property_account_payable_id.idorpartner.parent_id.property_account_payable_id.id
        returnaccount_dest

    def_get_account_move_line_values(self):
        move_line_values_by_expense={}
        forexpenseinself:
            move_line_name=expense.employee_id.name+':'+expense.name.split('\n')[0][:64]
            account_src=expense._get_expense_account_source()
            account_dst=expense._get_expense_account_destination()
            account_date=expense.dateorexpense.sheet_id.accounting_dateorfields.Date.context_today(expense)

            company_currency=expense.company_id.currency_id

            move_line_values=[]
            taxes=expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount,expense.currency_id,expense.quantity,expense.product_id)
            total_amount=0.0
            total_amount_currency=0.0
            partner_id=expense.employee_id.sudo().address_home_id.commercial_partner_id.id

            #sourcemoveline
            balance=expense.currency_id._convert(taxes['total_excluded'],company_currency,expense.company_id,account_date)
            amount_currency=taxes['total_excluded']
            move_line_src={
                'name':move_line_name,
                'quantity':expense.quantityor1,
                'debit':balanceifbalance>0else0,
                'credit':-balanceifbalance<0else0,
                'amount_currency':amount_currency,
                'account_id':account_src.id,
                'product_id':expense.product_id.id,
                'product_uom_id':expense.product_uom_id.id,
                'analytic_account_id':expense.analytic_account_id.id,
                'analytic_tag_ids':[(6,0,expense.analytic_tag_ids.ids)],
                'expense_id':expense.id,
                'partner_id':partner_id,
                'tax_ids':[(6,0,expense.tax_ids.ids)],
                'tax_tag_ids':[(6,0,taxes['base_tags'])],
                'currency_id':expense.currency_id.id,
            }
            move_line_values.append(move_line_src)
            total_amount-=balance
            total_amount_currency-=move_line_src['amount_currency']

            #taxesmovelines
            fortaxintaxes['taxes']:
                balance=expense.currency_id._convert(tax['amount'],company_currency,expense.company_id,account_date)
                amount_currency=tax['amount']

                iftax['tax_repartition_line_id']:
                    rep_ln=self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    base_amount=self.env['account.move']._get_base_amount_to_display(tax['base'],rep_ln)
                    base_amount=expense.currency_id._convert(base_amount,company_currency,expense.company_id,account_date)
                else:
                    base_amount=None

                move_line_tax_values={
                    'name':tax['name'],
                    'quantity':1,
                    'debit':balanceifbalance>0else0,
                    'credit':-balanceifbalance<0else0,
                    'amount_currency':amount_currency,
                    'account_id':tax['account_id']ormove_line_src['account_id'],
                    'tax_repartition_line_id':tax['tax_repartition_line_id'],
                    'tax_tag_ids':tax['tag_ids'],
                    'tax_base_amount':base_amount,
                    'expense_id':expense.id,
                    'partner_id':partner_id,
                    'currency_id':expense.currency_id.id,
                    'analytic_account_id':expense.analytic_account_id.idiftax['analytic']elseFalse,
                    'analytic_tag_ids':[(6,0,expense.analytic_tag_ids.ids)]iftax['analytic']elseFalse,
                }
                total_amount-=balance
                total_amount_currency-=move_line_tax_values['amount_currency']
                move_line_values.append(move_line_tax_values)

            #destinationmoveline
            move_line_dst={
                'name':move_line_name,
                'debit':total_amount>0andtotal_amount,
                'credit':total_amount<0and-total_amount,
                'account_id':account_dst,
                'date_maturity':account_date,
                'amount_currency':total_amount_currency,
                'currency_id':expense.currency_id.id,
                'expense_id':expense.id,
                'partner_id':partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id]=move_line_values
        returnmove_line_values_by_expense

    defaction_move_create(self):
        '''
        mainfunctionthatiscalledwhentryingtocreatetheaccountingentriesrelatedtoanexpense
        '''
        move_group_by_sheet=self._get_account_move_by_sheet()

        move_line_values_by_expense=self._get_account_move_line_values()

        forexpenseinself:
            #gettheaccountmoveoftherelatedsheet
            move=move_group_by_sheet[expense.sheet_id.id]

            #getmovelinevalues
            move_line_values=move_line_values_by_expense.get(expense.id)

            #linkmovelinestomove,andmovetoexpensesheet
            move.write({'line_ids':[(0,0,line)forlineinmove_line_values]})
            expense.sheet_id.write({'account_move_id':move.id})

            ifexpense.payment_mode=='company_account':
                expense.sheet_id.paid_expense_sheets()

        #postthemoves
        formoveinmove_group_by_sheet.values():
            move._post()

        returnmove_group_by_sheet

    defrefuse_expense(self,reason):
        self.write({'is_refused':True})
        self.sheet_id.write({'state':'cancel'})
        self.sheet_id.message_post_with_view('hr_expense.hr_expense_template_refuse_reason',
                                             values={'reason':reason,'is_sheet':False,'name':self.name})

    @api.model
    defget_expense_dashboard(self):
        expense_state={
            'draft':{
                'description':_('toreport'),
                'amount':0.0,
                'currency':self.env.company.currency_id.id,
            },
            'reported':{
                'description':_('undervalidation'),
                'amount':0.0,
                'currency':self.env.company.currency_id.id,
            },
            'approved':{
                'description':_('tobereimbursed'),
                'amount':0.0,
                'currency':self.env.company.currency_id.id,
            }
        }
        ifnotself.env.user.employee_ids:
            returnexpense_state
        target_currency=self.env.company.currency_id
        expenses=self.read_group(
            [
                ('employee_id','in',self.env.user.employee_ids.ids),
                ('payment_mode','=','own_account'),
                ('state','in',['draft','reported','approved'])
            ],['total_amount','currency_id','state'],['state','currency_id'],lazy=False)
        forexpenseinexpenses:
            state=expense['state']
            currency=self.env['res.currency'].browse(expense['currency_id'][0])ifexpense['currency_id']elsetarget_currency
            amount=currency._convert(
                    expense['total_amount'],target_currency,self.env.company,fields.Date.today())
            expense_state[state]['amount']+=amount
        returnexpense_state

    #----------------------------------------
    #MailThread
    #----------------------------------------

    @api.model
    defmessage_new(self,msg_dict,custom_values=None):
        email_address=email_split(msg_dict.get('email_from',False))[0]

        employee=self.env['hr.employee'].search([
            '|',
            ('work_email','ilike',email_address),
            ('user_id.email','ilike',email_address)
        ],limit=1)

        ifnotemployee:
            returnsuper().message_new(msg_dict,custom_values=custom_values)

        expense_description=msg_dict.get('subject','')

        ifemployee.user_id:
            company=employee.user_id.company_id
            currencies=company.currency_id|employee.user_id.company_ids.mapped('currency_id')
        else:
            company=employee.company_id
            currencies=company.currency_id

        ifnotcompany: #ultimatefallback,sincecompany_idisrequiredonexpense
            company=self.env.company

        #Theexpensesaliasisthesameforallcompanies,weneedtosetthepropercontext
        #Toselecttheproductaccount
        self=self.with_company(company)

        product,price,currency_id,expense_description=self._parse_expense_subject(expense_description,currencies)
        vals={
            'employee_id':employee.id,
            'name':expense_description,
            'unit_amount':price,
            'product_id':product.idifproductelseNone,
            'product_uom_id':product.uom_id.id,
            'tax_ids':[(4,tax.id,False)fortaxinproduct.supplier_taxes_id.filtered(lambdar:r.company_id==company)],
            'quantity':1,
            'company_id':company.id,
            'currency_id':currency_id.id
        }

        account=product.product_tmpl_id._get_product_accounts()['expense']
        ifaccount:
            vals['account_id']=account.id

        expense=super(HrExpense,self).message_new(msg_dict,dict(custom_valuesor{},**vals))
        self._send_expense_success_mail(msg_dict,expense)
        returnexpense

    @api.model
    def_parse_product(self,expense_description):
        """
        Parsethesubjecttofindtheproduct.
        Productcodeshouldbethefirstwordofexpense_description
        Returnproduct.productandupdateddescription
        """
        product_code=expense_description.split('')[0]
        product=self.env['product.product'].search([('can_be_expensed','=',True),('default_code','=ilike',product_code)],limit=1)
        ifproduct:
            expense_description=expense_description.replace(product_code,'',1)

        returnproduct,expense_description

    @api.model
    def_parse_price(self,expense_description,currencies):
        """Returnprice,currencyandupdateddescription"""
        symbols,symbols_pattern,float_pattern=[],'','[+-]?(\d+[.,]?\d*)'
        price=0.0
        forcurrencyincurrencies:
            symbols.append(re.escape(currency.symbol))
            symbols.append(re.escape(currency.name))
        symbols_pattern='|'.join(symbols)
        price_pattern="((%s)?\s?%s\s?(%s)?)"%(symbols_pattern,float_pattern,symbols_pattern)
        matches=re.findall(price_pattern,expense_description)
        currency=currenciesandcurrencies[0]
        ifmatches:
            match=max(matches,key=lambdamatch:len([groupforgroupinmatchifgroup]))#getthelonguestmatch.e.g."2chairs120$"->thepriceis120$,not2
            full_str=match[0]
            currency_str=match[1]ormatch[3]
            price=match[2].replace(',','.')

            ifcurrency_strandcurrencies:
                currencies=currencies.filtered(lambdac:currency_strin[c.symbol,c.name])
                currency=(currenciesandcurrencies[0])orcurrency
            expense_description=expense_description.replace(full_str,'')#removepricefromdescription
            expense_description=re.sub('+','',expense_description.strip())

        price=float(price)
        returnprice,currency,expense_description

    @api.model
    def_parse_expense_subject(self,expense_description,currencies):
        """Fetchproduct,priceandcurrencyinfofrommailsubject.

            Productcanbeidentifiedbasedonproductnameorproductcode.
            Itcanbepassedbetween[]oritcanbeplacedatstart.

            Whenparsing,onlyconsidercurrenciespassedasparameter.
            Thiswillfetchcurrencyinsymbol($)orISOname(USD).

            Somevalidexamples:
                TravelbyAir[TICKET]USD1205.91
                TICKET$1205.91TravelbyAir
                Extraexpenses29.10EUR[EXTRA]
        """
        product,expense_description=self._parse_product(expense_description)
        price,currency_id,expense_description=self._parse_price(expense_description,currencies)

        returnproduct,price,currency_id,expense_description

    #TODO:Makeapi.multi
    def_send_expense_success_mail(self,msg_dict,expense):
        mail_template_id='hr_expense.hr_expense_template_register'ifexpense.employee_id.user_idelse'hr_expense.hr_expense_template_register_no_user'
        expense_template=self.env.ref(mail_template_id)
        rendered_body=expense_template._render({'expense':expense},engine='ir.qweb')
        body=self.env['mail.render.mixin']._replace_local_links(rendered_body)
        #TDETODO:seemslouche,checktousenotify
        ifexpense.employee_id.user_id.partner_id:
            expense.message_post(
                partner_ids=expense.employee_id.user_id.partner_id.ids,
                subject='Re:%s'%msg_dict.get('subject',''),
                body=body,
                subtype_id=self.env.ref('mail.mt_note').id,
                email_layout_xmlid='mail.mail_notification_light',
            )
        else:
            self.env['mail.mail'].sudo().create({
                'email_from':self.env.user.email_formatted,
                'author_id':self.env.user.partner_id.id,
                'body_html':body,
                'subject':'Re:%s'%msg_dict.get('subject',''),
                'email_to':msg_dict.get('email_from',False),
                'auto_delete':True,
                'references':msg_dict.get('message_id'),
            }).send()


classHrExpenseSheet(models.Model):
    """
        Herearetherightsassociatedwiththeexpenseflow

        Action      Group                  Restriction
        =================================================================================
        Submit     Employee               Onlyhisown
                    Officer                Ifheisexpensemanageroftheemployee,manageroftheemployee
                                             ortheemployeeisinthedepartmentmanagedbytheofficer
                    Manager                Always
        Approve    Officer                Nothisownandheisexpensemanageroftheemployee,manageroftheemployee
                                             ortheemployeeisinthedepartmentmanagedbytheofficer
                    Manager                Always
        Post       Anybody                State=approveandjournal_iddefined
        Done       Anybody                State=approveandjournal_iddefined
        Cancel     Officer                Nothisownandheisexpensemanageroftheemployee,manageroftheemployee
                                             ortheemployeeisinthedepartmentmanagedbytheofficer
                    Manager                Always
        =================================================================================
    """
    _name="hr.expense.sheet"
    _inherit=['mail.thread','mail.activity.mixin']
    _description="ExpenseReport"
    _order="accounting_datedesc,iddesc"
    _check_company_auto=True

    @api.model
    def_default_employee_id(self):
        returnself.env.user.employee_id

    @api.model
    def_default_journal_id(self):
        """Thejournalisdeterminingthecompanyoftheaccountingentriesgeneratedfromexpense.Weneedtoforcejournalcompanyandexpensesheetcompanytobethesame."""
        default_company_id=self.default_get(['company_id'])['company_id']
        journal=self.env['account.journal'].search([('type','=','purchase'),('company_id','=',default_company_id)],limit=1)
        returnjournal.id

    @api.model
    def_default_bank_journal_id(self):
        default_company_id=self.default_get(['company_id'])['company_id']
        returnself.env['account.journal'].search([('type','in',['cash','bank']),('company_id','=',default_company_id)],limit=1)

    name=fields.Char('ExpenseReportSummary',required=True,tracking=True)
    expense_line_ids=fields.One2many(
        comodel_name='hr.expense',
        inverse_name='sheet_id',
        string='ExpenseLines',
        copy=False,
        states={'post':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}
    )
    state=fields.Selection([
        ('draft','Draft'),
        ('submit','Submitted'),
        ('approve','Approved'),
        ('post','Posted'),
        ('done','Paid'),
        ('cancel','Refused')
    ],string='Status',index=True,readonly=True,tracking=True,copy=False,default='draft',required=True,help='ExpenseReportState')
    employee_id=fields.Many2one('hr.employee',string="Employee",required=True,readonly=True,tracking=True,states={'draft':[('readonly',False)]},default=_default_employee_id,check_company=True,domain=lambdaself:self.env['hr.expense']._get_employee_id_domain())
    address_id=fields.Many2one('res.partner',compute='_compute_from_employee_id',store=True,readonly=False,copy=True,string="EmployeeHomeAddress",check_company=True)
    payment_mode=fields.Selection(related='expense_line_ids.payment_mode',default='own_account',readonly=True,string="PaidBy",tracking=True)
    user_id=fields.Many2one('res.users','Manager',compute='_compute_from_employee_id',store=True,readonly=True,copy=False,states={'draft':[('readonly',False)]},tracking=True,domain=lambdaself:[('groups_id','in',self.env.ref('hr_expense.group_hr_expense_team_approver').id)])
    total_amount=fields.Monetary('TotalAmount',currency_field='currency_id',compute='_compute_amount',store=True,tracking=True)
    amount_residual=fields.Monetary(
        string="AmountDue",store=True,
        currency_field='currency_id',
        compute='_compute_amount_residual')
    company_id=fields.Many2one('res.company',string='Company',required=True,readonly=True,states={'draft':[('readonly',False)]},default=lambdaself:self.env.company)
    currency_id=fields.Many2one('res.currency',string='Currency',readonly=True,states={'draft':[('readonly',False)]},default=lambdaself:self.env.company.currency_id)
    attachment_number=fields.Integer(compute='_compute_attachment_number',string='NumberofAttachments')
    journal_id=fields.Many2one('account.journal',string='ExpenseJournal',states={'done':[('readonly',True)],'post':[('readonly',True)]},check_company=True,domain="[('type','=','purchase'),('company_id','=',company_id)]",
        default=_default_journal_id,help="Thejournalusedwhentheexpenseisdone.")
    bank_journal_id=fields.Many2one('account.journal',string='BankJournal',states={'done':[('readonly',True)],'post':[('readonly',True)]},check_company=True,domain="[('type','in',['cash','bank']),('company_id','=',company_id)]",
        default=_default_bank_journal_id,help="Thepaymentmethodusedwhentheexpenseispaidbythecompany.")
    accounting_date=fields.Date("AccountingDate")
    account_move_id=fields.Many2one('account.move',string='JournalEntry',ondelete='restrict',copy=False,readonly=True)
    department_id=fields.Many2one('hr.department',compute='_compute_from_employee_id',store=True,readonly=False,copy=False,string='Department',states={'post':[('readonly',True)],'done':[('readonly',True)]})
    is_multiple_currency=fields.Boolean("Handlelineswithdifferentcurrencies",compute='_compute_is_multiple_currency')
    can_reset=fields.Boolean('CanReset',compute='_compute_can_reset')

    _sql_constraints=[
        ('journal_id_required_posted',"CHECK((stateIN('post','done')ANDjournal_idISNOTNULL)OR(stateNOTIN('post','done')))",'Thejournalmustbesetonpostedexpense'),
    ]

    @api.depends('expense_line_ids.total_amount_company')
    def_compute_amount(self):
        forsheetinself:
            sheet.total_amount=sum(sheet.expense_line_ids.mapped('total_amount_company'))

    @api.depends(
        'currency_id',
        'account_move_id.line_ids.amount_residual',
        'account_move_id.line_ids.amount_residual_currency',
        'account_move_id.line_ids.account_internal_type',)
    def_compute_amount_residual(self):
        forsheetinself:
            ifsheet.currency_id==sheet.company_id.currency_id:
                residual_field='amount_residual'
            else:
                residual_field='amount_residual_currency'

            payment_term_lines=sheet.account_move_id.line_ids\
                .filtered(lambdaline:line.account_internal_typein('receivable','payable'))
            sheet.amount_residual=-sum(payment_term_lines.mapped(residual_field))

    def_compute_attachment_number(self):
        forsheetinself:
            sheet.attachment_number=sum(sheet.expense_line_ids.mapped('attachment_number'))

    @api.depends('expense_line_ids.currency_id')
    def_compute_is_multiple_currency(self):
        forsheetinself:
            sheet.is_multiple_currency=len(sheet.expense_line_ids.mapped('currency_id'))>1

    def_compute_can_reset(self):
        is_expense_user=self.user_has_groups('hr_expense.group_hr_expense_team_approver')
        forsheetinself:
            sheet.can_reset=is_expense_userifis_expense_userelsesheet.employee_id.user_id==self.env.user

    @api.depends('employee_id')
    def_compute_from_employee_id(self):
        forsheetinself:
            sheet.address_id=sheet.employee_id.sudo().address_home_id
            sheet.department_id=sheet.employee_id.department_id
            sheet.user_id=sheet.employee_id.expense_manager_idorsheet.employee_id.parent_id.user_id

    @api.constrains('expense_line_ids')
    def_check_payment_mode(self):
        forsheetinself:
            expense_lines=sheet.mapped('expense_line_ids')
            ifexpense_linesandany(expense.payment_mode!=expense_lines[0].payment_modeforexpenseinexpense_lines):
                raiseValidationError(_("Expensesmustbepaidbythesameentity(Companyoremployee)."))

    @api.constrains('expense_line_ids','employee_id')
    def_check_employee(self):
        forsheetinself:
            employee_ids=sheet.expense_line_ids.mapped('employee_id')
            iflen(employee_ids)>1or(len(employee_ids)==1andemployee_ids!=sheet.employee_id):
                raiseValidationError(_('Youcannotaddexpensesofanotheremployee.'))

    @api.constrains('expense_line_ids','company_id')
    def_check_expense_lines_company(self):
        forsheetinself:
            ifany(expense.company_id!=sheet.company_idforexpenseinsheet.expense_line_ids):
                raiseValidationError(_('Anexpensereportmustcontainonlylinesfromthesamecompany.'))

    @api.model
    defcreate(self,vals):
        sheet=super(HrExpenseSheet,self.with_context(mail_create_nosubscribe=True,mail_auto_subscribe_no_notify=True)).create(vals)
        sheet.activity_update()
        returnsheet

    defunlink(self):
        forexpenseinself:
            ifexpense.statein['post','done']:
                raiseUserError(_('Youcannotdeleteapostedorpaidexpense.'))
        super(HrExpenseSheet,self).unlink()

    #--------------------------------------------
    #MailThread
    #--------------------------------------------

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'state'ininit_valuesandself.state=='approve':
            returnself.env.ref('hr_expense.mt_expense_approved')
        elif'state'ininit_valuesandself.state=='cancel':
            returnself.env.ref('hr_expense.mt_expense_refused')
        elif'state'ininit_valuesandself.state=='done':
            returnself.env.ref('hr_expense.mt_expense_paid')
        returnsuper(HrExpenseSheet,self)._track_subtype(init_values)

    def_message_auto_subscribe_followers(self,updated_values,subtype_ids):
        res=super(HrExpenseSheet,self)._message_auto_subscribe_followers(updated_values,subtype_ids)
        ifupdated_values.get('employee_id'):
            employee=self.env['hr.employee'].browse(updated_values['employee_id'])
            ifemployee.user_id:
                res.append((employee.user_id.partner_id.id,subtype_ids,False))
        returnres

    #--------------------------------------------
    #Actions
    #--------------------------------------------

    defaction_sheet_move_create(self):
        samples=self.mapped('expense_line_ids.sample')
        ifsamples.count(True):
            ifsamples.count(False):
                raiseUserError(_("Youcan'tmixsampleexpensesandregularones"))
            self.write({'state':'post'})
            return

        ifany(sheet.state!='approve'forsheetinself):
            raiseUserError(_("Youcanonlygenerateaccountingentryforapprovedexpense(s)."))

        ifany(notsheet.journal_idforsheetinself):
            raiseUserError(_("Expensesmusthaveanexpensejournalspecifiedtogenerateaccountingentries."))

        expense_line_ids=self.mapped('expense_line_ids')\
            .filtered(lambdar:notfloat_is_zero(r.total_amount,precision_rounding=(r.currency_idorself.env.company.currency_id).rounding))
        res=expense_line_ids.action_move_create()
        forsheetinself.filtered(lambdas:nots.accounting_date):
            sheet.accounting_date=sheet.account_move_id.date
        to_post=self.filtered(lambdasheet:sheet.payment_mode=='own_account'andsheet.expense_line_ids)
        to_post.write({'state':'post'})
        (self-to_post).write({'state':'done'})
        self.activity_update()
        returnres

    defaction_get_attachment_view(self):
        res=self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain']=[('res_model','=','hr.expense'),('res_id','in',self.expense_line_ids.ids)]
        res['context']={
            'default_res_model':'hr.expense.sheet',
            'default_res_id':self.id,
            'create':False,
            'edit':False,
        }
        returnres

    #--------------------------------------------
    #Business
    #--------------------------------------------

    defset_to_paid(self):
        self.write({'state':'done'})

    defaction_submit_sheet(self):
        self.write({'state':'submit'})
        self.activity_update()

    defapprove_expense_sheets(self):
        ifnotself.user_has_groups('hr_expense.group_hr_expense_team_approver'):
            raiseUserError(_("OnlyManagersandHROfficerscanapproveexpenses"))
        elifnotself.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers=self.employee_id.expense_manager_id|self.employee_id.parent_id.user_id|self.employee_id.department_id.manager_id.user_id

            ifself.employee_id.user_id==self.env.user:
                raiseUserError(_("Youcannotapproveyourownexpenses"))

            ifnotself.env.userincurrent_managersandnotself.user_has_groups('hr_expense.group_hr_expense_user')andself.employee_id.expense_manager_id!=self.env.user:
                raiseUserError(_("Youcanonlyapproveyourdepartmentexpenses"))
        
        notification={
            'type':'ir.actions.client',
            'tag':'display_notification',
            'params':{
                'title':_('Therearenoexpensereportstoapprove.'),
                'type':'warning',
                'sticky':False, #True/Falsewilldisplayforfewsecondsiffalse
            },
        }
        filtered_sheet=self.filtered(lambdas:s.statein['submit','draft'])
        ifnotfiltered_sheet:
            returnnotification
        forsheetinfiltered_sheet:
            sheet.write({'state':'approve','user_id':sheet.user_id.idorself.env.user.id})
        notification['params'].update({
            'title':_('Theexpensereportsweresuccessfullyapproved.'),
            'type':'success',
            'next':{'type':'ir.actions.act_window_close'},
        })
            
        self.activity_update()
        returnnotification

    defpaid_expense_sheets(self):
        self.write({'state':'done'})

    defrefuse_sheet(self,reason):
        ifnotself.user_has_groups('hr_expense.group_hr_expense_team_approver'):
            raiseUserError(_("OnlyManagersandHROfficerscanapproveexpenses"))
        elifnotself.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers=self.employee_id.expense_manager_id|self.employee_id.parent_id.user_id|self.employee_id.department_id.manager_id.user_id

            ifself.employee_id.user_id==self.env.user:
                raiseUserError(_("Youcannotrefuseyourownexpenses"))

            ifnotself.env.userincurrent_managersandnotself.user_has_groups('hr_expense.group_hr_expense_user')andself.employee_id.expense_manager_id!=self.env.user:
                raiseUserError(_("Youcanonlyrefuseyourdepartmentexpenses"))

        self.write({'state':'cancel'})
        forsheetinself:
            sheet.message_post_with_view('hr_expense.hr_expense_template_refuse_reason',values={'reason':reason,'is_sheet':True,'name':sheet.name})
        self.activity_update()

    defreset_expense_sheets(self):
        ifnotself.can_reset:
            raiseUserError(_("OnlyHROfficersortheconcernedemployeecanresettodraft."))
        self.mapped('expense_line_ids').write({'is_refused':False})
        self.write({'state':'draft'})
        self.activity_update()
        returnTrue

    def_get_responsible_for_approval(self):
        ifself.user_id:
            returnself.user_id
        elifself.employee_id.parent_id.user_id:
            returnself.employee_id.parent_id.user_id
        elifself.employee_id.department_id.manager_id.user_id:
            returnself.employee_id.department_id.manager_id.user_id
        returnself.env['res.users']

    defactivity_update(self):
        forexpense_reportinself.filtered(lambdahol:hol.state=='submit'):
            self.activity_schedule(
                'hr_expense.mail_act_expense_approval',
                user_id=expense_report.sudo()._get_responsible_for_approval().idorself.env.user.id)
        self.filtered(lambdahol:hol.state=='approve').activity_feedback(['hr_expense.mail_act_expense_approval'])
        self.filtered(lambdahol:hol.statein('draft','cancel')).activity_unlink(['hr_expense.mail_act_expense_approval'])

    defaction_register_payment(self):
        '''Opentheaccount.payment.registerwizardtopaytheselectedjournalentries.
        :return:Anactionopeningtheaccount.payment.registerwizard.
        '''
        return{
            'name':_('RegisterPayment'),
            'res_model':'account.payment.register',
            'view_mode':'form',
            'context':{
                'active_model':'account.move',
                'active_ids':self.account_move_id.ids,
            },
            'target':'new',
            'type':'ir.actions.act_window',
        }
