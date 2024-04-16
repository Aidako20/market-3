#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
fromcollectionsimportdefaultdict,namedtuple

fromdateutil.relativedeltaimportrelativedelta

fromflectraimportSUPERUSER_ID,_,api,fields,models,registry
fromflectra.exceptionsimportUserError
fromflectra.osvimportexpression
fromflectra.toolsimportfloat_compare,float_is_zero,html_escape
fromflectra.tools.miscimportsplit_every

_logger=logging.getLogger(__name__)


classProcurementException(Exception):
    """AnexceptionraisedbyProcurementGroup`run`containingallthefaulty
    procurements.
    """
    def__init__(self,procurement_exceptions):
        """:paramprocurement_exceptions:alistoftuplescontainingthefaulty
        procurementandtheirerrormessages
        :typeprocurement_exceptions:list
        """
        self.procurement_exceptions=procurement_exceptions


classStockRule(models.Model):
    """Aruledescribewhataprocurementshoulddo;produce,buy,move,..."""
    _name='stock.rule'
    _description="StockRule"
    _order="sequence,id"
    _check_company_auto=True

    @api.model
    defdefault_get(self,fields_list):
        res=super().default_get(fields_list)
        if'company_id'infields_listandnotres['company_id']:
            res['company_id']=self.env.company.id
        returnres

    name=fields.Char(
        'Name',required=True,translate=True,
        help="Thisfieldwillfillthepackingoriginandthenameofitsmoves")
    active=fields.Boolean(
        'Active',default=True,
        help="Ifunchecked,itwillallowyoutohidetherulewithoutremovingit.")
    group_propagation_option=fields.Selection([
        ('none','LeaveEmpty'),
        ('propagate','Propagate'),
        ('fixed','Fixed')],string="PropagationofProcurementGroup",default='propagate')
    group_id=fields.Many2one('procurement.group','FixedProcurementGroup')
    action=fields.Selection(
        selection=[('pull','PullFrom'),('push','PushTo'),('pull_push','Pull&Push')],string='Action',
        required=True,index=True)
    sequence=fields.Integer('Sequence',default=20)
    company_id=fields.Many2one('res.company','Company',
        default=lambdaself:self.env.company,
        domain="[('id','=?',route_company_id)]",index=True)
    location_id=fields.Many2one('stock.location','DestinationLocation',required=True,check_company=True,index=True)
    location_src_id=fields.Many2one('stock.location','SourceLocation',check_company=True)
    route_id=fields.Many2one('stock.location.route','Route',required=True,ondelete='cascade',index=True)
    route_company_id=fields.Many2one(related='route_id.company_id',string='RouteCompany')
    procure_method=fields.Selection([
        ('make_to_stock','TakeFromStock'),
        ('make_to_order','TriggerAnotherRule'),
        ('mts_else_mto','TakeFromStock,ifunavailable,TriggerAnotherRule')],string='SupplyMethod',default='make_to_stock',required=True,
        help="TakeFromStock:theproductswillbetakenfromtheavailablestockofthesourcelocation.\n"
             "TriggerAnotherRule:thesystemwilltrytofindastockruletobringtheproductsinthesourcelocation.Theavailablestockwillbeignored.\n"
             "TakeFromStock,ifUnavailable,TriggerAnotherRule:theproductswillbetakenfromtheavailablestockofthesourcelocation."
             "Ifthereisnostockavailable,thesystemwilltrytofinda ruletobringtheproductsinthesourcelocation.")
    route_sequence=fields.Integer('RouteSequence',related='route_id.sequence',store=True,readonly=False,compute_sudo=True)
    picking_type_id=fields.Many2one(
        'stock.picking.type','OperationType',
        required=True,check_company=True,
        domain="[('code','=?',picking_type_code_domain)]")
    picking_type_code_domain=fields.Char(compute='_compute_picking_type_code_domain')
    delay=fields.Integer('LeadTime',default=0,help="Theexpecteddateofthecreatedtransferwillbecomputedbasedonthisleadtime.")
    partner_address_id=fields.Many2one(
        'res.partner','PartnerAddress',
        check_company=True,
        help="Addresswheregoodsshouldbedelivered.Optional.")
    propagate_cancel=fields.Boolean(
        'CancelNextMove',default=False,
        help="Whenticked,ifthemovecreatedbythisruleiscancelled,thenextmovewillbecancelledtoo.")
    warehouse_id=fields.Many2one('stock.warehouse','Warehouse',check_company=True,index=True)
    propagate_warehouse_id=fields.Many2one(
        'stock.warehouse','WarehousetoPropagate',
        help="Thewarehousetopropagateonthecreatedmove/procurement,whichcanbedifferentofthewarehousethisruleisfor(e.gforresupplyingrulesfromanotherwarehouse)")
    auto=fields.Selection([
        ('manual','ManualOperation'),
        ('transparent','AutomaticNoStepAdded')],string='AutomaticMove',
        default='manual',index=True,required=True,
        help="The'ManualOperation'valuewillcreateastockmoveafterthecurrentone."
             "With'AutomaticNoStepAdded',thelocationisreplacedintheoriginalmove.")
    rule_message=fields.Html(compute='_compute_action_message')

    @api.onchange('picking_type_id')
    def_onchange_picking_type(self):
        """Modifylocationstothedefaultpickingtype'slocationssourceand
        destination.
        Enablethedelayalertifthepickingtypeisadelivery
        """
        self.location_src_id=self.picking_type_id.default_location_src_id.id
        self.location_id=self.picking_type_id.default_location_dest_id.id

    @api.onchange('route_id','company_id')
    def_onchange_route(self):
        """Ensurethattherule'scompanyisthesamethantheroute'scompany."""
        ifself.route_id.company_id:
            self.company_id=self.route_id.company_id
        ifself.picking_type_id.warehouse_id.company_id!=self.route_id.company_id:
            self.picking_type_id=False

    def_get_message_values(self):
        """Returnthesource,destinationandpicking_typeappliedonastock
        rule.Thepurposeofthisfunctionistoavoidcodeduplicationin
        _get_message_dictfunctionssinceitoftenrequiresthosedata.
        """
        source=self.location_src_idandself.location_src_id.display_nameor_('SourceLocation')
        destination=self.location_idandself.location_id.display_nameor_('DestinationLocation')
        operation=self.picking_type_idandself.picking_type_id.nameor_('OperationType')
        returnsource,destination,operation

    def_get_message_dict(self):
        """Returnadictwiththedifferentpossiblemessageusedforthe
        rulemessage.Itshouldreturnonemessageforeachstock.ruleaction
        (exceptpushandpull).Thisfunctionisoverrideinmrpand
        purchase_stockinordertocompletethedictionary.
        """
        message_dict={}
        source,destination,operation=self._get_message_values()
        ifself.actionin('push','pull','pull_push'):
            suffix=""
            ifself.procure_method=='make_to_order'andself.location_src_id:
                suffix=_("<br>Aneediscreatedin<b>%s</b>andarulewillbetriggeredtofulfillit.",source)
            ifself.procure_method=='mts_else_mto'andself.location_src_id:
                suffix=_("<br>Iftheproductsarenotavailablein<b>%s</b>,arulewillbetriggeredtobringproductsinthislocation.",source)
            message_dict={
                'pull':_('Whenproductsareneededin<b>%s</b>,<br/><b>%s</b>arecreatedfrom<b>%s</b>tofulfilltheneed.',destination,operation,source)+suffix,
                'push':_('Whenproductsarrivein<b>%s</b>,<br/><b>%s</b>arecreatedtosendthemin<b>%s</b>.',source,operation,destination)
            }
        returnmessage_dict

    @api.depends('action','location_id','location_src_id','picking_type_id','procure_method')
    def_compute_action_message(self):
        """Generatedynamicalyamessagethatdescribetherulepurposetothe
        enduser.
        """
        action_rules=self.filtered(lambdarule:rule.action)
        forruleinaction_rules:
            message_dict=rule._get_message_dict()
            message=message_dict.get(rule.action)andmessage_dict[rule.action]or""
            ifrule.action=='pull_push':
                message=message_dict['pull']+"<br/><br/>"+message_dict['push']
            rule.rule_message=message
        (self-action_rules).rule_message=None

    @api.depends('action')
    def_compute_picking_type_code_domain(self):
        self.picking_type_code_domain=False

    def_run_push(self,move):
        """Applyapushruleonamove.
        Iftheruleis'nostepadded'itwillmodifythedestinationlocation
        onthemove.
        Iftheruleis'manualoperation'itwillgenerateanewmoveinorder
        tocompletethesectiondefinebytherule.
        Carethisfunctionisnotcallbymethodrun.Itiscalledexplicitely
        instock_move.pyinsidethemethod_push_apply
        """
        new_date=fields.Datetime.to_string(move.date+relativedelta(days=self.delay))
        ifself.auto=='transparent':
            old_dest_location=move.location_dest_id
            move.write({'date':new_date,'location_dest_id':self.location_id.id})
            #makesurethelocation_dest_idisconsistentwiththemovelinelocationdest
            ifmove.move_line_ids:
                move.move_line_ids.location_dest_id=move.location_dest_id._get_putaway_strategy(move.product_id)ormove.location_dest_id

            #avoidloopingifapushruleisnotwellconfigured;otherwisecallagainpush_applytoseeifanextstepisdefined
            ifself.location_id!=old_dest_location:
                #TDEFIXME:shouldprobablybedoneinthemovemodelIMO
                move._push_apply()
        else:
            new_move_vals=self._push_prepare_move_copy_values(move,new_date)
            new_move=move.sudo().copy(new_move_vals)
            ifnew_move._should_bypass_reservation():
                new_move.write({'procure_method':'make_to_stock'})
            ifnotnew_move.location_id.should_bypass_reservation():
                move.write({'move_dest_ids':[(4,new_move.id)]})
            new_move._action_confirm()

    def_push_prepare_move_copy_values(self,move_to_copy,new_date):
        company_id=self.company_id.id
        ifnotcompany_id:
            company_id=self.sudo().warehouse_idandself.sudo().warehouse_id.company_id.idorself.sudo().picking_type_id.warehouse_id.company_id.id
        new_move_vals={
            'origin':move_to_copy.originormove_to_copy.picking_id.nameor"/",
            'location_id':move_to_copy.location_dest_id.id,
            'location_dest_id':self.location_id.id,
            'date':new_date,
            'company_id':company_id,
            'picking_id':False,
            'picking_type_id':self.picking_type_id.id,
            'propagate_cancel':self.propagate_cancel,
            'warehouse_id':self.warehouse_id.id,
            'procure_method':'make_to_order',
        }
        returnnew_move_vals

    @api.model
    def_run_pull(self,procurements):
        moves_values_by_company=defaultdict(list)
        mtso_products_by_locations=defaultdict(list)

        #Tohandlethe`mts_else_mto`procuremethod,wedoapreliminaryloopto
        #isolatetheproductswewouldneedtoreadtheforecastedquantity,
        #inordertotobatchtheread.Wealsomakeasanitarycheckonthe
        #`location_src_id`field.
        forprocurement,ruleinprocurements:
            ifnotrule.location_src_id:
                msg=_('Nosourcelocationdefinedonstockrule:%s!')%(rule.name,)
                raiseProcurementException([(procurement,msg)])

            ifrule.procure_method=='mts_else_mto':
                mtso_products_by_locations[rule.location_src_id].append(procurement.product_id.id)

        #Gettheforecastedquantityforthe`mts_else_mto`procurement.
        forecasted_qties_by_loc={}
        forlocation,product_idsinmtso_products_by_locations.items():
            products=self.env['product.product'].browse(product_ids).with_context(location=location.id)
            forecasted_qties_by_loc[location]={product.id:product.free_qtyforproductinproducts}

        #Preparethemovevalues,adaptthe`procure_method`ifneeded.
        forprocurement,ruleinprocurements:
            procure_method=rule.procure_method
            ifrule.procure_method=='mts_else_mto':
                qty_needed=procurement.product_uom._compute_quantity(procurement.product_qty,procurement.product_id.uom_id)
                qty_available=forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id]
                iffloat_compare(qty_needed,qty_available,precision_rounding=procurement.product_id.uom_id.rounding)<=0:
                    procure_method='make_to_stock'
                    forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id]-=qty_needed
                else:
                    procure_method='make_to_order'

            move_values=rule._get_stock_move_values(*procurement)
            move_values['procure_method']=procure_method
            moves_values_by_company[procurement.company_id.id].append(move_values)

        forcompany_id,moves_valuesinmoves_values_by_company.items():
            #createthemoveasSUPERUSERbecausethecurrentusermaynothavetherightstodoit(mtoproductlaunchedbyasaleforexample)
            moves=self.env['stock.move'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(moves_values)
            #Sinceaction_confirmlaunchfollowingprocurement_groupweshouldactivateit.
            moves._action_confirm()
        returnTrue

    def_get_custom_move_fields(self):
        """Thepurposeofthismethodistobeoverrideinordertoeasilyadd
        fieldsfromprocurement'values'argumenttomovedata.
        """
        return[]

    def_get_stock_move_values(self,product_id,product_qty,product_uom,location_id,name,origin,company_id,values):
        '''Returnsadictionaryofvaluesthatwillbeusedtocreateastockmovefromaprocurement.
        Thisfunctionassumesthatthegivenprocurementhasarule(action=='pull'or'pull_push')setonit.

        :paramprocurement:browserecord
        :rtype:dictionary
        '''
        group_id=False
        ifself.group_propagation_option=='propagate':
            group_id=values.get('group_id',False)andvalues['group_id'].id
        elifself.group_propagation_option=='fixed':
            group_id=self.group_id.id

        date_scheduled=fields.Datetime.to_string(
            fields.Datetime.from_string(values['date_planned'])-relativedelta(days=self.delayor0)
        )
        date_deadline=values.get('date_deadline')and(fields.Datetime.to_datetime(values['date_deadline'])-relativedelta(days=self.delayor0))orFalse
        partner=self.partner_address_idor(values.get('group_id',False)andvalues['group_id'].partner_id)
        ifpartner:
            product_id=product_id.with_context(lang=partner.langorself.env.user.lang)
        picking_description=product_id._get_description(self.picking_type_id)
        ifvalues.get('product_description_variants'):
            picking_description+=values['product_description_variants']
        #itispossiblethatwe'vealreadygotsomemovedone,socheckforthedoneqtyandcreate
        #anewmovewiththecorrectqty
        qty_left=product_qty

        move_dest_ids=[]
        ifnotself.location_id.should_bypass_reservation():
            move_dest_ids=values.get('move_dest_ids',False)and[(4,x.id)forxinvalues['move_dest_ids']]or[]

        #whencreatechainedmovesforinter-warehousetransfers,setthewarehousesaspartners
        ifnotpartnerandmove_dest_ids:
            move_dest=values['move_dest_ids']
            iflocation_id==company_id.internal_transit_location_id:
                partners=move_dest.location_dest_id.get_warehouse().partner_id
                iflen(partners)==1:
                    partner=partners
                move_dest.partner_id=self.location_src_id.get_warehouse().partner_idorself.company_id.partner_id

        move_values={
            'name':name[:2000],
            'company_id':self.company_id.idorself.location_src_id.company_id.idorself.location_id.company_id.idorcompany_id.id,
            'product_id':product_id.id,
            'product_uom':product_uom.id,
            'product_uom_qty':qty_left,
            'partner_id':partner.idifpartnerelseFalse,
            'location_id':self.location_src_id.id,
            'location_dest_id':location_id.id,
            'move_dest_ids':move_dest_ids,
            'rule_id':self.id,
            'procure_method':self.procure_method,
            'origin':origin,
            'picking_type_id':self.picking_type_id.id,
            'group_id':group_id,
            'route_ids':[(4,route.id)forrouteinvalues.get('route_ids',[])],
            'warehouse_id':self.propagate_warehouse_id.idorself.warehouse_id.id,
            'date':date_scheduled,
            'date_deadline':Falseifself.group_propagation_option=='fixed'elsedate_deadline,
            'propagate_cancel':self.propagate_cancel,
            'description_picking':picking_description,
            'priority':values.get('priority',"0"),
            'orderpoint_id':values.get('orderpoint_id')andvalues['orderpoint_id'].id,
        }
        forfieldinself._get_custom_move_fields():
            iffieldinvalues:
                move_values[field]=values.get(field)
        returnmove_values

    def_get_lead_days(self,product):
        """Returnsthecumulativedelayanditsdescriptionencounteredbya
        procurementgoingthroughtherulesin`self`.

        :paramproduct:theproductoftheprocurement
        :typeproduct::class:`~flectra.addons.product.models.product.ProductProduct`
        :return:thecumulativedelayandcumulativedelay'sdescription
        :rtype:tuple
        """
        delay=sum(self.filtered(lambdar:r.actionin['pull','pull_push']).mapped('delay'))
        ifself.env.context.get('bypass_delay_description'):
            delay_description=""
        else:
            delay_description=''.join(['<tr><td>%s%s</td><tdclass="text-right">+%d%s</td></tr>'%(_('Delayon'),html_escape(rule.name),rule.delay,_('day(s)'))forruleinselfifrule.actionin['pull','pull_push']andrule.delay])
        returndelay,delay_description


classProcurementGroup(models.Model):
    """
    Theprocurementgroupclassisusedtogroupproductstogether
    whencomputingprocurements.(tasks,physicalproducts,...)

    Thegoalisthatwhenyouhaveonesalesorderofseveralproducts
    andtheproductsarepulledfromthesameorseverallocation(s),tokeep
    havingthemovesgroupedintopickingsthatrepresentthesalesorder.

    Usedin:salesorder(togroupdeliveryorderlinesliketheso),pull/push
    rules(topacklikethedeliveryorder),onorderpoints(e.g.forwavepicking
    allthesimilarproductstogether).

    Groupingismadeonlyifthesourceandthedestinationisthesame.
    Supposeyouhave4linesonapickingfromOutputwhere2lineswillneed
    tocomefromInput(crossdock)and2linescomingfromStock->OutputAs
    thefourwillhavethesamegroupidsfromtheSO,themovefrominputwill
    haveastock.pickingwith2groupedlinesandthemovefromstockwillhave
    2groupedlinesalso.

    Thenameisusuallythenameoftheoriginaldocument(salesorder)ora
    sequencecomputedifcreatedmanually.
    """
    _name='procurement.group'
    _description='ProcurementGroup'
    _order="iddesc"

    Procurement=namedtuple('Procurement',['product_id','product_qty',
        'product_uom','location_id','name','origin','company_id','values'])
    partner_id=fields.Many2one('res.partner','Partner')
    name=fields.Char(
        'Reference',
        default=lambdaself:self.env['ir.sequence'].next_by_code('procurement.group')or'',
        required=True)
    move_type=fields.Selection([
        ('direct','Partial'),
        ('one','Allatonce')],string='DeliveryType',default='direct',
        required=True)
    stock_move_ids=fields.One2many('stock.move','group_id',string="RelatedStockMoves")

    @api.model
    defrun(self,procurements,raise_user_error=True):
        """Fulfil`procurements`withthehelpofstockrules.

        Procurementsareneedsofproductsatacertainlocation.Tofulfil
        theseneeds,weneedtocreatesomesortofdocuments(`stock.move`
        bydefault,butextensionsof`_run_`methodsallowtocreateevery
        typeofdocuments).

        :paramprocurements:thedescriptionoftheprocurement
        :typelist:listof`~flectra.addons.stock.models.stock_rule.ProcurementGroup.Procurement`
        :paramraise_user_error:willraiseeitheranUserErrororaProcurementException
        :typeraise_user_error:boolan,optional
        :raisesUserError:if`raise_user_error`isTrueandaprocurementisn'tfulfillable
        :raisesProcurementException:if`raise_user_error`isFalseandaprocurementisn'tfulfillable
        """

        defraise_exception(procurement_errors):
            ifraise_user_error:
                dummy,errors=zip(*procurement_errors)
                raiseUserError('\n'.join(errors))
            else:
                raiseProcurementException(procurement_errors)

        actions_to_run=defaultdict(list)
        procurement_errors=[]
        forprocurementinprocurements:
            procurement.values.setdefault('company_id',procurement.location_id.company_id)
            procurement.values.setdefault('priority','0')
            procurement.values.setdefault('date_planned',fields.Datetime.now())
            if(
                procurement.product_id.typenotin('consu','product')or
                float_is_zero(procurement.product_qty,precision_rounding=procurement.product_uom.rounding)
            ):
                continue
            rule=self._get_rule(procurement.product_id,procurement.location_id,procurement.values)
            ifnotrule:
                error=_('Norulehasbeenfoundtoreplenish"%s"in"%s".\nVerifytheroutesconfigurationontheproduct.')%\
                    (procurement.product_id.display_name,procurement.location_id.display_name)
                procurement_errors.append((procurement,error))
            else:
                action='pull'ifrule.action=='pull_push'elserule.action
                actions_to_run[action].append((procurement,rule))

        ifprocurement_errors:
            raise_exception(procurement_errors)

        foraction,procurementsinactions_to_run.items():
            ifhasattr(self.env['stock.rule'],'_run_%s'%action):
                try:
                    getattr(self.env['stock.rule'],'_run_%s'%action)(procurements)
                exceptProcurementExceptionase:
                    procurement_errors+=e.procurement_exceptions
            else:
                _logger.error("Themethod_run_%sdoesn'texistontheprocurementrules"%action)

        ifprocurement_errors:
            raise_exception(procurement_errors)
        returnTrue

    @api.model
    def_search_rule(self,route_ids,product_id,warehouse_id,domain):
        """Firstfindaruleamongtheonesdefinedontheprocurement
        group,thentryontheroutesdefinedfortheproduct,finallyfallback
        onthedefaultbehavior
        """
        ifwarehouse_id:
            domain=expression.AND([['|',('warehouse_id','=',warehouse_id.id),('warehouse_id','=',False)],domain])
        Rule=self.env['stock.rule']
        res=self.env['stock.rule']
        ifroute_ids:
            res=Rule.search(expression.AND([[('route_id','in',route_ids.ids)],domain]),order='route_sequence,sequence',limit=1)
        ifnotres:
            product_routes=product_id.route_ids|product_id.categ_id.total_route_ids
            ifproduct_routes:
                res=Rule.search(expression.AND([[('route_id','in',product_routes.ids)],domain]),order='route_sequence,sequence',limit=1)
        ifnotresandwarehouse_id:
            warehouse_routes=warehouse_id.route_ids
            ifwarehouse_routes:
                res=Rule.search(expression.AND([[('route_id','in',warehouse_routes.ids)],domain]),order='route_sequence,sequence',limit=1)
        returnres

    @api.model
    def_get_rule(self,product_id,location_id,values):
        """Findapullruleforthelocation_id,fallbackontheparent
        locationsifitcouldnotbefound.
        """
        result=self.env['stock.rule']
        location=location_id
        while(notresult)andlocation:
            domain=self._get_rule_domain(location,values)
            result=self._search_rule(values.get('route_ids',False),product_id,values.get('warehouse_id',False),domain)
            location=location.location_id
        returnresult

    @api.model
    def_get_rule_domain(self,location,values):
        domain=['&',('location_id','=',location.id),('action','!=','push')]
        #Incasethemethodiscalledbythesuperuser,weneedtorestricttherulestothe
        #onesofthecompany.Thisisnotusefulasaregularusersincethereisarecord
        #ruletofilterouttherulesbasedonthecompany.
        ifself.env.suandvalues.get('company_id'):
            domain_company=['|',('company_id','=',False),('company_id','child_of',values['company_id'].ids)]
            domain=expression.AND([domain,domain_company])
        returndomain

    def_merge_domain(self,values,rule,group_id):
        return[
            ('group_id','=',group_id),#extralogic?
            ('location_id','=',rule.location_src_id.id),
            ('location_dest_id','=',values['location_id'].id),
            ('picking_type_id','=',rule.picking_type_id.id),
            ('picking_id.printed','=',False),
            ('picking_id.state','in',['draft','confirmed','waiting','assigned']),
            ('picking_id.backorder_id','=',False),
            ('product_id','=',values['product_id'].id)]

    @api.model
    def_get_moves_to_assign_domain(self,company_id):
        moves_domain=[
            ('state','in',['confirmed','partially_available']),
            ('product_uom_qty','!=',0.0)
        ]
        ifcompany_id:
            moves_domain=expression.AND([[('company_id','=',company_id)],moves_domain])
        returnmoves_domain

    @api.model
    def_run_scheduler_tasks(self,use_new_cursor=False,company_id=False):
        #Minimumstockrules
        domain=self._get_orderpoint_domain(company_id=company_id)
        orderpoints=self.env['stock.warehouse.orderpoint'].search(domain)
        #ensurethatqty_*whichdependsondatetime.now()arecorrectly
        #recomputed
        orderpoints.sudo()._compute_qty_to_order()
        orderpoints.sudo()._procure_orderpoint_confirm(use_new_cursor=use_new_cursor,company_id=company_id,raise_user_error=False)
        ifuse_new_cursor:
            self._cr.commit()

        #Searchallconfirmedstock_movesandtrytoassignthem
        domain=self._get_moves_to_assign_domain(company_id)
        moves_to_assign=self.env['stock.move'].search(domain,limit=None,
            order='prioritydesc,dateasc,idasc')
        formoves_chunkinsplit_every(100,moves_to_assign.ids):
            self.env['stock.move'].browse(moves_chunk).sudo()._action_assign()
            ifuse_new_cursor:
                self._cr.commit()

        #Mergeduplicatedquants
        self.env['stock.quant']._quant_tasks()

        ifuse_new_cursor:
            self._cr.commit()

    @api.model
    defrun_scheduler(self,use_new_cursor=False,company_id=False):
        """Calltheschedulerinordertochecktherunningprocurements(supermethod),tochecktheminimumstockrules
        andtheavailabilityofmoves.Thisfunctionisintendedtoberunforallthecompaniesatthesametime,so
        werunfunctionsasSUPERUSERtoavoidintercompaniesandaccessrightsissues."""
        try:
            ifuse_new_cursor:
                cr=registry(self._cr.dbname).cursor()
                self=self.with_env(self.env(cr=cr)) #TDEFIXME

            self._run_scheduler_tasks(use_new_cursor=use_new_cursor,company_id=company_id)
        exceptException:
            _logger.error("Errorduringstockscheduler",exc_info=True)
            raise
        finally:
            ifuse_new_cursor:
                try:
                    self._cr.close()
                exceptException:
                    pass
        return{}

    @api.model
    def_get_orderpoint_domain(self,company_id=False):
        domain=[('trigger','=','auto'),('product_id.active','=',True)]
        ifcompany_id:
            domain+=[('company_id','=',company_id)]
        returndomain
