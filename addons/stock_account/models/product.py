#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.toolsimportfloat_is_zero,float_repr,float_round,float_compare
fromflectra.exceptionsimportValidationError
fromcollectionsimportdefaultdict


classProductTemplate(models.Model):
    _name='product.template'
    _inherit='product.template'

    cost_method=fields.Selection(related="categ_id.property_cost_method",readonly=True)
    valuation=fields.Selection(related="categ_id.property_valuation",readonly=True)

    defwrite(self,vals):
        impacted_templates={}
        move_vals_list=[]
        Product=self.env['product.product']
        SVL=self.env['stock.valuation.layer']

        if'categ_id'invals:
            #Whenachangeofcategoryimpliesachangeofcostmethod,weemptyoutandreplenish
            #thestock.
            new_product_category=self.env['product.category'].browse(vals.get('categ_id'))

            forproduct_templateinself:
                product_template=product_template.with_company(product_template.company_id)
                valuation_impacted=False
                ifproduct_template.cost_method!=new_product_category.property_cost_method:
                    valuation_impacted=True
                ifproduct_template.valuation!=new_product_category.property_valuation:
                    valuation_impacted=True
                ifvaluation_impactedisFalse:
                    continue

                #Emptyoutthestockwiththecurrentcostmethod.
                description=_("Duetoachangeofproductcategory(from%sto%s),thecostingmethod\
                                haschangedforproducttemplate%s:from%sto%s.")%\
                    (product_template.categ_id.display_name,new_product_category.display_name,
                     product_template.display_name,product_template.cost_method,new_product_category.property_cost_method)
                out_svl_vals_list,products_orig_quantity_svl,products=Product\
                    ._svl_empty_stock(description,product_template=product_template)
                out_stock_valuation_layers=SVL.create(out_svl_vals_list)
                ifproduct_template.valuation=='real_time':
                    move_vals_list+=Product._svl_empty_stock_am(out_stock_valuation_layers)
                impacted_templates[product_template]=(products,description,products_orig_quantity_svl)

        res=super(ProductTemplate,self).write(vals)

        forproduct_template,(products,description,products_orig_quantity_svl)inimpacted_templates.items():
            #Replenishthestockwiththenewcostmethod.
            in_svl_vals_list=products._svl_replenish_stock(description,products_orig_quantity_svl)
            in_stock_valuation_layers=SVL.create(in_svl_vals_list)
            ifproduct_template.valuation=='real_time':
                move_vals_list+=Product._svl_replenish_stock_am(in_stock_valuation_layers)

        #Checkaccessright
        ifmove_vals_listandnotself.env['stock.valuation.layer'].check_access_rights('read',raise_exception=False):
            raiseUserError(_("Theactionleadstothecreationofajournalentry,forwhichyoudon'thavetheaccessrights."))
        #Createtheaccountmoves.
        ifmove_vals_list:
            account_moves=self.env['account.move'].sudo().create(move_vals_list)
            account_moves._post()
        returnres

    #-------------------------------------------------------------------------
    #Misc.
    #-------------------------------------------------------------------------
    def_get_product_accounts(self):
        """Addthestockaccountsrelatedtoproducttotheresultofsuper()
        @return:dictionarywhichcontainsinformationregardingstockaccountsandsuper(income+expenseaccounts)
        """
        accounts=super(ProductTemplate,self)._get_product_accounts()
        res=self._get_asset_accounts()
        accounts.update({
            'stock_input':res['stock_input']orself.categ_id.property_stock_account_input_categ_id,
            'stock_output':res['stock_output']orself.categ_id.property_stock_account_output_categ_id,
            'stock_valuation':self.categ_id.property_stock_valuation_account_idorFalse,
        })
        returnaccounts

    defget_product_accounts(self,fiscal_pos=None):
        """Addthestockjournalrelatedtoproducttotheresultofsuper()
        @return:dictionarywhichcontainsallneededinformationregardingstockaccountsandjournalandsuper(income+expenseaccounts)
        """
        accounts=super(ProductTemplate,self).get_product_accounts(fiscal_pos=fiscal_pos)
        accounts.update({'stock_journal':self.categ_id.property_stock_journalorFalse})
        returnaccounts


