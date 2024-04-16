#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.toolsimportfloat_compare
fromflectra.tools.miscimportget_lang


classSaleOrder(models.Model):
    _inherit='sale.order'

    purchase_order_count=fields.Integer(
        "NumberofPurchaseOrderGenerated",
        compute='_compute_purchase_order_count',
        groups='purchase.group_purchase_user')

    @api.depends('order_line.purchase_line_ids.order_id')
    def_compute_purchase_order_count(self):
        fororderinself:
            order.purchase_order_count=len(order._get_purchase_orders())

    def_action_confirm(self):
        result=super(SaleOrder,self)._action_confirm()
        fororderinself:
            order.order_line.sudo()._purchase_service_generation()
        returnresult

    def_action_cancel(self):
        result=super()._action_cancel()
        #WhenasalepersoncancelaSO,hemightnothavetherightstowrite
        #onPO.ButweneedthesystemtocreateanactivityonthePO(so'write'
        #access),hencethe`sudo`.
        self.sudo()._activity_cancel_on_purchase()
        returnresult

    defaction_view_purchase_orders(self):
        self.ensure_one()
        purchase_order_ids=self._get_purchase_orders().ids
        action={
            'res_model':'purchase.order',
            'type':'ir.actions.act_window',
        }
        iflen(purchase_order_ids)==1:
            action.update({
                'view_mode':'form',
                'res_id':purchase_order_ids[0],
            })
        else:
            action.update({
                'name':_("PurchaseOrdergeneratedfrom%s",self.name),
                'domain':[('id','in',purchase_order_ids)],
                'view_mode':'tree,form',
            })
        returnaction

    def_get_purchase_orders(self):
        returnself.order_line.purchase_line_ids.order_id

    def_activity_cancel_on_purchase(self):
        """IfsomeSOarecancelled,weneedtoputanactivityontheirgeneratedpurchase.Ifsalelinesof
            differentsaleordersimpactdifferentpurchase,weonlywantoneactivitytobeattached.
        """
        purchase_to_notify_map={} #mapPO->recordsetofSOLas{purchase.order:set(sale.orde.liner)}

        purchase_order_lines=self.env['purchase.order.line'].search([('sale_line_id','in',self.mapped('order_line').ids),('state','!=','cancel')])
        forpurchase_lineinpurchase_order_lines:
            purchase_to_notify_map.setdefault(purchase_line.order_id,self.env['sale.order.line'])
            purchase_to_notify_map[purchase_line.order_id]|=purchase_line.sale_line_id

        forpurchase_order,sale_order_linesinpurchase_to_notify_map.items():
            purchase_order._activity_schedule_with_view('mail.mail_activity_data_warning',
                user_id=purchase_order.user_id.idorself.env.uid,
                views_or_xmlid='sale_purchase.exception_purchase_on_sale_cancellation',
                render_context={
                    'sale_orders':sale_order_lines.mapped('order_id'),
                    'sale_order_lines':sale_order_lines,
            })


