#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportUserError
fromflectra.tools.float_utilsimportfloat_is_zero


SPLIT_METHOD=[
    ('equal','Equal'),
    ('by_quantity','ByQuantity'),
    ('by_current_cost_price','ByCurrentCost'),
    ('by_weight','ByWeight'),
    ('by_volume','ByVolume'),
]


classStockLandedCost(models.Model):
    _name='stock.landed.cost'
    _description='StockLandedCost'
    _inherit=['mail.thread','mail.activity.mixin']

    def_default_account_journal_id(self):
        """Takethejournalconfiguredinthecompany,elsefallbackonthestockjournal."""
        lc_journal=self.env['account.journal']
        ifself.env.company.lc_journal_id:
            lc_journal=self.env.company.lc_journal_id
        else:
            lc_journal=self.env['ir.property']._get("property_stock_journal","product.category")
        returnlc_journal

    name=fields.Char(
        'Name',default=lambdaself:_('New'),
        copy=False,readonly=True,tracking=True)
    date=fields.Date(
        'Date',default=fields.Date.context_today,
        copy=False,required=True,states={'done':[('readonly',True)]},tracking=True)
    target_model=fields.Selection(
        [('picking','Transfers')],string="ApplyOn",
        required=True,default='picking',
        copy=False,states={'done':[('readonly',True)]})
    picking_ids=fields.Many2many(
        'stock.picking',string='Transfers',
        copy=False,states={'done':[('readonly',True)]})
    allowed_picking_ids=fields.Many2many('stock.picking',compute='_compute_allowed_picking_ids')
    cost_lines=fields.One2many(
        'stock.landed.cost.lines','cost_id','CostLines',
        copy=True,states={'done':[('readonly',True)]})
    valuation_adjustment_lines=fields.One2many(
        'stock.valuation.adjustment.lines','cost_id','ValuationAdjustments',
        states={'done':[('readonly',True)]})
    description=fields.Text(
        'ItemDescription',states={'done':[('readonly',True)]})
    amount_total=fields.Monetary(
        'Total',compute='_compute_total_amount',
        store=True,tracking=True)
    state=fields.Selection([
        ('draft','Draft'),
        ('done','Posted'),
        ('cancel','Cancelled')],'State',default='draft',
        copy=False,readonly=True,tracking=True)
    account_move_id=fields.Many2one(
        'account.move','JournalEntry',
        copy=False,readonly=True)
    account_journal_id=fields.Many2one(
        'account.journal','AccountJournal',
        required=True,states={'done':[('readonly',True)]},default=lambdaself:self._default_account_journal_id())
    company_id=fields.Many2one('res.company',string="Company",
        related='account_journal_id.company_id')
    stock_valuation_layer_ids=fields.One2many('stock.valuation.layer','stock_landed_cost_id')
    vendor_bill_id=fields.Many2one(
        'account.move','VendorBill',copy=False,domain=[('move_type','=','in_invoice')])
    currency_id=fields.Many2one('res.currency',related='company_id.currency_id')

    @api.depends('cost_lines.price_unit')
    def_compute_total_amount(self):
        forcostinself:
            cost.amount_total=sum(line.price_unitforlineincost.cost_lines)

    @api.depends('company_id')
    def_compute_allowed_picking_ids(self):
        #Backportoff329de26:allowed_picking_idsisuseless,view_stock_landed_cost_formnolongerusesit,
        #thefieldanditscomputearekeptsincethisisastableversion.Still,thiscomputehasbeenmade
        #moreresilienttoMemoryErrors.
        valued_picking_ids_per_company=defaultdict(list)
        ifself.company_id:
            self.env.cr.execute("""SELECTsm.picking_id,sm.company_id
                                     FROMstock_moveASsm
                               INNERJOINstock_valuation_layerASsvlONsvl.stock_move_id=sm.id
                                    WHEREsm.picking_idISNOTNULLANDsm.company_idIN%s
                                 GROUPBYsm.picking_id,sm.company_id""",[tuple(self.company_id.ids)])
            forresinself.env.cr.fetchall():
                valued_picking_ids_per_company[res[1]].append(res[0])
        forcostinself:
            n=5000
            cost.allowed_picking_ids=valued_picking_ids_per_company[cost.company_id.id][:n]
            forids_chunkintools.split_every(n,valued_picking_ids_per_company[cost.company_id.id][n:]):
                cost.allowed_picking_ids=[(4,id_)forid_inids_chunk]

    @api.onchange('target_model')
    def_onchange_target_model(self):
        ifself.target_model!='picking':
            self.picking_ids=False

    @api.model
    defcreate(self,vals):
        ifvals.get('name',_('New'))==_('New'):
            vals['name']=self.env['ir.sequence'].next_by_code('stock.landed.cost')
        returnsuper().create(vals)

    defunlink(self):
        self.button_cancel()
        returnsuper().unlink()

    def_track_subtype(self,init_values):
        if'state'ininit_valuesandself.state=='done':
            returnself.env.ref('stock_landed_costs.mt_stock_landed_cost_open')
        returnsuper()._track_subtype(init_values)

    defbutton_cancel(self):
        ifany(cost.state=='done'forcostinself):
            raiseUserError(
                _('Validatedlandedcostscannotbecancelled,butyoucouldcreatenegativelandedcoststoreversethem'))
        returnself.write({'state':'cancel'})

    defbutton_validate(self):
        self._check_can_validate()
        cost_without_adjusment_lines=self.filtered(lambdac:notc.valuation_adjustment_lines)
        ifcost_without_adjusment_lines:
            cost_without_adjusment_lines.compute_landed_cost()
        ifnotself._check_sum():
            raiseUserError(_('Costandadjustmentslinesdonotmatch.Youshouldmayberecomputethelandedcosts.'))

        forcostinself:
            cost=cost.with_company(cost.company_id)
            move=self.env['account.move']
            move_vals={
                'journal_id':cost.account_journal_id.id,
                'date':cost.date,
                'ref':cost.name,
                'line_ids':[],
                'move_type':'entry',
            }
            valuation_layer_ids=[]
            cost_to_add_byproduct=defaultdict(lambda:0.0)
            forlineincost.valuation_adjustment_lines.filtered(lambdaline:line.move_id):
                remaining_qty=sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))
                linked_layer=line.move_id.stock_valuation_layer_ids[:1]

                #Proratethevalueatwhat'sstillinstock
                cost_to_add=(remaining_qty/line.move_id.product_qty)*line.additional_landed_cost
                ifnotcost.company_id.currency_id.is_zero(cost_to_add):
                    valuation_layer=self.env['stock.valuation.layer'].create({
                        'value':cost_to_add,
                        'unit_cost':0,
                        'quantity':0,
                        'remaining_qty':0,
                        'stock_valuation_layer_id':linked_layer.id,
                        'description':cost.name,
                        'stock_move_id':line.move_id.id,
                        'product_id':line.move_id.product_id.id,
                        'stock_landed_cost_id':cost.id,
                        'company_id':cost.company_id.id,
                    })
                    linked_layer.remaining_value+=cost_to_add
                    valuation_layer_ids.append(valuation_layer.id)
                #UpdatetheAVCO
                product=line.move_id.product_id
                ifproduct.cost_method=='average':
                    cost_to_add_byproduct[product]+=cost_to_add
                #Productswithmanualinventoryvaluationareignoredbecausetheydonotneedtocreatejournalentries.
                ifproduct.valuation!="real_time":
                    continue
                #`remaining_qty`isnegativeifthemoveisoutanddeliveredproudctsthatwerenot
                #instock.
                qty_out=0
                ifline.move_id._is_in():
                    qty_out=line.move_id.product_qty-remaining_qty
                elifline.move_id._is_out():
                    qty_out=line.move_id.product_qty
                move_vals['line_ids']+=line._create_accounting_entries(move,qty_out)

            #batchstandardpricecomputationavoidrecomputequantity_svlateachiteration
            products=self.env['product.product'].browse(p.idforpincost_to_add_byproduct.keys())
            forproductinproducts: #iterateonrecordsettoprefetchefficientlyquantity_svl
                ifnotfloat_is_zero(product.quantity_svl,precision_rounding=product.uom_id.rounding):
                    product.with_company(cost.company_id).sudo().with_context(disable_auto_svl=True).standard_price+=cost_to_add_byproduct[product]/product.quantity_svl

            move_vals['stock_valuation_layer_ids']=[(6,None,valuation_layer_ids)]
            #Wewillonlycreatetheaccountingentrywhentherearedefinedlines(thelineswillbethoselinkedtoproductsofreal_timevaluationcategory).
            cost_vals={'state':'done'}
            ifmove_vals.get("line_ids"):
                move=move.create(move_vals)
                cost_vals.update({'account_move_id':move.id})
            cost.write(cost_vals)
            ifcost.account_move_id:
                move._post()

            ifcost.vendor_bill_idandcost.vendor_bill_id.state=='posted'andcost.company_id.anglo_saxon_accounting:
                all_amls=cost.vendor_bill_id.line_ids|cost.account_move_id.line_ids
                forproductincost.cost_lines.product_id:
                    accounts=product.product_tmpl_id.get_product_accounts()
                    input_account=accounts['stock_input']
                    all_amls.filtered(lambdaaml:aml.account_id==input_accountandnotaml.reconciled).reconcile()

        returnTrue

    defget_valuation_lines(self):
        self.ensure_one()
        lines=[]

        formoveinself._get_targeted_move_ids():
            #itdoesn'tmakesensetomakealandedcostforaproductthatisn'tsetasbeingvaluatedinrealtimeatrealcost
            ifmove.product_id.cost_methodnotin('fifo','average')ormove.state=='cancel'ornotmove.product_qty:
                continue
            vals={
                'product_id':move.product_id.id,
                'move_id':move.id,
                'quantity':move.product_qty,
                'former_cost':sum(move.stock_valuation_layer_ids.mapped('value')),
                'weight':move.product_id.weight*move.product_qty,
                'volume':move.product_id.volume*move.product_qty
            }
            lines.append(vals)

        ifnotlines:
            target_model_descriptions=dict(self._fields['target_model']._description_selection(self.env))
            raiseUserError(_("Youcannotapplylandedcostsonthechosen%s(s).LandedcostscanonlybeappliedforproductswithFIFOoraveragecostingmethod.",target_model_descriptions[self.target_model]))
        returnlines

    defcompute_landed_cost(self):
        AdjustementLines=self.env['stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id','in',self.ids)]).unlink()

        towrite_dict={}
        forcostinself.filtered(lambdacost:cost._get_targeted_move_ids()):
            rounding=cost.currency_id.rounding
            total_qty=0.0
            total_cost=0.0
            total_weight=0.0
            total_volume=0.0
            total_line=0.0
            all_val_line_values=cost.get_valuation_lines()
            forval_line_valuesinall_val_line_values:
                forcost_lineincost.cost_lines:
                    val_line_values.update({'cost_id':cost.id,'cost_line_id':cost_line.id})
                    self.env['stock.valuation.adjustment.lines'].create(val_line_values)
                total_qty+=val_line_values.get('quantity',0.0)
                total_weight+=val_line_values.get('weight',0.0)
                total_volume+=val_line_values.get('volume',0.0)

                former_cost=val_line_values.get('former_cost',0.0)
                #roundthisbecauseformer_costonthevaluationlinesisalsorounded
                total_cost+=cost.currency_id.round(former_cost)

                total_line+=1

            forlineincost.cost_lines:
                value_split=0.0
                forvaluationincost.valuation_adjustment_lines:
                    value=0.0
                    ifvaluation.cost_line_idandvaluation.cost_line_id.id==line.id:
                        ifline.split_method=='by_quantity'andtotal_qty:
                            per_unit=(line.price_unit/total_qty)
                            value=valuation.quantity*per_unit
                        elifline.split_method=='by_weight'andtotal_weight:
                            per_unit=(line.price_unit/total_weight)
                            value=valuation.weight*per_unit
                        elifline.split_method=='by_volume'andtotal_volume:
                            per_unit=(line.price_unit/total_volume)
                            value=valuation.volume*per_unit
                        elifline.split_method=='equal':
                            value=(line.price_unit/total_line)
                        elifline.split_method=='by_current_cost_price'andtotal_cost:
                            per_unit=(line.price_unit/total_cost)
                            value=valuation.former_cost*per_unit
                        else:
                            value=(line.price_unit/total_line)

                        ifrounding:
                            value=tools.float_round(value,precision_rounding=rounding,rounding_method='UP')
                            fnc=minifline.price_unit>0elsemax
                            value=fnc(value,line.price_unit-value_split)
                            value_split+=value

                        ifvaluation.idnotintowrite_dict:
                            towrite_dict[valuation.id]=value
                        else:
                            towrite_dict[valuation.id]+=value
        forkey,valueintowrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost':value})
        returnTrue

    defaction_view_stock_valuation_layers(self):
        self.ensure_one()
        domain=[('id','in',self.stock_valuation_layer_ids.ids)]
        action=self.env["ir.actions.actions"]._for_xml_id("stock_account.stock_valuation_layer_action")
        returndict(action,domain=domain)

    def_get_targeted_move_ids(self):
        returnself.picking_ids.move_lines

    def_check_can_validate(self):
        ifany(cost.state!='draft'forcostinself):
            raiseUserError(_('Onlydraftlandedcostscanbevalidated'))
        forcostinself:
            ifnotcost._get_targeted_move_ids():
                target_model_descriptions=dict(self._fields['target_model']._description_selection(self.env))
                raiseUserError(_('Pleasedefine%sonwhichthoseadditionalcostsshouldapply.',target_model_descriptions[cost.target_model]))

    def_check_sum(self):
        """Checkifeachcostlineitsvaluationlinessumtothecorrectamount
        andiftheoveralltotalamountiscorrectalso"""
        prec_digits=self.env.company.currency_id.decimal_places
        forlanded_costinself:
            total_amount=sum(landed_cost.valuation_adjustment_lines.mapped('additional_landed_cost'))
            ifnottools.float_is_zero(total_amount-landed_cost.amount_total,precision_digits=prec_digits):
                returnFalse

            val_to_cost_lines=defaultdict(lambda:0.0)
            forval_lineinlanded_cost.valuation_adjustment_lines:
                val_to_cost_lines[val_line.cost_line_id]+=val_line.additional_landed_cost
            ifany(nottools.float_is_zero(cost_line.price_unit-val_amount,precision_digits=prec_digits)
                   forcost_line,val_amountinval_to_cost_lines.items()):
                returnFalse
        returnTrue


