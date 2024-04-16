#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classProjectTaskCreateSalesOrder(models.TransientModel):
    _name='project.task.create.sale.order'
    _description="CreateSOfromtask"

    @api.model
    defdefault_get(self,fields):
        result=super(ProjectTaskCreateSalesOrder,self).default_get(fields)

        active_model=self._context.get('active_model')
        ifactive_model!='project.task':
            raiseUserError(_("Youcanonlyapplythisactionfromatask."))

        active_id=self._context.get('active_id')
        if'task_id'infieldsandactive_id:
            task=self.env['project.task'].browse(active_id)
            iftask.sale_order_id:
                raiseUserError(_("Thetaskhasalreadyasaleorder."))
            result['task_id']=active_id
            ifnotresult.get('partner_id',False):
                result['partner_id']=task.partner_id.id
        returnresult

    link_selection=fields.Selection([('create','Createanewsalesorder'),('link','Linktoanexistingsalesorder')],required=True,default='create')

    task_id=fields.Many2one('project.task',"Task",domain=[('sale_line_id','=',False)],help="Taskforwhichwearecreatingasalesorder",required=True)
    partner_id=fields.Many2one('res.partner',string="Customer",help="Customerofthesalesorder",required=True)
    product_id=fields.Many2one('product.product',domain=[('type','=','service'),('invoice_policy','=','delivery'),('service_type','=','timesheet')],string="Service",help="Productofthesalesorderitem.Mustbeaserviceinvoicedbasedontimesheetsontasks.Theexistingtimesheetwillbelinkedtothisproduct.",required=True)
    price_unit=fields.Float("UnitPrice",help="Unitpriceofthesalesorderitem.")
    currency_id=fields.Many2one('res.currency',string="Currency",related='product_id.currency_id',readonly=False)
    commercial_partner_id=fields.Many2one(related='partner_id.commercial_partner_id')
    sale_order_id=fields.Many2one(
        'sale.order',string="SalesOrder",
        domain="['|','|',('partner_id','=',partner_id),('partner_id','child_of',commercial_partner_id),('partner_id','parent_of',partner_id)]")
    sale_line_id=fields.Many2one(
        'sale.order.line','SalesOrderItem',
        domain="[('is_service','=',True),('order_partner_id','child_of',commercial_partner_id),('is_expense','=',False),('state','in',['sale','done']),('order_id','=?',sale_order_id)]")

    info_invoice=fields.Char(compute='_compute_info_invoice')

    @api.depends('sale_line_id','price_unit','link_selection')
    def_compute_info_invoice(self):
        forlineinself:
            domain=self.env['sale.order.line']._timesheet_compute_delivered_quantity_domain()
            timesheet=self.env['account.analytic.line'].read_group(domain+[('task_id','=',self.task_id.id),('so_line','=',False),('timesheet_invoice_id','=',False)],['unit_amount'],['task_id'])
            unit_amount=round(timesheet[0].get('unit_amount',0),2)iftimesheetelse0
            ifnotunit_amount:
                line.info_invoice=False
                continue
            company_uom=self.env.company.timesheet_encode_uom_id
            label=_("hours")
            ifcompany_uom==self.env.ref('uom.product_uom_day'):
                label=_("days")
            ifline.link_selection=='create'andline.price_unit:
                line.info_invoice=_("%(amount)s%(label)swillbeaddedtothenewSalesOrder.",amount=unit_amount,label=label)
            else:
                line.info_invoice=_("%(amount)s%(label)swillbeaddedtotheselectedSalesOrder.",amount=unit_amount,label=label)

    @api.onchange('product_id')
    def_onchange_product_id(self):
        ifself.product_id:
            self.price_unit=self.product_id.lst_price
        else:
            self.price_unit=0.0

    @api.onchange('partner_id')
    def_onchange_partner_id(self):
        self.sale_order_id=False
        self.sale_line_id=False

    @api.onchange('sale_order_id')
    def_onchange_sale_order_id(self):
        self.sale_line_id=False

    defaction_link_sale_order(self):
        #linktasktoSOL
        self.task_id.write({
            'sale_line_id':self.sale_line_id.id,
            'partner_id':self.partner_id.id,
            'email_from':self.partner_id.email,
        })

        #assignSOLtotimesheets
        self.env['account.analytic.line'].search([('task_id','=',self.task_id.id),('so_line','=',False),('timesheet_invoice_id','=',False)]).write({
            'so_line':self.sale_line_id.id
        })

    defaction_create_sale_order(self):
        sale_order=self._prepare_sale_order()
        sale_order.action_confirm()
        view_form_id=self.env.ref('sale.view_order_form').id
        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action.update({
            'views':[(view_form_id,'form')],
            'view_mode':'form',
            'name':sale_order.name,
            'res_id':sale_order.id,
        })
        returnaction

    def_prepare_sale_order(self):
        #iftasklinkedtoSOline,thenweconsideritasbillable.
        ifself.task_id.sale_line_id:
            raiseUserError(_("Thetaskisalreadylinkedtoasalesorderitem."))

        #createSO
        sale_order=self.env['sale.order'].create({
            'partner_id':self.partner_id.id,
            'company_id':self.task_id.company_id.id,
            'analytic_account_id':self.task_id.project_id.analytic_account_id.id,
        })
        sale_order.onchange_partner_id()
        sale_order.onchange_partner_shipping_id()
        #rewritetheuserastheonchange_partner_iderasesit
        sale_order.write({'user_id':self.task_id.user_id.id})
        sale_order.onchange_user_id()

        sale_order_line=self.env['sale.order.line'].create({
            'order_id':sale_order.id,
            'product_id':self.product_id.id,
            'price_unit':self.price_unit,
            'project_id':self.task_id.project_id.id, #preventtore-createaprojectonconfirmation
            'task_id':self.task_id.id,
            'product_uom_qty':round(sum(self.task_id.timesheet_ids.filtered(lambdat:nott.non_allow_billableandnott.so_line).mapped('unit_amount')),2),
        })

        #linktasktoSOL
        self.task_id.write({
            'sale_line_id':sale_order_line.id,
            'partner_id':sale_order.partner_id.id,
            'email_from':sale_order.partner_id.email,
        })

        #assignSOLtotimesheets
        self.env['account.analytic.line'].search([('task_id','=',self.task_id.id),('so_line','=',False),('timesheet_invoice_id','=',False)]).write({
            'so_line':sale_order_line.id
        })

        returnsale_order
