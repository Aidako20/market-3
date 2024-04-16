#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.toolsimportfloat_compare,float_is_zero,OrderedSet

importlogging
_logger=logging.getLogger(__name__)


classStockMove(models.Model):
    _inherit="stock.move"

    to_refund=fields.Boolean(string="UpdatequantitiesonSO/PO",copy=False,
                               help='Triggeradecreaseofthedelivered/receivedquantityintheassociatedSaleOrder/PurchaseOrder')
    account_move_ids=fields.One2many('account.move','stock_move_id')
    stock_valuation_layer_ids=fields.One2many('stock.valuation.layer','stock_move_id')

    def_filter_anglo_saxon_moves(self,product):
        returnself.filtered(lambdam:m.product_id.id==product.id)

    defaction_get_account_moves(self):
        self.ensure_one()
        action_data=self.env['ir.actions.act_window']._for_xml_id('account.action_move_journal_line')
        action_data['domain']=[('id','in',self.account_move_ids.ids)]
        returnaction_data

    def_should_force_price_unit(self):
        self.ensure_one()
        returnFalse

    def_get_price_unit(self):
        """Returnstheunitpricetovaluethisstockmove"""
        self.ensure_one()
        price_unit=self.price_unit
        precision=self.env['decimal.precision'].precision_get('ProductPrice')
        #Ifthemoveisareturn,usetheoriginalmove'spriceunit.
        ifself.origin_returned_move_idandself.origin_returned_move_id.sudo().stock_valuation_layer_ids:
            layers=self.origin_returned_move_id.sudo().stock_valuation_layer_ids
            #dropshippingcreateadditionalpositivesvltomakesurethereisnoimpactonthestockvaluation
            #Weneedtoremovethemfromthecomputationofthepriceunit.
            ifself.origin_returned_move_id._is_dropshipped()orself.origin_returned_move_id._is_dropshipped_returned():
                layers=layers.filtered(lambdal:float_compare(l.value,0,precision_rounding=l.product_id.uom_id.rounding)<=0)
            layers|=layers.stock_valuation_layer_ids
            quantity=sum(layers.mapped("quantity"))
            returnsum(layers.mapped("value"))/quantityifnotfloat_is_zero(quantity,precision_rounding=layers.uom_id.rounding)else0
        returnprice_unitifnotfloat_is_zero(price_unit,precision)orself._should_force_price_unit()elseself.product_id.standard_price

    @api.model
    def_get_valued_types(self):
        """Returnsalistof`valued_type`asstrings.During`action_done`,we'llcall
        `_is_[valued_type]'.Iftheresultofthismethodistruthy,we'llconsiderthemovetobe
        valued.

        :returns:alistof`valued_type`
        :rtype:list
        """
        return['in','out','dropshipped','dropshipped_returned']

    def_get_in_move_lines(self):
        """Returnsthe`stock.move.line`recordsof`self`consideredasincoming.Itisdonethanks
        tothe`_should_be_valued`methodoftheirsourceanddestionationlocationaswellastheir
        owner.

        :returns:asubsetof`self`containingtheincomingrecords
        :rtype:recordset
        """
        self.ensure_one()
        res=OrderedSet()
        formove_lineinself.move_line_ids:
            ifmove_line.owner_idandmove_line.owner_id!=move_line.company_id.partner_id:
                continue
            ifnotmove_line.location_id._should_be_valued()andmove_line.location_dest_id._should_be_valued():
                res.add(move_line.id)
        returnself.env['stock.move.line'].browse(res)

    def_is_in(self):
        """Checkifthemoveshouldbeconsideredasenteringthecompanysothatthecostmethod
        willbeabletoapplythecorrectlogic.

        :returns:TrueifthemoveisenteringthecompanyelseFalse
        :rtype:bool
        """
        self.ensure_one()
        ifself._get_in_move_lines()andnotself._is_dropshipped_returned():
            returnTrue
        returnFalse

    def_get_out_move_lines(self):
        """Returnsthe`stock.move.line`recordsof`self`consideredasoutgoing.Itisdonethanks
        tothe`_should_be_valued`methodoftheirsourceanddestionationlocationaswellastheir
        owner.

        :returns:asubsetof`self`containingtheoutgoingrecords
        :rtype:recordset
        """
        res=self.env['stock.move.line']
        formove_lineinself.move_line_ids:
            ifmove_line.owner_idandmove_line.owner_id!=move_line.company_id.partner_id:
                continue
            ifmove_line.location_id._should_be_valued()andnotmove_line.location_dest_id._should_be_valued():
                res|=move_line
        returnres

    def_is_out(self):
        """Checkifthemoveshouldbeconsideredasleavingthecompanysothatthecostmethod
        willbeabletoapplythecorrectlogic.

        :returns:TrueifthemoveisleavingthecompanyelseFalse
        :rtype:bool
        """
        self.ensure_one()
        ifself._get_out_move_lines()andnotself._is_dropshipped():
            returnTrue
        returnFalse

    def_is_dropshipped(self):
        """Checkifthemoveshouldbeconsideredasadropshippingmovesothatthecostmethod
        willbeabletoapplythecorrectlogic.

        :returns:TrueifthemoveisadropshippingoneelseFalse
        :rtype:bool
        """
        self.ensure_one()
        returnself.location_id.usage=='supplier'andself.location_dest_id.usage=='customer'

    def_is_dropshipped_returned(self):
        """Checkifthemoveshouldbeconsideredasareturneddropshippingmovesothatthecost
        methodwillbeabletoapplythecorrectlogic.

        :returns:TrueifthemoveisareturneddropshippingoneelseFalse
        :rtype:bool
        """
        self.ensure_one()
        returnself.location_id.usage=='customer'andself.location_dest_id.usage=='supplier'

    def_prepare_common_svl_vals(self):
        """Whena`stock.valuation.layer`iscreatedfroma`stock.move`,wecanprepareadictof
        commonvals.

        :returns:thecommonvalueswhencreatinga`stock.valuation.layer`froma`stock.move`
        :rtype:dict
        """
        self.ensure_one()
        return{
            'stock_move_id':self.id,
            'company_id':self.company_id.id,
            'product_id':self.product_id.id,
            'description':self.referenceand'%s-%s'%(self.reference,self.product_id.name)orself.product_id.name,
        }

    def_create_in_svl(self,forced_quantity=None):
        """Createa`stock.valuation.layer`from`self`.

        :paramforced_quantity:undersomecircunstances,thequantitytovalueisdifferentthan
            theinitialdemandofthemove(Defaultvalue=None)
        """
        svl_vals_list=[]
        formoveinself:
            move=move.with_company(move.company_id)
            valued_move_lines=move._get_in_move_lines()
            valued_quantity=0
            forvalued_move_lineinvalued_move_lines:
                valued_quantity+=valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,move.product_id.uom_id)
            unit_cost=abs(move._get_price_unit()) #Maybenegative(i.e.decreaseanoutmove).
            ifmove.product_id.cost_method=='standard':
                unit_cost=move.product_id.standard_price
            svl_vals=move.product_id._prepare_in_svl_vals(forced_quantityorvalued_quantity,unit_cost)
            svl_vals.update(move._prepare_common_svl_vals())
            ifforced_quantity:
                svl_vals['description']='Correctionof%s(modificationofpastmove)'%move.picking_id.nameormove.name
            svl_vals_list.append(svl_vals)
        returnself.env['stock.valuation.layer'].sudo().create(svl_vals_list)

    def_create_out_svl(self,forced_quantity=None):
        """Createa`stock.valuation.layer`from`self`.

        :paramforced_quantity:undersomecircunstances,thequantitytovalueisdifferentthan
            theinitialdemandofthemove(Defaultvalue=None)
        """
        svl_vals_list=[]
        formoveinself:
            move=move.with_company(move.company_id)
            valued_move_lines=move._get_out_move_lines()
            valued_quantity=0
            forvalued_move_lineinvalued_move_lines:
                valued_quantity+=valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,move.product_id.uom_id)
            iffloat_is_zero(forced_quantityorvalued_quantity,precision_rounding=move.product_id.uom_id.rounding):
                continue
            svl_vals=move.product_id._prepare_out_svl_vals(forced_quantityorvalued_quantity,move.company_id)
            svl_vals.update(move._prepare_common_svl_vals())
            ifforced_quantity:
                svl_vals['description']='Correctionof%s(modificationofpastmove)'%move.picking_id.nameormove.name
            svl_vals['description']+=svl_vals.pop('rounding_adjustment','')
            svl_vals_list.append(svl_vals)
        returnself.env['stock.valuation.layer'].sudo().create(svl_vals_list)

    def_create_dropshipped_svl(self,forced_quantity=None):
        """Createa`stock.valuation.layer`from`self`.

        :paramforced_quantity:undersomecircunstances,thequantitytovalueisdifferentthan
            theinitialdemandofthemove(Defaultvalue=None)
        """
        svl_vals_list=[]
        formoveinself:
            move=move.with_company(move.company_id)
            valued_move_lines=move.move_line_ids
            valued_quantity=0
            forvalued_move_lineinvalued_move_lines:
                valued_quantity+=valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,move.product_id.uom_id)
            quantity=forced_quantityorvalued_quantity

            unit_cost=move._get_price_unit()
            ifmove.product_id.cost_method=='standard':
                unit_cost=move.product_id.standard_price

            common_vals=dict(move._prepare_common_svl_vals(),remaining_qty=0)

            #createtheinifitdoesnotcomefromavaluedlocation(egsubcontract->customer)
            ifnotmove.location_id._should_be_valued():
                in_vals={
                    'unit_cost':unit_cost,
                    'value':unit_cost*quantity,
                    'quantity':quantity,
                }
                in_vals.update(common_vals)
                svl_vals_list.append(in_vals)

            #createtheoutifitdoesnotgotoavaluedlocation(egcustomer->subcontract)
            ifnotmove.location_dest_id._should_be_valued():
                out_vals={
                    'unit_cost':unit_cost,
                    'value':unit_cost*quantity*-1,
                    'quantity':quantity*-1,
                }
                out_vals.update(common_vals)
                svl_vals_list.append(out_vals)

        returnself.env['stock.valuation.layer'].sudo().create(svl_vals_list)

    def_create_dropshipped_returned_svl(self,forced_quantity=None):
        """Createa`stock.valuation.layer`from`self`.

        :paramforced_quantity:undersomecircunstances,thequantitytovalueisdifferentthan
            theinitialdemandofthemove(Defaultvalue=None)
        """
        returnself._create_dropshipped_svl(forced_quantity=forced_quantity)

    def_action_done(self,cancel_backorder=False):
        #Initadictthatwillgroupthemovesbyvaluationtype,accordingto`move._is_valued_type`.
        valued_moves={valued_type:self.env['stock.move']forvalued_typeinself._get_valued_types()}
        formoveinself:
            iffloat_is_zero(move.quantity_done,precision_rounding=move.product_uom.rounding):
                continue
            forvalued_typeinself._get_valued_types():
                ifgetattr(move,'_is_%s'%valued_type)():
                    valued_moves[valued_type]|=move

        #AVCOapplication
        valued_moves['in'].product_price_update_before_done()

        res=super(StockMove,self)._action_done(cancel_backorder=cancel_backorder)

        #'_action_done'mighthavedeletedsomeexplodedstockmoves
        valued_moves={value_type:moves.exists()forvalue_type,movesinvalued_moves.items()}

        #'_action_done'mighthavecreatedanextramovetobevalued
        formoveinres-self:
            forvalued_typeinself._get_valued_types():
                ifgetattr(move,'_is_%s'%valued_type)():
                    valued_moves[valued_type]|=move

        stock_valuation_layers=self.env['stock.valuation.layer'].sudo()
        #Createthevaluationlayersinbatchbycalling`moves._create_valued_type_svl`.
        forvalued_typeinself._get_valued_types():
            todo_valued_moves=valued_moves[valued_type]
            iftodo_valued_moves:
                todo_valued_moves._sanity_check_for_valuation()
                stock_valuation_layers|=getattr(todo_valued_moves,'_create_%s_svl'%valued_type)()


        forsvlinstock_valuation_layers:
            ifnotsvl.with_company(svl.company_id).product_id.valuation=='real_time':
                continue
            ifsvl.currency_id.is_zero(svl.value):
                continue
            svl.stock_move_id.with_company(svl.company_id)._account_entry_move(svl.quantity,svl.description,svl.id,svl.value)

        stock_valuation_layers._check_company()

        #Foreveryinmove,runthevacuumforthelinkedproduct.
        products_to_vacuum=valued_moves['in'].mapped('product_id')
        company=valued_moves['in'].mapped('company_id')andvalued_moves['in'].mapped('company_id')[0]orself.env.company
        forproduct_to_vacuuminproducts_to_vacuum:
            product_to_vacuum._run_fifo_vacuum(company)

        returnres

    def_sanity_check_for_valuation(self):
        formoveinself:
            #Applyrestrictionsonthestockmovetobeabletomake
            #consistentaccountingentries.
            ifmove._is_in()andmove._is_out():
                raiseUserError(_("Themovelinesarenotinaconsistentstate:someareenteringandotherareleavingthecompany."))
            company_src=move.mapped('move_line_ids.location_id.company_id')
            company_dst=move.mapped('move_line_ids.location_dest_id.company_id')
            try:
                ifcompany_src:
                    company_src.ensure_one()
                ifcompany_dst:
                    company_dst.ensure_one()
            exceptValueError:
                raiseUserError(_("Themovelinesarenotinaconsistentstates:theydonotsharethesameoriginordestinationcompany."))
            ifcompany_srcandcompany_dstandcompany_src.id!=company_dst.id:
                raiseUserError(_("Themovelinesarenotinaconsistentstates:theyaredoinganintercompanyinasinglestepwhiletheyshouldgothroughtheintercompanytransitlocation."))

    defproduct_price_update_before_done(self,forced_qty=None):
        tmpl_dict=defaultdict(lambda:0.0)
        #adaptstandardpriceonincommingmovesiftheproductcost_methodis'average'
        std_price_update={}
        formoveinself.filtered(lambdamove:move._is_in()andmove.with_company(move.company_id).product_id.cost_method=='average'):
            product_tot_qty_available=move.product_id.sudo().with_company(move.company_id).quantity_svl+tmpl_dict[move.product_id.id]
            rounding=move.product_id.uom_id.rounding

            valued_move_lines=move._get_in_move_lines()
            qty_done=0
            forvalued_move_lineinvalued_move_lines:
                qty_done+=valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,move.product_id.uom_id)

            qty=forced_qtyorqty_done
            iffloat_is_zero(product_tot_qty_available,precision_rounding=rounding):
                new_std_price=move._get_price_unit()
            eliffloat_is_zero(product_tot_qty_available+move.product_qty,precision_rounding=rounding)or\
                    float_is_zero(product_tot_qty_available+qty,precision_rounding=rounding):
                new_std_price=move._get_price_unit()
            else:
                #Getthestandardprice
                amount_unit=std_price_update.get((move.company_id.id,move.product_id.id))ormove.product_id.with_company(move.company_id).standard_price
                new_std_price=((amount_unit*product_tot_qty_available)+(move._get_price_unit()*qty))/(product_tot_qty_available+qty)

            tmpl_dict[move.product_id.id]+=qty_done
            #Writethestandardprice,asSUPERUSER_IDbecauseawarehousemanagermaynothavetherighttowriteonproducts
            move.product_id.with_company(move.company_id.id).with_context(disable_auto_svl=True).sudo().write({'standard_price':new_std_price})
            std_price_update[move.company_id.id,move.product_id.id]=new_std_price

        #adaptstandardpriceonincommingmovesiftheproductcost_methodis'fifo'
        formoveinself.filtered(lambdamove:
                                  move.with_company(move.company_id).product_id.cost_method=='fifo'
                                  andfloat_is_zero(move.product_id.sudo().quantity_svl,precision_rounding=move.product_id.uom_id.rounding)):
            move.product_id.with_company(move.company_id.id).sudo().write({'standard_price':move._get_price_unit()})

    def_get_accounting_data_for_valuation(self):
        """ReturntheaccountsandjournaltousetopostJournalEntriesfor
        thereal-timevaluationofthequant."""
        self.ensure_one()
        self=self.with_company(self.company_id)
        accounts_data=self.product_id.product_tmpl_id.get_product_accounts()

        acc_src=self._get_src_account(accounts_data)
        acc_dest=self._get_dest_account(accounts_data)

        acc_valuation=accounts_data.get('stock_valuation',False)
        ifacc_valuation:
            acc_valuation=acc_valuation.id
        ifnotaccounts_data.get('stock_journal',False):
            raiseUserError(_('Youdon\'thaveanystockjournaldefinedonyourproductcategory,checkifyouhaveinstalledachartofaccounts.'))
        ifnotacc_src:
            raiseUserError(_('Cannotfindastockinputaccountfortheproduct%s.Youmustdefineoneontheproductcategory,oronthelocation,beforeprocessingthisoperation.')%(self.product_id.display_name))
        ifnotacc_dest:
            raiseUserError(_('Cannotfindastockoutputaccountfortheproduct%s.Youmustdefineoneontheproductcategory,oronthelocation,beforeprocessingthisoperation.')%(self.product_id.display_name))
        ifnotacc_valuation:
            raiseUserError(_('Youdon\'thaveanystockvaluationaccountdefinedonyourproductcategory.Youmustdefineonebeforeprocessingthisoperation.'))
        journal_id=accounts_data['stock_journal'].id
        returnjournal_id,acc_src,acc_dest,acc_valuation

    def_get_src_account(self,accounts_data):
        returnself.location_id.valuation_out_account_id.idoraccounts_data['stock_input'].id

    def_get_dest_account(self,accounts_data):
        returnself.location_dest_id.valuation_in_account_id.idoraccounts_data['stock_output'].id

    def_prepare_account_move_line(self,qty,cost,credit_account_id,debit_account_id,description):
        """
        Generatetheaccount.move.linevaluestoposttotrackthestockvaluationdifferenceduetothe
        processingofthegivenquant.
        """
        self.ensure_one()

        #thestandard_priceoftheproductmaybeinanotherdecimalprecision,ornotcompatiblewiththecoinageof
        #thecompanycurrency...soweneedtouseround()beforecreatingtheaccountingentries.
        debit_value=self.company_id.currency_id.round(cost)
        credit_value=debit_value

        valuation_partner_id=self._get_partner_id_for_valuation_lines()
        res=[(0,0,line_vals)forline_valsinself._generate_valuation_lines_data(valuation_partner_id,qty,debit_value,credit_value,debit_account_id,credit_account_id,description).values()]

        returnres

    def_generate_valuation_lines_data(self,partner_id,qty,debit_value,credit_value,debit_account_id,credit_account_id,description):
        #Thismethodreturnsadictionarytoprovideaneasyextensionhooktomodifythevaluationlines(seepurchaseforanexample)
        self.ensure_one()
        debit_line_vals={
            'name':description,
            'product_id':self.product_id.id,
            'quantity':qty,
            'product_uom_id':self.product_id.uom_id.id,
            'ref':description,
            'partner_id':partner_id,
            'debit':debit_valueifdebit_value>0else0,
            'credit':-debit_valueifdebit_value<0else0,
            'account_id':debit_account_id,
        }

        credit_line_vals={
            'name':description,
            'product_id':self.product_id.id,
            'quantity':qty,
            'product_uom_id':self.product_id.uom_id.id,
            'ref':description,
            'partner_id':partner_id,
            'credit':credit_valueifcredit_value>0else0,
            'debit':-credit_valueifcredit_value<0else0,
            'account_id':credit_account_id,
        }

        rslt={'credit_line_vals':credit_line_vals,'debit_line_vals':debit_line_vals}
        ifcredit_value!=debit_value:
            #forsupplierreturnsofproductinaveragecostingmethod,inanglosaxonmode
            diff_amount=debit_value-credit_value
            price_diff_account=self.product_id.property_account_creditor_price_difference

            ifnotprice_diff_account:
                price_diff_account=self.product_id.categ_id.property_account_creditor_price_difference_categ
            ifnotprice_diff_account:
                raiseUserError(_('Configurationerror.Pleaseconfigurethepricedifferenceaccountontheproductoritscategorytoprocessthisoperation.'))

            rslt['price_diff_line_vals']={
                'name':self.name,
                'product_id':self.product_id.id,
                'quantity':qty,
                'product_uom_id':self.product_id.uom_id.id,
                'ref':description,
                'partner_id':partner_id,
                'credit':diff_amount>0anddiff_amountor0,
                'debit':diff_amount<0and-diff_amountor0,
                'account_id':price_diff_account.id,
            }
        returnrslt

    def_get_partner_id_for_valuation_lines(self):
        return(self.picking_id.partner_idandself.env['res.partner']._find_accounting_partner(self.picking_id.partner_id).id)orFalse

    def_prepare_move_split_vals(self,uom_qty):
        vals=super(StockMove,self)._prepare_move_split_vals(uom_qty)
        vals['to_refund']=self.to_refund
        returnvals

    def_create_account_move_line(self,credit_account_id,debit_account_id,journal_id,qty,description,svl_id,cost):
        self.ensure_one()
        AccountMove=self.env['account.move'].with_context(default_journal_id=journal_id)

        move_lines=self._prepare_account_move_line(qty,cost,credit_account_id,debit_account_id,description)
        ifmove_lines:
            date=self._context.get('force_period_date',fields.Date.context_today(self))
            new_account_move=AccountMove.sudo().create({
                'journal_id':journal_id,
                'line_ids':move_lines,
                'date':date,
                'ref':description,
                'stock_move_id':self.id,
                'stock_valuation_layer_ids':[(6,None,[svl_id])],
                'move_type':'entry',
            })
            new_account_move._post()

    def_account_entry_move(self,qty,description,svl_id,cost):
        """AccountingValuationEntries"""
        self.ensure_one()
        ifself.product_id.type!='product':
            #nostockvaluationforconsumableproducts
            returnFalse
        ifself.restrict_partner_idandself.restrict_partner_id!=self.company_id.partner_id:
            #ifthemoveisn'townedbythecompany,wedon'tmakeanyvaluation
            returnFalse

        company_from=self._is_out()andself.mapped('move_line_ids.location_id.company_id')orFalse
        company_to=self._is_in()andself.mapped('move_line_ids.location_dest_id.company_id')orFalse

        journal_id,acc_src,acc_dest,acc_valuation=self._get_accounting_data_for_valuation()
        #CreateJournalEntryforproductsarrivinginthecompany;incaseofroutesmakingthelinkbetweenseveral
        #warehouseofthesamecompany,thetransitlocationbelongstothiscompany,sowedon'tneedtocreateaccountingentries
        ifself._is_in():
            ifself._is_returned(valued_type='in'):
                self.with_company(company_to)._create_account_move_line(acc_dest,acc_valuation,journal_id,qty,description,svl_id,cost)
            else:
                self.with_company(company_to)._create_account_move_line(acc_src,acc_valuation,journal_id,qty,description,svl_id,cost)

        #CreateJournalEntryforproductsleavingthecompany
        ifself._is_out():
            cost=-1*cost
            ifself._is_returned(valued_type='out'):
                self.with_company(company_from)._create_account_move_line(acc_valuation,acc_src,journal_id,qty,description,svl_id,cost)
            else:
                self.with_company(company_from)._create_account_move_line(acc_valuation,acc_dest,journal_id,qty,description,svl_id,cost)

        ifself.company_id.anglo_saxon_accounting:
            #Createsanaccountentryfromstock_inputtostock_outputonadropshipmove.https://github.com/flectra/flectra/issues/12687
            ifself._is_dropshipped():
                ifcost>0:
                    self.with_company(self.company_id)._create_account_move_line(acc_src,acc_valuation,journal_id,qty,description,svl_id,cost)
                else:
                    cost=-1*cost
                    self.with_company(self.company_id)._create_account_move_line(acc_valuation,acc_dest,journal_id,qty,description,svl_id,cost)
            elifself._is_dropshipped_returned():
                ifcost>0andself.location_dest_id._should_be_valued():
                    self.with_company(self.company_id)._create_account_move_line(acc_valuation,acc_src,journal_id,qty,description,svl_id,cost)
                elifcost>0:
                    self.with_company(self.company_id)._create_account_move_line(acc_dest,acc_valuation,journal_id,qty,description,svl_id,cost)
                else:
                    cost=-1*cost
                    self.with_company(self.company_id)._create_account_move_line(acc_valuation,acc_src,journal_id,qty,description,svl_id,cost)

        ifself.company_id.anglo_saxon_accounting:
            #Eventuallyreconciletogethertheinvoiceandvaluationaccountingentriesonthestockinterimaccounts
            self._get_related_invoices()._stock_account_anglo_saxon_reconcile_valuation(product=self.product_id)

    def_get_related_invoices(self): #Tobeoverriddeninpurchaseandsale_stock
        """Thismethodisoverridedinbothpurchaseandsale_stockmodulestoadapt
        tothewaytheymixstockmoveswithinvoices.
        """
        returnself.env['account.move']

    def_is_returned(self,valued_type):
        self.ensure_one()
        ifvalued_type=='in':
            returnself.location_idandself.location_id.usage=='customer'  #goodsreturnedfromcustomer
        ifvalued_type=='out':
            returnself.location_dest_idandself.location_dest_id.usage=='supplier'  #goodsreturnedtosupplier
