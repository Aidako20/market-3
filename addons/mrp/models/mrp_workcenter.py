#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdateutilimportrelativedelta
fromdatetimeimporttimedelta
fromfunctoolsimportpartial
importdatetime
frompytzimporttimezone

fromflectraimportapi,exceptions,fields,models,_
fromflectra.exceptionsimportValidationError
fromflectra.addons.resource.models.resourceimportmake_aware,Intervals
fromflectra.tools.float_utilsimportfloat_compare


classMrpWorkcenter(models.Model):
    _name='mrp.workcenter'
    _description='WorkCenter'
    _order="sequence,id"
    _inherit=['resource.mixin']
    _check_company_auto=True

    #resource
    name=fields.Char('WorkCenter',related='resource_id.name',store=True,readonly=False)
    time_efficiency=fields.Float('TimeEfficiency',related='resource_id.time_efficiency',default=100,store=True,readonly=False)
    active=fields.Boolean('Active',related='resource_id.active',default=True,store=True,readonly=False)

    code=fields.Char('Code',copy=False)
    note=fields.Text(
        'Description',
        help="DescriptionoftheWorkCenter.")
    capacity=fields.Float(
        'Capacity',default=1.0,
        help="Numberofpiecesthatcanbeproducedinparallel.Incasetheworkcenterhasacapacityof5andyouhavetoproduce10unitsonyourworkorder,theusualoperationtimewillbemultipliedby2.")
    sequence=fields.Integer(
        'Sequence',default=1,required=True,
        help="Givesthesequenceorderwhendisplayingalistofworkcenters.")
    color=fields.Integer('Color')
    costs_hour=fields.Float(string='Costperhour',help='Specifycostofworkcenterperhour.',default=0.0)
    time_start=fields.Float('Timebeforeprod.',help="Timeinminutesforthesetup.")
    time_stop=fields.Float('Timeafterprod.',help="Timeinminutesforthecleaning.")
    routing_line_ids=fields.One2many('mrp.routing.workcenter','workcenter_id',"RoutingLines")
    order_ids=fields.One2many('mrp.workorder','workcenter_id',"Orders")
    workorder_count=fields.Integer('#WorkOrders',compute='_compute_workorder_count')
    workorder_ready_count=fields.Integer('#ReadWorkOrders',compute='_compute_workorder_count')
    workorder_progress_count=fields.Integer('TotalRunningOrders',compute='_compute_workorder_count')
    workorder_pending_count=fields.Integer('TotalPendingOrders',compute='_compute_workorder_count')
    workorder_late_count=fields.Integer('TotalLateOrders',compute='_compute_workorder_count')

    time_ids=fields.One2many('mrp.workcenter.productivity','workcenter_id','TimeLogs')
    working_state=fields.Selection([
        ('normal','Normal'),
        ('blocked','Blocked'),
        ('done','InProgress')],'WorkcenterStatus',compute="_compute_working_state",store=True)
    blocked_time=fields.Float(
        'BlockedTime',compute='_compute_blocked_time',
        help='Blockedhoursoverthelastmonth',digits=(16,2))
    productive_time=fields.Float(
        'ProductiveTime',compute='_compute_productive_time',
        help='Productivehoursoverthelastmonth',digits=(16,2))
    oee=fields.Float(compute='_compute_oee',help='OverallEquipmentEffectiveness,basedonthelastmonth')
    oee_target=fields.Float(string='OEETarget',help="OverallEffectiveEfficiencyTargetinpercentage",default=90)
    performance=fields.Integer('Performance',compute='_compute_performance',help='Performanceoverthelastmonth')
    workcenter_load=fields.Float('WorkCenterLoad',compute='_compute_workorder_count')
    alternative_workcenter_ids=fields.Many2many(
        'mrp.workcenter',
        'mrp_workcenter_alternative_rel',
        'workcenter_id',
        'alternative_workcenter_id',
        domain="[('id','!=',id),'|',('company_id','=',company_id),('company_id','=',False)]",
        string="AlternativeWorkcenters",check_company=True,
        help="Alternativeworkcentersthatcanbesubstitutedtothisoneinordertodispatchproduction"
    )

    @api.constrains('alternative_workcenter_ids')
    def_check_alternative_workcenter(self):
        ifselfinself.alternative_workcenter_ids:
            raiseValidationError(_("Aworkcentercannotbeanalternativeofitself"))

    @api.depends('order_ids.duration_expected','order_ids.workcenter_id','order_ids.state','order_ids.date_planned_start')
    def_compute_workorder_count(self):
        MrpWorkorder=self.env['mrp.workorder']
        result={wid:{}forwidinself._ids}
        result_duration_expected={wid:0forwidinself._ids}
        #CountLateWorkorder
        data=MrpWorkorder.read_group([('workcenter_id','in',self.ids),('state','in',('pending','ready')),('date_planned_start','<',datetime.datetime.now().strftime('%Y-%m-%d'))],['workcenter_id'],['workcenter_id'])
        count_data=dict((item['workcenter_id'][0],item['workcenter_id_count'])foritemindata)
        #CountAll,Pending,Ready,ProgressWorkorder
        res=MrpWorkorder.read_group(
            [('workcenter_id','in',self.ids)],
            ['workcenter_id','state','duration_expected'],['workcenter_id','state'],
            lazy=False)
        forres_groupinres:
            result[res_group['workcenter_id'][0]][res_group['state']]=res_group['__count']
            ifres_group['state']in('pending','ready','progress'):
                result_duration_expected[res_group['workcenter_id'][0]]+=res_group['duration_expected']
        forworkcenterinself:
            workcenter.workorder_count=sum(countforstate,countinresult[workcenter.id].items()ifstatenotin('done','cancel'))
            workcenter.workorder_pending_count=result[workcenter.id].get('pending',0)
            workcenter.workcenter_load=result_duration_expected[workcenter.id]
            workcenter.workorder_ready_count=result[workcenter.id].get('ready',0)
            workcenter.workorder_progress_count=result[workcenter.id].get('progress',0)
            workcenter.workorder_late_count=count_data.get(workcenter.id,0)

    @api.depends('time_ids','time_ids.date_end','time_ids.loss_type')
    def_compute_working_state(self):
        forworkcenterinself:
            #Wesearchforaproductivitylineassociatedtothisworkcenterhavingno`date_end`.
            #Ifwedonotfindone,theworkcenterisnotcurrentlybeingused.Ifwefindone,according
            #toits`type_loss`,theworkcenteriseitherbeingusedorblocked.
            time_log=self.env['mrp.workcenter.productivity'].search([
                ('workcenter_id','=',workcenter.id),
                ('date_end','=',False)
            ],limit=1)
            ifnottime_log:
                #theworkcenterisnotbeingused
                workcenter.working_state='normal'
            eliftime_log.loss_typein('productive','performance'):
                #theproductivitylinehasa`loss_type`thatmeanstheworkcenterisbeingused
                workcenter.working_state='done'
            else:
                #theworkcenterisblocked
                workcenter.working_state='blocked'

    def_compute_blocked_time(self):
        #TDEFIXME:productivitylosstypeshouldbeonlylosses,probablycountothertimelogsdifferently??
        data=self.env['mrp.workcenter.productivity'].read_group([
            ('date_start','>=',fields.Datetime.to_string(datetime.datetime.now()-relativedelta.relativedelta(months=1))),
            ('workcenter_id','in',self.ids),
            ('date_end','!=',False),
            ('loss_type','!=','productive')],
            ['duration','workcenter_id'],['workcenter_id'],lazy=False)
        count_data=dict((item['workcenter_id'][0],item['duration'])foritemindata)
        forworkcenterinself:
            workcenter.blocked_time=count_data.get(workcenter.id,0.0)/60.0

    def_compute_productive_time(self):
        #TDEFIXME:productivitylosstypeshouldbeonlylosses,probablycountothertimelogsdifferently
        data=self.env['mrp.workcenter.productivity'].read_group([
            ('date_start','>=',fields.Datetime.to_string(datetime.datetime.now()-relativedelta.relativedelta(months=1))),
            ('workcenter_id','in',self.ids),
            ('date_end','!=',False),
            ('loss_type','=','productive')],
            ['duration','workcenter_id'],['workcenter_id'],lazy=False)
        count_data=dict((item['workcenter_id'][0],item['duration'])foritemindata)
        forworkcenterinself:
            workcenter.productive_time=count_data.get(workcenter.id,0.0)/60.0

    @api.depends('blocked_time','productive_time')
    def_compute_oee(self):
        fororderinself:
            iforder.productive_time:
                order.oee=round(order.productive_time*100.0/(order.productive_time+order.blocked_time),2)
            else:
                order.oee=0.0

    def_compute_performance(self):
        wo_data=self.env['mrp.workorder'].read_group([
            ('date_start','>=',fields.Datetime.to_string(datetime.datetime.now()-relativedelta.relativedelta(months=1))),
            ('workcenter_id','in',self.ids),
            ('state','=','done')],['duration_expected','workcenter_id','duration'],['workcenter_id'],lazy=False)
        duration_expected=dict((data['workcenter_id'][0],data['duration_expected'])fordatainwo_data)
        duration=dict((data['workcenter_id'][0],data['duration'])fordatainwo_data)
        forworkcenterinself:
            ifduration.get(workcenter.id):
                workcenter.performance=100*duration_expected.get(workcenter.id,0.0)/duration[workcenter.id]
            else:
                workcenter.performance=0.0

    @api.constrains('capacity')
    def_check_capacity(self):
        ifany(workcenter.capacity<=0.0forworkcenterinself):
            raiseexceptions.UserError(_('Thecapacitymustbestrictlypositive.'))

    defunblock(self):
        self.ensure_one()
        ifself.working_state!='blocked':
            raiseexceptions.UserError(_("Ithasalreadybeenunblocked."))
        times=self.env['mrp.workcenter.productivity'].search([('workcenter_id','=',self.id),('date_end','=',False)])
        times.write({'date_end':fields.Datetime.now()})
        return{'type':'ir.actions.client','tag':'reload'}

    @api.model_create_multi
    defcreate(self,vals_list):
        #resource_typeis'human'bydefault.Aswearenotlivingin
        #/r/latestagecapitalism,workcentersare'material'
        records=super(MrpWorkcenter,self.with_context(default_resource_type='material')).create(vals_list)
        returnrecords

    defwrite(self,vals):
        if'company_id'invals:
            self.resource_id.company_id=vals['company_id']
        returnsuper(MrpWorkcenter,self).write(vals)

    defaction_work_order(self):
        action=self.env["ir.actions.actions"]._for_xml_id("mrp.action_work_orders")
        returnaction

    def_get_unavailability_intervals(self,start_datetime,end_datetime):
        """Gettheunavailabilitiesintervalsfortheworkcentersin`self`.

        Returnthelistofunavailabilities(atupleofdatetimes)indexed
        byworkcenterid.

        :paramstart_datetime:filterunavailabilitywithonlyslotsafterthisstart_datetime
        :paramend_datetime:filterunavailabilitywithonlyslotsbeforethisend_datetime
        :rtype:dict
        """
        unavailability_ressources=self.resource_id._get_unavailable_intervals(start_datetime,end_datetime)
        return{wc.id:unavailability_ressources.get(wc.resource_id.id,[])forwcinself}

    def_get_first_available_slot(self,start_datetime,duration):
        """Getthefirstavailableintervalfortheworkcenterin`self`.

        Theavailableintervalisdisjoinctwithallotherworkordersplannedonthisworkcenter,but
        canoverlapthetime-offoftherelatedcalendar(inverseoftheworkinghours).
        Returnthefirstavailableinterval(startdatetime,enddatetime)or,
        ifthereisnonebefore700days,atupleerror(False,'errormessage').

        :paramstart_datetime:beginthesearchatthisdatetime
        :paramduration:minutesneededtomaketheworkorder(float)
        :rtype:tuple
        """
        self.ensure_one()
        start_datetime,revert=make_aware(start_datetime)

        get_available_intervals=partial(self.resource_calendar_id._work_intervals,domain=[('time_type','in',['other','leave'])],resource=self.resource_id,tz=timezone(self.resource_calendar_id.tz))
        get_workorder_intervals=partial(self.resource_calendar_id._leave_intervals,domain=[('time_type','=','other')],resource=self.resource_id,tz=timezone(self.resource_calendar_id.tz))

        remaining=duration
        start_interval=start_datetime
        delta=timedelta(days=14)

        forninrange(50): #50*14=700daysinadvance(hardcoded)
            dt=start_datetime+delta*n
            available_intervals=get_available_intervals(dt,dt+delta)
            workorder_intervals=get_workorder_intervals(dt,dt+delta)
            forstart,stop,dummyinavailable_intervals:
                #Shouldn'tloopmorethan2timesbecausetheavailable_intervalscontainstheworkorder_intervals
                #Andremaining==durationcanonlyoccuratthefirstloopandattheintervalintersection(cannothappenseveraltimebecauseavailable_intervals>workorder_intervals
                foriinrange(2):
                    interval_minutes=(stop-start).total_seconds()/60
                    #Iftheremainingminuteshasneverdecreaseupdatestart_interval
                    ifremaining==duration:
                        start_interval=start
                    #IfthereisaoverlapbetweenthepossibleavailableintervalandaothersWO
                    ifIntervals([(start_interval,start+timedelta(minutes=min(remaining,interval_minutes)),dummy)])&workorder_intervals:
                        remaining=duration
                    eliffloat_compare(interval_minutes,remaining,precision_digits=3)>=0:
                        returnrevert(start_interval),revert(start+timedelta(minutes=remaining))
                    else:
                        #Decreaseapartoftheremainingduration
                        remaining-=interval_minutes
                        #Gotothenextavailableintervalbecausethepossiblecurrentintervaldurationhasbeenused
                        break
        returnFalse,'Notavailableslot700daysaftertheplannedstart'

    defaction_archive(self):
        res=super().action_archive()
        filtered_workcenters=",".join(workcenter.nameforworkcenterinself.filtered('routing_line_ids'))
        iffiltered_workcenters:
            return{
                'type':'ir.actions.client',
                'tag':'display_notification',
                'params':{
                'title':_("Notethatarchivedworkcenter(s):'%s'is/arestilllinkedtoactiveBillofMaterials,whichmeansthatoperationscanstillbeplannedonit/them."
                           "Topreventthis,deletionoftheworkcenterisrecommendedinstead.",filtered_workcenters),
                'type':'warning',
                'sticky':True, #True/Falsewilldisplayforfewsecondsiffalse
                'next':{'type':'ir.actions.act_window_close'},
                },
            }
        returnres


