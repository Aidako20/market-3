#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.tools.float_utilsimportfloat_compare,float_is_zero


classAccountMove(models.Model):
    _inherit='account.move'

    def_stock_account_prepare_anglo_saxon_in_lines_vals(self):
        '''Preparevaluesusedtocreatethejournalitems(account.move.line)correspondingtothepricedifference
         linesforvendorbills.

        Example:

        Buyaproducthavingacostof9andasupplierpriceof10andbeingastorableproductandhavingaperpetual
        valuationinFIFO.Thevendorbill'sjournalentrieslookslike:

        Account                                    |Debit|Credit
        ---------------------------------------------------------------
        101120StockInterimAccount(Received)    |10.0 |
        ---------------------------------------------------------------
        101100AccountPayable                     |      |10.0
        ---------------------------------------------------------------

        Thismethodcomputesvaluesusedtomaketwoadditionaljournalitems:

        ---------------------------------------------------------------
        101120StockInterimAccount(Received)    |      |1.0
        ---------------------------------------------------------------
        xxxxxxPriceDifferenceAccount            |1.0  |
        ---------------------------------------------------------------

        :return:AlistofPythondictionarytobepassedtoenv['account.move.line'].create.
        '''
        lines_vals_list=[]
        price_unit_prec=self.env['decimal.precision'].precision_get('ProductPrice')

        formoveinself:
            ifmove.move_typenotin('in_invoice','in_refund','in_receipt')ornotmove.company_id.anglo_saxon_accounting:
                continue

            move=move.with_company(move.company_id)
            forlineinmove.invoice_line_ids:
                #Filteroutlinesbeingnoteligibleforpricedifference.
                ifline.product_id.type!='product'orline.product_id.valuation!='real_time':
                    continue

                #Retrieveaccountsneededtogeneratethepricedifference.
                debit_pdiff_account=line.product_id.property_account_creditor_price_difference\
                                orline.product_id.categ_id.property_account_creditor_price_difference_categ
                debit_pdiff_account=move.fiscal_position_id.map_account(debit_pdiff_account)
                ifnotdebit_pdiff_account:
                    continue
                #Retrievestockvaluationmoves.
                valuation_stock_moves=self.env['stock.move'].search([
                    ('purchase_line_id','=',line.purchase_line_id.id),
                    ('state','=','done'),
                    ('product_qty','!=',0.0),
                ])ifline.purchase_line_idelseself.env['stock.move']
                ifmove.move_type=='in_refund':
                    valuation_stock_moves=valuation_stock_moves.filtered(lambdastock_move:stock_move._is_out())
                else:
                    valuation_stock_moves=valuation_stock_moves.filtered(lambdastock_move:stock_move._is_in())

                ifline.product_id.cost_method!='standard'andline.purchase_line_id:
                    po_currency=line.purchase_line_id.currency_id
                    po_company=line.purchase_line_id.company_id

                    ifvaluation_stock_moves:
                        valuation_price_unit_total,valuation_total_qty=valuation_stock_moves._get_valuation_price_and_qty(line,move.currency_id)
                        valuation_price_unit=valuation_price_unit_total/valuation_total_qty
                        valuation_price_unit=line.product_id.uom_id._compute_price(valuation_price_unit,line.product_uom_id)

                    elifline.product_id.cost_method=='fifo':
                        #Inthiscondition,wehavearealprice-valuatedproductwhichhasnotyetbeenreceived
                        valuation_price_unit=po_currency._convert(
                            line.purchase_line_id.price_unit,move.currency_id,
                            po_company,move.date,round=False,
                        )
                    else:
                        #Foraverage/fifo/lifocostingmethod,fetchrealcostpricefromincomingmoves.
                        price_unit=line.purchase_line_id.product_uom._compute_price(line.purchase_line_id.price_unit,line.product_uom_id)
                        valuation_price_unit=po_currency._convert(
                            price_unit,move.currency_id,
                            po_company,move.date,round=False
                        )

                else:
                    #Valuation_priceunitisalwaysexpressedininvoicecurrency,sothatitcanalwaysbecomputedwiththegoodrate
                    price_unit=line.product_id.uom_id._compute_price(line.product_id.standard_price,line.product_uom_id)
                    valuation_date=valuation_stock_movesandmax(valuation_stock_moves.mapped('date'))ormove.date
                    valuation_price_unit=line.company_currency_id._convert(
                        price_unit,move.currency_id,
                        move.company_id,valuation_date,round=False
                    )


                price_unit=line.price_unit*(1-(line.discountor0.0)/100.0)
                ifline.tax_ids:
                    #Wedonotwanttoroundthepriceunitsince:
                    #-Itdoesnotfollowthecurrencyprecision
                    #-Itmayincludeadiscount
                    #Sincecompute_allstillroundsthetotal,weuseanuglyworkaround:
                    #shiftthedecimalpartusingafixedquantitytoavoidroundingissues
                    prec=1e+6
                    price_unit*=prec
                    price_unit=line.tax_ids.with_context(round=False,force_sign=move._get_tax_force_sign()).compute_all(
                        price_unit,currency=move.currency_id,quantity=1.0,is_refund=move.move_type=='in_refund')['total_excluded']
                    price_unit/=prec

                price_unit_val_dif=price_unit-valuation_price_unit
                price_subtotal=line.quantity*price_unit_val_dif

                #Weconsiderthereisapricedifferenceif:
                #-priceunitisnotzerowithrespecttoproductpricedecimalprecision.
                #-subtotalisnotzerowithrespecttomovecurrencyprecision.
                #-nodiscountwasapplied,aswecan'troundthepriceunitanymore
                if(
                    notmove.currency_id.is_zero(price_subtotal)
                    andnotfloat_is_zero(price_unit_val_dif,precision_digits=price_unit_prec)
                    andfloat_compare(line["price_unit"],line.price_unit,precision_digits=price_unit_prec)==0
                ):

                    #Addpricedifferenceaccountline.
                    vals={
                        'name':line.name[:64],
                        'move_id':move.id,
                        'partner_id':line.partner_id.idormove.commercial_partner_id.id,
                        'currency_id':line.currency_id.id,
                        'product_id':line.product_id.id,
                        'product_uom_id':line.product_uom_id.id,
                        'quantity':line.quantity,
                        'price_unit':price_unit_val_dif,
                        'price_subtotal':line.quantity*price_unit_val_dif,
                        'account_id':debit_pdiff_account.id,
                        'analytic_account_id':line.analytic_account_id.id,
                        'analytic_tag_ids':[(6,0,line.analytic_tag_ids.ids)],
                        'exclude_from_invoice_tab':True,
                        'is_anglo_saxon_line':True,
                    }
                    vals.update(line._get_fields_onchange_subtotal(price_subtotal=vals['price_subtotal']))
                    lines_vals_list.append(vals)

                    #Correcttheamountofthecurrentline.
                    vals={
                        'name':line.name[:64],
                        'move_id':move.id,
                        'partner_id':line.partner_id.idormove.commercial_partner_id.id,
                        'currency_id':line.currency_id.id,
                        'product_id':line.product_id.id,
                        'product_uom_id':line.product_uom_id.id,
                        'quantity':line.quantity,
                        'price_unit':-price_unit_val_dif,
                        'price_subtotal':line.quantity*-price_unit_val_dif,
                        'account_id':line.account_id.id,
                        'analytic_account_id':line.analytic_account_id.id,
                        'analytic_tag_ids':[(6,0,line.analytic_tag_ids.ids)],
                        'exclude_from_invoice_tab':True,
                        'is_anglo_saxon_line':True,
                    }
                    vals.update(line._get_fields_onchange_subtotal(price_subtotal=vals['price_subtotal']))
                    lines_vals_list.append(vals)
        returnlines_vals_list

    def_post(self,soft=True):
        #OVERRIDE
        #Createadditionalpricedifferencelinesforvendorbills.
        ifself._context.get('move_reverse_cancel'):
            returnsuper()._post(soft)
        self.env['account.move.line'].create(self._stock_account_prepare_anglo_saxon_in_lines_vals())
        returnsuper()._post(soft)

    def_stock_account_get_last_step_stock_moves(self):
        """Overriddenfromstock_account.
        Returnsthestockmovesassociatedtothisinvoice."""
        rslt=super(AccountMove,self)._stock_account_get_last_step_stock_moves()
        forinvoiceinself.filtered(lambdax:x.move_type=='in_invoice'):
            rslt+=invoice.mapped('invoice_line_ids.purchase_line_id.move_ids').filtered(lambdax:x.state=='done'andx.location_id.usage=='supplier')
        forinvoiceinself.filtered(lambdax:x.move_type=='in_refund'):
            rslt+=invoice.mapped('invoice_line_ids.purchase_line_id.move_ids').filtered(lambdax:x.state=='done'andx.location_dest_id.usage=='supplier')
        returnrslt
