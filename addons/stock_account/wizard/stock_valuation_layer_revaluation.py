#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError
fromflectra.toolsimportfloat_compare,float_is_zero


classStockValuationLayerRevaluation(models.TransientModel):
    _name='stock.valuation.layer.revaluation'
    _description="Wizardmodeltoreavaluateastockinventoryforaproduct"
    _check_company_auto=True

    @api.model
    defdefault_get(self,default_fields):
        res=super().default_get(default_fields)
        ifres.get('product_id'):
            product=self.env['product.product'].browse(res['product_id'])
            ifproduct.categ_id.property_cost_method=='standard':
                raiseUserError(_("Youcannotrevalueaproductwithastandardcostmethod."))
            ifproduct.quantity_svl<=0:
                raiseUserError(_("Youcannotrevalueaproductwithanemptyornegativestock."))
            if'account_journal_id'notinresand'account_journal_id'indefault_fieldsandproduct.categ_id.property_valuation=='real_time':              
                accounts=product.product_tmpl_id.get_product_accounts()
                res['account_journal_id']=accounts['stock_journal'].id
        returnres

    company_id=fields.Many2one('res.company',"Company",readonly=True,required=True)
    currency_id=fields.Many2one('res.currency',"Currency",related='company_id.currency_id',required=True)

    product_id=fields.Many2one('product.product',"Relatedproduct",required=True,check_company=True)
    property_valuation=fields.Selection(related='product_id.categ_id.property_valuation')
    product_uom_name=fields.Char("UnitofMeasure",related='product_id.uom_id.name')
    current_value_svl=fields.Float("CurrentValue",related="product_id.value_svl")
    current_quantity_svl=fields.Float("CurrentQuantity",related="product_id.quantity_svl")

    added_value=fields.Monetary("Addedvalue",required=True)
    new_value=fields.Monetary("Newvalue",compute='_compute_new_value')
    new_value_by_qty=fields.Monetary("Newvaluebyquantity",compute='_compute_new_value')
    reason=fields.Char("Reason",help="Reasonoftherevaluation")

    account_journal_id=fields.Many2one('account.journal',"Journal",check_company=True)
    account_id=fields.Many2one('account.account',"CounterpartAccount",domain=[('deprecated','=',False)],check_company=True)
    date=fields.Date("AccountingDate")

    @api.depends('current_value_svl','current_quantity_svl','added_value')
    def_compute_new_value(self):
        forrevalinself:
            reval.new_value=reval.current_value_svl+reval.added_value
            ifnotfloat_is_zero(reval.current_quantity_svl,precision_rounding=self.product_id.uom_id.rounding):
                reval.new_value_by_qty=reval.new_value/reval.current_quantity_svl
            else:
                reval.new_value_by_qty=0.0

    defaction_validate_revaluation(self):
        """Revaluatethestockfor`self.product_id`in`self.company_id`.

        -Changethestardardpricewiththenewvaluationbyproductunit.
        -Createamanualstockvaluationlayerwiththe`added_value`of`self`.
        -Distributethe`added_value`ontheremaining_valueoflayersstillinstock(witharemainingquantity)
        -IftheInventoryValuationoftheproductcategoryisautomated,create
        relatedaccountmove.
        """
        self.ensure_one()
        ifself.currency_id.is_zero(self.added_value):
            raiseUserError(_("Theaddedvaluedoesn'thaveanyimpactonthestockvaluation"))

        product_id=self.product_id.with_company(self.company_id)

        remaining_svls=self.env['stock.valuation.layer'].search([
            ('product_id','=',product_id.id),
            ('remaining_qty','>',0),
            ('company_id','=',self.company_id.id),
        ])

        #Createamanualstockvaluationlayer
        ifself.reason:
            description=_("ManualStockValuation:%s.",self.reason)
        else:
            description=_("ManualStockValuation:NoReasonGiven.")
        ifproduct_id.categ_id.property_cost_method=='average':
            description+=_(
                "Productcostupdatedfrom%(previous)sto%(new_cost)s.",
                previous=product_id.standard_price,
                new_cost=product_id.standard_price+self.added_value/self.current_quantity_svl
            )
        revaluation_svl_vals={
            'company_id':self.company_id.id,
            'product_id':product_id.id,
            'description':description,
            'value':self.added_value,
            'quantity':0,
        }

        remaining_qty=sum(remaining_svls.mapped('remaining_qty'))
        remaining_value=self.added_value
        remaining_value_unit_cost=self.currency_id.round(remaining_value/remaining_qty)
        forsvlinremaining_svls:
            iffloat_is_zero(svl.remaining_qty-remaining_qty,precision_rounding=self.product_id.uom_id.rounding):
                taken_remaining_value=remaining_value
            else:
                taken_remaining_value=remaining_value_unit_cost*svl.remaining_qty
            iffloat_compare(svl.remaining_value+taken_remaining_value,0,precision_rounding=self.product_id.uom_id.rounding)<0:
                raiseUserError(_('Thevalueofastockvaluationlayercannotbenegative.Landedcostcouldbeusetocorrectaspecifictransfer.'))

            svl.remaining_value+=taken_remaining_value
            remaining_value-=taken_remaining_value
            remaining_qty-=svl.remaining_qty

        revaluation_svl=self.env['stock.valuation.layer'].create(revaluation_svl_vals)

        #UpdatethestardardpriceincaseofAVCO
        ifproduct_id.categ_id.property_cost_methodin('average','fifo'):
            product_id.with_context(disable_auto_svl=True).standard_price+=self.added_value/self.current_quantity_svl

        #IftheInventoryValuationoftheproductcategoryisautomated,createrelatedaccountmove.
        ifself.property_valuation!='real_time':
            returnTrue

        accounts=product_id.product_tmpl_id.get_product_accounts()

        ifself.added_value<0:
            debit_account_id=self.account_id.id
            credit_account_id=accounts.get('stock_valuation')andaccounts['stock_valuation'].id
        else:
            debit_account_id=accounts.get('stock_valuation')andaccounts['stock_valuation'].id
            credit_account_id=self.account_id.id

        move_vals={
            'journal_id':self.account_journal_id.idoraccounts['stock_journal'].id,
            'company_id':self.company_id.id,
            'ref':_("Revaluationof%s",product_id.display_name),
            'stock_valuation_layer_ids':[(6,None,[revaluation_svl.id])],
            'date':self.dateorfields.Date.today(),
            'move_type':'entry',
            'line_ids':[(0,0,{
                'name':_('%(user)schangedstockvaluationfrom %(previous)sto%(new_value)s-%(product)s',
                    user=self.env.user.name,
                    previous=self.current_value_svl,
                    new_value=self.current_value_svl+self.added_value,
                    product=product_id.display_name,
                ),
                'account_id':debit_account_id,
                'debit':abs(self.added_value),
                'credit':0,
                'product_id':product_id.id,
            }),(0,0,{
                'name':_('%(user)schangedstockvaluationfrom %(previous)sto%(new_value)s-%(product)s',
                    user=self.env.user.name,
                    previous=self.current_value_svl,
                    new_value=self.current_value_svl+self.added_value,
                    product=product_id.display_name,
                ),
                'account_id':credit_account_id,
                'debit':0,
                'credit':abs(self.added_value),
                'product_id':product_id.id,
            })],
        }
        account_move=self.env['account.move'].create(move_vals)
        account_move._post()

        returnTrue
