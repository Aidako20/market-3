#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime
importlogging
importtraceback
fromcollectionsimportdefaultdict

fromdateutil.relativedeltaimportrelativedelta

fromflectraimport_,api,fields,models,SUPERUSER_ID
fromflectra.toolsimportDEFAULT_SERVER_DATETIME_FORMAT
fromflectra.toolsimportsafe_eval

_logger=logging.getLogger(__name__)

DATE_RANGE_FUNCTION={
    'minutes':lambdainterval:relativedelta(minutes=interval),
    'hour':lambdainterval:relativedelta(hours=interval),
    'day':lambdainterval:relativedelta(days=interval),
    'month':lambdainterval:relativedelta(months=interval),
    False:lambdainterval:relativedelta(0),
}

DATE_RANGE_FACTOR={
    'minutes':1,
    'hour':60,
    'day':24*60,
    'month':30*24*60,
    False:0,
}


classBaseAutomation(models.Model):
    _name='base.automation'
    _description='AutomatedAction'
    _order='sequence'

    action_server_id=fields.Many2one(
        'ir.actions.server','ServerActions',
        domain="[('model_id','=',model_id)]",
        delegate=True,required=True,ondelete='restrict')
    active=fields.Boolean(default=True,help="Whenunchecked,theruleishiddenandwillnotbeexecuted.")
    trigger=fields.Selection([
        ('on_create','OnCreation'),
        ('on_write','OnUpdate'),
        ('on_create_or_write','OnCreation&Update'),
        ('on_unlink','OnDeletion'),
        ('on_change','BasedonFormModification'),
        ('on_time','BasedonTimedCondition')
        ],string='Trigger',required=True)
    trg_date_id=fields.Many2one('ir.model.fields',string='TriggerDate',
                                  help="""Whenshouldtheconditionbetriggered.
                                  Ifpresent,willbecheckedbythescheduler.Ifempty,willbecheckedatcreationandupdate.""",
                                  domain="[('model_id','=',model_id),('ttype','in',('date','datetime'))]")
    trg_date_range=fields.Integer(string='Delayaftertriggerdate',
                                    help="""Delayafterthetriggerdate.
                                    Youcanputanegativenumberifyouneedadelaybeforethe
                                    triggerdate,likesendingareminder15minutesbeforeameeting.""")
    trg_date_range_type=fields.Selection([('minutes','Minutes'),('hour','Hours'),('day','Days'),('month','Months')],
                                           string='Delaytype',default='hour')
    trg_date_calendar_id=fields.Many2one("resource.calendar",string='UseCalendar',
                                            help="Whencalculatingaday-basedtimedcondition,itispossibletouseacalendartocomputethedatebasedonworkingdays.")
    filter_pre_domain=fields.Char(string='BeforeUpdateDomain',
                                    help="Ifpresent,thisconditionmustbesatisfiedbeforetheupdateoftherecord.")
    filter_domain=fields.Char(string='Applyon',help="Ifpresent,thisconditionmustbesatisfiedbeforeexecutingtheactionrule.")
    last_run=fields.Datetime(readonly=True,copy=False)
    on_change_field_ids=fields.Many2many(
        "ir.model.fields",
        relation="base_automation_onchange_fields_rel",
        string="OnChangeFieldsTrigger",
        help="Fieldsthattriggertheonchange.",
    )
    trigger_field_ids=fields.Many2many('ir.model.fields',string='TriggerFields',
                                        help="Theactionwillbetriggeredifandonlyifoneofthesefieldsisupdated."
                                             "Ifempty,allfieldsarewatched.")
    least_delay_msg=fields.Char(compute='_compute_least_delay_msg')

    #whichfieldshaveanimpactontheregistryandthecron
    CRITICAL_FIELDS=['model_id','active','trigger','on_change_field_ids']
    RANGE_FIELDS=['trg_date_range','trg_date_range_type']

    @api.onchange('model_id')
    defonchange_model_id(self):
        self.model_name=self.model_id.model

    @api.onchange('trigger')
    defonchange_trigger(self):
        ifself.triggerin['on_create','on_create_or_write','on_unlink']:
            self.filter_pre_domain=self.trg_date_id=self.trg_date_range=self.trg_date_range_type=False
        elifself.triggerin['on_write','on_create_or_write']:
            self.trg_date_id=self.trg_date_range=self.trg_date_range_type=False
        elifself.trigger=='on_time':
            self.filter_pre_domain=False
            self.trg_date_range_type='hour'

    @api.onchange('trigger','state')
    def_onchange_state(self):
        ifself.trigger=='on_change'andself.state!='code':
            ff=self.fields_get(['trigger','state'])
            return{'warning':{
                'title':_("Warning"),
                'message':_("The\"%(trigger_value)s\"%(trigger_label)scanonlybeusedwiththe\"%(state_value)s\"actiontype")%{
                    'trigger_value':dict(ff['trigger']['selection'])['on_change'],
                    'trigger_label':ff['trigger']['string'],
                    'state_value':dict(ff['state']['selection'])['code'],
                }
            }}

        MAIL_STATES=('email','followers','next_activity')
        ifself.trigger=='on_unlink'andself.stateinMAIL_STATES:
            return{'warning':{
                'title':_("Warning"),
                'message':_(
                    "Youcannotsendanemail,addfollowersorcreateanactivity"
                    "foradeletedrecord. Itsimplydoesnotwork."
                ),
            }}

    @api.model_create_multi
    defcreate(self,vals_list):
        forvalsinvals_list:
            vals['usage']='base_automation'
        base_automations=super(BaseAutomation,self).create(vals_list)
        self._update_cron()
        self._update_registry()
        returnbase_automations

    defwrite(self,vals):
        res=super(BaseAutomation,self).write(vals)
        ifset(vals).intersection(self.CRITICAL_FIELDS):
            self._update_cron()
            self._update_registry()
        elifset(vals).intersection(self.RANGE_FIELDS):
            self._update_cron()
        returnres

    defunlink(self):
        res=super(BaseAutomation,self).unlink()
        self._update_cron()
        self._update_registry()
        returnres

    def_update_cron(self):
        """Activatethecronjobdependingonwhetherthereexistsactionrules
            basedontimeconditions. Alsoupdateitsfrequencyaccordingto
            thesmallestactiondelay,orrestorethedefault4hoursifthere
            isnotimebasedaction.
        """
        cron=self.env.ref('base_automation.ir_cron_data_base_automation_check',raise_if_not_found=False)
        ifcron:
            actions=self.with_context(active_test=True).search([('trigger','=','on_time')])
            cron.try_write({
                'active':bool(actions),
                'interval_type':'minutes',
                'interval_number':self._get_cron_interval(actions),
            })

    def_update_registry(self):
        """Updatetheregistryafteramodificationonactionrules."""
        ifself.env.registry.readyandnotself.env.context.get('import_file'):
            #re-installthemodelpatches,andnotifyotherworkers
            self._unregister_hook()
            self._register_hook()
            self.env.registry.registry_invalidated=True

    def_get_actions(self,records,triggers):
        """Returntheactionsofthegiventriggersforrecords'model.The
            returnedactions'contextcontainanobjecttomanageprocessing.
        """
        if'__action_done'notinself._context:
            self=self.with_context(__action_done={})
        domain=[('model_name','=',records._name),('trigger','in',triggers)]
        actions=self.with_context(active_test=True).sudo().search(domain)
        returnactions.with_env(self.env)

    def_get_eval_context(self):
        """Preparethecontextusedwhenevaluatingpythoncode
            :returns:dict--evaluationcontextgiventosafe_eval
        """
        return{
            'datetime':safe_eval.datetime,
            'dateutil':safe_eval.dateutil,
            'time':safe_eval.time,
            'uid':self.env.uid,
            'user':self.env.user,
        }

    def_get_cron_interval(self,actions=None):
        """Returntheexpectedtimeintervalusedbythecron,inminutes."""
        defget_delay(rec):
            returnrec.trg_date_range*DATE_RANGE_FACTOR[rec.trg_date_range_type]

        ifactionsisNone:
            actions=self.with_context(active_test=True).search([('trigger','=','on_time')])

        #Minimum1minute,maximum4hours,10%tolerance
        delay=min(actions.mapped(get_delay),default=0)
        returnmin(max(1,delay//10),4*60)ifdelayelse4*60

    def_compute_least_delay_msg(self):
        msg=_("Notethatthisactioncanbetriggedupto%dminutesafteritsschedule.")
        self.least_delay_msg=msg%self._get_cron_interval()

    def_filter_pre(self,records):
        """Filtertherecordsthatsatisfythepreconditionofaction``self``."""
        self_sudo=self.sudo()
        ifself_sudo.filter_pre_domainandrecords:
            domain=safe_eval.safe_eval(self_sudo.filter_pre_domain,self._get_eval_context())
            returnrecords.sudo().filtered_domain(domain).with_env(records.env)
        else:
            returnrecords

    def_filter_post(self,records):
        returnself._filter_post_export_domain(records)[0]

    def_filter_post_export_domain(self,records):
        """Filtertherecordsthatsatisfythepostconditionofaction``self``."""
        self_sudo=self.sudo()
        ifself_sudo.filter_domainandrecords:
            domain=safe_eval.safe_eval(self_sudo.filter_domain,self._get_eval_context())
            returnrecords.sudo().filtered_domain(domain).with_env(records.env),domain
        else:
            returnrecords,None

    @api.model
    def_add_postmortem_action(self,e):
        ifself.user_has_groups('base.group_user'):
            e.context={}
            e.context['exception_class']='base_automation'
            e.context['base_automation']={
                'id':self.id,
                'name':self.sudo().name,
            }

    def_process(self,records,domain_post=None):
        """Processaction``self``onthe``records``thathavenotbeendoneyet."""
        #filterouttherecordsonwhichselfhasalreadybeendone
        action_done=self._context['__action_done']
        records_done=action_done.get(self,records.browse())
        records-=records_done
        ifnotrecords:
            return

        #marktheremainingrecordsasdone(toavoidrecursiveprocessing)
        action_done=dict(action_done)
        action_done[self]=records_done+records
        self=self.with_context(__action_done=action_done)
        records=records.with_context(__action_done=action_done)

        #modifyrecords
        values={}
        if'date_action_last'inrecords._fields:
            values['date_action_last']=fields.Datetime.now()
        ifvalues:
            records.write(values)

        #executeserveractions
        action_server=self.action_server_id
        ifaction_server:
            forrecordinrecords:
                #weprocesstheactionifanywatchedfieldhasbeenmodified
                ifself._check_trigger_fields(record):
                    ctx={
                        'active_model':record._name,
                        'active_ids':record.ids,
                        'active_id':record.id,
                        'domain_post':domain_post,
                    }
                    try:
                        action_server.sudo().with_context(**ctx).run()
                    exceptExceptionase:
                        self._add_postmortem_action(e)
                        raisee

    def_check_trigger_fields(self,record):
        """Returnwhetheranyofthetriggerfieldshasbeenmodifiedon``record``."""
        self_sudo=self.sudo()
        ifnotself_sudo.trigger_field_ids:
            #allfieldsareimplicittriggers
            returnTrue

        ifnotself._context.get('old_values'):
            #thisisacreate:allfieldsareconsideredmodified
            returnTrue

        #Note:old_valsareintheformatofread()
        old_vals=self._context['old_values'].get(record.id,{})

        defdiffer(name):
            field=record._fields[name]
            return(
                nameinold_valsand
                field.convert_to_cache(record[name],record,validate=False)!=
                field.convert_to_cache(old_vals[name],record,validate=False)
            )
        returnany(differ(field.name)forfieldinself_sudo.trigger_field_ids)

    def_register_hook(self):
        """Patchmodelsthatshouldtriggeractionrulesbasedoncreation,
            modification,deletionofrecordsandformonchanges.
        """
        #
        #Note:thepatchedmethodsmustbedefinedinsideanotherfunction,
        #otherwisetheirclosuremaybewrong.Forinstance,thefunction
        #createreferstotheoutervariable'create',whichyouexpecttobe
        #boundtocreateitself.Butthatexpectationiswrongifcreateis
        #definedinsidealoop;inthatcase,thevariable'create'isboundto
        #thelastfunctiondefinedbytheloop.
        #

        defmake_create():
            """Instanciateacreatemethodthatprocessesactionrules."""
            @api.model_create_multi
            defcreate(self,vals_list,**kw):
                #retrievetheactionrulestopossiblyexecute
                actions=self.env['base.automation']._get_actions(self,['on_create','on_create_or_write'])
                ifnotactions:
                    returncreate.origin(self,vals_list,**kw)
                #calloriginalmethod
                records=create.origin(self.with_env(actions.env),vals_list,**kw)
                #checkpostconditions,andexecuteactionsontherecordsthatsatisfythem
                foractioninactions.with_context(old_values=None):
                    action._process(action._filter_post(records))
                returnrecords.with_env(self.env)

            returncreate

        defmake_write():
            """Instanciateawritemethodthatprocessesactionrules."""
            defwrite(self,vals,**kw):
                #retrievetheactionrulestopossiblyexecute
                actions=self.env['base.automation']._get_actions(self,['on_write','on_create_or_write'])
                ifnot(actionsandself):
                    returnwrite.origin(self,vals,**kw)
                records=self.with_env(actions.env).filtered('id')
                #checkpreconditionsonrecords
                pre={action:action._filter_pre(records)foractioninactions}
                #readoldvaluesbeforetheupdate
                old_values={
                    old_vals.pop('id'):old_vals
                    forold_valsin(records.read(list(vals))ifvalselse[])
                }
                #calloriginalmethod
                write.origin(self.with_env(actions.env),vals,**kw)
                #checkpostconditions,andexecuteactionsontherecordsthatsatisfythem
                foractioninactions.with_context(old_values=old_values):
                    records,domain_post=action._filter_post_export_domain(pre[action])
                    action._process(records,domain_post=domain_post)
                returnTrue

            returnwrite

        defmake_compute_field_value():
            """Instanciateacompute_field_valuemethodthatprocessesactionrules."""
            #
            #Note:Thisistocatchupdatesmadebyfieldrecomputations.
            #
            def_compute_field_value(self,field):
                #determinefieldsthatmaytriggeranaction
                stored_fields=[fforfinself.pool.field_computed[field]iff.store]
                ifnotany(stored_fields):
                    return_compute_field_value.origin(self,field)
                #retrievetheactionrulestopossiblyexecute
                actions=self.env['base.automation']._get_actions(self,['on_write','on_create_or_write'])
                records=self.filtered('id').with_env(actions.env)
                ifnot(actionsandrecords):
                    _compute_field_value.origin(self,field)
                    returnTrue
                #checkpreconditionsonrecords
                pre={action:action._filter_pre(records)foractioninactions}
                #readoldvaluesbeforetheupdate
                old_values={
                    old_vals.pop('id'):old_vals
                    forold_valsin(records.read([f.nameforfinstored_fields]))
                }
                #calloriginalmethod
                _compute_field_value.origin(self,field)
                #checkpostconditions,andexecuteactionsontherecordsthatsatisfythem
                foractioninactions.with_context(old_values=old_values):
                    records,domain_post=action._filter_post_export_domain(pre[action])
                    action._process(records,domain_post=domain_post)
                returnTrue

            return_compute_field_value

        defmake_unlink():
            """Instanciateanunlinkmethodthatprocessesactionrules."""
            defunlink(self,**kwargs):
                #retrievetheactionrulestopossiblyexecute
                actions=self.env['base.automation']._get_actions(self,['on_unlink'])
                records=self.with_env(actions.env)
                #checkconditions,andexecuteactionsontherecordsthatsatisfythem
                foractioninactions:
                    action._process(action._filter_post(records))
                #calloriginalmethod
                returnunlink.origin(self,**kwargs)

            returnunlink

        defmake_onchange(action_rule_id):
            """Instanciateanonchangemethodforthegivenactionrule."""
            defbase_automation_onchange(self):
                action_rule=self.env['base.automation'].browse(action_rule_id)
                result={}
                server_action=action_rule.sudo().action_server_id.with_context(
                    active_model=self._name,
                    active_id=self._origin.id,
                    active_ids=self._origin.ids,
                    onchange_self=self,
                )
                try:
                    res=server_action.run()
                exceptExceptionase:
                    action_rule._add_postmortem_action(e)
                    raisee

                ifres:
                    if'value'inres:
                        res['value'].pop('id',None)
                        self.update({key:valforkey,valinres['value'].items()ifkeyinself._fields})
                    if'domain'inres:
                        result.setdefault('domain',{}).update(res['domain'])
                    if'warning'inres:
                        result['warning']=res['warning']
                returnresult

            returnbase_automation_onchange

        patched_models=defaultdict(set)
        defpatch(model,name,method):
            """Patchmethod`name`on`model`,unlessithasbeenpatchedalready."""
            ifmodelnotinpatched_models[name]:
                patched_models[name].add(model)
                ModelClass=model.env.registry[model._name]
                origin=getattr(ModelClass,name)
                method.origin=origin
                wrapped=api.propagate(origin,method)
                wrapped.origin=origin
                setattr(ModelClass,name,wrapped)

        #retrieveallactions,andpatchtheircorrespondingmodel
        foraction_ruleinself.with_context({}).search([]):
            Model=self.env.get(action_rule.model_name)

            #Donotcrashifthemodelofthebase_action_rulewasuninstalled
            ifModelisNone:
                _logger.warning("ActionrulewithID%ddependsonmodel%s"%
                                (action_rule.id,
                                 action_rule.model_name))
                continue

            ifaction_rule.trigger=='on_create':
                patch(Model,'create',make_create())

            elifaction_rule.trigger=='on_create_or_write':
                patch(Model,'create',make_create())
                patch(Model,'write',make_write())
                patch(Model,'_compute_field_value',make_compute_field_value())

            elifaction_rule.trigger=='on_write':
                patch(Model,'write',make_write())
                patch(Model,'_compute_field_value',make_compute_field_value())

            elifaction_rule.trigger=='on_unlink':
                patch(Model,'unlink',make_unlink())

            elifaction_rule.trigger=='on_change':
                #registeranonchangemethodfortheaction_rule
                method=make_onchange(action_rule.id)
                forfieldinaction_rule.on_change_field_ids:
                    Model._onchange_methods[field.name].append(method)

    def_unregister_hook(self):
        """Removethepatchesinstalledby_register_hook()"""
        NAMES=['create','write','_compute_field_value','unlink','_onchange_methods']
        forModelinself.env.registry.values():
            fornameinNAMES:
                try:
                    delattr(Model,name)
                exceptAttributeError:
                    pass

    @api.model
    def_check_delay(self,action,record,record_dt):
        ifaction.trg_date_calendar_idandaction.trg_date_range_type=='day':
            returnaction.trg_date_calendar_id.plan_days(
                action.trg_date_range,
                fields.Datetime.from_string(record_dt),
                compute_leaves=True,
            )
        else:
            delay=DATE_RANGE_FUNCTION[action.trg_date_range_type](action.trg_date_range)
            returnfields.Datetime.from_string(record_dt)+delay

    @api.model
    def_check(self,automatic=False,use_new_cursor=False):
        """ThisFunctioniscalledbyscheduler."""
        if'__action_done'notinself._context:
            self=self.with_context(__action_done={})

        #retrievealltheactionrulestorunbasedonatimedcondition
        eval_context=self._get_eval_context()
        foractioninself.with_context(active_test=True).search([('trigger','=','on_time')]):
            _logger.info("Startingtime-basedautomatedaction`%s`.",action.name)
            last_run=fields.Datetime.from_string(action.last_run)ordatetime.datetime.utcfromtimestamp(0)

            #retrievealltherecordsthatsatisfytheaction'scondition
            domain=[]
            context=dict(self._context)
            ifaction.filter_domain:
                domain=safe_eval.safe_eval(action.filter_domain,eval_context)
            records=self.env[action.model_name].with_context(context).search(domain)

            #determinewhenactionshouldoccurfortherecords
            ifaction.trg_date_id.name=='date_action_last'and'create_date'inrecords._fields:
                get_record_dt=lambdarecord:record[action.trg_date_id.name]orrecord.create_date
            else:
                get_record_dt=lambdarecord:record[action.trg_date_id.name]

            #processactionontherecordsthatshouldbeexecuted
            now=datetime.datetime.now()
            forrecordinrecords:
                record_dt=get_record_dt(record)
                ifnotrecord_dt:
                    continue
                action_dt=self._check_delay(action,record,record_dt)
                iflast_run<=action_dt<now:
                    try:
                        action._process(record)
                    exceptException:
                        _logger.error(traceback.format_exc())

            action.write({'last_run':now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
            _logger.info("Time-basedautomatedaction`%s`done.",action.name)

            ifautomatic:
                #auto-commitforbatchprocessing
                self._cr.commit()
