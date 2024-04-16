#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classExpense(models.Model):
    _inherit="hr.expense"

    sale_order_id=fields.Many2one('sale.order',compute='_compute_sale_order_id',store=True,string='CustomertoReinvoice',readonly=False,tracking=True,
        states={'approved':[('readonly',True)],'done':[('readonly',True)],'refused':[('readonly',True)]},
        #NOTE:onlyconfirmedSOcanbeselected,butthisdomaininactivatedthroughtthenamesearchwiththe`sale_expense_all_order`
        #contextkey.So,thisdomainisnottheoneapplied.
        domain="[('state','=','sale'),('company_id','=',company_id)]",
        help="Iftheproducthasanexpensepolicy,itwillbereinvoicedonthissalesorder")
    can_be_reinvoiced=fields.Boolean("Canbereinvoiced",compute='_compute_can_be_reinvoiced')
    analytic_account_id=fields.Many2one(compute='_compute_analytic_account_id',store=True,readonly=False)

    @api.depends('product_id.expense_policy')
    def_compute_can_be_reinvoiced(self):
        forexpenseinself:
            expense.can_be_reinvoiced=expense.product_id.expense_policyin['sales_price','cost']

    @api.depends('can_be_reinvoiced')
    def_compute_sale_order_id(self):
        forexpenseinself.filtered(lambdae:note.can_be_reinvoiced):
            expense.sale_order_id=False

    @api.depends('sale_order_id')
    def_compute_analytic_account_id(self):
        forexpenseinself.filtered('sale_order_id'):
            expense.analytic_account_id=expense.sale_order_id.sudo().analytic_account_id #`sudo`requiredfornormalemployeewithoutsaleaccessrights

    defaction_move_create(self):
        """Whenpostingexpense,iftheAAisgiven,wewilltrackcostinthat
            IfaSOisset,thismeanswewanttoreinvoicetheexpense.Buttodoso,we
            needtheanalyticentriestobegenerated,soaAAisrequiredtoreinvoice.So,
            weensuretheAAifaSOisgiven.
        """
        forexpenseinself.filtered(lambdaexpense:expense.sale_order_idandnotexpense.analytic_account_id):
            ifnotexpense.sale_order_id.analytic_account_id:
                expense.sale_order_id._create_analytic_account()
            expense.write({
                'analytic_account_id':expense.sale_order_id.analytic_account_id.id
            })
        returnsuper(Expense,self).action_move_create()
