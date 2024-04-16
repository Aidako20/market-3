#-*-coding:utf-8-*-
fromflectraimport_,models
fromflectra.addons.sale_timesheet.models.project_overviewimport_to_action_data


classProject(models.Model):
    _inherit='project.project'

    def_plan_get_stat_button(self):
        stat_buttons=super(Project,self)._plan_get_stat_button()
        ifself.env.user.has_group('purchase.group_purchase_user'):
            accounts=self.mapped('analytic_account_id.id')
            purchase_order_lines=self.env['purchase.order.line'].search([('account_analytic_id','in',accounts)])
            purchase_orders=purchase_order_lines.mapped('order_id')
            ifpurchase_orders:
                stat_buttons.append({
                    'name':_('PurchaseOrders'),
                    'count':len(purchase_orders),
                    'icon':'fafa-shopping-cart',
                    'action':_to_action_data('purchase.order',
                        domain=[('id','in',purchase_orders.ids)],
                        context={'create':False,'edit':False,'delete':False}
                    )
                })
            account_invoice_lines=self.env['account.move.line'].search(
                [('analytic_account_id','in',accounts),
                 ('move_id.move_type','in',['in_invoice','in_refund'])])
            account_invoices=account_invoice_lines.mapped('move_id')
            ifaccount_invoices:
                stat_buttons.append({
                    'name':_('VendorBills'),
                    'count':len(account_invoices),
                    'icon':'fafa-pencil-square-o',
                    'action':_to_action_data(
                        action=self.env.ref('account.action_move_in_invoice_type'),
                        domain=[('id','in',account_invoices.ids)],
                        context={'create':False,'edit':False,'delete':False}
                    )})

        returnstat_buttons
