#-*-coding:utf-8-*-

fromflectraimportfields,models
fromflectra.toolsimportfloat_is_zero


classAccountMove(models.Model):
    _inherit='account.move'

    stock_move_id=fields.Many2one('stock.move',string='StockMove',index=True)
    stock_valuation_layer_ids=fields.One2many('stock.valuation.layer','account_move_id',string='StockValuationLayer')

    #-------------------------------------------------------------------------
    #OVERRIDEMETHODS
    #-------------------------------------------------------------------------

    def_get_lines_onchange_currency(self):
        #OVERRIDE
        returnself.line_ids.filtered(lambdal:notl.is_anglo_saxon_line)

    def_reverse_move_vals(self,default_values,cancel=True):
        #OVERRIDE
        #Don'tkeepanglo-saxonlinesifnotcancellinganexistinginvoice.
        move_vals=super(AccountMove,self)._reverse_move_vals(default_values,cancel=cancel)
        ifnotcancel:
            move_vals['line_ids']=[valsforvalsinmove_vals['line_ids']ifnotvals[2]['is_anglo_saxon_line']]
        returnmove_vals

    defcopy_data(self,default=None):
        #OVERRIDE
        #Don'tkeepanglo-saxonlineswhencopyingajournalentry.
        res=super().copy_data(default=default)

        ifnotself._context.get('move_reverse_cancel'):
            forcopy_valsinres:
                if'line_ids'incopy_vals:
                    copy_vals['line_ids']=[line_valsforline_valsincopy_vals['line_ids']
                                             ifline_vals[0]!=0ornotline_vals[2].get('is_anglo_saxon_line')]

        returnres

    def_post(self,soft=True):
        #OVERRIDE

        #Don'tchangeanythingonmovesusedtocancelanotherones.
        ifself._context.get('move_reverse_cancel'):
            returnsuper()._post(soft)

        #CreateadditionalCOGSlinesforcustomerinvoices.
        self.env['account.move.line'].create(self._stock_account_prepare_anglo_saxon_out_lines_vals())

        #Postentries.
        posted=super()._post(soft)

        #ReconcileCOGSlinesincaseofanglo-saxonaccountingwithperpetualvaluation.
        posted._stock_account_anglo_saxon_reconcile_valuation()
        returnposted

    defbutton_draft(self):
        res=super(AccountMove,self).button_draft()

        #UnlinktheCOGSlinesgeneratedduringthe'post'method.
        self.mapped('line_ids').filtered(lambdaline:line.is_anglo_saxon_line).unlink()
        returnres

    defbutton_cancel(self):
        #OVERRIDE
        res=super(AccountMove,self).button_cancel()

        #UnlinktheCOGSlinesgeneratedduringthe'post'method.
        #Inmostcasesitshouldn'tbenecessarysincetheyshouldbeunlinkedwith'button_draft'.
        #However,sinceitcanbecalledinRPC,betterbesafe.
        self.mapped('line_ids').filtered(lambdaline:line.is_anglo_saxon_line).unlink()
        returnres

    #-------------------------------------------------------------------------
    #COGSMETHODS
    #-------------------------------------------------------------------------

    def_stock_account_prepare_anglo_saxon_out_lines_vals(self):
        '''Preparevaluesusedtocreatethejournalitems(account.move.line)correspondingtotheCostofGoodSold
        lines(COGS)forcustomerinvoices.

        Example:

        Buyaproducthavingacostof9beingastorableproductandhavingaperpetualvaluationinFIFO.
        Sellthisproductatapriceof10.Thecustomerinvoice'sjournalentrieslookslike:

        Account                                    |Debit|Credit
        ---------------------------------------------------------------
        200000ProductSales                       |      |10.0
        ---------------------------------------------------------------
        101200AccountReceivable                  |10.0 |
        ---------------------------------------------------------------

        Thismethodcomputesvaluesusedtomaketwoadditionaljournalitems:

        ---------------------------------------------------------------
        220000Expenses                            |9.0  |
        ---------------------------------------------------------------
        101130StockInterimAccount(Delivered)   |      |9.0
        ---------------------------------------------------------------

        Note:COGSareonlygeneratedforcustomerinvoicesexceptrefundmadetocancelaninvoice.

        :return:AlistofPythondictionarytobepassedtoenv['account.move.line'].create.
        '''
        lines_vals_list=[]
        price_unit_prec=self.env['decimal.precision'].precision_get('ProductPrice')
        formoveinself:
            #Maketheloopmulti-companysafewhenaccessingmodelslikeproduct.product
            move=move.with_company(move.company_id)

            ifnotmove.is_sale_document(include_receipts=True)ornotmove.company_id.anglo_saxon_accounting:
                continue

            forlineinmove.invoice_line_ids:

                #FilteroutlinesbeingnoteligibleforCOGS.
                ifline.product_id.type!='product'orline.product_id.valuation!='real_time':
                    continue

                #RetrieveaccountsneededtogeneratetheCOGS.
                accounts=line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=move.fiscal_position_id)
                debit_interim_account=accounts['stock_output']
                credit_expense_account=accounts['expense']ormove.journal_id.default_account_id
                ifnotdebit_interim_accountornotcredit_expense_account:
                    continue

                #Computeaccountingfields.
                sign=-1ifmove.move_type=='out_refund'else1
                price_unit=line._stock_account_get_anglo_saxon_price_unit()
                balance=sign*line.quantity*price_unit

                ifmove.currency_id.is_zero(balance)orfloat_is_zero(price_unit,precision_digits=price_unit_prec):
                    continue

                #Addinterimaccountline.
                lines_vals_list.append({
                    'name':line.name[:64],
                    'move_id':move.id,
                    'partner_id':move.commercial_partner_id.id,
                    'product_id':line.product_id.id,
                    'product_uom_id':line.product_uom_id.id,
                    'quantity':line.quantity,
                    'price_unit':price_unit,
                    'debit':balance<0.0and-balanceor0.0,
                    'credit':balance>0.0andbalanceor0.0,
                    'account_id':debit_interim_account.id,
                    'exclude_from_invoice_tab':True,
                    'is_anglo_saxon_line':True,
                })

                #Addexpenseaccountline.
                lines_vals_list.append({
                    'name':line.name[:64],
                    'move_id':move.id,
                    'partner_id':move.commercial_partner_id.id,
                    'product_id':line.product_id.id,
                    'product_uom_id':line.product_uom_id.id,
                    'quantity':line.quantity,
                    'price_unit':-price_unit,
                    'debit':balance>0.0andbalanceor0.0,
                    'credit':balance<0.0and-balanceor0.0,
                    'account_id':credit_expense_account.id,
                    'analytic_account_id':line.analytic_account_id.id,
                    'analytic_tag_ids':[(6,0,line.analytic_tag_ids.ids)],
                    'exclude_from_invoice_tab':True,
                    'is_anglo_saxon_line':True,
                })
        returnlines_vals_list

    def_stock_account_get_last_step_stock_moves(self):
        """Tobeoverriddenforcustomerinvoicesandvendorbillsinorderto
        returnthestockmovesrelatedtotheinvoicesinself.
        """
        returnself.env['stock.move']

    def_stock_account_anglo_saxon_reconcile_valuation(self,product=False):
        """Reconcilestheentriesmadeintheinterimaccountsinanglosaxonaccounting,
        reconcilingstockvaluationmovelineswiththeinvoice's.
        """
        formoveinself:
            ifnotmove.is_invoice():
                continue
            ifnotmove.company_id.anglo_saxon_accounting:
                continue

            stock_moves=move._stock_account_get_last_step_stock_moves()

            ifnotstock_moves:
                continue

            products=productormove.mapped('invoice_line_ids.product_id')
            forprodinproducts:
                ifprod.valuation!='real_time':
                    continue

                #Wefirstgettheinvoicesmovelines(takingtheinvoiceandthepreviousonesintoaccount)...
                product_accounts=prod.product_tmpl_id._get_product_accounts()
                ifmove.is_sale_document():
                    product_interim_account=product_accounts['stock_output']
                else:
                    product_interim_account=product_accounts['stock_input']

                ifproduct_interim_account.reconcile:
                    #Searchforanglo-saxonlineslinkedtotheproductinthejournalentry.
                    product_account_moves=move.line_ids.filtered(
                        lambdaline:line.product_id==prodandline.account_id==product_interim_accountandnotline.reconciled)

                    #Searchforanglo-saxonlineslinkedtotheproductinthestockmoves.
                    product_stock_moves=stock_moves.filtered(lambdastock_move:stock_move.product_id==prod)
                    product_account_moves+=product_stock_moves.mapped('account_move_ids.line_ids')\
                        .filtered(lambdaline:line.account_id==product_interim_accountandnotline.reconciled)

                    #Reconcile.
                    product_account_moves.reconcile()


