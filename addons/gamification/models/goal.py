#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importast
importlogging
fromdatetimeimportdate,datetime,timedelta

fromflectraimportapi,fields,models,_,exceptions
fromflectra.osvimportexpression
fromflectra.tools.safe_evalimportsafe_eval,time

_logger=logging.getLogger(__name__)


DOMAIN_TEMPLATE="[('store','=',True),'|',('model_id','=',model_id),('model_id','in',model_inherited_ids)%s]"
classGoalDefinition(models.Model):
    """Goaldefinition

    Agoaldefinitioncontainsthewaytoevaluateanobjective
    Eachmodulewantingtobeabletosetgoalstotheusersneedstocreate
    anewgamification_goal_definition
    """
    _name='gamification.goal.definition'
    _description='GamificationGoalDefinition'

    name=fields.Char("GoalDefinition",required=True,translate=True)
    description=fields.Text("GoalDescription")
    monetary=fields.Boolean("MonetaryValue",default=False,help="Thetargetandcurrentvaluearedefinedinthecompanycurrency.")
    suffix=fields.Char("Suffix",help="Theunitofthetargetandcurrentvalues",translate=True)
    full_suffix=fields.Char("FullSuffix",compute='_compute_full_suffix',help="Thecurrencyandsuffixfield")
    computation_mode=fields.Selection([
        ('manually',"Recordedmanually"),
        ('count',"Automatic:numberofrecords"),
        ('sum',"Automatic:sumonafield"),
        ('python',"Automatic:executeaspecificPythoncode"),
    ],default='manually',string="ComputationMode",required=True,
       help="Definehowthegoalswillbecomputed.Theresultoftheoperationwillbestoredinthefield'Current'.")
    display_mode=fields.Selection([
        ('progress',"Progressive(usingnumericalvalues)"),
        ('boolean',"Exclusive(doneornot-done)"),
    ],default='progress',string="Displayedas",required=True)
    model_id=fields.Many2one('ir.model',string='Model',help='Themodelobjectforthefieldtoevaluate')
    model_inherited_ids=fields.Many2many('ir.model',related='model_id.inherited_model_ids')
    field_id=fields.Many2one(
        'ir.model.fields',string='FieldtoSum',help='Thefieldcontainingthevaluetoevaluate',
        domain=DOMAIN_TEMPLATE%''
    )
    field_date_id=fields.Many2one(
        'ir.model.fields',string='DateField',help='Thedatetouseforthetimeperiodevaluated',
        domain=DOMAIN_TEMPLATE%",('ttype','in',('date','datetime'))"
    )
    domain=fields.Char(
        "FilterDomain",required=True,default="[]",
        help="Domainforfilteringrecords.Generalrule,notuserdepending,"
             "e.g.[('state','=','done')].Theexpressioncancontain"
             "referenceto'user'whichisabrowserecordofthecurrent"
             "userifnotinbatchmode.")

    batch_mode=fields.Boolean("BatchMode",help="Evaluatetheexpressioninbatchinsteadofonceforeachuser")
    batch_distinctive_field=fields.Many2one('ir.model.fields',string="Distinctivefieldforbatchuser",help="Inbatchmode,thisindicateswhichfielddistinguishesoneuserfromtheother,e.g.user_id,partner_id...")
    batch_user_expression=fields.Char("Evaluatedexpressionforbatchmode",help="Thevaluetocomparewiththedistinctivefield.Theexpressioncancontainreferenceto'user'whichisabrowserecordofthecurrentuser,e.g.user.id,user.partner_id.id...")
    compute_code=fields.Text("PythonCode",help="Pythoncodetobeexecutedforeachuser.'result'shouldcontainsthenewcurrentvalue.Evaluatedusercanbeaccessthroughobject.user_id.")
    condition=fields.Selection([
        ('higher',"Thehigherthebetter"),
        ('lower',"Thelowerthebetter")
    ],default='higher',required=True,string="GoalPerformance",
       help="Agoalisconsideredascompletedwhenthecurrentvalueiscomparedtothevaluetoreach")
    action_id=fields.Many2one('ir.actions.act_window',string="Action",help="Theactionthatwillbecalledtoupdatethegoalvalue.")
    res_id_field=fields.Char("IDFieldofuser",help="Thefieldnameontheuserprofile(res.users)containingthevalueforres_idforaction.")

    @api.depends('suffix','monetary') #alsodependsofuser...
    def_compute_full_suffix(self):
        forgoalinself:
            items=[]

            ifgoal.monetary:
                items.append(self.env.company.currency_id.symboloru'¤')
            ifgoal.suffix:
                items.append(goal.suffix)

            goal.full_suffix=u''.join(items)

    def_check_domain_validity(self):
        #takeadminasshouldalwaysbepresent
        fordefinitioninself:
            ifdefinition.computation_modenotin('count','sum'):
                continue

            Obj=self.env[definition.model_id.model]
            try:
                domain=safe_eval(definition.domain,{
                    'user':self.env.user.with_user(self.env.user)
                })
                #dummysearchtomakesurethedomainisvalid
                Obj.search_count(domain)
            except(ValueError,SyntaxError)ase:
                msg=e
                ifisinstance(e,SyntaxError):
                    msg=(e.msg+'\n'+e.text)
                raiseexceptions.UserError(_("Thedomainforthedefinition%sseemsincorrect,pleasecheckit.\n\n%s")%(definition.name,msg))
        returnTrue

    def_check_model_validity(self):
        """makesuretheselectedfieldandmodelareusable"""
        fordefinitioninself:
            try:
                ifnot(definition.model_idanddefinition.field_id):
                    continue

                Model=self.env[definition.model_id.model]
                field=Model._fields.get(definition.field_id.name)
                ifnot(fieldandfield.store):
                    raiseexceptions.UserError(_(
                        "Themodelconfigurationforthedefinition%(name)sseemsincorrect,pleasecheckit.\n\n%(field_name)snotstored",
                        name=definition.name,
                        field_name=definition.field_id.name
                    ))
            exceptKeyErrorase:
                raiseexceptions.UserError(_(
                    "Themodelconfigurationforthedefinition%(name)sseemsincorrect,pleasecheckit.\n\n%(error)snotfound",
                    name=definition.name,
                    error=e
                ))

    @api.model
    defcreate(self,vals):
        definition=super(GoalDefinition,self).create(vals)
        ifdefinition.computation_modein('count','sum'):
            definition._check_domain_validity()
        ifvals.get('field_id'):
            definition._check_model_validity()
        returndefinition

    defwrite(self,vals):
        res=super(GoalDefinition,self).write(vals)
        ifvals.get('computation_mode','count')in('count','sum')and(vals.get('domain')orvals.get('model_id')):
            self._check_domain_validity()
        ifvals.get('field_id')orvals.get('model_id')orvals.get('batch_mode'):
            self._check_model_validity()
        returnres