classMrpWorkcenterProductivityLossType(models.Model):
    _name="mrp.workcenter.productivity.loss.type"
    _description='MRPWorkorderproductivitylosses'
    _rec_name='loss_type'

    @api.depends('loss_type')
    defname_get(self):
        """As'category'fieldinformviewisaMany2one,itsvaluewillbein
        lowercase.Inordertodisplayitsvaluecapitalized'name_get'is
        overrided.
        """
        result=[]
        forrecinself:
            result.append((rec.id,rec.loss_type.title()))
        returnresult

    loss_type=fields.Selection([
            ('availability','Availability'),
            ('performance','Performance'),
            ('quality','Quality'),
            ('productive','Productive')],string='Category',default='availability',required=True)


classMrpWorkcenterProductivityLoss(models.Model):
    _name="mrp.workcenter.productivity.loss"
    _description="WorkcenterProductivityLosses"
    _order="sequence,id"

    name=fields.Char('BlockingReason',required=True)
    sequence=fields.Integer('Sequence',default=1)
    manual=fields.Boolean('IsaBlockingReason',default=True)
    loss_id=fields.Many2one('mrp.workcenter.productivity.loss.type',domain=([('loss_type','in',['quality','availability'])]),string='Category')
    loss_type=fields.Selection(string='EffectivenessCategory',related='loss_id.loss_type',store=True,readonly=False)


