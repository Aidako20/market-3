#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,SUPERUSER_ID,_
fromflectra.osvimportexpression
fromflectra.addons.stock.models.stock_ruleimportProcurementException


classStockRule(models.Model):
    _inherit='stock.rule'
    action=fields.Selection(selection_add=[
        ('manufacture','Manufacture')
    ],ondelete={'manufacture':'cascade'})

    def_get_message_dict(self):
        message_dict=super(StockRule,self)._get_message_dict()
        source,destination,operation=self._get_message_values()
        manufacture_message=_('Whenproductsareneededin<b>%s</b>,<br/>amanufacturingorderiscreatedtofulfilltheneed.')%(destination)
        ifself.location_src_id:
            manufacture_message+=_('<br/><br/>Thecomponentswillbetakenfrom<b>%s</b>.')%(source)
        message_dict.update({
            'manufacture':manufacture_message
        })
        returnmessage_dict

    @api.depends('action')
    def_compute_picking_type_code_domain(self):
        remaining=self.browse()
        forruleinself:
            ifrule.action=='manufacture':
                rule.picking_type_code_domain='mrp_operation'
            else:
                remaining|=rule
        super(StockRule,remaining)._compute_picking_type_code_domain()

    def_should_auto_confirm_procurement_mo(self,p):
        returnnotp.orderpoint_idandp.move_raw_ids

    @api.model
    def_run_manufacture(self,procurements):
        productions_values_by_company=defaultdict(list)
        errors=[]
        forprocurement,ruleinprocurements:
            bom=rule._get_matching_bom(procurement.product_id,procurement.company_id,procurement.values)
            ifnotbom:
                msg=_('ThereisnoBillofMaterialoftypemanufactureorkitfoundfortheproduct%s.PleasedefineaBillofMaterialforthisproduct.')%(procurement.product_id.display_name,)
                errors.append((procurement,msg))

            productions_values_by_company[procurement.company_id.id].append(rule._prepare_mo_vals(*procurement,bom))

        iferrors:
            raiseProcurementException(errors)

        forcompany_id,productions_valuesinproductions_values_by_company.items():
            #createtheMOasSUPERUSERbecausethecurrentusermaynothavetherightstodoit(mtoproductlaunchedbyasaleforexample)
            productions=self.env['mrp.production'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(productions_values)
            self.env['stock.move'].sudo().create(productions._get_moves_raw_values())
            self.env['stock.move'].sudo().create(productions._get_moves_finished_values())
            productions._create_workorder()
            productions.filtered(self._should_auto_confirm_procurement_mo).action_confirm()

            forproductioninproductions:
                origin_production=production.move_dest_idsandproduction.move_dest_ids[0].raw_material_production_idorFalse
                orderpoint=production.orderpoint_id
                iforderpoint:
                    production.message_post_with_view('mail.message_origin_link',
                                                      values={'self':production,'origin':orderpoint},
                                                      subtype_id=self.env.ref('mail.mt_note').id)
                iforigin_production:
                    production.message_post_with_view('mail.message_origin_link',
                                                      values={'self':production,'origin':origin_production},
                                                      subtype_id=self.env.ref('mail.mt_note').id)
        returnTrue

    @api.model
    def_run_pull(self,procurements):
        #Overridetocorrectlyassignthemovegeneratedfromthepull
        #initsproductionorder(pbm_samonly)
        forprocurement,ruleinprocurements:
            warehouse_id=rule.warehouse_id
            ifnotwarehouse_id:
                warehouse_id=rule.location_id.get_warehouse()
            ifrule.picking_type_id==warehouse_id.sam_type_id:
                manu_type_id=warehouse_id.manu_type_id
                ifmanu_type_id:
                    name=manu_type_id.sequence_id.next_by_id()
                else:
                    name=self.env['ir.sequence'].next_by_code('mrp.production')or_('New')
                #CreatenowtheprocurementgroupthatwillbeassignedtothenewMO
                #ThisensurethattheoutgoingmovePostProduction->StockislinkedtoitsMO
                #ratherthantheoriginalrecord(MOorSO)
                group=procurement.values.get('group_id')
                ifgroup:
                    procurement.values['group_id']=group.copy({'name':name})
                else:
                    procurement.values['group_id']=self.env["procurement.group"].create({'name':name})
        returnsuper()._run_pull(procurements)

    def_get_custom_move_fields(self):
        fields=super(StockRule,self)._get_custom_move_fields()
        fields+=['bom_line_id']
        returnfields

    def_get_matching_bom(self,product_id,company_id,values):
        ifvalues.get('bom_id',False):
            returnvalues['bom_id']
        ifvalues.get('orderpoint_id',False)andvalues['orderpoint_id'].bom_id:
            returnvalues['orderpoint_id'].bom_id
        returnself.env['mrp.bom']._bom_find(
            product=product_id,picking_type=self.picking_type_id,bom_type='normal',company_id=company_id.id)

    def_prepare_mo_vals(self,product_id,product_qty,product_uom,location_id,name,origin,company_id,values,bom):
        date_planned=self._get_date_planned(product_id,company_id,values)
        date_deadline=values.get('date_deadline')ordate_planned+relativedelta(days=company_id.manufacturing_lead)+relativedelta(days=product_id.produce_delay)
        mo_values={
            'origin':origin,
            'product_id':product_id.id,
            'product_description_variants':values.get('product_description_variants'),
            'product_qty':product_qty,
            'product_uom_id':product_uom.id,
            'location_src_id':self.location_src_id.idorself.picking_type_id.default_location_src_id.idorlocation_id.id,
            'location_dest_id':location_id.id,
            'bom_id':bom.id,
            'date_deadline':date_deadline,
            'date_planned_start':date_planned,
            'date_planned_finished':fields.Datetime.from_string(values['date_planned']),
            'procurement_group_id':False,
            'propagate_cancel':self.propagate_cancel,
            'orderpoint_id':values.get('orderpoint_id',False)andvalues.get('orderpoint_id').id,
            'picking_type_id':self.picking_type_id.idorvalues['warehouse_id'].manu_type_id.id,
            'company_id':company_id.id,
            'move_dest_ids':values.get('move_dest_ids')and[(4,x.id)forxinvalues['move_dest_ids']]orFalse,
            'user_id':False,
        }
        #Usetheprocurementgroupcreatedin_run_pullmrpoverride
        #Preservetheoriginfromtheoriginalstockmove,ifavailable
        iflocation_id.get_warehouse().manufacture_steps=='pbm_sam'andvalues.get('move_dest_ids')andvalues.get('group_id')andvalues['move_dest_ids'][0].origin!=values['group_id'].name:
            origin=values['move_dest_ids'][0].origin
            mo_values.update({
                'name':values['group_id'].name,
                'procurement_group_id':values['group_id'].id,
                'origin':origin,
            })
        returnmo_values

    def_get_date_planned(self,product_id,company_id,values):
        format_date_planned=fields.Datetime.from_string(values['date_planned'])
        date_planned=format_date_planned-relativedelta(days=product_id.produce_delay)
        date_planned=date_planned-relativedelta(days=company_id.manufacturing_lead)
        ifdate_planned==format_date_planned:
            date_planned=date_planned-relativedelta(hours=1)
        returndate_planned

    def_get_lead_days(self,product):
        """Addtheproductandcompanymanufacturedelaytothecumulativedelay
        andcumulativedescription.
        """
        delay,delay_description=super()._get_lead_days(product)
        bypass_delay_description=self.env.context.get('bypass_delay_description')
        manufacture_rule=self.filtered(lambdar:r.action=='manufacture')
        ifnotmanufacture_rule:
            returndelay,delay_description
        manufacture_rule.ensure_one()
        manufacture_delay=product.produce_delay
        delay+=manufacture_delay
        ifnotbypass_delay_description:
            delay_description+='<tr><td>%s</td><tdclass="text-right">+%d%s</td></tr>'%(_('ManufacturingLeadTime'),manufacture_delay,_('day(s)'))
        security_delay=manufacture_rule.picking_type_id.company_id.manufacturing_lead
        delay+=security_delay
        ifnotbypass_delay_description:
            delay_description+='<tr><td>%s</td><tdclass="text-right">+%d%s</td></tr>'%(_('ManufactureSecurityLeadTime'),security_delay,_('day(s)'))
        returndelay,delay_description

    def_push_prepare_move_copy_values(self,move_to_copy,new_date):
        new_move_vals=super(StockRule,self)._push_prepare_move_copy_values(move_to_copy,new_date)
        new_move_vals['production_id']=False
        returnnew_move_vals


classProcurementGroup(models.Model):
    _inherit='procurement.group'

    mrp_production_ids=fields.One2many('mrp.production','procurement_group_id')

    @api.model
    defrun(self,procurements,raise_user_error=True):
        """If'run'iscalledonakit,thisoverrideismadeinordertocall
        theoriginal'run'methodwiththevaluesofthecomponentsofthatkit.
        """
        procurements_without_kit=[]
        forprocurementinprocurements:
            bom_kit=self.env['mrp.bom']._bom_find(
                product=procurement.product_id,
                company_id=procurement.company_id.id,
                bom_type='phantom',
            )
            ifbom_kit:
                order_qty=procurement.product_uom._compute_quantity(procurement.product_qty,bom_kit.product_uom_id,round=False)
                qty_to_produce=(order_qty/bom_kit.product_qty)
                boms,bom_sub_lines=bom_kit.explode(procurement.product_id,qty_to_produce)
                forbom_line,bom_line_datainbom_sub_lines:
                    bom_line_uom=bom_line.product_uom_id
                    quant_uom=bom_line.product_id.uom_id
                    #recreatedictofvaluessinceeachchildhasitsownbom_line_id
                    values=dict(procurement.values,bom_line_id=bom_line.id)
                    component_qty,procurement_uom=bom_line_uom._adjust_uom_quantities(bom_line_data['qty'],quant_uom)
                    procurements_without_kit.append(self.env['procurement.group'].Procurement(
                        bom_line.product_id,component_qty,procurement_uom,
                        procurement.location_id,procurement.name,
                        procurement.origin,procurement.company_id,values))
            else:
                procurements_without_kit.append(procurement)
        returnsuper(ProcurementGroup,self).run(procurements_without_kit,raise_user_error=raise_user_error)

    def_get_moves_to_assign_domain(self,company_id):
        domain=super(ProcurementGroup,self)._get_moves_to_assign_domain(company_id)
        domain=expression.AND([domain,[('production_id','=',False)]])
        returndomain
