#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta
fromitertoolsimportgroupby

fromflectraimportapi,fields,models,SUPERUSER_ID,_
fromflectra.addons.stock.models.stock_ruleimportProcurementException


classStockRule(models.Model):
    _inherit='stock.rule'

    action=fields.Selection(selection_add=[
        ('buy','Buy')
    ],ondelete={'buy':'cascade'})

    def_get_message_dict(self):
        message_dict=super(StockRule,self)._get_message_dict()
        dummy,destination,dummy=self._get_message_values()
        message_dict.update({
            'buy':_('Whenproductsareneededin<b>%s</b>,<br/>'
                     'arequestforquotationiscreatedtofulfilltheneed.<br/>'
                     'Note:Thisrulewillbeusedincombinationwiththerules<br/>'
                     'ofthereceptionroute(s)')%(destination)
        })
        returnmessage_dict

    @api.depends('action')
    def_compute_picking_type_code_domain(self):
        remaining=self.browse()
        forruleinself:
            ifrule.action=='buy':
                rule.picking_type_code_domain='incoming'
            else:
                remaining|=rule
        super(StockRule,remaining)._compute_picking_type_code_domain()

    @api.onchange('action')
    def_onchange_action(self):
        ifself.action=='buy':
            self.location_src_id=False

    @api.model
    def_run_buy(self,procurements):
        procurements_by_po_domain=defaultdict(list)
        errors=[]
        forprocurement,ruleinprocurements:

            #Getthescheduledateinordertofindavalidseller
            procurement_date_planned=fields.Datetime.from_string(procurement.values['date_planned'])
            schedule_date=(procurement_date_planned-relativedelta(days=procurement.company_id.po_lead))

            supplier=False
            ifprocurement.values.get('supplierinfo_id'):
                supplier=procurement.values['supplierinfo_id']
            else:
                supplier=procurement.product_id.with_company(procurement.company_id.id)._select_seller(
                    partner_id=procurement.values.get("supplierinfo_name"),
                    quantity=procurement.product_qty,
                    date=max(schedule_date.date(),fields.Date.today()),
                    uom_id=procurement.product_uom)

            #Fallbackonasupplierforwhichnopricemaybedefined.Notideal,butbetterthan
            #blockingtheuser.
            supplier=supplierorprocurement.product_id._prepare_sellers(False).filtered(
                lambdas:nots.company_idors.company_id==procurement.company_id
            )[:1]

            ifnotsupplier:
                msg=_('Thereisnomatchingvendorpricetogeneratethepurchaseorderforproduct%s(novendordefined,minimumquantitynotreached,datesnotvalid,...).Goontheproductformandcompletethelistofvendors.')%(procurement.product_id.display_name)
                errors.append((procurement,msg))

            partner=supplier.name
            #weput`supplier_info`invaluesforextensibilitypurposes
            procurement.values['supplier']=supplier
            procurement.values['propagate_cancel']=rule.propagate_cancel

            domain=rule._make_po_get_domain(procurement.company_id,procurement.values,partner)
            procurements_by_po_domain[domain].append((procurement,rule))

        iferrors:
            raiseProcurementException(errors)

        fordomain,procurements_rulesinprocurements_by_po_domain.items():
            #Gettheprocurementsforthecurrentdomain.
            #Gettherulesforthecurrentdomain.Theironlyuseistocreate
            #thePOifitdoesnotexist.
            procurements,rules=zip(*procurements_rules)

            #Getthesetofprocurementoriginforthecurrentdomain.
            origins=set([p.originforpinprocurements])
            #CheckifaPOexistsforthecurrentdomain.
            po=self.env['purchase.order'].sudo().search([domfordomindomain],limit=1)
            company_id=procurements[0].company_id
            ifnotpo:
                #WeneedaruletogeneratethePO.Howevertherulegenerated
                #thesamedomainforPOandthe_prepare_purchase_ordermethod
                #shouldonlyusesthecommonrules'sfields.
                vals=rules[0]._prepare_purchase_order(company_id,origins,[p.valuesforpinprocurements])
                #Thecompany_idisthesameforallprocurementssince
                #_make_po_get_domainaddthecompanyinthedomain.
                #WeuseSUPERUSER_IDsincewedon'twantthecurrentusertobefollowerofthePO.
                #Indeed,thecurrentusermaybeauserwithoutaccesstoPurchase,orevenbeaportaluser.
                po=self.env['purchase.order'].with_company(company_id).with_user(SUPERUSER_ID).create(vals)
            else:
                #Ifapurchaseorderisfound,adaptits`origin`field.
                ifpo.origin:
                    missing_origins=origins-set(po.origin.split(','))
                    ifmissing_origins:
                        po.write({'origin':po.origin+','+','.join(missing_origins)})
                else:
                    po.write({'origin':','.join(origins)})

            procurements_to_merge=self._get_procurements_to_merge(procurements)
            procurements=self._merge_procurements(procurements_to_merge)

            po_lines_by_product={}
            grouped_po_lines=groupby(po.order_line.filtered(lambdal:notl.display_typeandl.product_uom==l.product_id.uom_po_id).sorted(lambdal:l.product_id.id),key=lambdal:l.product_id.id)
            forproduct,po_linesingrouped_po_lines:
                po_lines_by_product[product]=self.env['purchase.order.line'].concat(*list(po_lines))
            po_line_values=[]
            forprocurementinprocurements:
                po_lines=po_lines_by_product.get(procurement.product_id.id,self.env['purchase.order.line'])
                po_line=po_lines._find_candidate(*procurement)

                ifpo_line:
                    #Iftheprocurementcanbemergeinanexistingline.Directly
                    #writethenewvaluesonit.
                    vals=self._update_purchase_order_line(procurement.product_id,
                        procurement.product_qty,procurement.product_uom,company_id,
                        procurement.values,po_line)
                    po_line.write(vals)
                else:
                    #IfitdoesnotexistaPOlineforcurrentprocurement.
                    #Generatethecreatevaluesforitandaddittoalistin
                    #ordertocreateitinbatch.
                    partner=procurement.values['supplier'].name
                    po_line_values.append(self.env['purchase.order.line']._prepare_purchase_order_line_from_procurement(
                        procurement.product_id,procurement.product_qty,
                        procurement.product_uom,procurement.company_id,
                        procurement.values,po))
            self.env['purchase.order.line'].sudo().create(po_line_values)

    def_get_lead_days(self,product):
        """Addthecompanysecurityleadtime,daystopurchaseandthesupplier
        delaytothecumulativedelayandcumulativedescription.Thedaysto
        purchaseandcompanyleadtimearealwaysdisplayedforonboarding
        purposeinordertoindicatethatthoseoptionsareavailable.
        """
        delay,delay_description=super()._get_lead_days(product)
        bypass_delay_description=self.env.context.get('bypass_delay_description')
        buy_rule=self.filtered(lambdar:r.action=='buy')
        seller=product.with_company(buy_rule.company_id)._select_seller(quantity=None)
        ifnotbuy_ruleornotseller:
            returndelay,delay_description
        buy_rule.ensure_one()
        supplier_delay=seller[0].delay
        ifsupplier_delayandnotbypass_delay_description:
            delay_description+='<tr><td>%s</td><tdclass="text-right">+%d%s</td></tr>'%(_('VendorLeadTime'),supplier_delay,_('day(s)'))
        security_delay=buy_rule.picking_type_id.company_id.po_lead
        ifnotbypass_delay_description:
            delay_description+='<tr><td>%s</td><tdclass="text-right">+%d%s</td></tr>'%(_('PurchaseSecurityLeadTime'),security_delay,_('day(s)'))
        days_to_purchase=buy_rule.company_id.days_to_purchase
        ifnotbypass_delay_description:
            delay_description+='<tr><td>%s</td><tdclass="text-right">+%d%s</td></tr>'%(_('DaystoPurchase'),days_to_purchase,_('day(s)'))
        returndelay+supplier_delay+security_delay+days_to_purchase,delay_description

    @api.model
    def_get_procurements_to_merge_groupby(self,procurement):
        #Donotgroupprocumentfromdifferentorderpoint.1._quantity_in_progress
        #directlydependsfromtheorderpoint_idontheline.2.Thestockmove
        #generatedfromtheorderlinehastheorderpoint'slocationas
        #destinationlocation.Incaseofmove_dest_idsthosetwopointsarenot
        #necessaryanymoresincethosevaluesaretakenfromdestinationmoves.
        returnprocurement.product_id,procurement.product_uom,procurement.values['propagate_cancel'],\
            procurement.values.get('product_description_variants'),\
            (procurement.values.get('orderpoint_id')andnotprocurement.values.get('move_dest_ids'))andprocurement.values['orderpoint_id']

    @api.model
    def_get_procurements_to_merge_sorted(self,procurement):
        returnprocurement.product_id.id,procurement.product_uom.id,procurement.values['propagate_cancel'],\
            procurement.values.get('product_description_variants'),\
            (procurement.values.get('orderpoint_id')andnotprocurement.values.get('move_dest_ids'))andprocurement.values['orderpoint_id']

    @api.model
    def_get_procurements_to_merge(self,procurements):
        """Getalistofprocurementsvaluesandcreategroupsofprocurements
        thatwouldusethesamepurchaseorderline.
        paramsprocurements_listlist:procurementsrequests(notorderednor
        sorted).
        returnlist:procurementsrequestsgroupedbytheirproduct_id.
        """
        procurements_to_merge=[]

        fork,procurementsingroupby(sorted(procurements,key=self._get_procurements_to_merge_sorted),key=self._get_procurements_to_merge_groupby):
            procurements_to_merge.append(list(procurements))
        returnprocurements_to_merge

    @api.model
    def_merge_procurements(self,procurements_to_merge):
        """Mergethequantityforprocurementsrequeststhatcouldusethesame
        orderline.
        paramssimilar_procurementslist:listofprocurementsthathavebeen
        markedas'alike'from_get_procurements_to_mergemethod.
        returnalistofprocurementsvalueswherevaluesofsimilar_procurements
        listhavebeenmerged.
        """
        merged_procurements=[]
        forprocurementsinprocurements_to_merge:
            quantity=0
            move_dest_ids=self.env['stock.move']
            orderpoint_id=self.env['stock.warehouse.orderpoint']
            forprocurementinprocurements:
                ifprocurement.values.get('move_dest_ids'):
                    move_dest_ids|=procurement.values['move_dest_ids']
                ifnotorderpoint_idandprocurement.values.get('orderpoint_id'):
                    orderpoint_id=procurement.values['orderpoint_id']
                quantity+=procurement.product_qty
            #Themergedprocurementcanbebuildfromanarbitraryprocurement
            #sincetheyweremarkassimilarbefore.Onlythequantityand
            #somekeysinvaluesareupdated.
            values=dict(procurement.values)
            values.update({
                'move_dest_ids':move_dest_ids,
                'orderpoint_id':orderpoint_id,
            })
            merged_procurement=self.env['procurement.group'].Procurement(
                procurement.product_id,quantity,procurement.product_uom,
                procurement.location_id,procurement.name,procurement.origin,
                procurement.company_id,values
            )
            merged_procurements.append(merged_procurement)
        returnmerged_procurements

    def_update_purchase_order_line(self,product_id,product_qty,product_uom,company_id,values,line):
        partner=values['supplier'].name
        procurement_uom_po_qty=product_uom._compute_quantity(product_qty,product_id.uom_po_id)
        seller=product_id.with_company(company_id)._select_seller(
            partner_id=partner,
            quantity=line.product_qty+procurement_uom_po_qty,
            date=line.order_id.date_orderandline.order_id.date_order.date(),
            uom_id=product_id.uom_po_id)

        price_unit=self.env['account.tax']._fix_tax_included_price_company(seller.price,line.product_id.supplier_taxes_id,line.taxes_id,company_id)ifsellerelse0.0
        ifprice_unitandsellerandline.order_id.currency_idandseller.currency_id!=line.order_id.currency_id:
            price_unit=seller.currency_id._convert(
                price_unit,line.order_id.currency_id,line.order_id.company_id,fields.Date.today())

        res={
            'product_qty':line.product_qty+procurement_uom_po_qty,
            'price_unit':price_unit,
            'move_dest_ids':[(4,x.id)forxinvalues.get('move_dest_ids',[])]
        }
        orderpoint_id=values.get('orderpoint_id')
        iforderpoint_id:
            res['orderpoint_id']=orderpoint_id.id
        returnres

    def_prepare_purchase_order(self,company_id,origins,values):
        """Createapurchaseorderforprocuremetsthatsharethesamedomain
        returnedby_make_po_get_domain.
        paramsvalues:valuesofprocurements
        paramsorigins:procuremetsoriginstowriteonthePO
        """
        purchase_date=min([fields.Datetime.from_string(value['date_planned'])-relativedelta(days=int(value['supplier'].delay))forvalueinvalues])

        purchase_date=(purchase_date-relativedelta(days=company_id.po_lead))


        #Sincetheprocurementsaregroupediftheysharethesamedomainfor
        #PObutthePOdoesnotexist.InthiscaseitwillcreatethePOfrom
        #thecommonprocurementsvalues.Thecommonvaluesaretakenfroman
        #arbitraryprocurement.Inthiscasethefirst.
        values=values[0]
        partner=values['supplier'].name

        fpos=self.env['account.fiscal.position'].with_company(company_id).get_fiscal_position(partner.id)

        gpo=self.group_propagation_option
        group=(gpo=='fixed'andself.group_id.id)or\
                (gpo=='propagate'andvalues.get('group_id')andvalues['group_id'].id)orFalse

        return{
            'partner_id':partner.id,
            'user_id':False,
            'picking_type_id':self.picking_type_id.id,
            'company_id':company_id.id,
            'currency_id':partner.with_company(company_id).property_purchase_currency_id.idorcompany_id.currency_id.id,
            'dest_address_id':values.get('partner_id',False),
            'origin':','.join(origins),
            'payment_term_id':partner.with_company(company_id).property_supplier_payment_term_id.id,
            'date_order':purchase_date,
            'fiscal_position_id':fpos.id,
            'group_id':group
        }

    def_make_po_get_domain(self,company_id,values,partner):
        gpo=self.group_propagation_option
        group=(gpo=='fixed'andself.group_id)or\
                (gpo=='propagate'and'group_id'invaluesandvalues['group_id'])orFalse

        domain=(
            ('partner_id','=',partner.id),
            ('state','=','draft'),
            ('picking_type_id','=',self.picking_type_id.id),
            ('company_id','=',company_id.id),
            ('user_id','=',False),
        )
        delta_days=self.env['ir.config_parameter'].sudo().get_param('purchase_stock.delta_days_merge')
        ifdelta_daysisnotFalse:
            procurement_date=fields.Date.to_date(values['date_planned'])-relativedelta(days=int(values['supplier'].delay)+company_id.po_lead)
            delta_days=int(delta_days)
            domain+=(
                ('date_order','<=',datetime.combine(procurement_date+relativedelta(days=delta_days),datetime.max.time())),
                ('date_order','>=',datetime.combine(procurement_date-relativedelta(days=delta_days),datetime.min.time()))
            )
        ifgroup:
            domain+=(('group_id','=',group.id),)
        returndomain

    def_push_prepare_move_copy_values(self,move_to_copy,new_date):
        res=super(StockRule,self)._push_prepare_move_copy_values(move_to_copy,new_date)
        res['purchase_line_id']=None
        returnres

    def_get_stock_move_values(self,product_id,product_qty,product_uom,location_id,name,origin,company_id,values):
        move_values=super()._get_stock_move_values(product_id,product_qty,product_uom,location_id,name,origin,company_id,values)
        ifvalues.get('supplierinfo_name'):
            move_values['restrict_partner_id']=values['supplierinfo_name'].id
        elifvalues.get('supplierinfo_id'):
            partner=values['supplierinfo_id'].name
            move_values['restrict_partner_id']=partner.id
        returnmove_values