classMrpWorkcenterProductivity(models.Model):
    _name="mrp.workcenter.productivity"
    _description="WorkcenterProductivityLog"
    _order="iddesc"
    _rec_name="loss_id"
    _check_company_auto=True

    def_get_default_company_id(self):
        company_id=False
        ifself.env.context.get('default_company_id'):
            company_id=self.env.context['default_company_id']
        ifnotcompany_idandself.env.context.get('default_workorder_id'):
            workorder=self.env['mrp.workorder'].browse(self.env.context['default_workorder_id'])
            company_id=workorder.company_id
        ifnotcompany_idandself.env.context.get('default_workcenter_id'):
            workcenter=self.env['mrp.workcenter'].browse(self.env.context['default_workcenter_id'])
            company_id=workcenter.company_id
        ifnotcompany_id:
            company_id=self.env.company
        returncompany_id

    production_id=fields.Many2one('mrp.production',string='ManufacturingOrder',related='workorder_id.production_id',readonly='True')
    workcenter_id=fields.Many2one('mrp.workcenter',"WorkCenter",required=True,check_company=True)
    company_id=fields.Many2one(
        'res.company',required=True,index=True,
        default=lambdaself:self._get_default_company_id())
    workorder_id=fields.Many2one('mrp.workorder','WorkOrder',check_company=True)
    user_id=fields.Many2one(
        'res.users',"User",
        default=lambdaself:self.env.uid)
    loss_id=fields.Many2one(
        'mrp.workcenter.productivity.loss',"LossReason",
        ondelete='restrict',required=True)
    loss_type=fields.Selection(
        string="Effectiveness",related='loss_id.loss_type',store=True,readonly=False)
    description=fields.Text('Description')
    date_start=fields.Datetime('StartDate',default=fields.Datetime.now,required=True)
    date_end=fields.Datetime('EndDate')
    duration=fields.Float('Duration',compute='_compute_duration',store=True)

    @api.depends('date_end','date_start')
    def_compute_duration(self):
        forblocktimeinself:
            ifblocktime.date_startandblocktime.date_end:
                d1=fields.Datetime.from_string(blocktime.date_start)
                d2=fields.Datetime.from_string(blocktime.date_end)
                diff=d2-d1
                if(blocktime.loss_typenotin('productive','performance'))andblocktime.workcenter_id.resource_calendar_id:
                    r=blocktime.workcenter_id._get_work_days_data_batch(d1,d2)[blocktime.workcenter_id.id]['hours']
                    blocktime.duration=round(r*60,2)
                else:
                    blocktime.duration=round(diff.total_seconds()/60.0,2)
            else:
                blocktime.duration=0.0

    @api.constrains('workorder_id')
    def_check_open_time_ids(self):
        forworkorderinself.workorder_id:
            open_time_ids_by_user=self.env["mrp.workcenter.productivity"].read_group([("id","in",workorder.time_ids.ids),("date_end","=",False)],["user_id","open_time_ids_count:count(id)"],["user_id"])
            ifany(data["open_time_ids_count"]>1fordatainopen_time_ids_by_user):
                raiseValidationError(_('TheWorkorder(%s)cannotbestartedtwice!',workorder.display_name))

    defbutton_block(self):
        self.ensure_one()
        self.workcenter_id.order_ids.end_all()
