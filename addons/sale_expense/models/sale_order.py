#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectraimportSUPERUSER_ID
fromflectra.osvimportexpression


classSaleOrder(models.Model):
    _inherit='sale.order'

    expense_ids=fields.One2many('hr.expense','sale_order_id',string='Expenses',domain=[('state','=','done')],readonly=True,copy=False)
    expense_count=fields.Integer("#ofExpenses",compute='_compute_expense_count',compute_sudo=True)

    @api.model
    def_name_search(self,name='',args=None,operator='ilike',limit=100,name_get_uid=None):
        """Forexpense,wewanttoshowallsalesorderbutonlytheirname_get(noir.ruleapplied),thisistheonlywaytodoit."""
        ifself._context.get('sale_expense_all_order')andself.user_has_groups('sales_team.group_sale_salesman')andnotself.user_has_groups('sales_team.group_sale_salesman_all_leads'):
            domain=expression.AND([argsor[],['&',('state','=','sale'),('company_id','in',self.env.companies.ids)]])
            returnsuper(SaleOrder,self.sudo())._name_search(name=name,args=domain,operator=operator,limit=limit,name_get_uid=SUPERUSER_ID)
        returnsuper(SaleOrder,self)._name_search(name=name,args=args,operator=operator,limit=limit,name_get_uid=name_get_uid)

    @api.depends('expense_ids')
    def_compute_expense_count(self):
        expense_data=self.env['hr.expense'].read_group([('sale_order_id','in',self.ids)],['sale_order_id'],['sale_order_id'])
        mapped_data=dict([(item['sale_order_id'][0],item['sale_order_id_count'])foriteminexpense_data])
        forsale_orderinself:
            sale_order.expense_count=mapped_data.get(sale_order.id,0)
