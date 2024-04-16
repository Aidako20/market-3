#-*-encoding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimportdatetime,time

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


PURCHASE_REQUISITION_STATES=[
    ('draft','Draft'),
    ('ongoing','Ongoing'),
    ('in_progress','Confirmed'),
    ('open','BidSelection'),
    ('done','Closed'),
    ('cancel','Cancelled')
]


classPurchaseRequisitionType(models.Model):
    _name="purchase.requisition.type"
    _description="PurchaseRequisitionType"
    _order="sequence"

    name=fields.Char(string='AgreementType',required=True,translate=True)
    sequence=fields.Integer(default=1)
    exclusive=fields.Selection([
        ('exclusive','SelectonlyoneRFQ(exclusive)'),('multiple','SelectmultipleRFQ(non-exclusive)')],
        string='AgreementSelectionType',required=True,default='multiple',
            help="""SelectonlyoneRFQ(exclusive): whenapurchaseorderisconfirmed,canceltheremainingpurchaseorder.\n
                    SelectmultipleRFQ(non-exclusive):allowsmultiplepurchaseorders.Onconfirmationofapurchaseorderitdoesnotcanceltheremainingorders""")
    quantity_copy=fields.Selection([
        ('copy','Usequantitiesofagreement'),('none','Setquantitiesmanually')],
        string='Quantities',required=True,default='none')
    line_copy=fields.Selection([
        ('copy','Uselinesofagreement'),('none','DonotcreateRfQlinesautomatically')],
        string='Lines',required=True,default='copy')


