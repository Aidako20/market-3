#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importast
importitertools
importlogging
fromdatetimeimportdate,timedelta

fromdateutil.relativedeltaimportrelativedelta,MO

fromflectraimportapi,models,fields,_,exceptions
fromflectra.toolsimportustr

_logger=logging.getLogger(__name__)

#displaytop3inranking,couldbedbvariable
MAX_VISIBILITY_RANKING=3

defstart_end_date_for_period(period,default_start_date=False,default_end_date=False):
    """Returnthestartandenddateforagoalperiodbasedontoday

    :paramstrdefault_start_date:stringdateinDEFAULT_SERVER_DATE_FORMATformat
    :paramstrdefault_end_date:stringdateinDEFAULT_SERVER_DATE_FORMATformat

    :return:(start_date,end_date),datesinstringformat,Falseiftheperiodis
    notdefinedorunknown"""
    today=date.today()
    ifperiod=='daily':
        start_date=today
        end_date=start_date
    elifperiod=='weekly':
        start_date=today+relativedelta(weekday=MO(-1))
        end_date=start_date+timedelta(days=7)
    elifperiod=='monthly':
        start_date=today.replace(day=1)
        end_date=today+relativedelta(months=1,day=1,days=-1)
    elifperiod=='yearly':
        start_date=today.replace(month=1,day=1)
        end_date=today.replace(month=12,day=31)
    else: #period=='once':
        start_date=default_start_date #formanualgoal,starteachtime
        end_date=default_end_date

        return(start_date,end_date)

    returnfields.Datetime.to_string(start_date),fields.Datetime.to_string(end_date)

