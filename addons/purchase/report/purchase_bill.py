#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools
fromflectra.osvimportexpression
fromflectra.toolsimportformatLang

classPurchaseBillUnion(models.Model):
    _name='purchase.bill.union'
    _auto=False
    _description='Purchases&BillsUnion'
    _order="datedesc,namedesc"

    name=fields.Char(string='Reference',readonly=True)
    reference=fields.Char(string='Source',readonly=True)
    partner_id=fields.Many2one('res.partner',string='Vendor',readonly=True)
    date=fields.Date(string='Date',readonly=True)
    amount=fields.Float(string='Amount',readonly=True)
    currency_id=fields.Many2one('res.currency',string='Currency',readonly=True)
    company_id=fields.Many2one('res.company','Company',readonly=True)
    vendor_bill_id=fields.Many2one('account.move',string='VendorBill',readonly=True)
    purchase_order_id=fields.Many2one('purchase.order',string='PurchaseOrder',readonly=True)

    definit(self):
        tools.drop_view_if_exists(self.env.cr,'purchase_bill_union')
        self.env.cr.execute("""
            CREATEORREPLACEVIEWpurchase_bill_unionAS(
                SELECT
                    id,name,refasreference,partner_id,date,amount_untaxedasamount,currency_id,company_id,
                    idasvendor_bill_id,NULLaspurchase_order_id
                FROMaccount_move
                WHERE
                    move_type='in_invoice'andstate='posted'
            UNION
                SELECT
                    -id,name,partner_refasreference,partner_id,date_order::dateasdate,amount_untaxedasamount,currency_id,company_id,
                    NULLasvendor_bill_id,idaspurchase_order_id
                FROMpurchase_order
                WHERE
                    statein('purchase','done')AND
                    invoice_statusin('toinvoice','no')
            )""")

    defname_get(self):
        result=[]
        fordocinself:
            name=doc.nameor''
            ifdoc.reference:
                name+='-'+doc.reference
            amount=doc.amount
            ifdoc.purchase_order_idanddoc.purchase_order_id.invoice_status=='no':
                amount=0.0
            name+=':'+formatLang(self.env,amount,monetary=True,currency_obj=doc.currency_id)
            result.append((doc.id,name))
        returnresult

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        args=argsor[]
        domain=[]
        ifname:
            domain=['|',('name',operator,name),('reference',operator,name)]
        purchase_bills_union_ids=self._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)
        returnpurchase_bills_union_ids