classStockLandedCostLine(models.Model):
    _name='stock.landed.cost.lines'
    _description='StockLandedCostLine'

    name=fields.Char('Description')
    cost_id=fields.Many2one(
        'stock.landed.cost','LandedCost',
        required=True,ondelete='cascade')
    product_id=fields.Many2one('product.product','Product',required=True)
    price_unit=fields.Monetary('Cost',required=True)
    split_method=fields.Selection(
        SPLIT_METHOD,
        string='SplitMethod',
        required=True,
        help="Equal:Costwillbeequallydivided.\n"
             "ByQuantity:Costwillbedividedaccordingtoproduct'squantity.\n"
             "ByCurrentcost:Costwillbedividedaccordingtoproduct'scurrentcost.\n"
             "ByWeight:Costwillbedivideddependingonitsweight.\n"
             "ByVolume:Costwillbedivideddependingonitsvolume.")
    account_id=fields.Many2one('account.account','Account',domain=[('deprecated','=',False)])
    currency_id=fields.Many2one('res.currency',related='cost_id.currency_id')

    @api.onchange('product_id')
    defonchange_product_id(self):
        self.name=self.product_id.nameor''
        self.split_method=self.product_id.product_tmpl_id.split_method_landed_costorself.split_methodor'equal'
        self.price_unit=self.product_id.standard_priceor0.0
        accounts_data=self.product_id.product_tmpl_id.get_product_accounts()
        self.account_id=accounts_data['stock_input']


