#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classAccountMove(models.Model):
    _inherit='account.move'

    landed_costs_ids=fields.One2many('stock.landed.cost','vendor_bill_id',string='LandedCosts')
    landed_costs_visible=fields.Boolean(compute='_compute_landed_costs_visible')

    @api.depends('line_ids','line_ids.is_landed_costs_line')
    def_compute_landed_costs_visible(self):
        foraccount_moveinself:
            ifaccount_move.landed_costs_ids:
                account_move.landed_costs_visible=False
            else:
                account_move.landed_costs_visible=any(line.is_landed_costs_lineforlineinaccount_move.line_ids)

    defbutton_create_landed_costs(self):
        """Createa`stock.landed.cost`recordassociatedtotheaccountmoveof`self`,each
        `stock.landed.costs`linesmirroringthecurrent`account.move.line`ofself.
        """
        self.ensure_one()
        landed_costs_lines=self.line_ids.filtered(lambdaline:line.is_landed_costs_line)

        landed_costs=self.env['stock.landed.cost'].create({
            'vendor_bill_id':self.id,
            'cost_lines':[(0,0,{
                'product_id':l.product_id.id,
                'name':l.product_id.name,
                'account_id':l.product_id.product_tmpl_id.get_product_accounts()['stock_input'].id,
                'price_unit':l.currency_id._convert(l.price_subtotal,l.company_currency_id,l.company_id,l.move_id.date),
                'split_method':l.product_id.split_method_landed_costor'equal',
            })forlinlanded_costs_lines],
        })
        action=self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        returndict(action,view_mode='form',res_id=landed_costs.id,views=[(False,'form')])

    defaction_view_landed_costs(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        domain=[('id','in',self.landed_costs_ids.ids)]
        context=dict(self.env.context,default_vendor_bill_id=self.id)
        views=[(self.env.ref('stock_landed_costs.view_stock_landed_cost_tree2').id,'tree'),(False,'form'),(False,'kanban')]
        returndict(action,domain=domain,context=context,views=views)


classAccountMoveLine(models.Model):
    _inherit='account.move.line'

    product_type=fields.Selection(related='product_id.type',readonly=True)
    is_landed_costs_line=fields.Boolean()

    @api.onchange('is_landed_costs_line')
    def_onchange_is_landed_costs_line(self):
        """Markaninvoicelineasalandedcostlineandadapt`self.account_id`.Thedefault
        valuecanbesetaccordingto`self.product_id.landed_cost_ok`."""
        ifself.product_id:
            accounts=self.product_id.product_tmpl_id._get_product_accounts()
            aml_account=accounts['expense']
            ifself.product_type!='service':
                self.is_landed_costs_line=False
            elifself.is_landed_costs_line:
                aml_account=(self.move_id.company_id.anglo_saxon_accountingandaccounts['stock_input'])oraml_account
            self.account_id=aml_account

    @api.onchange('product_id')
    def_onchange_is_landed_costs_line_product(self):
        ifself.product_id.landed_cost_ok:
            self.is_landed_costs_line=True
        else:
            self.is_landed_costs_line=False

    def_can_use_stock_accounts(self):
        returnsuper()._can_use_stock_accounts()or(self.product_id.type=='service'andself.product_id.landed_cost_ok)