classAccountMoveLine(models.Model):
    _inherit='account.move.line'

    is_anglo_saxon_line=fields.Boolean(help="Technicalfieldusedtoretrievetheanglo-saxonlines.")

    def_get_computed_account(self):
        #OVERRIDEtousethestockinputaccountbydefaultonvendorbillswhendealing
        #withanglo-saxonaccounting.
        self.ensure_one()
        self=self.with_company(self.move_id.journal_id.company_id)
        ifself._can_use_stock_accounts()\
            andself.move_id.company_id.anglo_saxon_accounting\
            andself.move_id.is_purchase_document():
            fiscal_position=self.move_id.fiscal_position_id
            accounts=self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
            ifaccounts['stock_input']:
                returnaccounts['stock_input']
        returnsuper(AccountMoveLine,self)._get_computed_account()

    def_can_use_stock_accounts(self):
        returnself.product_id.type=='product'andself.product_id.categ_id.property_valuation=='real_time'

    def_stock_account_get_anglo_saxon_price_unit(self):
        self.ensure_one()
        ifnotself.product_id:
            returnself.price_unit
        original_line=self.move_id.reversed_entry_id.line_ids.filtered(lambdal:l.is_anglo_saxon_line
            andl.product_id==self.product_idandl.product_uom_id==self.product_uom_idandl.price_unit>=0)
        original_line=original_lineandoriginal_line[0]
        returnoriginal_line.price_unitiforiginal_line\
            elseself.product_id.with_company(self.company_id)._stock_account_get_anglo_saxon_price_unit(uom=self.product_uom_id)