classAdjustmentLines(models.Model):
    _name='stock.valuation.adjustment.lines'
    _description='ValuationAdjustmentLines'

    name=fields.Char(
        'Description',compute='_compute_name',store=True)
    cost_id=fields.Many2one(
        'stock.landed.cost','LandedCost',
        ondelete='cascade',required=True)
    cost_line_id=fields.Many2one(
        'stock.landed.cost.lines','CostLine',readonly=True)
    move_id=fields.Many2one('stock.move','StockMove',readonly=True)
    product_id=fields.Many2one('product.product','Product',required=True)
    quantity=fields.Float(
        'Quantity',default=1.0,
        digits=0,required=True)
    weight=fields.Float(
        'Weight',default=1.0,
        digits='StockWeight')
    volume=fields.Float(
        'Volume',default=1.0,digits='Volume')
    former_cost=fields.Monetary(
        'OriginalValue')
    additional_landed_cost=fields.Monetary(
        'AdditionalLandedCost')
    final_cost=fields.Monetary(
        'NewValue',compute='_compute_final_cost',
        store=True)
    currency_id=fields.Many2one('res.currency',related='cost_id.company_id.currency_id')

    @api.depends('cost_line_id.name','product_id.code','product_id.name')
    def_compute_name(self):
        forlineinself:
            name='%s-'%(line.cost_line_id.nameifline.cost_line_idelse'')
            line.name=name+(line.product_id.codeorline.product_id.nameor'')

    @api.depends('former_cost','additional_landed_cost')
    def_compute_final_cost(self):
        forlineinself:
            line.final_cost=line.former_cost+line.additional_landed_cost

    def_create_accounting_entries(self,move,qty_out):
        #TDECLEANME:productchosenforcomputation?
        cost_product=self.cost_line_id.product_id
        ifnotcost_product:
            returnFalse
        accounts=self.product_id.product_tmpl_id.get_product_accounts()
        debit_account_id=accounts.get('stock_valuation')andaccounts['stock_valuation'].idorFalse
        #Ifthestockmoveisdropshippedmoveweneedtogetthecostaccountinsteadthestockvaluationaccount
        ifself.move_id._is_dropshipped():
            debit_account_id=accounts.get('expense')andaccounts['expense'].idorFalse
        already_out_account_id=accounts['stock_output'].id
        credit_account_id=self.cost_line_id.account_id.idorcost_product.categ_id.property_stock_account_input_categ_id.id

        ifnotcredit_account_id:
            raiseUserError(_('PleaseconfigureStockExpenseAccountforproduct:%s.')%(cost_product.name))

        returnself._create_account_move_line(move,credit_account_id,debit_account_id,qty_out,already_out_account_id)

    def_create_account_move_line(self,move,credit_account_id,debit_account_id,qty_out,already_out_account_id):
        """
        Generatetheaccount.move.linevaluestotrackthelandedcost.
        Afterwards,forthegoodsthatarealreadyoutofstock,weshouldcreatetheoutmoves
        """
        AccountMoveLine=[]

        base_line={
            'name':self.name,
            'product_id':self.product_id.id,
            'quantity':0,
        }
        debit_line=dict(base_line,account_id=debit_account_id)
        credit_line=dict(base_line,account_id=credit_account_id)
        diff=self.additional_landed_cost
        ifdiff>0:
            debit_line['debit']=diff
            credit_line['credit']=diff
        else:
            #negativecost,reversetheentry
            debit_line['credit']=-diff
            credit_line['debit']=-diff
        AccountMoveLine.append([0,0,debit_line])
        AccountMoveLine.append([0,0,credit_line])

        #Createaccountmovelinesforquantsalreadyoutofstock
        ifqty_out>0:
            debit_line=dict(base_line,
                              name=(self.name+":"+str(qty_out)+_('alreadyout')),
                              quantity=0,
                              account_id=already_out_account_id)
            credit_line=dict(base_line,
                               name=(self.name+":"+str(qty_out)+_('alreadyout')),
                               quantity=0,
                               account_id=debit_account_id)
            diff=diff*qty_out/self.quantity
            ifdiff>0:
                debit_line['debit']=diff
                credit_line['credit']=diff
            else:
                #negativecost,reversetheentry
                debit_line['credit']=-diff
                credit_line['debit']=-diff
            AccountMoveLine.append([0,0,debit_line])
            AccountMoveLine.append([0,0,credit_line])

            ifself.env.company.anglo_saxon_accounting:
                expense_account_id=self.product_id.product_tmpl_id.get_product_accounts()['expense'].id
                debit_line=dict(base_line,
                                  name=(self.name+":"+str(qty_out)+_('alreadyout')),
                                  quantity=0,
                                  account_id=expense_account_id)
                credit_line=dict(base_line,
                                   name=(self.name+":"+str(qty_out)+_('alreadyout')),
                                   quantity=0,
                                   account_id=already_out_account_id)

                ifdiff>0:
                    debit_line['debit']=diff
                    credit_line['credit']=diff
                else:
                    #negativecost,reversetheentry
                    debit_line['credit']=-diff
                    credit_line['debit']=-diff
                AccountMoveLine.append([0,0,debit_line])
                AccountMoveLine.append([0,0,credit_line])

        returnAccountMoveLine
