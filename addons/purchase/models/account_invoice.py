#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classAccountMove(models.Model):
    _inherit='account.move'

    purchase_vendor_bill_id=fields.Many2one('purchase.bill.union',store=False,readonly=True,
        states={'draft':[('readonly',False)]},
        string='Auto-complete',
        help="Auto-completefromapastbill/purchaseorder.")
    purchase_id=fields.Many2one('purchase.order',store=False,readonly=True,
        states={'draft':[('readonly',False)]},
        string='PurchaseOrder',
        help="Auto-completefromapastpurchaseorder.")

    def_get_invoice_reference(self):
        self.ensure_one()
        vendor_refs=[refforrefinset(self.line_ids.mapped('purchase_line_id.order_id.partner_ref'))ifref]
        ifself.ref:
            return[refforrefinself.ref.split(',')ifrefandrefnotinvendor_refs]+vendor_refs
        returnvendor_refs

    @api.onchange('purchase_vendor_bill_id','purchase_id')
    def_onchange_purchase_auto_complete(self):
        '''Loadfromeitheranoldpurchaseorder,eitheranoldvendorbill.

        Whensettinga'purchase.bill.union'in'purchase_vendor_bill_id':
        *Ifit'savendorbill,'invoice_vendor_bill_id'issetandtheloadingisdoneby'_onchange_invoice_vendor_bill'.
        *Ifit'sapurchaseorder,'purchase_id'issetandthismethodwillloadlines.

        /!\Allthisnot-storedfieldsmustbeemptyattheendofthisfunction.
        '''
        ifself.purchase_vendor_bill_id.vendor_bill_id:
            self.invoice_vendor_bill_id=self.purchase_vendor_bill_id.vendor_bill_id
            self._onchange_invoice_vendor_bill()
        elifself.purchase_vendor_bill_id.purchase_order_id:
            self.purchase_id=self.purchase_vendor_bill_id.purchase_order_id
        self.purchase_vendor_bill_id=False

        ifnotself.purchase_id:
            return

        #CopydatafromPO
        invoice_vals=self.purchase_id.with_company(self.purchase_id.company_id)._prepare_invoice()
        invoice_vals['currency_id']=self.line_idsandself.currency_idorinvoice_vals.get('currency_id')
        delinvoice_vals['ref']
        self.update(invoice_vals)

        #Copypurchaselines.
        po_lines=self.purchase_id.order_line-self.line_ids.mapped('purchase_line_id')
        new_lines=self.env['account.move.line']
        sequence=max(self.line_ids.mapped('sequence'))+1ifself.line_idselse10
        forlineinpo_lines.filtered(lambdal:notl.display_type):
            line_vals=line._prepare_account_move_line(self)
            line_vals.update({'sequence':sequence})
            new_line=new_lines.new(line_vals)
            sequence+=1
            new_line.account_id=new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines+=new_line
        new_lines._onchange_mark_recompute_taxes()

        #Computeinvoice_origin.
        origins=set(self.line_ids.mapped('purchase_line_id.order_id.name'))
        self.invoice_origin=','.join(list(origins))

        #Computeref.
        refs=self._get_invoice_reference()
        self.ref=','.join(refs)

        #Computepayment_reference.
        iflen(refs)==1:
            self.payment_reference=refs[0]

        self.purchase_id=False
        self._onchange_currency()

    @api.onchange('partner_id','company_id')
    def_onchange_partner_id(self):
        res=super(AccountMove,self)._onchange_partner_id()

        currency_id=(
                self.partner_id.property_purchase_currency_id
                orself.env['res.currency'].browse(self.env.context.get("default_currency_id"))
                orself.currency_id
        )

        ifself.partner_idandself.move_typein['in_invoice','in_refund']andself.currency_id!=currency_id:
            ifnotself.env.context.get('default_journal_id'):
                journal_domain=[
                    ('type','=','purchase'),
                    ('company_id','=',self.company_id.id),
                    ('currency_id','=',currency_id.id),
                ]
                default_journal_id=self.env['account.journal'].search(journal_domain,limit=1)
                ifdefault_journal_id:
                    self.journal_id=default_journal_id

            self.currency_id=currency_id
            self._onchange_currency()

        returnres

    @api.model_create_multi
    defcreate(self,vals_list):
        #OVERRIDE
        moves=super(AccountMove,self).create(vals_list)
        formoveinmoves:
            ifmove.reversed_entry_id:
                continue
            purchase=move.line_ids.mapped('purchase_line_id.order_id')
            ifnotpurchase:
                continue
            refs=["<ahref=#data-oe-model=purchase.orderdata-oe-id=%s>%s</a>"%tuple(name_get)forname_getinpurchase.name_get()]
            message=_("Thisvendorbillhasbeencreatedfrom:%s")%','.join(refs)
            move.message_post(body=message)
        returnmoves

    defwrite(self,vals):
        #OVERRIDE
        old_purchases=[move.mapped('line_ids.purchase_line_id.order_id')formoveinself]
        res=super(AccountMove,self).write(vals)
        fori,moveinenumerate(self):
            new_purchases=move.mapped('line_ids.purchase_line_id.order_id')
            ifnotnew_purchases:
                continue
            diff_purchases=new_purchases-old_purchases[i]
            ifdiff_purchases:
                refs=["<ahref=#data-oe-model=purchase.orderdata-oe-id=%s>%s</a>"%tuple(name_get)forname_getindiff_purchases.name_get()]
                message=_("Thisvendorbillhasbeenmodifiedfrom:%s")%','.join(refs)
                move.message_post(body=message)
        returnres


classAccountMoveLine(models.Model):
    """OverrideAccountInvoice_linetoaddthelinktothepurchaseorderlineitisrelatedto"""
    _inherit='account.move.line'

    purchase_line_id=fields.Many2one('purchase.order.line','PurchaseOrderLine',ondelete='setnull',index=True)
    purchase_order_id=fields.Many2one('purchase.order','PurchaseOrder',related='purchase_line_id.order_id',readonly=True)

    def_copy_data_extend_business_fields(self,values):
        #OVERRIDEtocopythe'purchase_line_id'fieldaswell.
        super(AccountMoveLine,self)._copy_data_extend_business_fields(values)
        values['purchase_line_id']=self.purchase_line_id.id