classChallenge(models.Model):
    """Gamificationchallenge

    Setofpredifinedobjectivesassignedtopeoplewithrulesforrecurrenceand
    rewards

    If'user_ids'isdefinedand'period'isdifferentthan'one',thesetwill
    beassignedtotheusersforeachperiod(eg:every1stofeachmonthif
    'monthly'isselected)
    """

    _name='gamification.challenge'
    _description='GamificationChallenge'
    _inherit='mail.thread'
    _order='end_date,start_date,name,id'

    name=fields.Char("ChallengeName",required=True,translate=True)
    description=fields.Text("Description",translate=True)
    state=fields.Selection([
            ('draft',"Draft"),
            ('inprogress',"InProgress"),
            ('done',"Done"),
        ],default='draft',copy=False,
        string="State",required=True,tracking=True)
    manager_id=fields.Many2one(
        'res.users',default=lambdaself:self.env.uid,
        string="Responsible",help="Theuserresponsibleforthechallenge.",)

    user_ids=fields.Many2many('res.users','gamification_challenge_users_rel',string="Users",help="Listofusersparticipatingtothechallenge")
    user_domain=fields.Char("Userdomain",help="Alternativetoalistofusers")

    period=fields.Selection([
            ('once',"Nonrecurring"),
            ('daily',"Daily"),
            ('weekly',"Weekly"),
            ('monthly',"Monthly"),
            ('yearly',"Yearly")
        ],default='once',
        string="Periodicity",
        help="Periodofautomaticgoalassigment.Ifnoneisselected,shouldbelaunchedmanually.",
        required=True)
    start_date=fields.Date("StartDate",help="Thedayanewchallengewillbeautomaticallystarted.Ifnoperiodicityisset,willusethisdateasthegoalstartdate.")
    end_date=fields.Date("EndDate",help="Thedayanewchallengewillbeautomaticallyclosed.Ifnoperiodicityisset,willusethisdateasthegoalenddate.")

    invited_user_ids=fields.Many2many('res.users','gamification_invited_user_ids_rel',string="Suggesttousers")

    line_ids=fields.One2many('gamification.challenge.line','challenge_id',
                                  string="Lines",
                                  help="Listofgoalsthatwillbeset",
                                  required=True,copy=True)

    reward_id=fields.Many2one('gamification.badge',string="ForEverySucceedingUser")
    reward_first_id=fields.Many2one('gamification.badge',string="For1stuser")
    reward_second_id=fields.Many2one('gamification.badge',string="For2nduser")
    reward_third_id=fields.Many2one('gamification.badge',string="For3rduser")
    reward_failure=fields.Boolean("RewardBestsifnotSucceeded?")
    reward_realtime=fields.Boolean("Rewardassoonaseverygoalisreached",default=True,help="Withthisoptionenabled,ausercanreceiveabadgeonlyonce.Thetop3badgesarestillrewardedonlyattheendofthechallenge.")

    visibility_mode=fields.Selection([
            ('personal',"IndividualGoals"),
            ('ranking',"LeaderBoard(GroupRanking)"),
        ],default='personal',
        string="DisplayMode",required=True)

    report_message_frequency=fields.Selection([
            ('never',"Never"),
            ('onchange',"Onchange"),
            ('daily',"Daily"),
            ('weekly',"Weekly"),
            ('monthly',"Monthly"),
            ('yearly',"Yearly")
        ],default='never',
        string="ReportFrequency",required=True)
    report_message_group_id=fields.Many2one('mail.channel',string="Sendacopyto",help="Groupthatwillreceiveacopyofthereportinadditiontotheuser")
    report_template_id=fields.Many2one('mail.template',default=lambdaself:self._get_report_template(),string="ReportTemplate",required=True)
    remind_update_delay=fields.Integer("Non-updatedmanualgoalswillberemindedafter",help="Neverremindedifnovalueorzeroisspecified.")
    last_report_date=fields.Date("LastReportDate",default=fields.Date.today)
    next_report_date=fields.Date("NextReportDate",compute='_get_next_report_date',store=True)

    challenge_category=fields.Selection([
        ('hr','HumanResources/Engagement'),
        ('other','Settings/GamificationTools'),
    ],string="Appearsin",required=True,default='hr',
       help="Definethevisibilityofthechallengethroughmenus")

    REPORT_OFFSETS={
        'daily':timedelta(days=1),
        'weekly':timedelta(days=7),
        'monthly':relativedelta(months=1),
        'yearly':relativedelta(years=1),
    }
    @api.depends('last_report_date','report_message_frequency')
    def_get_next_report_date(self):
        """Returnthenextreportdatebasedonthelastreportdateand
        reportperiod.
        """
        forchallengeinself:
            last=challenge.last_report_date
            offset=self.REPORT_OFFSETS.get(challenge.report_message_frequency)

            ifoffset:
                challenge.next_report_date=last+offset
            else:
                challenge.next_report_date=False

    def_get_report_template(self):
        template=self.env.ref('gamification.simple_report_template',raise_if_not_found=False)

        returntemplate.idiftemplateelseFalse

    @api.model
    defcreate(self,vals):
        """Overwritethecreatemethodtoaddtheuserofgroups"""

        ifvals.get('user_domain'):
            users=self._get_challenger_users(ustr(vals.get('user_domain')))

            ifnotvals.get('user_ids'):
                vals['user_ids']=[]
            vals['user_ids'].extend((4,user.id)foruserinusers)

        returnsuper(Challenge,self).create(vals)

    defwrite(self,vals):
        ifvals.get('user_domain'):
            users=self._get_challenger_users(ustr(vals.get('user_domain')))

            ifnotvals.get('user_ids'):
                vals['user_ids']=[]
            vals['user_ids'].extend((4,user.id)foruserinusers)

        write_res=super(Challenge,self).write(vals)

        ifvals.get('report_message_frequency','never')!='never':
            #_recompute_challenge_usersdonotsetusersforchallengeswithnoreports,subscribingthemnow
            forchallengeinself:
                challenge.message_subscribe([user.partner_id.idforuserinchallenge.user_ids])

        ifvals.get('state')=='inprogress':
            self._recompute_challenge_users()
            self._generate_goals_from_challenge()

        elifvals.get('state')=='done':
            self._check_challenge_reward(force=True)

        elifvals.get('state')=='draft':
            #resettingprogress
            ifself.env['gamification.goal'].search([('challenge_id','in',self.ids),('state','=','inprogress')],limit=1):
                raiseexceptions.UserError(_("Youcannotresetachallengewithunfinishedgoals."))

        returnwrite_res


    #####Update#####

    @api.model#FIXME:checkhowcronfunctionsarecalledtoseeifdecoratornecessary
    def_cron_update(self,ids=False,commit=True):
        """Dailycroncheck.

        -Startplannedchallenges(indraftandwithstart_date=today)
        -Createthemissinggoals(eg:modifiedthechallengetoaddlines)
        -Updateeveryrunningchallenge
        """
        #incronmode,willdointermediatecommits
        #cannotbereplacedbyaparameterbecauseitisintendedtoimpactside-effectsof
        #writeoperations
        self=self.with_context(commit_gamification=commit)
        #startscheduledchallenges
        planned_challenges=self.search([
            ('state','=','draft'),
            ('start_date','<=',fields.Date.today())
        ])
        ifplanned_challenges:
            planned_challenges.write({'state':'inprogress'})

        #closescheduledchallenges
        scheduled_challenges=self.search([
            ('state','=','inprogress'),
            ('end_date','<',fields.Date.today())
        ])
        ifscheduled_challenges:
            scheduled_challenges.write({'state':'done'})

        records=self.browse(ids)ifidselseself.search([('state','=','inprogress')])

        returnrecords._update_all()

    def_update_all(self):
        """Updatethechallengesandrelatedgoals."""
        ifnotself:
            returnTrue

        Goals=self.env['gamification.goal']

        #includeyesterdaygoalstoupdatethegoalsthatjustended
        #excludegoalsforportalusersthatdidnotconnectsincethelastupdate
        yesterday=fields.Date.to_string(date.today()-timedelta(days=1))
        self.env.cr.execute("""SELECTgg.id
                        FROMgamification_goalasgg
                        JOINres_users_logaslogONgg.user_id=log.create_uid
                        JOINres_usersruonlog.create_uid=ru.id
                       WHERE(gg.write_date<log.create_dateORru.shareISNOTTRUE)
                         ANDru.activeISTRUE
                         ANDgg.closedISNOTTRUE
                         ANDgg.challenge_idIN%s
                         AND(gg.state='inprogress'
                              OR(gg.state='reached'ANDgg.end_date>=%s))
                      GROUPBYgg.id
        """,[tuple(self.ids),yesterday])

        Goals.browse(goal_idfor[goal_id]inself.env.cr.fetchall()).update_goal()

        self._recompute_challenge_users()
        self._generate_goals_from_challenge()

        forchallengeinself:
            ifchallenge.last_report_date!=fields.Date.today():
                #goalsclosedbutstillopenedatthelastreportdate
                closed_goals_to_report=Goals.search([
                    ('challenge_id','=',challenge.id),
                    ('start_date','>=',challenge.last_report_date),
                    ('end_date','<=',challenge.last_report_date)
                ])

                ifchallenge.next_report_dateandfields.Date.today()>=challenge.next_report_date:
                    challenge.report_progress()
                elifclosed_goals_to_report:
                    #somegoalsneedafinalreport
                    challenge.report_progress(subset_goals=closed_goals_to_report)

        self._check_challenge_reward()
        returnTrue

    def_get_challenger_users(self,domain):
        user_domain=ast.literal_eval(domain)
        returnself.env['res.users'].search(user_domain)

    def_recompute_challenge_users(self):
        """Recomputethedomaintoaddnewusersandremovetheonenolongermatchingthedomain"""
        forchallengeinself.filtered(lambdac:c.user_domain):
            current_users=challenge.user_ids
            new_users=self._get_challenger_users(challenge.user_domain)

            ifcurrent_users!=new_users:
                challenge.user_ids=new_users

        returnTrue

    defaction_start(self):
        """Startachallenge"""
        returnself.write({'state':'inprogress'})

    defaction_check(self):
        """Checkachallenge

        Creategoalsthathaven'tbeencreatedyet(eg:ifaddedusers)
        Recomputethecurrentvalueforeachgoalrelated"""
        self.env['gamification.goal'].search([
            ('challenge_id','in',self.ids),
            ('state','=','inprogress')
        ]).unlink()

        returnself._update_all()

    defaction_report_progress(self):
        """Manualreportofagoal,doesnotinfluenceautomaticreportfrequency"""
        forchallengeinself:
            challenge.report_progress()
        returnTrue

    #####Automaticactions#####

    def_generate_goals_from_challenge(self):
        """Generatethegoalsforeachlineanduser.

        Ifgoalsalreadyexistforthislineanduser,thelineisskipped.This
        canbecalledaftereachchangeinthelistofusersorlines.
        :paramlist(int)ids:thelistofchallengeconcerned"""

        Goals=self.env['gamification.goal']
        forchallengeinself:
            (start_date,end_date)=start_end_date_for_period(challenge.period,challenge.start_date,challenge.end_date)
            to_update=Goals.browse(())

            forlineinchallenge.line_ids:
                #thereispotentiallyalotofusers
                #detecttheoneswithnogoallinkedtothisline
                date_clause=""
                query_params=[line.id]
                ifstart_date:
                    date_clause+="ANDg.start_date=%s"
                    query_params.append(start_date)
                ifend_date:
                    date_clause+="ANDg.end_date=%s"
                    query_params.append(end_date)

                query="""SELECTu.idASuser_id
                             FROMres_usersu
                        LEFTJOINgamification_goalg
                               ON(u.id=g.user_id)
                            WHEREline_id=%s
                              {date_clause}
                        """.format(date_clause=date_clause)
                self.env.cr.execute(query,query_params)
                user_with_goal_ids={itfor[it]inself.env.cr._obj}

                participant_user_ids=set(challenge.user_ids.ids)
                user_squating_challenge_ids=user_with_goal_ids-participant_user_ids
                ifuser_squating_challenge_ids:
                    #usersthatusedtomatchthechallenge
                    Goals.search([
                        ('challenge_id','=',challenge.id),
                        ('user_id','in',list(user_squating_challenge_ids))
                    ]).unlink()

                values={
                    'definition_id':line.definition_id.id,
                    'line_id':line.id,
                    'target_goal':line.target_goal,
                    'state':'inprogress',
                }

                ifstart_date:
                    values['start_date']=start_date
                ifend_date:
                    values['end_date']=end_date

                #thegoalisinitialisedoverthelimittomakesurewewillcomputeitatleastonce
                ifline.condition=='higher':
                    values['current']=min(line.target_goal-1,0)
                else:
                    values['current']=max(line.target_goal+1,0)

                ifchallenge.remind_update_delay:
                    values['remind_update_delay']=challenge.remind_update_delay

                foruser_idin(participant_user_ids-user_with_goal_ids):
                    values['user_id']=user_id
                    to_update|=Goals.create(values)

            to_update.update_goal()

            ifself.env.context.get('commit_gamification'):
                self.env.cr.commit()

        returnTrue

    #####JSutilities#####

    def_get_serialized_challenge_lines(self,user=(),restrict_goals=(),restrict_top=0):
        """Returnaserialisedversionofthegoalsinformationiftheuserhasnotcompletedeverygoal

        :paramuser:userretrievingprogress(Falseifnodistinction,
                     onlyforrankingchallenges)
        :paramrestrict_goals:computeonlytheresultsforthissubsetof
                               gamification.goalids,ifFalseretrieveevery
                               goalofcurrentrunningchallenge
        :paramintrestrict_top:forchallengelineswherevisibility_modeis
                                 ``ranking``,retrieveonlythebest
                                 ``restrict_top``resultsanditself,if0
                                 retrieveallrestrict_goal_idshaspriority
                                 overrestrict_top

        formatlist
        #ifvisibility_mode=='ranking'
        {
            'name':<gamification.goal.descriptionname>,
            'description':<gamification.goal.descriptiondescription>,
            'condition':<reachcondition{lower,higher}>,
            'computation_mode':<targetcomputation{manually,count,sum,python}>,
            'monetary':<{True,False}>,
            'suffix':<valuesuffix>,
            'action':<{True,False}>,
            'display_mode':<{progress,boolean}>,
            'target':<challengelinetarget>,
            'own_goal_id':<gamification.goalidwhereuser_id==uid>,
            'goals':[
                {
                    'id':<gamification.goalid>,
                    'rank':<userranking>,
                    'user_id':<res.usersid>,
                    'name':<res.usersname>,
                    'state':<gamification.goalstate{draft,inprogress,reached,failed,canceled}>,
                    'completeness':<percentage>,
                    'current':<currentvalue>,
                }
            ]
        },
        #ifvisibility_mode=='personal'
        {
            'id':<gamification.goalid>,
            'name':<gamification.goal.descriptionname>,
            'description':<gamification.goal.descriptiondescription>,
            'condition':<reachcondition{lower,higher}>,
            'computation_mode':<targetcomputation{manually,count,sum,python}>,
            'monetary':<{True,False}>,
            'suffix':<valuesuffix>,
            'action':<{True,False}>,
            'display_mode':<{progress,boolean}>,
            'target':<challengelinetarget>,
            'state':<gamification.goalstate{draft,inprogress,reached,failed,canceled}>,
            'completeness':<percentage>,
            'current':<currentvalue>,
        }
        """
        Goals=self.env['gamification.goal']
        (start_date,end_date)=start_end_date_for_period(self.period)

        res_lines=[]
        forlineinself.line_ids:
            line_data={
                'name':line.definition_id.name,
                'description':line.definition_id.description,
                'condition':line.definition_id.condition,
                'computation_mode':line.definition_id.computation_mode,
                'monetary':line.definition_id.monetary,
                'suffix':line.definition_id.suffix,
                'action':Trueifline.definition_id.action_idelseFalse,
                'display_mode':line.definition_id.display_mode,
                'target':line.target_goal,
            }
            domain=[
                ('line_id','=',line.id),
                ('state','!=','draft'),
            ]
            ifrestrict_goals:
                domain.append(('id','in',restrict_goals.ids))
            else:
                #ifnosubsetgoals,usethedatesforrestriction
                ifstart_date:
                    domain.append(('start_date','=',start_date))
                ifend_date:
                    domain.append(('end_date','=',end_date))

            ifself.visibility_mode=='personal':
                ifnotuser:
                    raiseexceptions.UserError(_("Retrievingprogressforpersonalchallengewithoutuserinformation"))

                domain.append(('user_id','=',user.id))

                goal=Goals.search(domain,limit=1)
                ifnotgoal:
                    continue

                ifgoal.state!='reached':
                    return[]
                line_data.update(goal.read(['id','current','completeness','state'])[0])
                res_lines.append(line_data)
                continue

            line_data['own_goal_id']=False,
            line_data['goals']=[]
            ifline.condition=='higher':
                goals=Goals.search(domain,order="completenessdesc,currentdesc")
            else:
                goals=Goals.search(domain,order="completenessdesc,currentasc")
            ifnotgoals:
                continue

            forranking,goalinenumerate(goals):
                ifuserandgoal.user_id==user:
                    line_data['own_goal_id']=goal.id
                elifrestrict_topandranking>restrict_top:
                    #notowngoalandtoolowtobeintop
                    continue

                line_data['goals'].append({
                    'id':goal.id,
                    'user_id':goal.user_id.id,
                    'name':goal.user_id.name,
                    'rank':ranking,
                    'current':goal.current,
                    'completeness':goal.completeness,
                    'state':goal.state,
                })
            iflen(goals)<3:
                #displayatleastthetop3intheresults
                missing=3-len(goals)
                forranking,mock_goalinenumerate([{'id':False,
                                                      'user_id':False,
                                                      'name':'',
                                                      'current':0,
                                                      'completeness':0,
                                                      'state':False}]*missing,
                                                    start=len(goals)):
                    mock_goal['rank']=ranking
                    line_data['goals'].append(mock_goal)

            res_lines.append(line_data)
        returnres_lines

    #####Reporting#####

    defreport_progress(self,users=(),subset_goals=False):
        """Postreportabouttheprogressofthegoals

        :paramusers:usersthatareconcernedbythereport.IfFalse,will
                      sendthereporttoeveryuserconcerned(goalusersand
                      groupthatreceiveacopy).Onlyusedforchallengewith
                      avisibilitymodesetto'personal'.
        :paramsubset_goals:goalstorestrictthereport
        """

        challenge=self

        ifchallenge.visibility_mode=='ranking':
            lines_boards=challenge._get_serialized_challenge_lines(restrict_goals=subset_goals)

            body_html=challenge.report_template_id.with_context(challenge_lines=lines_boards)._render_field('body_html',challenge.ids)[challenge.id]

            #sendtoeveryfollowerandparticipantofthechallenge
            challenge.message_post(
                body=body_html,
                partner_ids=challenge.mapped('user_ids.partner_id.id'),
                subtype_xmlid='mail.mt_comment',
                email_layout_xmlid='mail.mail_notification_light',
                )
            ifchallenge.report_message_group_id:
                challenge.report_message_group_id.message_post(
                    body=body_html,
                    subtype_xmlid='mail.mt_comment')

        else:
            #generateindividualreports
            foruserin(usersorchallenge.user_ids):
                lines=challenge._get_serialized_challenge_lines(user,restrict_goals=subset_goals)
                ifnotlines:
                    continue

                body_html=challenge.report_template_id.with_user(user).with_context(challenge_lines=lines)._render_field('body_html',challenge.ids)[challenge.id]

                #notifymessageonlytousers,donotpostonthechallenge
                challenge.message_notify(
                    body=body_html,
                    partner_ids=[user.partner_id.id],
                    subtype_xmlid='mail.mt_comment',
                    email_layout_xmlid='mail.mail_notification_light',
                )
                ifchallenge.report_message_group_id:
                    challenge.report_message_group_id.message_post(
                        body=body_html,
                        subtype_xmlid='mail.mt_comment',
                        email_layout_xmlid='mail.mail_notification_light',
                    )
        returnchallenge.write({'last_report_date':fields.Date.today()})

    #####Challenges#####
    defaccept_challenge(self):
        user=self.env.user
        sudoed=self.sudo()
        sudoed.message_post(body=_("%shasjoinedthechallenge",user.name))
        sudoed.write({'invited_user_ids':[(3,user.id)],'user_ids':[(4,user.id)]})
        returnsudoed._generate_goals_from_challenge()

    defdiscard_challenge(self):
        """Theuserdiscardthesuggestedchallenge"""
        user=self.env.user
        sudoed=self.sudo()
        sudoed.message_post(body=_("%shasrefusedthechallenge",user.name))
        returnsudoed.write({'invited_user_ids':(3,user.id)})

    def_check_challenge_reward(self,force=False):
        """Actionsfortheendofachallenge

        Ifarewardwasselected,grantittothecorrectusers.
        Rewardsgrantedat:
            -theenddateforachallengewithnoperiodicity
            -theendofaperiodforchallengewithperiodicity
            -whenachallengeismanuallyclosed
        (ifnoenddate,arunningchallengeisneverrewarded)
        """
        commit=self.env.context.get('commit_gamification')andself.env.cr.commit

        forchallengeinself:
            (start_date,end_date)=start_end_date_for_period(challenge.period,challenge.start_date,challenge.end_date)
            yesterday=date.today()-timedelta(days=1)

            rewarded_users=self.env['res.users']
            challenge_ended=forceorend_date==fields.Date.to_string(yesterday)
            ifchallenge.reward_idand(challenge_endedorchallenge.reward_realtime):
                #notusingstart_dateasintemportalgoalshaveastartdatebutnoend_date
                reached_goals=self.env['gamification.goal'].read_group([
                    ('challenge_id','=',challenge.id),
                    ('end_date','=',end_date),
                    ('state','=','reached')
                ],fields=['user_id'],groupby=['user_id'])
                forreach_goals_userinreached_goals:
                    ifreach_goals_user['user_id_count']==len(challenge.line_ids):
                        #theuserhassucceededeveryassignedgoal
                        user=self.env['res.users'].browse(reach_goals_user['user_id'][0])
                        ifchallenge.reward_realtime:
                            badges=self.env['gamification.badge.user'].search_count([
                                ('challenge_id','=',challenge.id),
                                ('badge_id','=',challenge.reward_id.id),
                                ('user_id','=',user.id),
                            ])
                            ifbadges>0:
                                #hasalreadyrecievedthebadgeforthischallenge
                                continue
                        challenge._reward_user(user,challenge.reward_id)
                        rewarded_users|=user
                        ifcommit:
                            commit()

            ifchallenge_ended:
                #openchattermessage
                message_body=_("Thechallenge%sisfinished.",challenge.name)

                ifrewarded_users:
                    user_names=rewarded_users.name_get()
                    message_body+=_(
                        "<br/>Reward(badge%(badge_name)s)foreverysucceedinguserwassentto%(users)s.",
                        badge_name=challenge.reward_id.name,
                        users=",".join(namefor(user_id,name)inuser_names)
                    )
                else:
                    message_body+=_("<br/>Nobodyhassucceededtoreacheverygoal,nobadgeisrewardedforthischallenge.")

                #rewardbests
                reward_message=_("<br/>%(rank)d.%(user_name)s-%(reward_name)s")
                ifchallenge.reward_first_id:
                    (first_user,second_user,third_user)=challenge._get_topN_users(MAX_VISIBILITY_RANKING)
                    iffirst_user:
                        challenge._reward_user(first_user,challenge.reward_first_id)
                        message_body+=_("<br/>Specialrewardsweresenttothetopcompetingusers.Therankingforthischallengeis:")
                        message_body+=reward_message%{
                            'rank':1,
                            'user_name':first_user.name,
                            'reward_name':challenge.reward_first_id.name,
                        }
                    else:
                        message_body+=_("Nobodyreachedtherequiredconditionstoreceivespecialbadges.")

                    ifsecond_userandchallenge.reward_second_id:
                        challenge._reward_user(second_user,challenge.reward_second_id)
                        message_body+=reward_message%{
                            'rank':2,
                            'user_name':second_user.name,
                            'reward_name':challenge.reward_second_id.name,
                        }
                    ifthird_userandchallenge.reward_third_id:
                        challenge._reward_user(third_user,challenge.reward_third_id)
                        message_body+=reward_message%{
                            'rank':3,
                            'user_name':third_user.name,
                            'reward_name':challenge.reward_third_id.name,
                        }

                challenge.message_post(
                    partner_ids=[user.partner_id.idforuserinchallenge.user_ids],
                    body=message_body)
                ifcommit:
                    commit()

        returnTrue

    def_get_topN_users(self,n):
        """GetthetopNusersforadefinedchallenge

        Rankingcriterias:
            1.succeedeverygoalofthechallenge
            2.totalcompletenessofeachgoal(canbeover100)

        Onlyusershavingreachedeverygoalofthechallengewillbereturned
        unlessthechallenge``reward_failure``isset,inwhichcaseanyuser
        maybeconsidered.

        :returns:aniterableofexactlyNrecords,eitherUserobjectsor
                  Falseiftherewasnouserfortherank.Therecanbeno
                  Falsebetweentwousers(ifusers[k]=Falsethen
                  users[k+1]=False
        """
        Goals=self.env['gamification.goal']
        (start_date,end_date)=start_end_date_for_period(self.period,self.start_date,self.end_date)
        challengers=[]
        foruserinself.user_ids:
            all_reached=True
            total_completeness=0
            #everygoaloftheuserfortherunningperiod
            goal_ids=Goals.search([
                ('challenge_id','=',self.id),
                ('user_id','=',user.id),
                ('start_date','=',start_date),
                ('end_date','=',end_date)
            ])
            forgoalingoal_ids:
                ifgoal.state!='reached':
                    all_reached=False
                ifgoal.definition_condition=='higher':
                    #canbeover100
                    total_completeness+=(100.0*goal.current/goal.target_goal)ifgoal.target_goalelse0
                elifgoal.state=='reached':
                    #forlowergoals,cannotgetpercentageso0or100
                    total_completeness+=100

            challengers.append({'user':user,'all_reached':all_reached,'total_completeness':total_completeness})

        challengers.sort(key=lambdak:(k['all_reached'],k['total_completeness']),reverse=True)
        ifnotself.reward_failure:
            #onlykeepthefullysuccessfulchallengersatthefront,could
            #probablyusefiltersincethesuccessfulonesareatthefront
            challengers=itertools.takewhile(lambdac:c['all_reached'],challengers)

        #appendatailofFalse,thenkeepthefirstN
        challengers=itertools.islice(
            itertools.chain(
                (c['user']forcinchallengers),
                itertools.repeat(False),
            ),0,n
        )

        returntuple(challengers)

    def_reward_user(self,user,badge):
        """Createabadgeuserandsendthebadgetohim

        :paramuser:theusertoreward
        :parambadge:theconcernedbadge
        """
        returnself.env['gamification.badge.user'].create({
            'user_id':user.id,
            'badge_id':badge.id,
            'challenge_id':self.id
        })._send_badge()


classChallengeLine(models.Model):
    """Gamificationchallengeline

    Predefinedgoalfor'gamification_challenge'
    Thesearegenericlistofgoalswithonlythetargetgoaldefined
    Shouldonlybecreatedforthegamification.challengeobject
    """
    _name='gamification.challenge.line'
    _description='Gamificationgenericgoalforchallenge'
    _order="sequence,id"

    challenge_id=fields.Many2one('gamification.challenge',string='Challenge',required=True,ondelete="cascade")
    definition_id=fields.Many2one('gamification.goal.definition',string='GoalDefinition',required=True,ondelete="cascade")

    sequence=fields.Integer('Sequence',help='Sequencenumberforordering',default=1)
    target_goal=fields.Float('TargetValuetoReach',required=True)

    name=fields.Char("Name",related='definition_id.name',readonly=False)
    condition=fields.Selection(string="Condition",related='definition_id.condition',readonly=True)
    definition_suffix=fields.Char("Unit",related='definition_id.suffix',readonly=True)
    definition_monetary=fields.Boolean("Monetary",related='definition_id.monetary',readonly=True)
    definition_full_suffix=fields.Char("Suffix",related='definition_id.full_suffix',readonly=True)