classPurchaseRequisition(models.Model):
    _name="purchase.requisition"
    _description="PurchaseRequisition"
    _inherit=['mail.thread','mail.activity.mixin']
    _order="iddesc"

    def_get_type_id(self):
        returnself.env['purchase.requisition.type'].search([],limit=1)

    name=fields.Char(string='Reference',required=True,copy=False,default='New',readonly=True)
    origin=fields.Char(string='SourceDocument')
    order_count=fields.Integer(compute='_compute_orders_number',string='NumberofOrders')
    vendor_id=fields.Many2one('res.partner',string="Vendor",domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    type_id=fields.Many2one('purchase.requisition.type',string="AgreementType",required=True,default=_get_type_id)
    ordering_date=fields.Date(string="OrderingDate",tracking=True)
    date_end=fields.Datetime(string='AgreementDeadline',tracking=True)
    schedule_date=fields.Date(string='DeliveryDate',index=True,help="Theexpectedandscheduleddeliverydatewherealltheproductsarereceived",tracking=True)
    user_id=fields.Many2one(
        'res.users',string='PurchaseRepresentative',
        default=lambdaself:self.env.user,check_company=True)
    description=fields.Text()
    company_id=fields.Many2one('res.company',string='Company',required=True,default=lambdaself:self.env.company)
    purchase_ids=fields.One2many('purchase.order','requisition_id',string='PurchaseOrders',states={'done':[('readonly',True)]})
    line_ids=fields.One2many('purchase.requisition.line','requisition_id',string='ProductstoPurchase',states={'done':[('readonly',True)]},copy=True)
    product_id=fields.Many2one('product.product',related='line_ids.product_id',string='Product',readonly=False)
    state=fields.Selection(PURCHASE_REQUISITION_STATES,
                              'Status',tracking=True,required=True,
                              copy=False,default='draft')
    state_blanket_order=fields.Selection(PURCHASE_REQUISITION_STATES,compute='_set_state')
    is_quantity_copy=fields.Selection(related='type_id.quantity_copy',readonly=True)
    currency_id=fields.Many2one('res.currency','Currency',required=True,
        default=lambdaself:self.env.company.currency_id.id)

    @api.depends('state')
    def_set_state(self):
        forrequisitioninself:
            requisition.state_blanket_order=requisition.state

    @api.onchange('vendor_id')
    def_onchange_vendor(self):
        self=self.with_company(self.company_id)
        ifnotself.vendor_id:
            self.currency_id=self.env.company.currency_id.id
        else:
            self.currency_id=self.vendor_id.property_purchase_currency_id.idorself.env.company.currency_id.id

        requisitions=self.env['purchase.requisition'].search([
            ('vendor_id','=',self.vendor_id.id),
            ('state','=','ongoing'),
            ('type_id.quantity_copy','=','none'),
            ('company_id','=',self.company_id.id),
        ])
        ifany(requisitions):
            title=_("Warningfor%s",self.vendor_id.name)
            message=_("Thereisalreadyanopenblanketorderforthissupplier.Wesuggestyoucompletethisopenblanketorder,insteadofcreatinganewone.")
            warning={
                'title':title,
                'message':message
            }
            return{'warning':warning}

    @api.depends('purchase_ids')
    def_compute_orders_number(self):
        forrequisitioninself:
            requisition.order_count=len(requisition.purchase_ids)

    defaction_cancel(self):
        #trytosetallassociatedquotationstocancelstate
        forrequisitioninself:
            forrequisition_lineinrequisition.line_ids:
                requisition_line.supplier_info_ids.unlink()
            requisition.purchase_ids.button_cancel()
            forpoinrequisition.purchase_ids:
                po.message_post(body=_('Cancelledbytheagreementassociatedtothisquotation.'))
        self.write({'state':'cancel'})

    defaction_in_progress(self):
        self.ensure_one()
        ifnotself.line_ids:
            raiseUserError(_("Youcannotconfirmagreement'%s'becausethereisnoproductline.",self.name))
        ifself.type_id.quantity_copy=='none'andself.vendor_id:
            forrequisition_lineinself.line_ids:
                ifrequisition_line.price_unit<=0.0:
                    raiseUserError(_('Youcannotconfirmtheblanketorderwithoutprice.'))
                ifrequisition_line.product_qty<=0.0:
                    raiseUserError(_('Youcannotconfirmtheblanketorderwithoutquantity.'))
                requisition_line.create_supplier_info()
            self.write({'state':'ongoing'})
        else:
            self.write({'state':'in_progress'})
        #Setthesequencenumberregardingtherequisitiontype
        ifself.name=='New':
            ifself.is_quantity_copy!='none':
                self.name=self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.tender')
            else:
                self.name=self.env['ir.sequence'].next_by_code('purchase.requisition.blanket.order')

    defaction_open(self):
        self.write({'state':'open'})

    defaction_draft(self):
        self.ensure_one()
        self.name='New'
        self.write({'state':'draft'})

    defaction_done(self):
        """
        Generateallpurchaseorderbasedonselectedlines,shouldonlybecalledononeagreementatatime
        """
        ifany(purchase_order.statein['draft','sent','toapprove']forpurchase_orderinself.mapped('purchase_ids')):
            raiseUserError(_('YouhavetocancelorvalidateeveryRfQbeforeclosingthepurchaserequisition.'))
        forrequisitioninself:
            forrequisition_lineinrequisition.line_ids:
                requisition_line.supplier_info_ids.unlink()
        self.write({'state':'done'})

    defunlink(self):
        ifany(requisition.statenotin('draft','cancel')forrequisitioninself):
            raiseUserError(_('Youcanonlydeletedraftrequisitions.'))
        #Draftrequisitionscouldhavesomerequisitionlines.
        self.mapped('line_ids').unlink()
        returnsuper(PurchaseRequisition,self).unlink()


classPurchaseRequisitionLine(models.Model):
    _name="purchase.requisition.line"
    _description="PurchaseRequisitionLine"
    _rec_name='product_id'

    product_id=fields.Many2one('product.product',string='Product',domain=[('purchase_ok','=',True)],required=True)
    product_uom_id=fields.Many2one('uom.uom',string='ProductUnitofMeasure',domain="[('category_id','=',product_uom_category_id)]")
    product_uom_category_id=fields.Many2one(related='product_id.uom_id.category_id')
    product_qty=fields.Float(string='Quantity',digits='ProductUnitofMeasure')
    product_description_variants=fields.Char('CustomDescription')
    price_unit=fields.Float(string='UnitPrice',digits='ProductPrice')
    qty_ordered=fields.Float(compute='_compute_ordered_qty',string='OrderedQuantities')
    requisition_id=fields.Many2one('purchase.requisition',required=True,string='PurchaseAgreement',ondelete='cascade')
    company_id=fields.Many2one('res.company',related='requisition_id.company_id',string='Company',store=True,readonly=True,default=lambdaself:self.env.company)
    account_analytic_id=fields.Many2one('account.analytic.account',string='AnalyticAccount',store=True,compute='_compute_account_analytic_id',readonly=False)
    analytic_tag_ids=fields.Many2many('account.analytic.tag',string='AnalyticTags',store=True,compute='_compute_analytic_tag_ids',readonly=False)
    schedule_date=fields.Date(string='ScheduledDate')
    supplier_info_ids=fields.One2many('product.supplierinfo','purchase_requisition_line_id')

    @api.model
    defcreate(self,vals):
        res=super(PurchaseRequisitionLine,self).create(vals)
        ifres.requisition_id.statenotin['draft','cancel','done']andres.requisition_id.is_quantity_copy=='none':
            supplier_infos=self.env['product.supplierinfo'].search([
                ('product_id','=',vals.get('product_id')),
                ('name','=',res.requisition_id.vendor_id.id),
            ])
            ifnotany(s.purchase_requisition_idforsinsupplier_infos):
                res.create_supplier_info()
            ifvals['price_unit']<=0.0:
                raiseUserError(_('Youcannotconfirmtheblanketorderwithoutprice.'))
        returnres

    defwrite(self,vals):
        res=super(PurchaseRequisitionLine,self).write(vals)
        if'price_unit'invals:
            ifvals['price_unit']<=0.0andany(
                    requisition.statenotin['draft','cancel','done']and
                    requisition.is_quantity_copy=='none'forrequisitioninself.mapped('requisition_id')):
                raiseUserError(_('Youcannotconfirmtheblanketorderwithoutprice.'))
            #Ifthepriceisupdated,wehavetoupdatetherelatedSupplierInfo
            self.supplier_info_ids.write({'price':vals['price_unit']})
        returnres

    defunlink(self):
        to_unlink=self.filtered(lambdar:r.requisition_id.statenotin['draft','cancel','done'])
        to_unlink.mapped('supplier_info_ids').unlink()
        returnsuper(PurchaseRequisitionLine,self).unlink()

    defcreate_supplier_info(self):
        purchase_requisition=self.requisition_id
        ifpurchase_requisition.type_id.quantity_copy=='none'andpurchase_requisition.vendor_id:
            #createasupplier_infoonlyincaseofblanketorder
            self.env['product.supplierinfo'].create({
                'name':purchase_requisition.vendor_id.id,
                'product_id':self.product_id.id,
                'product_tmpl_id':self.product_id.product_tmpl_id.id,
                'price':self.price_unit,
                'currency_id':self.requisition_id.currency_id.id,
                'purchase_requisition_line_id':self.id,
            })

    @api.depends('requisition_id.purchase_ids.state')
    def_compute_ordered_qty(self):
        line_found=set()
        forlineinself:
            total=0.0
            forpoinline.requisition_id.purchase_ids.filtered(lambdapurchase_order:purchase_order.statein['purchase','done']):
                forpo_lineinpo.order_line.filtered(lambdaorder_line:order_line.product_id==line.product_id):
                    ifpo_line.product_uom!=line.product_uom_id:
                        total+=po_line.product_uom._compute_quantity(po_line.product_qty,line.product_uom_id)
                    else:
                        total+=po_line.product_qty
            ifline.product_idnotinline_found:
                line.qty_ordered=total
                line_found.add(line.product_id)
            else:
                line.qty_ordered=0

    @api.depends('product_id','schedule_date')
    def_compute_account_analytic_id(self):
        forlineinself:
            default_analytic_account=line.env['account.analytic.default'].sudo().account_get(
                product_id=line.product_id.id,
                partner_id=line.requisition_id.vendor_id.id,
                user_id=line.env.uid,
                date=line.schedule_date,
                company_id=line.company_id.id,
            )
            line.account_analytic_id=default_analytic_account.analytic_id

    @api.depends('product_id','schedule_date')
    def_compute_analytic_tag_ids(self):
        forlineinself:
            default_analytic_account=line.env['account.analytic.default'].sudo().account_get(
                product_id=line.product_id.id,
                partner_id=line.requisition_id.vendor_id.id,
                user_id=line.env.uid,
                date=line.schedule_date,
                company_id=line.company_id.id,
            )
            line.analytic_tag_ids=default_analytic_account.analytic_tag_ids

    @api.onchange('product_id')
    def_onchange_product_id(self):
        ifself.product_id:
            self.product_uom_id=self.product_id.uom_po_id
            self.product_qty=1.0
        ifnotself.schedule_date:
            self.schedule_date=self.requisition_id.schedule_date

    def_prepare_purchase_order_line(self,name,product_qty=0.0,price_unit=0.0,taxes_ids=False):
        self.ensure_one()
        requisition=self.requisition_id
        ifself.product_description_variants:
            name+='\n'+self.product_description_variants
        ifrequisition.schedule_date:
            date_planned=datetime.combine(requisition.schedule_date,time.min)
        else:
            date_planned=datetime.now()
        return{
            'name':name,
            'product_id':self.product_id.id,
            'product_uom':self.product_id.uom_po_id.id,
            'product_qty':product_qty,
            'price_unit':price_unit,
            'taxes_id':[(6,0,taxes_ids)],
            'date_planned':date_planned,
            'account_analytic_id':self.account_analytic_id.id,
            'analytic_tag_ids':self.analytic_tag_ids.ids,
        }