classGoal(models.Model):
    """Goalinstanceforauser

    Anindividualgoalforauseronaspecifiedtimeperiod"""

    _name='gamification.goal'
    _description='GamificationGoal'
    _rec_name='definition_id'
    _order='start_datedesc,end_datedesc,definition_id,id'

    definition_id=fields.Many2one('gamification.goal.definition',string="GoalDefinition",required=True,ondelete="cascade")
    user_id=fields.Many2one('res.users',string="User",required=True,auto_join=True,ondelete="cascade")
    line_id=fields.Many2one('gamification.challenge.line',string="ChallengeLine",ondelete="cascade")
    challenge_id=fields.Many2one(
        related='line_id.challenge_id',store=True,readonly=True,index=True,
        help="Challengethatgeneratedthegoal,assignchallengetousers"
             "togenerategoalswithavalueinthisfield.")
    start_date=fields.Date("StartDate",default=fields.Date.today)
    end_date=fields.Date("EndDate") #nostartandend=alwaysactive
    target_goal=fields.Float('ToReach',required=True)
#nogoal=globalindex
    current=fields.Float("CurrentValue",required=True,default=0)
    completeness=fields.Float("Completeness",compute='_get_completion')
    state=fields.Selection([
        ('draft',"Draft"),
        ('inprogress',"Inprogress"),
        ('reached',"Reached"),
        ('failed',"Failed"),
        ('canceled',"Canceled"),
    ],default='draft',string='State',required=True)
    to_update=fields.Boolean('Toupdate')
    closed=fields.Boolean('Closedgoal',help="Thesegoalswillnotberecomputed.")

    computation_mode=fields.Selection(related='definition_id.computation_mode',readonly=False)
    remind_update_delay=fields.Integer(
        "Reminddelay",help="Thenumberofdaysafterwhichtheuser"
                             "assignedtoamanualgoalwillbereminded."
                             "Neverremindedifnovalueisspecified.")
    last_update=fields.Date(
        "LastUpdate",
        help="Incaseofmanualgoal,remindersaresentifthegoalasnot"
             "beenupdatedforawhile(definedinchallenge).Ignoredin"
             "caseofnon-manualgoalorgoalnotlinkedtoachallenge.")

    definition_description=fields.Text("DefinitionDescription",related='definition_id.description',readonly=True)
    definition_condition=fields.Selection(string="DefinitionCondition",related='definition_id.condition',readonly=True)
    definition_suffix=fields.Char("Suffix",related='definition_id.full_suffix',readonly=True)
    definition_display=fields.Selection(string="DisplayMode",related='definition_id.display_mode',readonly=True)

    @api.depends('current','target_goal','definition_id.condition')
    def_get_completion(self):
        """Returnthepercentageofcompletenessofthegoal,between0and100"""
        forgoalinself:
            ifgoal.definition_condition=='higher':
                ifgoal.current>=goal.target_goal:
                    goal.completeness=100.0
                else:
                    goal.completeness=round(100.0*goal.current/goal.target_goal,2)ifgoal.target_goalelse0
            elifgoal.current<goal.target_goal:
                #agoal'lowerthan'hasonlytwovaluespossible:0or100%
                goal.completeness=100.0
            else:
                goal.completeness=0.0

    def_check_remind_delay(self):
        """Verifyifagoalhasnotbeenupdatedforsometimeandsenda
        remindermessageofneeded.

        :return:datatowriteonthegoalobject
        """
        ifnot(self.remind_update_delayandself.last_update):
            return{}

        delta_max=timedelta(days=self.remind_update_delay)
        last_update=fields.Date.from_string(self.last_update)
        ifdate.today()-last_update<delta_max:
            return{}

        #generateareminderreport
        body_html=self.env.ref('gamification.email_template_goal_reminder')._render_field('body_html',self.ids,compute_lang=True)[self.id]
        self.message_notify(
            body=body_html,
            partner_ids=[self.user_id.partner_id.id],
            subtype_xmlid='mail.mt_comment',
            email_layout_xmlid='mail.mail_notification_light',
        )

        return{'to_update':True}

    def_get_write_values(self,new_value):
        """Generatevaluestowriteafterrecomputationofagoalscore"""
        ifnew_value==self.current:
            #avoiduselesswriteifthenewvalueisthesameastheoldone
            return{}

        result={'current':new_value}
        if(self.definition_id.condition=='higher'andnew_value>=self.target_goal)\
          or(self.definition_id.condition=='lower'andnew_value<=self.target_goal):
            #success,donosetclosedascanstillchange
            result['state']='reached'

        elifself.end_dateandfields.Date.today()>self.end_date:
            #checkgoalfailure
            result['state']='failed'
            result['closed']=True

        return{self:result}

    defupdate_goal(self):
        """Updatethegoalstorecomputesvaluesandchangeofstates

        Ifamanualgoalisnotupdatedforenoughtime,theuserwillbe
        remindedtodoso(doneonlyonce,in'inprogress'state).
        Ifagoalreachesthetargetvalue,thestatusissettoreached
        Iftheenddateispassed(atleast+1day,timenotconsidered)without
        thetargetvaluebeingreached,thegoalissetasfailed."""
        goals_by_definition={}
        forgoalinself.with_context(prefetch_fields=False):
            goals_by_definition.setdefault(goal.definition_id,[]).append(goal)

        fordefinition,goalsingoals_by_definition.items():
            goals_to_write={}
            ifdefinition.computation_mode=='manually':
                forgoalingoals:
                    goals_to_write[goal]=goal._check_remind_delay()
            elifdefinition.computation_mode=='python':
                #TODObatchexecution
                forgoalingoals:
                    #executethechosenmethod
                    cxt={
                        'object':goal,
                        'env':self.env,

                        'date':date,
                        'datetime':datetime,
                        'timedelta':timedelta,
                        'time':time,
                    }
                    code=definition.compute_code.strip()
                    safe_eval(code,cxt,mode="exec",nocopy=True)
                    #theresultoftheevaluatedcodeisputinthe'result'localvariable,propagatedtothecontext
                    result=cxt.get('result')
                    ifisinstance(result,(float,int)):
                        goals_to_write.update(goal._get_write_values(result))
                    else:
                        _logger.error(
                            "Invalidreturncontent'%r'fromtheevaluation"
                            "ofcodefordefinition%s,expectedanumber",
                            result,definition.name)

            elifdefinition.computation_modein('count','sum'): #countorsum
                Obj=self.env[definition.model_id.model]

                field_date_name=definition.field_date_id.name
                ifdefinition.batch_mode:
                    #batchmode,tryingtodoasmuchaspossibleinonerequest
                    general_domain=ast.literal_eval(definition.domain)
                    field_name=definition.batch_distinctive_field.name
                    subqueries={}
                    forgoalingoals:
                        start_date=field_date_nameandgoal.start_dateorFalse
                        end_date=field_date_nameandgoal.end_dateorFalse
                        subqueries.setdefault((start_date,end_date),{}).update({goal.id:safe_eval(definition.batch_user_expression,{'user':goal.user_id})})

                    #theglobalqueryshouldbesplitbytimeperiods(especiallyforrecurrentgoals)
                    for(start_date,end_date),query_goalsinsubqueries.items():
                        subquery_domain=list(general_domain)
                        subquery_domain.append((field_name,'in',list(set(query_goals.values()))))
                        ifstart_date:
                            subquery_domain.append((field_date_name,'>=',start_date))
                        ifend_date:
                            subquery_domain.append((field_date_name,'<=',end_date))

                        ifdefinition.computation_mode=='count':
                            value_field_name=field_name+'_count'
                            iffield_name=='id':
                                #groupingoniddoesnotworkandissimilartosearchanyway
                                users=Obj.search(subquery_domain)
                                user_values=[{'id':user.id,value_field_name:1}foruserinusers]
                            else:
                                user_values=Obj.read_group(subquery_domain,fields=[field_name],groupby=[field_name])

                        else: #sum
                            value_field_name=definition.field_id.name
                            iffield_name=='id':
                                user_values=Obj.search_read(subquery_domain,fields=['id',value_field_name])
                            else:
                                user_values=Obj.read_group(subquery_domain,fields=[field_name,"%s:sum"%value_field_name],groupby=[field_name])

                        #user_valueshasformatofread_group:[{'partner_id':42,'partner_id_count':3},...]
                        forgoalin[gforgingoalsifg.idinquery_goals]:
                            foruser_valueinuser_values:
                                queried_value=field_nameinuser_valueanduser_value[field_name]orFalse
                                ifisinstance(queried_value,tuple)andlen(queried_value)==2andisinstance(queried_value[0],int):
                                    queried_value=queried_value[0]
                                ifqueried_value==query_goals[goal.id]:
                                    new_value=user_value.get(value_field_name,goal.current)
                                    goals_to_write.update(goal._get_write_values(new_value))

                else:
                    forgoalingoals:
                        #evalthedomainwithuserreplacedbygoaluserobject
                        domain=safe_eval(definition.domain,{'user':goal.user_id})

                        #addtemporalclause(s)tothedomainiffieldsarefilledonthegoal
                        ifgoal.start_dateandfield_date_name:
                            domain.append((field_date_name,'>=',goal.start_date))
                        ifgoal.end_dateandfield_date_name:
                            domain.append((field_date_name,'<=',goal.end_date))

                        ifdefinition.computation_mode=='sum':
                            field_name=definition.field_id.name
                            res=Obj.read_group(domain,[field_name],[])
                            new_value=resandres[0][field_name]or0.0

                        else: #computationmode=count
                            new_value=Obj.search_count(domain)

                        goals_to_write.update(goal._get_write_values(new_value))

            else:
                _logger.error(
                    "Invalidcomputationmode'%s'indefinition%s",
                    definition.computation_mode,definition.name)

            forgoal,valuesingoals_to_write.items():
                ifnotvalues:
                    continue
                goal.write(values)
            ifself.env.context.get('commit_gamification'):
                self.env.cr.commit()
        returnTrue

    defaction_start(self):
        """Markagoalasstarted.

        Thisshouldonlybeusedwhencreatinggoalsmanually(indraftstate)"""
        self.write({'state':'inprogress'})
        returnself.update_goal()

    defaction_reach(self):
        """Markagoalasreached.

        Ifthetargetgoalconditionisnotmet,thestatewillberesettoIn
        Progressatthenextgoalupdateuntiltheenddate."""
        returnself.write({'state':'reached'})

    defaction_fail(self):
        """Setthestateofthegoaltofailed.

        Afailedgoalwillbeignoredinfuturechecks."""
        returnself.write({'state':'failed'})

    defaction_cancel(self):
        """Resetthecompletionaftersettingagoalasreachedorfailed.

        Thisisonlythecurrentstate,ifthedateand/ortargetcriteria
        matchtheconditionsforachangeofstate,thiswillbeappliedatthe
        nextgoalupdate."""
        returnself.write({'state':'inprogress'})

    @api.model
    defcreate(self,vals):
        returnsuper(Goal,self.with_context(no_remind_goal=True)).create(vals)

    defwrite(self,vals):
        """Overwritethewritemethodtoupdatethelast_updatefieldtotoday

        IfthecurrentvalueischangedandthereportfrequencyissettoOn
        change,areportisgenerated
        """
        vals['last_update']=fields.Date.context_today(self)
        result=super(Goal,self).write(vals)
        forgoalinself:
            ifgoal.state!="draft"and('definition_id'invalsor'user_id'invals):
                #avoiddrag&dropinkanbanview
                raiseexceptions.UserError(_('Cannotmodifytheconfigurationofastartedgoal'))

            ifvals.get('current')and'no_remind_goal'notinself.env.context:
                ifgoal.challenge_id.report_message_frequency=='onchange':
                    goal.challenge_id.sudo().report_progress(users=goal.user_id)
        returnresult

    defget_action(self):
        """Gettheir.actionrelatedtoupdatethegoal

        Incaseofamanualgoal,shouldreturnawizardtoupdatethevalue
        :return:actiondescriptioninadictionary
        """
        ifself.definition_id.action_id:
            #openatheactionlinkedtothegoal
            action=self.definition_id.action_id.read()[0]

            ifself.definition_id.res_id_field:
                current_user=self.env.user.with_user(self.env.user)
                action['res_id']=safe_eval(self.definition_id.res_id_field,{
                    'user':current_user
                })

                #ifoneelementtodisplay,shouldseeitinformmodeifpossible
                action['views']=[
                    (view_id,mode)
                    for(view_id,mode)inaction['views']
                    ifmode=='form'
                ]oraction['views']
            returnaction

        ifself.computation_mode=='manually':
            #openawizardwindowtoupdatethevaluemanually
            action={
                'name':_("Update%s",self.definition_id.name),
                'id':self.id,
                'type':'ir.actions.act_window',
                'views':[[False,'form']],
                'target':'new',
                'context':{'default_goal_id':self.id,'default_current':self.current},
                'res_model':'gamification.goal.wizard'
            }
            returnaction

        returnFalse