classSaleOrderLine(models.Model):
    _inherit='sale.order.line'

    purchase_line_ids=fields.One2many('purchase.order.line','sale_line_id',string="GeneratedPurchaseLines",readonly=True,help="PurchaselinegeneratedbythisSalesitemonorderconfirmation,orwhenthequantitywasincreased.")
    purchase_line_count=fields.Integer("Numberofgeneratedpurchaseitems",compute='_compute_purchase_count')

    @api.depends('purchase_line_ids')
    def_compute_purchase_count(self):
        database_data=self.env['purchase.order.line'].sudo().read_group([('sale_line_id','in',self.ids)],['sale_line_id'],['sale_line_id'])
        mapped_data=dict([(db['sale_line_id'][0],db['sale_line_id_count'])fordbindatabase_data])
        forlineinself:
            line.purchase_line_count=mapped_data.get(line.id,0)

    @api.onchange('product_uom_qty')
    def_onchange_service_product_uom_qty(self):
        ifself.state=='sale'andself.product_id.type=='service'andself.product_id.service_to_purchase:
            ifself.product_uom_qty<self._origin.product_uom_qty:
                ifself.product_uom_qty<self.qty_delivered:
                    return{}
                warning_mess={
                    'title':_('Orderedquantitydecreased!'),
                    'message':_('Youaredecreasingtheorderedquantity!Donotforgettomanuallyupdatethepurchaseorderifneeded.'),
                }
                return{'warning':warning_mess}
        return{}

    #--------------------------
    #CRUD
    #--------------------------

    @api.model_create_multi
    defcreate(self,values):
        lines=super(SaleOrderLine,self).create(values)
        #DonotgeneratepurchasewhenexpenseSOlinesincetheproductisalreadydelivered
        lines.filtered(
            lambdaline:line.state=='sale'andnotline.is_expense
        )._purchase_service_generation()
        returnlines

    defwrite(self,values):
        increased_lines=None
        decreased_lines=None
        increased_values={}
        decreased_values={}
        if'product_uom_qty'invalues:
            precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
            increased_lines=self.sudo().filtered(lambdar:r.product_id.service_to_purchaseandr.purchase_line_countandfloat_compare(r.product_uom_qty,values['product_uom_qty'],precision_digits=precision)==-1)
            decreased_lines=self.sudo().filtered(lambdar:r.product_id.service_to_purchaseandr.purchase_line_countandfloat_compare(r.product_uom_qty,values['product_uom_qty'],precision_digits=precision)==1)
            increased_values={line.id:line.product_uom_qtyforlineinincreased_lines}
            decreased_values={line.id:line.product_uom_qtyforlineindecreased_lines}

        result=super(SaleOrderLine,self).write(values)

        ifincreased_lines:
            increased_lines._purchase_increase_ordered_qty(values['product_uom_qty'],increased_values)
        ifdecreased_lines:
            decreased_lines._purchase_decrease_ordered_qty(values['product_uom_qty'],decreased_values)
        returnresult

    #--------------------------
    #BusinessMethods
    #--------------------------

    def_purchase_decrease_ordered_qty(self,new_qty,origin_values):
        """DecreasethequantityfromSOlinewilladdanextacitivitiesontherelatedpurchaseorder
            :paramnew_qty:newquantity(lowerthanthecurrentoneonSOline),expressed
                inUoMofSOline.
            :paramorigin_values:mapfromsalelineidtooldvaluefortheorderedquantity(dict)
        """
        purchase_to_notify_map={} #mapPO->set(SOL)
        last_purchase_lines=self.env['purchase.order.line'].search([('sale_line_id','in',self.ids)])
        forpurchase_lineinlast_purchase_lines:
            purchase_to_notify_map.setdefault(purchase_line.order_id,self.env['sale.order.line'])
            purchase_to_notify_map[purchase_line.order_id]|=purchase_line.sale_line_id

        #createnextactivity
        forpurchase_order,sale_linesinpurchase_to_notify_map.items():
            render_context={
                'sale_lines':sale_lines,
                'sale_orders':sale_lines.mapped('order_id'),
                'origin_values':origin_values,
            }
            purchase_order._activity_schedule_with_view('mail.mail_activity_data_warning',
                user_id=purchase_order.user_id.idorself.env.uid,
                views_or_xmlid='sale_purchase.exception_purchase_on_sale_quantity_decreased',
                render_context=render_context)

    def_purchase_increase_ordered_qty(self,new_qty,origin_values):
        """Increasethequantityontherelatedpurchaselines
            :paramnew_qty:newquantity(higherthanthecurrentoneonSOline),expressed
                inUoMofSOline.
            :paramorigin_values:mapfromsalelineidtooldvaluefortheorderedquantity(dict)
        """
        forlineinself:
            last_purchase_line=self.env['purchase.order.line'].search([('sale_line_id','=',line.id)],order='create_dateDESC',limit=1)
            iflast_purchase_line.statein['draft','sent','toapprove']: #updateqtyfordraftPOlines
                quantity=line.product_uom._compute_quantity(new_qty,last_purchase_line.product_uom)
                last_purchase_line.write({'product_qty':quantity})
            eliflast_purchase_line.statein['purchase','done','cancel']: #createnewPO,byforcingthequantityasthedifferencefromSOline
                quantity=line.product_uom._compute_quantity(new_qty-origin_values.get(line.id,0.0),last_purchase_line.product_uom)
                line._purchase_service_create(quantity=quantity)

    def_purchase_get_date_order(self,supplierinfo):
        """returntheordereddateforthepurchaseorder,computedas:SOcommitmentdate-supplierdelay"""
        commitment_date=fields.Datetime.from_string(self.order_id.commitment_dateorfields.Datetime.now())
        returncommitment_date-relativedelta(days=int(supplierinfo.delay))

    def_purchase_service_prepare_order_values(self,supplierinfo):
        """ReturnsthevaluestocreatethepurchaseorderfromthecurrentSOline.
            :paramsupplierinfo:recordofproduct.supplierinfo
            :rtype:dict
        """
        self.ensure_one()
        partner_supplier=supplierinfo.name
        fpos=self.env['account.fiscal.position'].sudo().get_fiscal_position(partner_supplier.id)
        date_order=self._purchase_get_date_order(supplierinfo)
        return{
            'partner_id':partner_supplier.id,
            'partner_ref':partner_supplier.ref,
            'company_id':self.company_id.id,
            'currency_id':partner_supplier.property_purchase_currency_id.idorself.env.company.currency_id.id,
            'dest_address_id':False,#Falsesinceonlysupportedinstock
            'origin':self.order_id.name,
            'payment_term_id':partner_supplier.property_supplier_payment_term_id.id,
            'date_order':date_order,
            'fiscal_position_id':fpos.id,
        }

    def_purchase_service_prepare_line_values(self,purchase_order,quantity=False):
        """ReturnsthevaluestocreatethepurchaseorderlinefromthecurrentSOline.
            :parampurchase_order:recordofpurchase.order
            :rtype:dict
            :paramquantity:thequantitytoforceonthePOline,expressedinSOlineUoM
        """
        self.ensure_one()
        #computequantityfromSOlineUoM
        product_quantity=self.product_uom_qty
        ifquantity:
            product_quantity=quantity

        purchase_qty_uom=self.product_uom._compute_quantity(product_quantity,self.product_id.uom_po_id)

        #determinevendor(realsupplier,sharingthesamepartnerastheonefromthePO,butwithmoreaccurateinformationslikevalidity,quantity,...)
        #Note:onepartnercanhavemultiplesupplierinfoforthesameproduct
        supplierinfo=self.product_id._select_seller(
            partner_id=purchase_order.partner_id,
            quantity=purchase_qty_uom,
            date=purchase_order.date_orderandpurchase_order.date_order.date(),#andpurchase_order.date_order[:10],
            uom_id=self.product_id.uom_po_id
        )
        fpos=purchase_order.fiscal_position_id
        taxes=fpos.map_tax(self.product_id.supplier_taxes_id)
        iftaxes:
            taxes=taxes.filtered(lambdat:t.company_id.id==self.company_id.id)

        #computeunitprice
        price_unit=0.0
        product_ctx={
            'lang':get_lang(self.env,purchase_order.partner_id.lang).code,
            'company_id':purchase_order.company_id,
        }
        ifsupplierinfo:
            price_unit=self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price,self.product_id.supplier_taxes_id,taxes,self.company_id)
            ifpurchase_order.currency_idandsupplierinfo.currency_id!=purchase_order.currency_id:
                price_unit=supplierinfo.currency_id._convert(price_unit,purchase_order.currency_id,purchase_order.company_id,fields.Date.context_today(self))
            product_ctx.update({'seller_id':supplierinfo.id})
        else:
            product_ctx.update({'partner_id':purchase_order.partner_id.id})

        return{
            'name':self.product_id.with_context(**product_ctx).display_name,
            'product_qty':purchase_qty_uom,
            'product_id':self.product_id.id,
            'product_uom':self.product_id.uom_po_id.id,
            'price_unit':price_unit,
            'date_planned':fields.Date.from_string(purchase_order.date_order)+relativedelta(days=int(supplierinfo.delay)),
            'taxes_id':[(6,0,taxes.ids)],
            'order_id':purchase_order.id,
            'sale_line_id':self.id,
        }

    def_purchase_service_create(self,quantity=False):
        """OnSalesOrderconfirmation,somelines(servicesones)cancreateapurchaseorderlineandmaybeapurchaseorder.
            IfalineshouldcreateaRFQ,itwillcheckforexistingPO.Ifnooneisfind,theSOlinewillcreateone,thenadds
            anewPOline.ThecreatedpurchaseorderlinewillbelinkedtotheSOline.
            :paramquantity:thequantitytoforceonthePOline,expressedinSOlineUoM
        """
        PurchaseOrder=self.env['purchase.order']
        supplier_po_map={}
        sale_line_purchase_map={}
        forlineinself:
            line=line.with_company(line.company_id)
            #determinevendoroftheorder(takethefirstmatchingcompanyandproduct)
            suppliers=line.product_id._select_seller(quantity=line.product_uom_qty,uom_id=line.product_uom)
            ifnotsuppliers:
                raiseUserError(_("Thereisnovendorassociatedtotheproduct%s.Pleasedefineavendorforthisproduct.")%(line.product_id.display_name,))
            supplierinfo=suppliers[0]
            partner_supplier=supplierinfo.name #yes,thisfieldisnotexplicit....itisares.partner!

            #determine(orcreate)PO
            purchase_order=supplier_po_map.get(partner_supplier.id)
            ifnotpurchase_order:
                purchase_order=PurchaseOrder.search([
                    ('partner_id','=',partner_supplier.id),
                    ('state','=','draft'),
                    ('company_id','=',line.company_id.id),
                ],limit=1)
            ifnotpurchase_order:
                values=line._purchase_service_prepare_order_values(supplierinfo)
                purchase_order=PurchaseOrder.create(values)
            else: #updateoriginofexistingPO
                so_name=line.order_id.name
                origins=[]
                ifpurchase_order.origin:
                    origins=purchase_order.origin.split(',')+origins
                ifso_namenotinorigins:
                    origins+=[so_name]
                    purchase_order.write({
                        'origin':','.join(origins)
                    })
            supplier_po_map[partner_supplier.id]=purchase_order

            #addaPOlinetothePO
            values=line._purchase_service_prepare_line_values(purchase_order,quantity=quantity)
            purchase_line=line.env['purchase.order.line'].create(values)

            #linkthegeneratedpurchasetotheSOline
            sale_line_purchase_map.setdefault(line,line.env['purchase.order.line'])
            sale_line_purchase_map[line]|=purchase_line
        returnsale_line_purchase_map

    def_purchase_service_generation(self):
        """CreateaPurchaseforthefirsttimefromthesaleline.IftheSOlinealreadycreatedaPO,it
            willnotcreateasecondone.
        """
        sale_line_purchase_map={}
        forlineinself:
            #DonotregeneratePOlineiftheSOlinehasalreadycreatedoneinthepast(SOcancel/reconfirmationcase)
            ifline.product_id.service_to_purchaseandnotline.purchase_line_count:
                result=line._purchase_service_create()
                sale_line_purchase_map.update(result)
        returnsale_line_purchase_map
