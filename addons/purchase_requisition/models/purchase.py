#-*-encoding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classPurchaseOrder(models.Model):
    _inherit='purchase.order'

    requisition_id=fields.Many2one('purchase.requisition',string='PurchaseAgreement',copy=False)
    is_quantity_copy=fields.Selection(related='requisition_id.is_quantity_copy',readonly=False)

    @api.onchange('requisition_id')
    def_onchange_requisition_id(self):
        ifnotself.requisition_id:
            return

        self=self.with_company(self.company_id)
        requisition=self.requisition_id
        ifself.partner_id:
            partner=self.partner_id
        else:
            partner=requisition.vendor_id
        payment_term=partner.property_supplier_payment_term_id

        FiscalPosition=self.env['account.fiscal.position']
        fpos=FiscalPosition.with_company(self.company_id).get_fiscal_position(partner.id)

        self.partner_id=partner.id
        self.fiscal_position_id=fpos.id
        self.payment_term_id=payment_term.id,
        self.company_id=requisition.company_id.id
        self.currency_id=requisition.currency_id.id
        ifnotself.originorrequisition.namenotinself.origin.split(','):
            ifself.origin:
                ifrequisition.name:
                    self.origin=self.origin+','+requisition.name
            else:
                self.origin=requisition.name
        self.notes=requisition.description
        self.date_order=fields.Datetime.now()

        ifrequisition.type_id.line_copy!='copy':
            return

        #CreatePOlinesifnecessary
        order_lines=[]
        forlineinrequisition.line_ids:
            #Computename
            product_lang=line.product_id.with_context(
                lang=partner.langorself.env.user.lang,
                partner_id=partner.id
            )
            name=product_lang.display_name
            ifproduct_lang.description_purchase:
                name+='\n'+product_lang.description_purchase

            #Computetaxes
            taxes_ids=fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambdatax:tax.company_id==requisition.company_id)).ids

            #Computequantityandprice_unit
            ifline.product_uom_id!=line.product_id.uom_po_id:
                product_qty=line.product_uom_id._compute_quantity(line.product_qty,line.product_id.uom_po_id)
                price_unit=line.product_uom_id._compute_price(line.price_unit,line.product_id.uom_po_id)
            else:
                product_qty=line.product_qty
                price_unit=line.price_unit

            ifrequisition.type_id.quantity_copy!='copy':
                product_qty=0

            #CreatePOline
            order_line_values=line._prepare_purchase_order_line(
                name=name,product_qty=product_qty,price_unit=price_unit,
                taxes_ids=taxes_ids)
            order_lines.append((0,0,order_line_values))
        self.order_line=order_lines

    defbutton_confirm(self):
        res=super(PurchaseOrder,self).button_confirm()
        forpoinself:
            ifnotpo.requisition_id:
                continue
            ifpo.requisition_id.type_id.exclusive=='exclusive':
                others_po=po.requisition_id.mapped('purchase_ids').filtered(lambdar:r.id!=po.id)
                others_po.button_cancel()
                ifpo.statenotin['draft','sent','toapprove']:
                    po.requisition_id.action_done()
        returnres

    @api.model
    defcreate(self,vals):
        purchase=super(PurchaseOrder,self).create(vals)
        ifpurchase.requisition_id:
            purchase.message_post_with_view('mail.message_origin_link',
                    values={'self':purchase,'origin':purchase.requisition_id},
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'))
        returnpurchase

    defwrite(self,vals):
        result=super(PurchaseOrder,self).write(vals)
        ifvals.get('requisition_id'):
            self.message_post_with_view('mail.message_origin_link',
                    values={'self':self,'origin':self.requisition_id,'edit':True},
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'))
        returnresult


classPurchaseOrderLine(models.Model):
    _inherit='purchase.order.line'

    def_compute_account_analytic_id(self):
        super(PurchaseOrderLine,self.filtered(lambdapol:notpol.order_id.requisition_id))._compute_account_analytic_id()

    def_compute_analytic_tag_ids(self):
        super(PurchaseOrderLine,self.filtered(lambdapol:notpol.order_id.requisition_id))._compute_analytic_tag_ids()

    @api.onchange('product_qty','product_uom')
    def_onchange_quantity(self):
        res=super(PurchaseOrderLine,self)._onchange_quantity()
        ifself.order_id.requisition_id:
            forlineinself.order_id.requisition_id.line_ids.filtered(lambdal:l.product_id==self.product_id):
                ifline.product_uom_id!=self.product_uom:
                    self.price_unit=line.product_uom_id._compute_price(
                        line.price_unit,self.product_uom)
                else:
                    self.price_unit=line.price_unit
                break
        returnres
