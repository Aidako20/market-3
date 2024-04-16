#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classProjectCreateInvoice(models.TransientModel):
    _name='project.create.invoice'
    _description="CreateInvoicefromproject"

    @api.model
    defdefault_get(self,fields):
        result=super(ProjectCreateInvoice,self).default_get(fields)

        active_model=self._context.get('active_model')
        ifactive_model!='project.project':
            raiseUserError(_('Youcanonlyapplythisactionfromaproject.'))

        active_id=self._context.get('active_id')
        if'project_id'infieldsandactive_id:
            result['project_id']=active_id
        returnresult

    project_id=fields.Many2one('project.project',"Project",help="Projecttomakebillable",required=True)
    _candidate_orders=fields.Many2many('sale.order',compute='_compute_candidate_orders')
    sale_order_id=fields.Many2one(
        'sale.order',string="ChoosetheSalesOrdertoinvoice",required=True,
        domain="[('id','in',_candidate_orders)]"
    )
    amount_to_invoice=fields.Monetary("Amounttoinvoice",compute='_compute_amount_to_invoice',currency_field='currency_id',help="Totalamounttoinvoiceonthesalesorder,includingallitems(services,storables,expenses,...)")
    currency_id=fields.Many2one(related='sale_order_id.currency_id',readonly=True)

    @api.depends('project_id.tasks.sale_line_id.order_id.invoice_status')
    def_compute_candidate_orders(self):
        forpinself:
            p._candidate_orders=p.project_id\
                .mapped('tasks.sale_line_id.order_id')\
                .filtered(lambdaso:so.invoice_status=='toinvoice')

    @api.depends('sale_order_id')
    def_compute_amount_to_invoice(self):
        forwizardinself:
            amount_untaxed=0.0
            amount_tax=0.0
            forlineinwizard.sale_order_id.order_line.filtered(lambdasol:sol.invoice_status=='toinvoice'):
                amount_untaxed+=line.price_reduce*line.qty_to_invoice
                amount_tax+=line.price_tax
            wizard.amount_to_invoice=amount_untaxed+amount_tax

    defaction_create_invoice(self):
        ifnotself.sale_order_idandself.sale_order_id.invoice_status!='toinvoice':
            raiseUserError(_("TheselectedSalesOrdershouldcontainsomethingtoinvoice."))
        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_view_sale_advance_payment_inv")
        action['context']={
            'active_ids':self.sale_order_id.ids
        }
        returnaction
