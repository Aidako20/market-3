#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.toolsimportfloat_compare,float_is_zero


classAccountMove(models.Model):
    _inherit='account.move'

    defaction_post(self):
        #inheritofthefunctionfromaccount.movetovalidateanewtaxandthepriceunitofadownpayment
        res=super(AccountMove,self).action_post()
        line_ids=self.mapped('line_ids').filtered(lambdaline:any(line.sale_line_ids.mapped('is_downpayment')))
        forlineinline_ids:
            try:
                line.sale_line_ids.tax_id=line.tax_ids
                line.sale_line_ids.price_unit=line.price_unit
            exceptUserError:
                #aUserErrorheremeanstheSOwaslocked,whichpreventschangingthetaxes
                #justignoretheerror-thisisanicetohavefeatureandshouldnotbeblocking
                pass
        returnres

classAccountMoveLine(models.Model):
    _inherit='account.move.line'

    sale_line_ids=fields.Many2many(
        'sale.order.line',
        'sale_order_line_invoice_rel',
        'invoice_line_id','order_line_id',
        string='SalesOrderLines',readonly=True,copy=False)

    def_copy_data_extend_business_fields(self,values):
        #OVERRIDEtocopythe'sale_line_ids'fieldaswell.
        super(AccountMoveLine,self)._copy_data_extend_business_fields(values)
        values['sale_line_ids']=[(6,None,self.sale_line_ids.ids)]

    def_prepare_analytic_line(self):
        """Note:Thismethodiscalledonlyonthemove.linethathavingananalyticaccount,and
            sothatshouldcreateanalyticentries.
        """
        values_list=super(AccountMoveLine,self)._prepare_analytic_line()

        #filterthemovelinesthatcanbereinvoiced:acost(negativeamount)analyticlinewithoutSOlinebutwithaproductcanbereinvoiced
        move_to_reinvoice=self.env['account.move.line']
        forindex,move_lineinenumerate(self):
            values=values_list[index]
            if'so_line'notinvalues:
                ifmove_line._sale_can_be_reinvoice():
                    move_to_reinvoice|=move_line

        #insertthesalelineinthecreatevaluesoftheanalyticentries
        ifmove_to_reinvoice:
            map_sale_line_per_move=move_to_reinvoice._sale_create_reinvoice_sale_line()

            forvaluesinvalues_list:
                sale_line=map_sale_line_per_move.get(values.get('move_id'))
                ifsale_line:
                    values['so_line']=sale_line.id

        returnvalues_list

    def_sale_can_be_reinvoice(self):
        """determineifthegeneratedanalyticlineshouldbereinvoicedornot.
            ForVendorBillflow,iftheproducthasa'erinvoicepolicy'andisacost,thenwewillfindtheSOonwhichreinvoicetheAAL
        """
        self.ensure_one()
        ifself.sale_line_ids:
            returnFalse
        uom_precision_digits=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
        returnfloat_compare(self.creditor0.0,self.debitor0.0,precision_digits=uom_precision_digits)!=1andself.product_id.expense_policynotin[False,'no']

    def_sale_create_reinvoice_sale_line(self):

        sale_order_map=self._sale_determine_order()

        sale_line_values_to_create=[] #thelistofcreationvaluesofsalelinetocreate.
        existing_sale_line_cache={} #inthesales_price-deliverycase,wecanreusethesamesaleline.Thiscachewillavoiddoingasearcheachtimethecasehappen
        #`map_move_sale_line`ismapwhere
        #  -keyisthemovelineidentifier
        #  -valueiseitherasale.order.linerecord(existingcase),oranintegerrepresentingtheindexofthesalelinetocreatein
        #    the`sale_line_values_to_create`(notexistingcase,whichwillhappenmoreoftenthanthefirstone).
        map_move_sale_line={}

        formove_lineinself:
            sale_order=sale_order_map.get(move_line.id)

            #noreinvoiceasnosalesorderwasfound
            ifnotsale_order:
                continue

            #raiseifthesaleorderisnotcurrenltyopen
            ifsale_order.state!='sale':
                message_unconfirmed=_('TheSalesOrder%slinkedtotheAnalyticAccount%smustbevalidatedbeforeregisteringexpenses.')
                messages={
                    'draft':message_unconfirmed,
                    'sent':message_unconfirmed,
                    'done':_('TheSalesOrder%slinkedtotheAnalyticAccount%siscurrentlylocked.YoucannotregisteranexpenseonalockedSalesOrder.PleasecreateanewSOlinkedtothisAnalyticAccount.'),
                    'cancel':_('TheSalesOrder%slinkedtotheAnalyticAccount%siscancelled.YoucannotregisteranexpenseonacancelledSalesOrder.'),
                }
                raiseUserError(messages[sale_order.state]%(sale_order.name,sale_order.analytic_account_id.name))

            price=move_line._sale_get_invoice_price(sale_order)

            #findtheexistingsale.lineorkeepitscreationvaluestoprocessthisinbatch
            sale_line=None
            ifmove_line.product_id.expense_policy=='sales_price'andmove_line.product_id.invoice_policy=='delivery': #forthosecaseonly,wecantrytoreuseone
                map_entry_key=(sale_order.id,move_line.product_id.id,price) #cacheentrytolimitthecalltosearch
                sale_line=existing_sale_line_cache.get(map_entry_key)
                ifsale_line: #alreadysearch,soreuseit.sale_linecanbesale.order.linerecordorindexofa"tocreatevalues"in`sale_line_values_to_create`
                    map_move_sale_line[move_line.id]=sale_line
                    existing_sale_line_cache[map_entry_key]=sale_line
                else: #searchforexistingsaleline
                    sale_line=self.env['sale.order.line'].search([
                        ('order_id','=',sale_order.id),
                        ('price_unit','=',price),
                        ('product_id','=',move_line.product_id.id),
                        ('is_expense','=',True),
                    ],limit=1)
                    ifsale_line: #foundexistingone,sokeepthebrowserecord
                        map_move_sale_line[move_line.id]=existing_sale_line_cache[map_entry_key]=sale_line
                    else: #shouldbecreate,sousetheindexofcreationvaluesinsteadofbrowserecord
                        #savevaluetocreateit
                        sale_line_values_to_create.append(move_line._sale_prepare_sale_line_values(sale_order,price))
                        #storeitinthecacheofexistingones
                        existing_sale_line_cache[map_entry_key]=len(sale_line_values_to_create)-1 #savetheindexofthevaluetocreatesaleline
                        #storeitinthemap_move_sale_linemap
                        map_move_sale_line[move_line.id]=len(sale_line_values_to_create)-1 #savetheindexofthevaluetocreatesaleline

            else: #saveitsvaluetocreateitanyway
                sale_line_values_to_create.append(move_line._sale_prepare_sale_line_values(sale_order,price))
                map_move_sale_line[move_line.id]=len(sale_line_values_to_create)-1 #savetheindexofthevaluetocreatesaleline

        #createthesalelinesinbatch
        new_sale_lines=self.env['sale.order.line'].create(sale_line_values_to_create)
        forsolinnew_sale_lines:
            ifsol.product_id.expense_policy!='cost':
                sol._onchange_discount()

        #buildresultmapbyreplacingindexwithnewlycreatedrecordofsale.order.line
        result={}
        formove_line_id,unknown_sale_lineinmap_move_sale_line.items():
            ifisinstance(unknown_sale_line,int): #indexofnewlycreatedsaleline
                result[move_line_id]=new_sale_lines[unknown_sale_line]
            elifisinstance(unknown_sale_line,models.BaseModel): #alreadyrecordofsale.order.line
                result[move_line_id]=unknown_sale_line
        returnresult

    def_sale_determine_order(self):
        """Getthemappingofmove.linewiththesale.orderrecordonwhichitsanalyticentriesshouldbereinvoiced
            :returnadictwherekeyisthemovelineid,andvalueissale.orderrecord(orNone).
        """
        analytic_accounts=self.mapped('analytic_account_id')

        #linktheanalyticaccountwithitsopenSObycreatingamap:{AA.id:sale.order},ifwefindsomeanalyticaccounts
        mapping={}
        ifanalytic_accounts: #first,searchfortheopensalesorder
            sale_orders=self.env['sale.order'].search([('analytic_account_id','in',analytic_accounts.ids),('state','=','sale')],order='create_dateDESC')
            forsale_orderinsale_orders:
                mapping[sale_order.analytic_account_id.id]=sale_order

            analytic_accounts_without_open_order=analytic_accounts.filtered(lambdaaccount:notmapping.get(account.id))
            ifanalytic_accounts_without_open_order: #then,filltheblankwithnotopensalesorders
                sale_orders=self.env['sale.order'].search([('analytic_account_id','in',analytic_accounts_without_open_order.ids)],order='create_dateDESC')
            forsale_orderinsale_orders:
                mapping[sale_order.analytic_account_id.id]=sale_order

        #mapofAALindexwiththeSOonwhichitneedstobereinvoiced.MaybebeNoneifnoSOfound
        return{move_line.id:mapping.get(move_line.analytic_account_id.id)formove_lineinself}

    def_sale_prepare_sale_line_values(self,order,price):
        """Generatethesale.linecreationvaluefromthecurrentmoveline"""
        self.ensure_one()
        last_so_line=self.env['sale.order.line'].search([('order_id','=',order.id)],order='sequencedesc',limit=1)
        last_sequence=last_so_line.sequence+1iflast_so_lineelse100

        fpos=order.fiscal_position_idororder.fiscal_position_id.get_fiscal_position(order.partner_id.id)
        taxes=fpos.map_tax(self.product_id.taxes_id,self.product_id,order.partner_id)

        return{
            'order_id':order.id,
            'name':self.name,
            'sequence':last_sequence,
            'price_unit':price,
            'tax_id':[x.idforxintaxes],
            'discount':0.0,
            'product_id':self.product_id.id,
            'product_uom':self.product_uom_id.id,
            'product_uom_qty':0.0,
            'is_expense':True,
        }

    def_sale_get_invoice_price(self,order):
        """Basedonthecurrentmoveline,computethepricetoreinvoicetheanalyticlinethatisgoingtobecreated(sothe
            priceofthesaleline).
        """
        self.ensure_one()

        unit_amount=self.quantity
        amount=(self.creditor0.0)-(self.debitor0.0)

        ifself.product_id.expense_policy=='sales_price':
            product=self.product_id.with_context(
                partner=order.partner_id,
                date_order=order.date_order,
                pricelist=order.pricelist_id.id,
                uom=self.product_uom_id.id,
                quantity=unit_amount
            )
            iforder.pricelist_id.discount_policy=='with_discount':
                returnproduct.price
            returnproduct.lst_price

        uom_precision_digits=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
        iffloat_is_zero(unit_amount,precision_digits=uom_precision_digits):
            return0.0

        #Preventunnecessarycurrencyconversionthatcouldbeimpactedbyexchangerate
        #fluctuations
        ifself.company_id.currency_idandamountandself.company_id.currency_id==order.currency_id:
            returnabs(amount/unit_amount)

        price_unit=abs(amount/unit_amount)
        currency_id=self.company_id.currency_id
        ifcurrency_idandcurrency_id!=order.currency_id:
            price_unit=currency_id._convert(price_unit,order.currency_id,order.company_id,order.date_orderorfields.Date.today())
        returnprice_unit

    def_get_downpayment_lines(self):
        #OVERRIDE
        returnself.sale_line_ids.filtered('is_downpayment').invoice_lines.filtered(lambdaline:line.move_id._is_downpayment())
