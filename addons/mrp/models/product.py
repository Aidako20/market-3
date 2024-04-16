#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importcollections
fromdatetimeimporttimedelta
importoperatoraspy_operator
fromflectraimportapi,fields,models,_
fromflectra.tools.float_utilsimportfloat_round,float_is_zero


OPERATORS={
    '<':py_operator.lt,
    '>':py_operator.gt,
    '<=':py_operator.le,
    '>=':py_operator.ge,
    '=':py_operator.eq,
    '!=':py_operator.ne
}

classProductTemplate(models.Model):
    _inherit="product.template"

    bom_line_ids=fields.One2many('mrp.bom.line','product_tmpl_id','BoMComponents')
    bom_ids=fields.One2many('mrp.bom','product_tmpl_id','BillofMaterials')
    bom_count=fields.Integer('#BillofMaterial',
        compute='_compute_bom_count',compute_sudo=False)
    used_in_bom_count=fields.Integer('#ofBoMWhereisUsed',
        compute='_compute_used_in_bom_count',compute_sudo=False)
    mrp_product_qty=fields.Float('Manufactured',
        compute='_compute_mrp_product_qty',compute_sudo=False)
    produce_delay=fields.Float(
        'ManufacturingLeadTime',default=0.0,
        help="Averageleadtimeindaystomanufacturethisproduct.Inthecaseofmulti-levelBOM,themanufacturingleadtimesofthecomponentswillbeadded.")

    @api.depends('product_variant_count','bom_ids','bom_ids.type')
    def_compute_show_on_hand_qty_status_button(self):
        super()._compute_show_on_hand_qty_status_button()
        #Ifthe`super`calldefinesthefieldasTrue,incasethisisakit,weneedtochecksomeadditional
        #conditions:wehideallinformationrelativetothekitquantityifatemplatehasmorethanonevariantand
        #ifatleastoneofthevariantsisakit
        fortemplateinself:
            ifnottemplate.show_on_hand_qty_status_buttonortemplate.product_variant_count<=1:
                continue
            domain=self.env['mrp.bom']._bom_find_domain(product_tmpl=template,bom_type='phantom',company_id=self.env.company.id)
            kit_count=self.env['mrp.bom'].search_count(domain)
            template.show_on_hand_qty_status_button=kit_count==0

    def_compute_bom_count(self):
        forproductinself:
            product.bom_count=self.env['mrp.bom'].search_count([('product_tmpl_id','=',product.id)])

    def_compute_used_in_bom_count(self):
        fortemplateinself:
            template.used_in_bom_count=self.env['mrp.bom'].search_count(
                [('bom_line_ids.product_tmpl_id','=',template.id)])

    defwrite(self,values):
        if'active'invalues:
            self.filtered(lambdap:p.active!=values['active']).with_context(active_test=False).bom_ids.write({
                'active':values['active']
            })
        returnsuper().write(values)

    defaction_used_in_bom(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_bom_form_action")
        action['domain']=[('bom_line_ids.product_tmpl_id','=',self.id)]
        returnaction

    def_compute_mrp_product_qty(self):
        fortemplateinself:
            template.mrp_product_qty=float_round(sum(template.mapped('product_variant_ids').mapped('mrp_product_qty')),precision_rounding=template.uom_id.rounding)

    defaction_view_mos(self):
        action=self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_production_report")
        action['domain']=[('state','=','done'),('product_tmpl_id','in',self.ids)]
        action['context']={
            'graph_measure':'product_uom_qty',
            'search_default_filter_plan_date':1,
        }
        returnaction

    defaction_archive(self):
        filtered_products=self.env['mrp.bom.line'].search([('product_id','in',self.product_variant_ids.ids)]).product_id.mapped('display_name')
        res=super().action_archive()
        iffiltered_products:
            return{
                'type':'ir.actions.client',
                'tag':'display_notification',
                'params':{
                'title':_("Notethatproduct(s):'%s'is/arestilllinkedtoactiveBillofMaterials,"
                            "whichmeansthattheproductcanstillbeusedonit/them.",filtered_products),
                'type':'warning',
                'sticky':True, #True/Falsewilldisplayforfewsecondsiffalse
                'next':{'type':'ir.actions.act_window_close'},
                },
            }
        returnres


classProductProduct(models.Model):
    _inherit="product.product"

    variant_bom_ids=fields.One2many('mrp.bom','product_id','BOMProductVariants')
    bom_line_ids=fields.One2many('mrp.bom.line','product_id','BoMComponents')
    bom_count=fields.Integer('#BillofMaterial',
        compute='_compute_bom_count',compute_sudo=False)
    used_in_bom_count=fields.Integer('#BoMWhereUsed',
        compute='_compute_used_in_bom_count',compute_sudo=False)
    mrp_product_qty=fields.Float('Manufactured',
        compute='_compute_mrp_product_qty',compute_sudo=False)

    def_compute_bom_count(self):
        forproductinself:
            product.bom_count=self.env['mrp.bom'].search_count(['|',('product_id','=',product.id),'&',('product_id','=',False),('product_tmpl_id','=',product.product_tmpl_id.id)])

    def_compute_used_in_bom_count(self):
        forproductinself:
            product.used_in_bom_count=self.env['mrp.bom'].search_count([('bom_line_ids.product_id','=',product.id)])

    defwrite(self,values):
        if'active'invalues:
            self.filtered(lambdap:p.active!=values['active']).with_context(active_test=False).variant_bom_ids.write({
                'active':values['active']
            })
        returnsuper().write(values)

    defget_components(self):
        """Returnthecomponentslistidsincaseofkitproduct.
        Returntheproductitselfotherwise"""
        self.ensure_one()
        bom_kit=self.env['mrp.bom']._bom_find(product=self,bom_type='phantom')
        ifbom_kit:
            boms,bom_sub_lines=bom_kit.explode(self,1)
            return[bom_line.product_id.idforbom_line,datainbom_sub_linesifbom_line.product_id.type=='product']
        else:
            returnsuper(ProductProduct,self).get_components()

    defaction_used_in_bom(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_bom_form_action")
        action['domain']=[('bom_line_ids.product_id','=',self.id)]
        returnaction

    def_compute_mrp_product_qty(self):
        date_from=fields.Datetime.to_string(fields.datetime.now()-timedelta(days=365))
        #TODO:state=done?
        domain=[('state','=','done'),('product_id','in',self.ids),('date_planned_start','>',date_from)]
        read_group_res=self.env['mrp.production'].read_group(domain,['product_id','product_uom_qty'],['product_id'])
        mapped_data=dict([(data['product_id'][0],data['product_uom_qty'])fordatainread_group_res])
        forproductinself:
            ifnotproduct.id:
                product.mrp_product_qty=0.0
                continue
            product.mrp_product_qty=float_round(mapped_data.get(product.id,0),precision_rounding=product.uom_id.rounding)

    def_compute_quantities_dict(self,lot_id,owner_id,package_id,from_date=False,to_date=False):
        """Whentheproductisakit,thisoverridecomputesthefields:
         -'virtual_available'
         -'qty_available'
         -'incoming_qty'
         -'outgoing_qty'
         -'free_qty'

        Thisoverrideisusedtogetthecorrectquantitiesofproducts
        with'phantom'asBoMtype.
        """
        bom_kits=self.env['mrp.bom']._get_product2bom(self,bom_type='phantom')
        kits=self.filtered(lambdap:bom_kits.get(p))
        regular_products=self-kits
        res=(
            super(ProductProduct,regular_products)._compute_quantities_dict(lot_id,owner_id,package_id,from_date=from_date,to_date=to_date)
            ifregular_products
            else{}
        )
        qties=self.env.context.get("mrp_compute_quantities",{})
        qties.update(res)
        #pre-computebomlinesandidentifymissingkitcomponentstoprefetch
        bom_sub_lines_per_kit={}
        prefetch_component_ids=set()
        forproductinbom_kits:
            __,bom_sub_lines=bom_kits[product].explode(product,1)
            bom_sub_lines_per_kit[product]=bom_sub_lines
            forbom_line,__inbom_sub_lines:
                ifbom_line.product_id.idnotinqties:
                    prefetch_component_ids.add(bom_line.product_id.id)
        #computekitquantities
        forproductinbom_kits:
            bom_sub_lines=bom_sub_lines_per_kit[product]
            #grouplinesbycomponent
            bom_sub_lines_grouped=collections.defaultdict(list)
            forinfoinbom_sub_lines:
                bom_sub_lines_grouped[info[0].product_id].append(info)
            ratios_virtual_available=[]
            ratios_qty_available=[]
            ratios_incoming_qty=[]
            ratios_outgoing_qty=[]
            ratios_free_qty=[]

            forcomponent,bom_sub_linesinbom_sub_lines_grouped.items():
                component=component.with_context(mrp_compute_quantities=qties).with_prefetch(prefetch_component_ids)
                qty_per_kit=0
                forbom_line,bom_line_datainbom_sub_lines:
                    ifcomponent.type!='product'orfloat_is_zero(bom_line_data['qty'],precision_rounding=bom_line.product_uom_id.rounding):
                        #AsBoMsallowcomponentswith0qty,a.k.a.optionnalcomponents,wesimplyskipthose
                        #toavoidadivisionbyzero.Thesamelogicisappliedtonon-storableproductsasthose
                        #productshave0qtyavailable.
                        continue
                    uom_qty_per_kit=bom_line_data['qty']/bom_line_data['original_qty']
                    qty_per_kit+=bom_line.product_uom_id._compute_quantity(uom_qty_per_kit,bom_line.product_id.uom_id,round=False,raise_if_failure=False)
                ifnotqty_per_kit:
                    continue
                rounding=component.uom_id.rounding
                component_res=(
                    qties.get(component.id)
                    ifcomponent.idinqties
                    else{
                        "virtual_available":float_round(component.virtual_available,precision_rounding=rounding),
                        "qty_available":float_round(component.qty_available,precision_rounding=rounding),
                        "incoming_qty":float_round(component.incoming_qty,precision_rounding=rounding),
                        "outgoing_qty":float_round(component.outgoing_qty,precision_rounding=rounding),
                        "free_qty":float_round(component.free_qty,precision_rounding=rounding),
                    }
                )
                ratios_virtual_available.append(component_res["virtual_available"]/qty_per_kit)
                ratios_qty_available.append(component_res["qty_available"]/qty_per_kit)
                ratios_incoming_qty.append(component_res["incoming_qty"]/qty_per_kit)
                ratios_outgoing_qty.append(component_res["outgoing_qty"]/qty_per_kit)
                ratios_free_qty.append(component_res["free_qty"]/qty_per_kit)
            ifbom_sub_linesandratios_virtual_available: #Guardagainstallcnsumablebom:atleastoneratioshouldbepresent.
                res[product.id]={
                    'virtual_available':min(ratios_virtual_available)*bom_kits[product].product_qty//1,
                    'qty_available':min(ratios_qty_available)*bom_kits[product].product_qty//1,
                    'incoming_qty':min(ratios_incoming_qty)*bom_kits[product].product_qty//1,
                    'outgoing_qty':min(ratios_outgoing_qty)*bom_kits[product].product_qty//1,
                    'free_qty':min(ratios_free_qty)*bom_kits[product].product_qty//1,
                }
            else:
                res[product.id]={
                    'virtual_available':0,
                    'qty_available':0,
                    'incoming_qty':0,
                    'outgoing_qty':0,
                    'free_qty':0,
                }

        returnres

    defaction_view_bom(self):
        action=self.env["ir.actions.actions"]._for_xml_id("mrp.product_open_bom")
        template_ids=self.mapped('product_tmpl_id').ids
        #bomspecifictothisvariantorglobaltotemplate
        action['context']={
            'default_product_tmpl_id':template_ids[0],
            'default_product_id':self.env.user.has_group('product.group_product_variant')andself.ids[0]orFalse,
        }
        action['domain']=['|',('product_id','in',self.ids),'&',('product_id','=',False),('product_tmpl_id','in',template_ids)]
        returnaction

    defaction_view_mos(self):
        action=self.product_tmpl_id.action_view_mos()
        action['domain']=[('state','=','done'),('product_id','in',self.ids)]
        returnaction

    defaction_open_quants(self):
        bom_kits={}
        forproductinself:
            bom=self.env['mrp.bom']._bom_find(product=product,bom_type='phantom')
            ifbom:
                bom_kits[product]=bom
        components=self-self.env['product.product'].concat(*list(bom_kits.keys()))
        forproductinbom_kits:
            boms,bom_sub_lines=bom_kits[product].explode(product,1)
            components|=self.env['product.product'].concat(*[l[0].product_idforlinbom_sub_lines])
        res=super(ProductProduct,components).action_open_quants()
        ifbom_kits:
            res['context']['single_product']=False
            res['context'].pop('default_product_tmpl_id',None)
        returnres

    def_count_returned_sn_products(self,sn_lot):
        res=self.env['stock.move.line'].search_count([
            ('lot_id','=',sn_lot.id),
            ('qty_done','=',1),
            ('state','=','done'),
            ('production_id','=',False),
            ('location_id.usage','=','production'),
            ('move_id.unbuild_id','!=',False),
        ])
        returnsuper()._count_returned_sn_products(sn_lot)+res

    def_search_qty_available_new(self,operator,value,lot_id=False,owner_id=False,package_id=False):
        '''extendingthemethodinstock.producttotakeintoaccountkits'''
        product_ids=super(ProductProduct,self)._search_qty_available_new(operator,value,lot_id,owner_id,package_id)
        kit_boms=self.env['mrp.bom'].search([('type',"=",'phantom')])
        kit_products=self.env['product.product']
        forkitinkit_boms:
            ifkit.product_id:
                kit_products|=kit.product_id
            else:
                kit_products|=kit.product_tmpl_id.product_variant_ids
        forproductinkit_products:
            ifOPERATORS[operator](product.qty_available,value):
                product_ids.append(product.id)
        returnlist(set(product_ids))

    defaction_archive(self):
        filtered_products=self.env['mrp.bom.line'].search([('product_id','in',self.ids)]).product_id.mapped('display_name')
        res=super().action_archive()
        iffiltered_products:
            return{
                'type':'ir.actions.client',
                'tag':'display_notification',
                'params':{
                'title':_("Notethatproduct(s):'%s'is/arestilllinkedtoactiveBillofMaterials,"
                            "whichmeansthattheproductcanstillbeusedonit/them.",filtered_products),
                'type':'warning',
                'sticky':True, #True/Falsewilldisplayforfewsecondsiffalse
                'next':{'type':'ir.actions.act_window_close'},
                },
            }
        returnres