classProductProduct(models.Model):
    _inherit='product.product'

    value_svl=fields.Float(compute='_compute_value_svl',compute_sudo=True)
    quantity_svl=fields.Float(compute='_compute_value_svl',compute_sudo=True)
    stock_valuation_layer_ids=fields.One2many('stock.valuation.layer','product_id')
    valuation=fields.Selection(related="categ_id.property_valuation",readonly=True)
    cost_method=fields.Selection(related="categ_id.property_cost_method",readonly=True)

    defwrite(self,vals):
        if'standard_price'invalsandnotself.env.context.get('disable_auto_svl'):
            self.filtered(lambdap:p.cost_method!='fifo')._change_standard_price(vals['standard_price'])
        returnsuper(ProductProduct,self).write(vals)

    @api.depends('stock_valuation_layer_ids')
    @api.depends_context('to_date','company')
    def_compute_value_svl(self):
        """Compute`value_svl`and`quantity_svl`."""
        company_id=self.env.company.id
        domain=[
            ('product_id','in',self.ids),
            ('company_id','=',company_id),
        ]
        ifself.env.context.get('to_date'):
            to_date=fields.Datetime.to_datetime(self.env.context['to_date'])
            domain.append(('create_date','<=',to_date))
        groups=self.env['stock.valuation.layer'].read_group(domain,['value:sum','quantity:sum'],['product_id'])
        products=self.browse()
        forgroupingroups:
            product=self.browse(group['product_id'][0])
            product.value_svl=self.env.company.currency_id.round(group['value'])
            product.quantity_svl=group['quantity']
            products|=product
        remaining=(self-products)
        remaining.value_svl=0
        remaining.quantity_svl=0

    #-------------------------------------------------------------------------
    #Actions
    #-------------------------------------------------------------------------
    defaction_revaluation(self):
        self.ensure_one()
        ctx=dict(self._context,default_product_id=self.id,default_company_id=self.env.company.id)
        return{
            'name':_("ProductRevaluation"),
            'view_mode':'form',
            'res_model':'stock.valuation.layer.revaluation',
            'view_id':self.env.ref('stock_account.stock_valuation_layer_revaluation_form_view').id,
            'type':'ir.actions.act_window',
            'context':ctx,
            'target':'new'
        }

    #-------------------------------------------------------------------------
    #SVLcreationhelpers
    #-------------------------------------------------------------------------
    def_prepare_in_svl_vals(self,quantity,unit_cost):
        """Preparethevaluesforastockvaluationlayercreatedbyareceipt.

        :paramquantity:thequantitytovalue,expressedin`self.uom_id`
        :paramunit_cost:theunitcosttovalue`quantity`
        :return:valuestouseinacalltocreate
        :rtype:dict
        """
        self.ensure_one()
        company_id=self.env.context.get('force_company',self.env.company.id)
        company=self.env['res.company'].browse(company_id)
        vals={
            'product_id':self.id,
            'value':company.currency_id.round(unit_cost*quantity),
            'unit_cost':unit_cost,
            'quantity':quantity,
        }
        ifself.cost_methodin('average','fifo'):
            vals['remaining_qty']=quantity
            vals['remaining_value']=vals['value']
        returnvals

    def_prepare_out_svl_vals(self,quantity,company):
        """Preparethevaluesforastockvaluationlayercreatedbyadelivery.

        :paramquantity:thequantitytovalue,expressedin`self.uom_id`
        :return:valuestouseinacalltocreate
        :rtype:dict
        """
        self.ensure_one()
        company_id=self.env.context.get('force_company',self.env.company.id)
        company=self.env['res.company'].browse(company_id)
        currency=company.currency_id
        #Quantityisnegativeforoutvaluationlayers.
        quantity=-1*quantity
        vals={
            'product_id':self.id,
            'value':currency.round(quantity*self.standard_price),
            'unit_cost':self.standard_price,
            'quantity':quantity,
        }
        ifself.product_tmpl_id.cost_methodin('average','fifo'):
            fifo_vals=self._run_fifo(abs(quantity),company)
            vals['remaining_qty']=fifo_vals.get('remaining_qty')
            #IncaseofAVCO,fixroundingissueofstandardpricewhenneeded.
            ifself.product_tmpl_id.cost_method=='average'andnotfloat_is_zero(self.quantity_svl,precision_rounding=self.uom_id.rounding):
                rounding_error=currency.round(
                    (self.standard_price*self.quantity_svl-self.value_svl)*abs(quantity/self.quantity_svl)
                )
                ifrounding_error:
                    #Ifitisbiggerthanthe(smallestnumberofthecurrency*quantity)/2,
                    #thenitisn'taroundingerrorbutastockvaluationerror,weshouldn'tfixitunderthehood...
                    ifabs(rounding_error)<=max((abs(quantity)*currency.rounding)/2,currency.rounding):
                        vals['value']+=rounding_error
                        vals['rounding_adjustment']='\nRoundingAdjustment:%s%s%s'%(
                            '+'ifrounding_error>0else'',
                            float_repr(rounding_error,precision_digits=currency.decimal_places),
                            currency.symbol
                        )
            ifself.product_tmpl_id.cost_method=='fifo':
                vals.update(fifo_vals)
        returnvals

    def_change_standard_price(self,new_price):
        """Helpertocreatethestockvaluationlayersandtheaccountmoves
        afteranupdateofstandardprice.

        :paramnew_price:newstandardprice
        """
        #Handlestockvaluationlayers.

        ifself.filtered(lambdap:p.valuation=='real_time')andnotself.env['stock.valuation.layer'].check_access_rights('read',raise_exception=False):
            raiseUserError(_("Youcannotupdatethecostofaproductinautomatedvaluationasitleadstothecreationofajournalentry,forwhichyoudon'thavetheaccessrights."))

        svl_vals_list=[]
        company_id=self.env.company
        price_unit_prec=self.env['decimal.precision'].precision_get('ProductPrice')
        rounded_new_price=float_round(new_price,precision_digits=price_unit_prec)
        forproductinself:
            ifproduct.cost_methodnotin('standard','average'):
                continue
            quantity_svl=product.sudo().quantity_svl
            iffloat_compare(quantity_svl,0.0,precision_rounding=product.uom_id.rounding)<=0:
                continue
            value_svl=product.sudo().value_svl
            value=company_id.currency_id.round((rounded_new_price*quantity_svl)-value_svl)
            ifcompany_id.currency_id.is_zero(value):
                continue

            svl_vals={
                'company_id':company_id.id,
                'product_id':product.id,
                'description':_('Productvaluemanuallymodified(from%sto%s)')%(product.standard_price,rounded_new_price),
                'value':value,
                'quantity':0,
            }
            svl_vals_list.append(svl_vals)
        stock_valuation_layers=self.env['stock.valuation.layer'].sudo().create(svl_vals_list)

        #Handleaccountmoves.
        product_accounts={product.id:product.product_tmpl_id.get_product_accounts()forproductinself}
        am_vals_list=[]
        forstock_valuation_layerinstock_valuation_layers:
            product=stock_valuation_layer.product_id
            value=stock_valuation_layer.value

            ifproduct.type!='product'orproduct.valuation!='real_time':
                continue

            #Sanitycheck.
            ifnotproduct_accounts[product.id].get('expense'):
                raiseUserError(_('Youmustsetacounterpartaccountonyourproductcategory.'))
            ifnotproduct_accounts[product.id].get('stock_valuation'):
                raiseUserError(_('Youdon\'thaveanystockvaluationaccountdefinedonyourproductcategory.Youmustdefineonebeforeprocessingthisoperation.'))

            ifvalue<0:
                debit_account_id=product_accounts[product.id]['expense'].id
                credit_account_id=product_accounts[product.id]['stock_valuation'].id
            else:
                debit_account_id=product_accounts[product.id]['stock_valuation'].id
                credit_account_id=product_accounts[product.id]['expense'].id

            move_vals={
                'journal_id':product_accounts[product.id]['stock_journal'].id,
                'company_id':company_id.id,
                'ref':product.default_code,
                'stock_valuation_layer_ids':[(6,None,[stock_valuation_layer.id])],
                'move_type':'entry',
                'line_ids':[(0,0,{
                    'name':_(
                        '%(user)schangedcostfrom%(previous)sto%(new_price)s-%(product)s',
                        user=self.env.user.name,
                        previous=product.standard_price,
                        new_price=new_price,
                        product=product.display_name
                    ),
                    'account_id':debit_account_id,
                    'debit':abs(value),
                    'credit':0,
                    'product_id':product.id,
                }),(0,0,{
                    'name':_(
                        '%(user)schangedcostfrom%(previous)sto%(new_price)s-%(product)s',
                        user=self.env.user.name,
                        previous=product.standard_price,
                        new_price=new_price,
                        product=product.display_name
                    ),
                    'account_id':credit_account_id,
                    'debit':0,
                    'credit':abs(value),
                    'product_id':product.id,
                })],
            }
            am_vals_list.append(move_vals)

        account_moves=self.env['account.move'].sudo().create(am_vals_list)
        ifaccount_moves:
            account_moves._post()

    def_run_fifo(self,quantity,company):
        self.ensure_one()

        #Findbackincomingstockvaluationlayers(calledcandidateshere)tovalue`quantity`.
        qty_to_take_on_candidates=quantity
        candidates=self.env['stock.valuation.layer'].sudo().search([
            ('product_id','=',self.id),
            ('remaining_qty','>',0),
            ('company_id','=',company.id),
        ])
        new_standard_price=0
        tmp_value=0 #toaccumulatethevaluetakenonthecandidates
        forcandidateincandidates:
            qty_taken_on_candidate=min(qty_to_take_on_candidates,candidate.remaining_qty)

            candidate_unit_cost=candidate.remaining_value/candidate.remaining_qty
            new_standard_price=candidate_unit_cost
            value_taken_on_candidate=qty_taken_on_candidate*candidate_unit_cost
            value_taken_on_candidate=candidate.currency_id.round(value_taken_on_candidate)
            new_remaining_value=candidate.remaining_value-value_taken_on_candidate

            candidate_vals={
                'remaining_qty':candidate.remaining_qty-qty_taken_on_candidate,
                'remaining_value':new_remaining_value,
            }

            candidate.write(candidate_vals)

            qty_to_take_on_candidates-=qty_taken_on_candidate
            tmp_value+=value_taken_on_candidate

            iffloat_is_zero(qty_to_take_on_candidates,precision_rounding=self.uom_id.rounding):
                iffloat_is_zero(candidate.remaining_qty,precision_rounding=self.uom_id.rounding):
                    next_candidates=candidates.filtered(lambdasvl:svl.remaining_qty>0)
                    new_standard_price=next_candidatesandnext_candidates[0].unit_costornew_standard_price
                break

        #Updatethestandardpricewiththepriceofthelastusedcandidate,ifany.
        ifnew_standard_priceandself.cost_method=='fifo':
            self.sudo().with_company(company.id).with_context(disable_auto_svl=True).standard_price=new_standard_price

        #Ifthere'sstillquantitytovaluebutwe'reoutofcandidates,wefallinthe
        #negativestockusecase.Wechosetovaluetheoutmoveatthepriceofthe
        #lastoutandacorrectionentrywillbemadeonce`_fifo_vacuum`iscalled.
        vals={}
        iffloat_is_zero(qty_to_take_on_candidates,precision_rounding=self.uom_id.rounding):
            vals={
                'value':-tmp_value,
                'unit_cost':tmp_value/quantity,
            }
        else:
            assertqty_to_take_on_candidates>0
            last_fifo_price=new_standard_priceorself.standard_price
            negative_stock_value=last_fifo_price*-qty_to_take_on_candidates
            tmp_value+=abs(negative_stock_value)
            vals={
                'remaining_qty':-qty_to_take_on_candidates,
                'value':-tmp_value,
                'unit_cost':last_fifo_price,
            }
        returnvals

    def_run_fifo_vacuum(self,company=None):
        """Compensatelayervaluedatanestimatedpricewiththepriceoffuturereceipts
        ifany.Iftheestimatedpriceisequalstotherealprice,nolayeriscreatedbut
        theoriginallayerismarkedascompensated.

        :paramcompany:recordsetof`res.company`tolimittheexecutionofthevacuum
        """
        self.ensure_one()
        ifcompanyisNone:
            company=self.env.company
        svls_to_vacuum=self.env['stock.valuation.layer'].sudo().search([
            ('product_id','=',self.id),
            ('remaining_qty','<',0),
            ('stock_move_id','!=',False),
            ('company_id','=',company.id),
        ],order='create_date,id')
        ifnotsvls_to_vacuum:
            return

        domain=[
            ('company_id','=',company.id),
            ('product_id','=',self.id),
            ('remaining_qty','>',0),
            ('create_date','>=',svls_to_vacuum[0].create_date),
        ]
        all_candidates=self.env['stock.valuation.layer'].sudo().search(domain)

        forsvl_to_vacuuminsvls_to_vacuum:
            #Wedon'tusesearchtoavoidexecuting_flush_searchandtodecreaseinteractionwithDB
            candidates=all_candidates.filtered(
                lambdar:r.create_date>svl_to_vacuum.create_date
                orr.create_date==svl_to_vacuum.create_date
                andr.id>svl_to_vacuum.id
            )
            ifnotcandidates:
                break
            qty_to_take_on_candidates=abs(svl_to_vacuum.remaining_qty)
            qty_taken_on_candidates=0
            tmp_value=0
            forcandidateincandidates:
                qty_taken_on_candidate=min(candidate.remaining_qty,qty_to_take_on_candidates)
                qty_taken_on_candidates+=qty_taken_on_candidate

                candidate_unit_cost=candidate.remaining_value/candidate.remaining_qty
                value_taken_on_candidate=qty_taken_on_candidate*candidate_unit_cost
                value_taken_on_candidate=candidate.currency_id.round(value_taken_on_candidate)
                new_remaining_value=candidate.remaining_value-value_taken_on_candidate

                candidate_vals={
                    'remaining_qty':candidate.remaining_qty-qty_taken_on_candidate,
                    'remaining_value':new_remaining_value
                }
                candidate.write(candidate_vals)
                ifnot(candidate.remaining_qty>0):
                    all_candidates-=candidate

                qty_to_take_on_candidates-=qty_taken_on_candidate
                tmp_value+=value_taken_on_candidate
                iffloat_is_zero(qty_to_take_on_candidates,precision_rounding=self.uom_id.rounding):
                    break

            #Gettheestimatedvaluewewillcorrect.
            remaining_value_before_vacuum=svl_to_vacuum.unit_cost*qty_taken_on_candidates
            new_remaining_qty=svl_to_vacuum.remaining_qty+qty_taken_on_candidates
            corrected_value=remaining_value_before_vacuum-tmp_value
            svl_to_vacuum.write({
                'remaining_qty':new_remaining_qty,
            })

            #Don'tcreatealayeroranaccountingentryifthecorrectedvalueiszero.
            ifsvl_to_vacuum.currency_id.is_zero(corrected_value):
                continue

            corrected_value=svl_to_vacuum.currency_id.round(corrected_value)
            move=svl_to_vacuum.stock_move_id
            vals={
                'product_id':self.id,
                'value':corrected_value,
                'unit_cost':0,
                'quantity':0,
                'remaining_qty':0,
                'stock_move_id':move.id,
                'company_id':move.company_id.id,
                'description':'Revaluationof%s(negativeinventory)'%(move.picking_id.nameormove.name),
                'stock_valuation_layer_id':svl_to_vacuum.id,
            }
            vacuum_svl=self.env['stock.valuation.layer'].sudo().create(vals)

            #Createtheaccountmove.
            ifself.valuation!='real_time':
                continue
            vacuum_svl.stock_move_id._account_entry_move(
                vacuum_svl.quantity,vacuum_svl.description,vacuum_svl.id,vacuum_svl.value
            )
            #Createtherelatedexpenseentry
            self._create_fifo_vacuum_anglo_saxon_expense_entry(vacuum_svl,svl_to_vacuum)

        #Ifsomenegativestockwerefixed,weneedtorecomputethestandardprice.
        product=self.with_company(company.id)
        ifproduct.cost_method=='average'andnotfloat_is_zero(product.quantity_svl,precision_rounding=self.uom_id.rounding):
            product.sudo().with_context(disable_auto_svl=True).write({'standard_price':product.value_svl/product.quantity_svl})


    def_create_fifo_vacuum_anglo_saxon_expense_entry(self,vacuum_svl,svl_to_vacuum):
        """Whenproductisdeliveredandinvoicedwhileyoudon'thaveunitsinstockanymore,therearechancesofthat
            productgettingundervalued/overvalued.So,weshouldneverthelesstakeintoaccountthefactthattheproducthas
            alreadybeendeliveredandinvoicedtothecustomerbypostingthevaluedifferenceintheexpenseaccountalso.
            Considerthebelowcasewhereproductisgettingundervalued:

            Youbought8units@10$->Youhaveastockvaluationof8units,unitcost10.
            Thenyoudeliver10unitsoftheproduct.
            Youassumedthemissing2shouldgooutatavalueof10$butyouarenotsureyetasithasn'tbeenboughtinFlectrayet.
            Afterwards,youbuymissing2unitsofthesameproductat12$insteadofexpected10$.
            Incasetheproducthasbeenundervaluedwhendeliveredwithoutstock,thevacuumentryisthefollowingone(thisentryalreadytakesplace):

            Account                        |Debit  |Credit
            ===================================================
            StockValuation                |0.00    |4.00
            StockInterim(Delivered)      |4.00    |0.00

            So,ondeliveringproductwithdifferentprice,Weshouldcreateadditionaljournalitemslike:
            Account                        |Debit   |Credit
            ===================================================
            StockInterim(Delivered)      |0.00    |4.00
            ExpensesRevaluation           |4.00    |0.00
        """
        ifnotvacuum_svl.company_id.anglo_saxon_accountingornotsvl_to_vacuum.stock_move_id._is_out():
            returnFalse
        AccountMove=self.env['account.move'].sudo()
        account_move_lines=svl_to_vacuum.account_move_id.line_ids
        #Findrelatedcustomerinvoicewhereproductisdeliveredwhileyoudon'thaveunitsinstockanymore
        reconciled_line_ids=list(set(account_move_lines._reconciled_lines())-set(account_move_lines.ids))
        account_move=AccountMove.search([('line_ids','in',reconciled_line_ids)],limit=1)
        #Ifdeliveredquantityisnotinvoicedthennoneedtocreatethisentry
        ifnotaccount_move:
            returnFalse
        accounts=svl_to_vacuum.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=account_move.fiscal_position_id)
        ifnotaccounts.get('stock_output')ornotaccounts.get('expense'):
            returnFalse
        description="Expenses%s"%(vacuum_svl.description)
        move_lines=vacuum_svl.stock_move_id._prepare_account_move_line(
            vacuum_svl.quantity,vacuum_svl.value*-1,
            accounts['stock_output'].id,accounts['expense'].id,
            description)
        new_account_move=AccountMove.sudo().create({
            'journal_id':accounts['stock_journal'].id,
            'line_ids':move_lines,
            'date':self._context.get('force_period_date',fields.Date.context_today(self)),
            'ref':description,
            'stock_move_id':vacuum_svl.stock_move_id.id,
            'move_type':'entry',
        })
        new_account_move._post()
        to_reconcile_account_move_lines=vacuum_svl.account_move_id.line_ids.filtered(lambdal:notl.reconciledandl.account_id==accounts['stock_output']andl.account_id.reconcile)
        to_reconcile_account_move_lines+=new_account_move.line_ids.filtered(lambdal:notl.reconciledandl.account_id==accounts['stock_output']andl.account_id.reconcile)
        returnto_reconcile_account_move_lines.reconcile()

    @api.model
    def_svl_empty_stock(self,description,product_category=None,product_template=None):
        impacted_product_ids=[]
        impacted_products=self.env['product.product']
        products_orig_quantity_svl={}

        #gettheimpactedproducts
        domain=[('type','=','product')]
        ifproduct_categoryisnotNone:
            domain+=[('categ_id','=',product_category.id)]
        elifproduct_templateisnotNone:
            domain+=[('product_tmpl_id','=',product_template.id)]
        else:
            raiseValueError()
        products=self.env['product.product'].search_read(domain,['quantity_svl'])
        forproductinproducts:
            impacted_product_ids.append(product['id'])
            products_orig_quantity_svl[product['id']]=product['quantity_svl']
        impacted_products|=self.env['product.product'].browse(impacted_product_ids)

        #emptyoutthestockfortheimpactedproducts
        empty_stock_svl_list=[]
        forproductinimpacted_products:
            #FIXMEsle:whynotuseproducts_orig_quantity_svlhere?
            iffloat_is_zero(product.quantity_svl,precision_rounding=product.uom_id.rounding):
                #FIXME:createanemptylayertotrackthechange?
                continue
            iffloat_compare(product.quantity_svl,0,precision_rounding=product.uom_id.rounding)>0:
                svsl_vals=product._prepare_out_svl_vals(product.quantity_svl,self.env.company)
            else:
                svsl_vals=product._prepare_in_svl_vals(abs(product.quantity_svl),product.value_svl/product.quantity_svl)
            svsl_vals['description']=description+svsl_vals.pop('rounding_adjustment','')
            svsl_vals['company_id']=self.env.company.id
            empty_stock_svl_list.append(svsl_vals)
        returnempty_stock_svl_list,products_orig_quantity_svl,impacted_products

    def_svl_replenish_stock(self,description,products_orig_quantity_svl):
        refill_stock_svl_list=[]
        forproductinself:
            quantity_svl=products_orig_quantity_svl[product.id]
            ifquantity_svl:
                iffloat_compare(quantity_svl,0,precision_rounding=product.uom_id.rounding)>0:
                    svl_vals=product._prepare_in_svl_vals(quantity_svl,product.standard_price)
                else:
                    svl_vals=product._prepare_out_svl_vals(abs(quantity_svl),self.env.company)
                svl_vals['description']=description
                svl_vals['company_id']=self.env.company.id
                refill_stock_svl_list.append(svl_vals)
        returnrefill_stock_svl_list

    @api.model
    def_svl_empty_stock_am(self,stock_valuation_layers):
        move_vals_list=[]
        product_accounts={product.id:product.product_tmpl_id.get_product_accounts()forproductinstock_valuation_layers.mapped('product_id')}
        forout_stock_valuation_layerinstock_valuation_layers:
            product=out_stock_valuation_layer.product_id
            expense_account=product._get_product_accounts()['expense']
            ifnotexpense_account:
                raiseUserError(_('Pleasedefineanexpenseaccountforthisproduct:"%s"(id:%d)-orforitscategory:"%s".')%(product.name,product.id,self.name))
            ifnotproduct_accounts[product.id].get('stock_valuation'):
                raiseUserError(_('Youdon\'thaveanystockvaluationaccountdefinedonyourproductcategory.Youmustdefineonebeforeprocessingthisoperation.'))

            debit_account_id=expense_account.id
            credit_account_id=product_accounts[product.id]['stock_valuation'].id
            value=out_stock_valuation_layer.value
            move_vals={
                'journal_id':product_accounts[product.id]['stock_journal'].id,
                'company_id':self.env.company.id,
                'ref':product.default_code,
                'stock_valuation_layer_ids':[(6,None,[out_stock_valuation_layer.id])],
                'line_ids':[(0,0,{
                    'name':out_stock_valuation_layer.description,
                    'account_id':debit_account_id,
                    'debit':abs(value),
                    'credit':0,
                    'product_id':product.id,
                }),(0,0,{
                    'name':out_stock_valuation_layer.description,
                    'account_id':credit_account_id,
                    'debit':0,
                    'credit':abs(value),
                    'product_id':product.id,
                })],
                'move_type':'entry',
            }
            move_vals_list.append(move_vals)
        returnmove_vals_list

    def_svl_replenish_stock_am(self,stock_valuation_layers):
        move_vals_list=[]
        product_accounts={product.id:product.product_tmpl_id.get_product_accounts()forproductinstock_valuation_layers.mapped('product_id')}
        forout_stock_valuation_layerinstock_valuation_layers:
            product=out_stock_valuation_layer.product_id
            ifnotproduct_accounts[product.id].get('stock_input'):
                raiseUserError(_('Youdon\'thaveanyinputvaluationaccountdefinedonyourproductcategory.Youmustdefineonebeforeprocessingthisoperation.'))
            ifnotproduct_accounts[product.id].get('stock_valuation'):
                raiseUserError(_('Youdon\'thaveanystockvaluationaccountdefinedonyourproductcategory.Youmustdefineonebeforeprocessingthisoperation.'))

            debit_account_id=product_accounts[product.id]['stock_valuation'].id
            credit_account_id=product_accounts[product.id]['stock_input'].id
            value=out_stock_valuation_layer.value
            move_vals={
                'journal_id':product_accounts[product.id]['stock_journal'].id,
                'company_id':self.env.company.id,
                'ref':product.default_code,
                'stock_valuation_layer_ids':[(6,None,[out_stock_valuation_layer.id])],
                'line_ids':[(0,0,{
                    'name':out_stock_valuation_layer.description,
                    'account_id':debit_account_id,
                    'debit':abs(value),
                    'credit':0,
                    'product_id':product.id,
                }),(0,0,{
                    'name':out_stock_valuation_layer.description,
                    'account_id':credit_account_id,
                    'debit':0,
                    'credit':abs(value),
                    'product_id':product.id,
                })],
                'move_type':'entry',
            }
            move_vals_list.append(move_vals)
        returnmove_vals_list

    #-------------------------------------------------------------------------
    #Anglosaxonhelpers
    #-------------------------------------------------------------------------
    def_stock_account_get_anglo_saxon_price_unit(self,uom=False):
        price=self.standard_price
        ifnotselfornotuomorself.uom_id.id==uom.id:
            returnpriceor0.0
        returnself.uom_id._compute_price(price,uom)

    def_compute_average_price(self,qty_invoiced,qty_to_invoice,stock_moves):
        """Gooverthevaluationlayersof`stock_moves`tovalue`qty_to_invoice`whiletaking
        careofignoring`qty_invoiced`.If`qty_to_invoice`isgreaterthanwhat'spossibleto
        valuewiththevaluationlayers,usetheproduct'sstandardprice.

        :paramqty_invoiced:quantityalreadyinvoiced
        :paramqty_to_invoice:quantitytoinvoice
        :paramstock_moves:recordsetof`stock.move`
        :returns:theanglosaxonpriceunit
        :rtype:float
        """
        self.ensure_one()
        ifnotqty_to_invoice:
            return0.0

        #ifTrue,considertheincomingmoves
        is_returned=self.env.context.get('is_returned',False)

        candidates=stock_moves\
            .sudo()\
            .filtered(lambdam:is_returned==bool(m.origin_returned_move_idandsum(m.stock_valuation_layer_ids.mapped('quantity'))>=0))\
            .mapped('stock_valuation_layer_ids')\
            .sorted()

        value_invoiced=self.env.context.get('value_invoiced',0)
        if'value_invoiced'inself.env.context:
            qty_valued,valuation=candidates._consume_all(qty_invoiced,value_invoiced,qty_to_invoice)
        else:
            qty_valued,valuation=candidates._consume_specific_qty(qty_invoiced,qty_to_invoice)

        #Ifthere'sstillquantitytoinvoicebutwe'reoutofcandidates,wechosethestandard
        #pricetoestimatetheanglosaxonpriceunit.
        missing=qty_to_invoice-qty_valued
        forsmlinstock_moves.move_line_ids:
            ifnotsml.owner_idorsml.owner_id==sml.company_id.partner_id:
                continue
            missing-=sml.product_uom_id._compute_quantity(sml.qty_done,self.uom_id,rounding_method='HALF-UP')
        iffloat_compare(missing,0,precision_rounding=self.uom_id.rounding)>0:
            valuation+=self.standard_price*missing

        returnvaluation/qty_to_invoice


classProductCategory(models.Model):
    _inherit='product.category'

    property_valuation=fields.Selection([
        ('manual_periodic','Manual'),
        ('real_time','Automated')],string='InventoryValuation',
        company_dependent=True,copy=True,required=True,
        help="""Manual:Theaccountingentriestovaluetheinventoryarenotpostedautomatically.
        Automated:Anaccountingentryisautomaticallycreatedtovaluetheinventorywhenaproductentersorleavesthecompany.
        """)
    property_cost_method=fields.Selection([
        ('standard','StandardPrice'),
        ('fifo','FirstInFirstOut(FIFO)'),
        ('average','AverageCost(AVCO)')],string="CostingMethod",
        company_dependent=True,copy=True,required=True,
        help="""StandardPrice:Theproductsarevaluedattheirstandardcostdefinedontheproduct.
        AverageCost(AVCO):Theproductsarevaluedatweightedaveragecost.
        FirstInFirstOut(FIFO):Theproductsarevaluedsupposingthosethatenterthecompanyfirstwillalsoleaveitfirst.
        """)
    property_stock_journal=fields.Many2one(
        'account.journal','StockJournal',company_dependent=True,
        domain="[('company_id','=',allowed_company_ids[0])]",check_company=True,
        help="Whendoingautomatedinventoryvaluation,thisistheAccountingJournalinwhichentrieswillbeautomaticallypostedwhenstockmovesareprocessed.")
    property_stock_account_input_categ_id=fields.Many2one(
        'account.account','StockInputAccount',company_dependent=True,
        domain="[('company_id','=',allowed_company_ids[0]),('deprecated','=',False)]",check_company=True,
        help="""Counterpartjournalitemsforallincomingstockmoveswillbepostedinthisaccount,unlessthereisaspecificvaluationaccount
                setonthesourcelocation.Thisisthedefaultvalueforallproductsinthiscategory.Itcanalsodirectlybesetoneachproduct.""")
    property_stock_account_output_categ_id=fields.Many2one(
        'account.account','StockOutputAccount',company_dependent=True,
        domain="[('company_id','=',allowed_company_ids[0]),('deprecated','=',False)]",check_company=True,
        help="""Whendoingautomatedinventoryvaluation,counterpartjournalitemsforalloutgoingstockmoveswillbepostedinthisaccount,
                unlessthereisaspecificvaluationaccountsetonthedestinationlocation.Thisisthedefaultvalueforallproductsinthiscategory.
                Itcanalsodirectlybesetoneachproduct.""")
    property_stock_valuation_account_id=fields.Many2one(
        'account.account','StockValuationAccount',company_dependent=True,
        domain="[('company_id','=',allowed_company_ids[0]),('deprecated','=',False)]",check_company=True,
        help="""Whenautomatedinventoryvaluationisenabledonaproduct,thisaccountwillholdthecurrentvalueoftheproducts.""",)

    @api.constrains('property_stock_valuation_account_id','property_stock_account_output_categ_id','property_stock_account_input_categ_id')
    def_check_valuation_accouts(self):
        #Preventtosetthevaluationaccountastheinputoroutputaccount.
        forcategoryinself:
            valuation_account=category.property_stock_valuation_account_id
            input_and_output_accounts=category.property_stock_account_input_categ_id|category.property_stock_account_output_categ_id
            ifvaluation_accountandvaluation_accountininput_and_output_accounts:
                raiseValidationError(_('TheStockInputand/orOutputaccountscannotbethesameastheStockValuationaccount.'))

    @api.onchange('property_cost_method')
    defonchange_property_cost(self):
        ifnotself._origin:
            #don'tdisplaythewarningwhencreatingaproductcategory
            return
        return{
            'warning':{
                'title':_("Warning"),
                'message':_("Changingyourcostmethodisanimportantchangethatwillimpactyourinventoryvaluation.Areyousureyouwanttomakethatchange?"),
            }
        }

    defwrite(self,vals):
        impacted_categories={}
        move_vals_list=[]
        Product=self.env['product.product']
        SVL=self.env['stock.valuation.layer']

        if'property_cost_method'invalsor'property_valuation'invals:
            #Whenthecostmethodorthevaluationarechangedonaproductcategory,weempty
            #outandreplenishthestockforeachimpactedproducts.
            new_cost_method=vals.get('property_cost_method')
            new_valuation=vals.get('property_valuation')

            forproduct_categoryinself:
                property_stock_fields=['property_stock_account_input_categ_id','property_stock_account_output_categ_id','property_stock_valuation_account_id']
                if'property_valuation'invalsandvals['property_valuation']=='manual_periodic'andproduct_category.property_valuation!='manual_periodic':
                    forstock_propertyinproperty_stock_fields:
                        vals[stock_property]=False
                elif'property_valuation'invalsandvals['property_valuation']=='real_time'andproduct_category.property_valuation!='real_time':
                    company_id=self.env.company
                    forstock_propertyinproperty_stock_fields:
                        vals[stock_property]=vals.get(stock_property,False)orcompany_id[stock_property]
                elifproduct_category.property_valuation=='manual_periodic':
                    forstock_propertyinproperty_stock_fields:
                        ifstock_propertyinvals:
                            vals.pop(stock_property)
                else:
                    forstock_propertyinproperty_stock_fields:
                        ifstock_propertyinvalsandvals[stock_property]isFalse:
                            vals.pop(stock_property)
                valuation_impacted=False
                ifnew_cost_methodandnew_cost_method!=product_category.property_cost_method:
                    valuation_impacted=True
                ifnew_valuationandnew_valuation!=product_category.property_valuation:
                    valuation_impacted=True
                ifvaluation_impactedisFalse:
                    continue

                #Emptyoutthestockwiththecurrentcostmethod.
                ifnew_cost_method:
                    description=_("Costingmethodchangeforproductcategory%s:from%sto%s.")\
                        %(product_category.display_name,product_category.property_cost_method,new_cost_method)
                else:
                    description=_("Valuationmethodchangeforproductcategory%s:from%sto%s.")\
                        %(product_category.display_name,product_category.property_valuation,new_valuation)
                out_svl_vals_list,products_orig_quantity_svl,products=Product\
                    ._svl_empty_stock(description,product_category=product_category)
                out_stock_valuation_layers=SVL.sudo().create(out_svl_vals_list)
                ifproduct_category.property_valuation=='real_time':
                    move_vals_list+=Product._svl_empty_stock_am(out_stock_valuation_layers)
                impacted_categories[product_category]=(products,description,products_orig_quantity_svl)

        res=super(ProductCategory,self).write(vals)

        forproduct_category,(products,description,products_orig_quantity_svl)inimpacted_categories.items():
            #Replenishthestockwiththenewcostmethod.
            in_svl_vals_list=products._svl_replenish_stock(description,products_orig_quantity_svl)
            in_stock_valuation_layers=SVL.sudo().create(in_svl_vals_list)
            ifproduct_category.property_valuation=='real_time':
                move_vals_list+=Product._svl_replenish_stock_am(in_stock_valuation_layers)

        #Checkaccessright
        ifmove_vals_listandnotself.env['stock.valuation.layer'].check_access_rights('read',raise_exception=False):
            raiseUserError(_("Theactionleadstothecreationofajournalentry,forwhichyoudon'thavetheaccessrights."))
        #Createtheaccountmoves.
        ifmove_vals_list:
            account_moves=self.env['account.move'].sudo().create(move_vals_list)
            account_moves._post()
        returnres


    @api.model
    defcreate(self,vals):
        if'property_valuation'notinvalsorvals['property_valuation']=='manual_periodic':
            vals['property_stock_account_input_categ_id']=False
            vals['property_stock_account_output_categ_id']=False
            vals['property_stock_valuation_account_id']=False
        if'property_valuation'invalsandvals['property_valuation']=='real_time':
            company_id=self.env.company
            vals['property_stock_account_input_categ_id']=vals.get('property_stock_account_input_categ_id',False)orcompany_id.property_stock_account_input_categ_id
            vals['property_stock_account_output_categ_id']=vals.get('property_stock_account_output_categ_id',False)orcompany_id.property_stock_account_output_categ_id
            vals['property_stock_valuation_account_id']=vals.get('property_stock_valuation_account_id',False)orcompany_id.property_stock_valuation_account_id

        returnsuper().create(vals)

    @api.onchange('property_valuation')
    defonchange_property_valuation(self):
        #Removeorsettheaccountstockpropertiesifnecessary
        ifself.property_valuation=='manual_periodic':
            self.property_stock_account_input_categ_id=False
            self.property_stock_account_output_categ_id=False
            self.property_stock_valuation_account_id=False
        ifself.property_valuation=='real_time':
            company_id=self.env.company
            self.property_stock_account_input_categ_id=company_id.property_stock_account_input_categ_id
            self.property_stock_account_output_categ_id=company_id.property_stock_account_output_categ_id
            self.property_stock_valuation_account_id=company_id.property_stock_valuation_account_id
