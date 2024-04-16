#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importrandom
importuuid
importwerkzeug

fromflectraimportapi,exceptions,fields,models,_
fromflectra.exceptionsimportAccessError,UserError
fromflectra.osvimportexpression
fromflectra.toolsimportis_html_empty


classSurvey(models.Model):
    """Settingsforamulti-page/multi-questionsurvey.Eachsurveycanhaveoneormoreattachedpages
    andeachpagecandisplayoneormorequestions."""
    _name='survey.survey'
    _description='Survey'
    _rec_name='title'
    _inherit=['mail.thread','mail.activity.mixin']

    def_get_default_access_token(self):
        returnstr(uuid.uuid4())

    def_get_default_session_code(self):
        """Attempttogenerateasessioncodeforoursurvey.
        Themethodwillfirsttrytogenerate20codeswith4digitseachandcheckifanyarecolliding.
        Ifwehaveatleastonenon-collidingcode,weuseit.
        Ifall20generatedcodesarecolliding,wetrywith20codesof5digits,
        then6,...upto10digits."""

        fordigits_countinrange(4,10):
            range_lower_bound=1*(10**(digits_count-1))
            range_upper_bound=(range_lower_bound*10)-1
            code_candidates=set([str(random.randint(range_lower_bound,range_upper_bound))foriinrange(20)])
            colliding_codes=self.sudo().search_read(
                [('session_code','in',list(code_candidates))],
                ['session_code']
            )
            code_candidates-=set([colliding_code['session_code']forcolliding_codeincolliding_codes])
            ifcode_candidates:
                returnlist(code_candidates)[0]

        returnFalse #couldnotgenerateacode

    #description
    title=fields.Char('SurveyTitle',required=True,translate=True)
    color=fields.Integer('ColorIndex',default=0)
    description=fields.Html(
        "Description",translate=True,sanitize=False, #TDEFIXME:findawaytoauthorizevideos
        help="Thedescriptionwillbedisplayedonthehomepageofthesurvey.Youcanusethistogivethepurposeandguidelinestoyourcandidatesbeforetheystartit.")
    description_done=fields.Html(
        "EndMessage",translate=True,
        help="Thismessagewillbedisplayedwhensurveyiscompleted")
    background_image=fields.Binary("BackgroundImage")
    active=fields.Boolean("Active",default=True)
    state=fields.Selection(selection=[
        ('draft','Draft'),('open','InProgress'),('closed','Closed')
    ],string="SurveyStage",default='draft',required=True,
        group_expand='_read_group_states')
    #questions
    question_and_page_ids=fields.One2many('survey.question','survey_id',string='SectionsandQuestions',copy=True)
    page_ids=fields.One2many('survey.question',string='Pages',compute="_compute_page_and_question_ids")
    question_ids=fields.One2many('survey.question',string='Questions',compute="_compute_page_and_question_ids")
    questions_layout=fields.Selection([
        ('one_page','Onepagewithallthequestions'),
        ('page_per_section','Onepagepersection'),
        ('page_per_question','Onepageperquestion')],
        string="Layout",required=True,default='one_page')
    questions_selection=fields.Selection([
        ('all','Allquestions'),
        ('random','Randomizedpersection')],
        string="Selection",required=True,default='all',
        help="Ifrandomizedisselected,youcanconfigurethenumberofrandomquestionsbysection.Thismodeisignoredinlivesession.")
    progression_mode=fields.Selection([
        ('percent','Percentage'),
        ('number','Number')],string='ProgressionMode',default='percent',
        help="IfNumberisselected,itwilldisplaythenumberofquestionsansweredonthetotalnumberofquestiontoanswer.")
    #attendees
    user_input_ids=fields.One2many('survey.user_input','survey_id',string='Userresponses',readonly=True,groups='survey.group_survey_user')
    #security/access
    access_mode=fields.Selection([
        ('public','Anyonewiththelink'),
        ('token','Invitedpeopleonly')],string='AccessMode',
        default='public',required=True)
    access_token=fields.Char('AccessToken',default=lambdaself:self._get_default_access_token(),copy=False)
    users_login_required=fields.Boolean('LoginRequired',help="Ifchecked,usershavetologinbeforeansweringevenwithavalidtoken.")
    users_can_go_back=fields.Boolean('Userscangoback',help="Ifchecked,userscangobacktopreviouspages.")
    users_can_signup=fields.Boolean('Userscansignup',compute='_compute_users_can_signup')
    #statistics
    answer_count=fields.Integer("Registered",compute="_compute_survey_statistic")
    answer_done_count=fields.Integer("Attempts",compute="_compute_survey_statistic")
    answer_score_avg=fields.Float("AvgScore%",compute="_compute_survey_statistic")
    success_count=fields.Integer("Success",compute="_compute_survey_statistic")
    success_ratio=fields.Integer("SuccessRatio",compute="_compute_survey_statistic")
    #scoring
    scoring_type=fields.Selection([
        ('no_scoring','Noscoring'),
        ('scoring_with_answers','Scoringwithanswersattheend'),
        ('scoring_without_answers','Scoringwithoutanswersattheend')],
        string="Scoring",required=True,default='no_scoring')
    scoring_success_min=fields.Float('Success%',default=80.0)
    #attendeescontext:attemptsandtimelimitation
    is_attempts_limited=fields.Boolean('Limitednumberofattempts',help="Checkthisoptionifyouwanttolimitthenumberofattemptsperuser",
                                         compute="_compute_is_attempts_limited",store=True,readonly=False)
    attempts_limit=fields.Integer('Numberofattempts',default=1)
    is_time_limited=fields.Boolean('Thesurveyislimitedintime')
    time_limit=fields.Float("Timelimit(minutes)",default=10)
    #certification
    certification=fields.Boolean('IsaCertification',compute='_compute_certification',
                                   readonly=False,store=True)
    certification_mail_template_id=fields.Many2one(
        'mail.template','EmailTemplate',
        domain="[('model','=','survey.user_input')]",
        help="Automatedemailsenttotheuserwhenhesucceedsthecertification,containinghiscertificationdocument.")
    certification_report_layout=fields.Selection([
        ('modern_purple','ModernPurple'),
        ('modern_blue','ModernBlue'),
        ('modern_gold','ModernGold'),
        ('classic_purple','ClassicPurple'),
        ('classic_blue','ClassicBlue'),
        ('classic_gold','ClassicGold')],
        string='Certificationtemplate',default='modern_purple')
    #Certificationbadge
    #  certification_badge_id_dummyisusedtohavetwodifferentbehavioursintheformview:
    #  -Ifthecertificationbadgeisnotset,showcertification_badge_idandonlydisplaycreateoptioninthem2o
    #  -Ifthecertificationbadgeisset,showcertification_badge_id_dummyin'nocreate'mode.
    #      Soitcanbeeditedbutnotremovedorreplaced.
    certification_give_badge=fields.Boolean('GiveBadge',compute='_compute_certification_give_badge',
                                              readonly=False,store=True)
    certification_badge_id=fields.Many2one('gamification.badge','CertificationBadge')
    certification_badge_id_dummy=fields.Many2one(related='certification_badge_id',string='CertificationBadge')
    #livesessions
    session_state=fields.Selection([
        ('ready','Ready'),
        ('in_progress','InProgress'),
        ],string="SessionState",copy=False)
    session_code=fields.Char('SessionCode',default=lambdaself:self._get_default_session_code(),copy=False,
        help="Thiscodewillbeusedbyyourattendeestoreachyoursession.Feelfreetocustomizeithoweveryoulike!")
    session_link=fields.Char('SessionLink',compute='_compute_session_link')
    #livesessions-currentquestionfields
    session_question_id=fields.Many2one('survey.question',string="CurrentQuestion",copy=False,
        help="Thecurrentquestionofthesurveysession.")
    session_start_time=fields.Datetime("CurrentSessionStartTime",copy=False)
    session_question_start_time=fields.Datetime("CurrentQuestionStartTime",copy=False,
        help="Thetimeatwhichthecurrentquestionhasstarted,usedtohandlethetimerforattendees.")
    session_answer_count=fields.Integer("AnswersCount",compute='_compute_session_answer_count')
    session_question_answer_count=fields.Integer("QuestionAnswersCount",compute='_compute_session_question_answer_count')
    #livesessions-settings
    session_show_leaderboard=fields.Boolean("ShowSessionLeaderboard",compute='_compute_session_show_leaderboard',
        help="Whetherornotwewanttoshowtheattendeesleaderboardforthissurvey.")
    session_speed_rating=fields.Boolean("Rewardquickanswers",help="Attendeesgetmorepointsiftheyanswerquickly")
    #conditionalquestionsmanagement
    has_conditional_questions=fields.Boolean("Containsconditionalquestions",compute="_compute_has_conditional_questions")

    _sql_constraints=[
        ('access_token_unique','unique(access_token)','Accesstokenshouldbeunique'),
        ('session_code_unique','unique(session_code)','Sessioncodeshouldbeunique'),
        ('certification_check',"CHECK(scoring_type!='no_scoring'ORcertification=False)",
            'Youcanonlycreatecertificationsforsurveysthathaveascoringmechanism.'),
        ('scoring_success_min_check',"CHECK(scoring_success_minISNULLOR(scoring_success_min>=0ANDscoring_success_min<=100))",
            'Thepercentageofsuccesshastobedefinedbetween0and100.'),
        ('time_limit_check',"CHECK((is_time_limited=False)OR(time_limitisnotnullANDtime_limit>0))",
            'Thetimelimitneedstobeapositivenumberifthesurveyistimelimited.'),
        ('attempts_limit_check',"CHECK((is_attempts_limited=False)OR(attempts_limitisnotnullANDattempts_limit>0))",
            'Theattemptslimitneedstobeapositivenumberifthesurveyhasalimitednumberofattempts.'),
        ('badge_uniq','unique(certification_badge_id)',"Thebadgeforeachsurveyshouldbeunique!"),
        ('give_badge_check',"CHECK(certification_give_badge=FalseOR(certification_give_badge=TrueANDcertification_badge_idisnotnull))",
            'CertificationbadgemustbeconfiguredifGiveBadgeisset.'),
    ]

    def_compute_users_can_signup(self):
        signup_allowed=self.env['res.users'].sudo()._get_signup_invitation_scope()=='b2c'
        forsurveyinself:
            survey.users_can_signup=signup_allowed

    @api.depends('user_input_ids.state','user_input_ids.test_entry','user_input_ids.scoring_percentage','user_input_ids.scoring_success')
    def_compute_survey_statistic(self):
        default_vals={
            'answer_count':0,'answer_done_count':0,'success_count':0,
            'answer_score_avg':0.0,'success_ratio':0.0
        }
        stat=dict((cid,dict(default_vals,answer_score_avg_total=0.0))forcidinself.ids)
        UserInput=self.env['survey.user_input']
        base_domain=['&',('survey_id','in',self.ids),('test_entry','!=',True)]

        read_group_res=UserInput.read_group(base_domain,['survey_id','state'],['survey_id','state','scoring_percentage','scoring_success'],lazy=False)
        foriteminread_group_res:
            stat[item['survey_id'][0]]['answer_count']+=item['__count']
            stat[item['survey_id'][0]]['answer_score_avg_total']+=item['scoring_percentage']
            ifitem['state']=='done':
                stat[item['survey_id'][0]]['answer_done_count']+=item['__count']
            ifitem['scoring_success']:
                stat[item['survey_id'][0]]['success_count']+=item['__count']

        forsurvey_id,valuesinstat.items():
            avg_total=stat[survey_id].pop('answer_score_avg_total')
            stat[survey_id]['answer_score_avg']=avg_total/(stat[survey_id]['answer_done_count']or1)
            stat[survey_id]['success_ratio']=(stat[survey_id]['success_count']/(stat[survey_id]['answer_done_count']or1.0))*100

        forsurveyinself:
            survey.update(stat.get(survey._origin.id,default_vals))

    @api.depends('question_and_page_ids')
    def_compute_page_and_question_ids(self):
        forsurveyinself:
            survey.page_ids=survey.question_and_page_ids.filtered(lambdaquestion:question.is_page)
            survey.question_ids=survey.question_and_page_ids-survey.page_ids

    @api.depends('question_and_page_ids.is_conditional','users_login_required','access_mode')
    def_compute_is_attempts_limited(self):
        forsurveyinself:
            ifnotsurvey.is_attempts_limitedor\
               (survey.access_mode=='public'andnotsurvey.users_login_required)or\
               any(question.is_conditionalforquestioninsurvey.question_and_page_ids):
                survey.is_attempts_limited=False

    @api.depends('session_start_time','user_input_ids')
    def_compute_session_answer_count(self):
        """Wehavetoloopsinceourresultisdependentofthesurvey.session_start_time.
        Thisfieldiscurrentlyusedtodisplaythecountaboutasinglesurvey,inthe
        contextofsessions,soitshouldnotmattertoomuch."""

        forsurveyinself:
            answer_count=0
            input_count=self.env['survey.user_input'].read_group(
                [('survey_id','=',survey.id),
                 ('is_session_answer','=',True),
                 ('state','!=','done'),
                 ('create_date','>=',survey.session_start_time)],
                ['create_uid:count'],
                ['survey_id'],
            )
            ifinput_count:
                answer_count=input_count[0].get('create_uid',0)

            survey.session_answer_count=answer_count

    @api.depends('session_question_id','session_start_time','user_input_ids.user_input_line_ids')
    def_compute_session_question_answer_count(self):
        """Wehavetoloopsinceourresultisdependentofthesurvey.session_question_idand
        thesurvey.session_start_time.
        Thisfieldiscurrentlyusedtodisplaythecountaboutasinglesurvey,inthe
        contextofsessions,soitshouldnotmattertoomuch."""
        forsurveyinself:
            answer_count=0
            input_line_count=self.env['survey.user_input.line'].read_group(
                [('question_id','=',survey.session_question_id.id),
                 ('survey_id','=',survey.id),
                 ('create_date','>=',survey.session_start_time)],
                ['user_input_id:count_distinct'],
                ['question_id'],
            )
            ifinput_line_count:
                answer_count=input_line_count[0].get('user_input_id',0)

            survey.session_question_answer_count=answer_count

    @api.depends('session_code')
    def_compute_session_link(self):
        forsurveyinself:
            ifsurvey.session_code:
                survey.session_link=werkzeug.urls.url_join(
                    survey.get_base_url(),
                    '/s/%s'%survey.session_code)
            else:
                survey.session_link=werkzeug.urls.url_join(
                    survey.get_base_url(),
                    survey.get_start_url())

    @api.depends('scoring_type','question_and_page_ids.save_as_nickname')
    def_compute_session_show_leaderboard(self):
        forsurveyinself:
            survey.session_show_leaderboard=survey.scoring_type!='no_scoring'and\
                any(question.save_as_nicknameforquestioninsurvey.question_and_page_ids)

    @api.depends('question_and_page_ids.is_conditional')
    def_compute_has_conditional_questions(self):
        forsurveyinself:
            survey.has_conditional_questions=any(question.is_conditionalforquestioninsurvey.question_and_page_ids)

    @api.depends('scoring_type')
    def_compute_certification(self):
        forsurveyinself:
            ifnotsurvey.certificationorsurvey.scoring_type=='no_scoring':
                survey.certification=False

    @api.depends('users_login_required','certification')
    def_compute_certification_give_badge(self):
        forsurveyinself:
            ifnotsurvey.certification_give_badgeor\
               notsurvey.users_login_requiredor\
               notsurvey.certification:
                survey.certification_give_badge=False

    def_read_group_states(self,values,domain,order):
        selection=self.env['survey.survey'].fields_get(allfields=['state'])['state']['selection']
        return[s[0]forsinselection]

    #------------------------------------------------------------
    #CRUD
    #------------------------------------------------------------

    @api.model
    defcreate(self,vals):
        survey=super(Survey,self).create(vals)
        ifvals.get('certification_give_badge'):
            survey.sudo()._create_certification_badge_trigger()
        returnsurvey

    defwrite(self,vals):
        result=super(Survey,self).write(vals)
        if'certification_give_badge'invals:
            returnself.sudo()._handle_certification_badges(vals)
        returnresult

    defcopy_data(self,default=None):
        title=_("%s(copy)")%(self.title)
        default=dict(defaultor{},title=title)
        returnsuper(Survey,self).copy_data(default)

    deftoggle_active(self):
        super(Survey,self).toggle_active()
        activated=self.filtered(lambdasurvey:survey.active)
        activated.mapped('certification_badge_id').action_unarchive()
        (self-activated).mapped('certification_badge_id').action_archive()

    #------------------------------------------------------------
    #ANSWERMANAGEMENT
    #------------------------------------------------------------

    def_create_answer(self,user=False,partner=False,email=False,test_entry=False,check_attempts=True,**additional_vals):
        """Mainentrypointtogetatokenbackorcreateanewone.Thismethod
        doescheckforcurrentuseraccessinordertoexplicitelyvalidate
        security.

          :paramuser:targetuseraskingforatoken;itmightbevoidora
                       publicuserinwhichcaseanemailiswelcomed;
          :paramemail:emailofthepersonaskingthetokenisnouserexists;
        """
        self.check_access_rights('read')
        self.check_access_rule('read')

        user_inputs=self.env['survey.user_input']
        forsurveyinself:
            ifpartnerandnotuserandpartner.user_ids:
                user=partner.user_ids[0]

            invite_token=additional_vals.pop('invite_token',False)
            survey._check_answer_creation(user,partner,email,test_entry=test_entry,check_attempts=check_attempts,invite_token=invite_token)
            answer_vals={
                'survey_id':survey.id,
                'test_entry':test_entry,
                'is_session_answer':survey.session_statein['ready','in_progress']
            }
            ifsurvey.session_state=='in_progress':
                #ifthesessionisalreadyinprogress,theanswerskipsthe'new'state
                answer_vals.update({
                    'state':'in_progress',
                    'start_datetime':fields.Datetime.now(),
                })
            ifuserandnotuser._is_public():
                answer_vals['partner_id']=user.partner_id.id
                answer_vals['email']=user.email
                answer_vals['nickname']=user.name
            elifpartner:
                answer_vals['partner_id']=partner.id
                answer_vals['email']=partner.email
                answer_vals['nickname']=partner.name
            else:
                answer_vals['email']=email
                answer_vals['nickname']=email

            ifinvite_token:
                answer_vals['invite_token']=invite_token
            elifsurvey.is_attempts_limitedandsurvey.access_mode!='public':
                #attemptslimited:createanewinvite_token
                #exceptionmadefor'public'access_modesincetheattemptspoolisglobalbecauseanswersare
                #createdeverytimetheuserlandson'/start'
                answer_vals['invite_token']=self.env['survey.user_input']._generate_invite_token()

            answer_vals.update(additional_vals)
            user_inputs+=user_inputs.create(answer_vals)

        forquestioninself.mapped('question_ids').filtered(
                lambdaq:q.question_type=='char_box'and(q.save_as_emailorq.save_as_nickname)):
            foruser_inputinuser_inputs:
                ifquestion.save_as_emailanduser_input.email:
                    user_input.save_lines(question,user_input.email)
                ifquestion.save_as_nicknameanduser_input.nickname:
                    user_input.save_lines(question,user_input.nickname)

        returnuser_inputs

    def_check_answer_creation(self,user,partner,email,test_entry=False,check_attempts=True,invite_token=False):
        """Ensureconditionstocreatenewtokensaremet."""
        self.ensure_one()
        iftest_entry:
            #thecurrentusermusthavetheaccessrightstosurvey
            ifnotuser.has_group('survey.group_survey_user'):
                raiseexceptions.UserError(_('Creatingtesttokenisnotallowedforyou.'))
        else:
            ifnotself.active:
                raiseexceptions.UserError(_('Creatingtokenforarchivedsurveysisnotallowed.'))
            elifself.state=='closed':
                raiseexceptions.UserError(_('Creatingtokenforclosedsurveysisnotallowed.'))
            ifself.access_mode=='authentication':
                #signuppossible->shouldhaveatleastapartnertocreateanaccount
                ifself.users_can_signupandnotuserandnotpartner:
                    raiseexceptions.UserError(_('Creatingtokenforexternalpeopleisnotallowedforsurveysrequestingauthentication.'))
                #nosignuppossible->shouldbeanotpublicuser(employeeorportalusers)
                ifnotself.users_can_signupand(notuseroruser._is_public()):
                    raiseexceptions.UserError(_('Creatingtokenforexternalpeopleisnotallowedforsurveysrequestingauthentication.'))
            ifself.access_mode=='internal'and(notuserornotuser.has_group('base.group_user')):
                raiseexceptions.UserError(_('Creatingtokenforanybodyelsethanemployeesisnotallowedforinternalsurveys.'))
            ifcheck_attemptsandnotself._has_attempts_left(partneror(useranduser.partner_id),email,invite_token):
                raiseexceptions.UserError(_('Noattemptsleft.'))

    def_prepare_user_input_predefined_questions(self):
        """Willgeneratethequestionsforarandomizedsurvey.
        Itusestherandom_questions_countofeverysectionsofthesurveyto
        pickarandomnumberofquestionsandreturnsthemergedrecordset"""
        self.ensure_one()

        questions=self.env['survey.question']

        #Firstappendquestionswithoutpage
        forquestioninself.question_ids:
            ifnotquestion.page_id:
                questions|=question

        #Then,questionsinsections

        forpageinself.page_ids:
            ifself.questions_selection=='all':
                questions|=page.question_ids
            else:
                ifpage.random_questions_count>0andlen(page.question_ids)>page.random_questions_count:
                    questions=questions.concat(*random.sample(page.question_ids,page.random_questions_count))
                else:
                    questions|=page.question_ids

        returnquestions

    def_can_go_back(self,answer,page_or_question):
        """Checkiftheusercangobacktothepreviousquestion/pageforthecurrently
        viewedquestion/page.
        Backbuttonneedstobeconfiguredonsurveyand,dependingonthelayout:
        -In'page_per_section',wecangobackifwe'renotonthefirstpage
        -In'page_per_question',wecangobackif:
          -Itisnotasessionanswer(doesn'tmakesensetogobackinsessioncontext)
          -Wearenotonthefirstquestion
          -ThesurveydoesnothavepagesORthisisnotthefirstpageofthesurvey
            (pagesaredisplayedin'page_per_question'layoutwhentheyhaveadescription,seePR#44271)
        """
        self.ensure_one()

        ifself.users_can_go_backandanswer.state=='in_progress':
            ifself.questions_layout=='page_per_section'andpage_or_question!=self.page_ids[0]:
                returnTrue
            elifself.questions_layout=='page_per_question'and\
                 notanswer.is_session_answerand\
                 page_or_question!=answer.predefined_question_ids[0]\
                 and(notself.page_idsorpage_or_question!=self.page_ids[0]):
                returnTrue

        returnFalse

    def_has_attempts_left(self,partner,email,invite_token):
        self.ensure_one()

        if(self.access_mode!='public'orself.users_login_required)andself.is_attempts_limited:
            returnself._get_number_of_attempts_lefts(partner,email,invite_token)>0

        returnTrue

    def_get_number_of_attempts_lefts(self,partner,email,invite_token):
        """Returnsthenumberofattemptsleft."""
        self.ensure_one()

        domain=[
            ('survey_id','=',self.id),
            ('test_entry','=',False),
            ('state','=','done')
        ]

        ifpartner:
            domain=expression.AND([domain,[('partner_id','=',partner.id)]])
        else:
            domain=expression.AND([domain,[('email','=',email)]])

        ifinvite_token:
            domain=expression.AND([domain,[('invite_token','=',invite_token)]])

        returnself.attempts_limit-self.env['survey.user_input'].search_count(domain)

    #------------------------------------------------------------
    #QUESTIONSMANAGEMENT
    #------------------------------------------------------------

    @api.model
    def_get_pages_or_questions(self,user_input):
        """Returnsthepagesorquestions(dependingonthelayout)thatwillbeshown
        totheusertakingthesurvey.
        In'page_per_question'layout,wealsowanttoshowpagesthathaveadescription."""

        result=self.env['survey.question']
        ifself.questions_layout=='page_per_section':
            result=self.page_ids
        elifself.questions_layout=='page_per_question':
            ifself.questions_selection=='random'andnotself.session_state:
                result=user_input.predefined_question_ids
            else:
                result=self._get_pages_and_questions_to_show()

        returnresult

    def_get_pages_and_questions_to_show(self):
        """
        :return:survey.questionrecordsetexcludinginvalidconditionalquestionsandpageswithoutdescription
        """

        self.ensure_one()
        invalid_questions=self.env['survey.question']
        questions_and_valid_pages=self.question_and_page_ids.filtered(
            lambdaquestion:notquestion.is_pageornotis_html_empty(question.description))
        forquestioninquestions_and_valid_pages.filtered(lambdaq:q.is_conditional).sorted():
            trigger=question.triggering_question_id
            if(triggerininvalid_questions
                    ortrigger.is_page
                    ortrigger.question_typenotin['simple_choice','multiple_choice']
                    ornottrigger.suggested_answer_ids
                    ortrigger.sequence>question.sequence
                    or(trigger.sequence==question.sequenceandtrigger.id>question.id)):
                invalid_questions|=question
        returnquestions_and_valid_pages-invalid_questions

    def_get_next_page_or_question(self,user_input,page_or_question_id,go_back=False):
        """Generalizedlogictoretrievethenextquestionorpagetoshowonthesurvey.
        It'sbasedonthepage_or_question_idparameter,thatisusuallythecurrentlydisplayedquestion/page.

        Thereisaspecialcasewhenthesurveyisconfiguredwithconditionalquestions:
        -for"page_per_question"layout,thenextquestiontodisplaydependsontheselectedanswersand
          thequestions'hierarchy'.
        -for"page_per_section"layout,beforereturningtheresult,wecheckthatitcontainsatleastaquestion
          (allsectionquestionscouldbedisabledbasedonpreviouslyselectedanswers)

        Thewholelogicisinvertedif"go_back"ispassedasTrue.

        Aspageswithdescriptionareconsideredaspotentialquestiontodisplay,weshowthepage
        ifitcontainsatleastoneactivequestionoradescription.

        :paramuser_input:user'sanswers
        :parampage_or_question_id:currentpageorquestionid
        :paramgo_back:reversethelogicandgetthePREVIOUSquestion/page
        :return:nextorpreviousquestion/page
        """

        survey=user_input.survey_id
        pages_or_questions=survey._get_pages_or_questions(user_input)
        Question=self.env['survey.question']

        #GetNext
        ifnotgo_back:
            ifnotpages_or_questions:
                returnQuestion
            #Firstpage
            ifpage_or_question_id==0:
                returnpages_or_questions[0]

        current_page_index=pages_or_questions.ids.index(page_or_question_id)

        #Getpreviousandweareonfirstpage ORGetNextandweareonlastpage
        if(go_backandcurrent_page_index==0)or(notgo_backandcurrent_page_index==len(pages_or_questions)-1):
            returnQuestion

        #ConditionalQuestionsManagement
        triggering_answer_by_question,triggered_questions_by_answer,selected_answers=user_input._get_conditional_values()
        inactive_questions=user_input._get_inactive_conditional_questions()
        ifsurvey.questions_layout=='page_per_question':
            question_candidates=pages_or_questions[0:current_page_index]ifgo_back\
                elsepages_or_questions[current_page_index+1:]
            forquestioninquestion_candidates.sorted(reverse=go_back):
                #pageswithdescriptionarepotentialquestionstodisplay(arepartofquestion_candidates)
                ifquestion.is_page:
                    contains_active_question=any(sub_questionnotininactive_questionsforsub_questioninquestion.question_ids)
                    is_description_section=notquestion.question_idsandnotis_html_empty(question.description)
                    ifcontains_active_questionoris_description_section:
                        returnquestion
                else:
                    triggering_answer=triggering_answer_by_question.get(question)
                    ifnottriggering_answerortriggering_answerinselected_answers:
                        #questionisvisiblebecausenotconditionedorconditionedbyaselectedanswer
                        returnquestion
        elifsurvey.questions_layout=='page_per_section':
            section_candidates=pages_or_questions[0:current_page_index]ifgo_back\
                elsepages_or_questions[current_page_index+1:]
            forsectioninsection_candidates.sorted(reverse=go_back):
                contains_active_question=any(questionnotininactive_questionsforquestioninsection.question_ids)
                is_description_section=notsection.question_idsandnotis_html_empty(section.description)
                ifcontains_active_questionoris_description_section:
                    returnsection
            returnQuestion

    def_is_last_page_or_question(self,user_input,page_or_question):
        """Thismethodchecksifthegivenquestionorpageisthelastone.
        Thisincludesconditionalquestionsconfiguration.Ifthegivenquestionisnormallynotthelastonebut
        everyfollowingquestionsareinactiveduetoconditionalquestionsconfigurations(anduserchoices),
        thegivenquestionwillbethelastone,exceptifthegivenquestionisconditioningatleast
        oneofthefollowingquestions.
        Forsection,wecheckineachfollowingsectionifthereisanactivequestion.
        Ifyes,thegivenpageisnotthelastone.
        """
        pages_or_questions=self._get_pages_or_questions(user_input)
        current_page_index=pages_or_questions.ids.index(page_or_question.id)
        next_page_or_question_candidates=pages_or_questions[current_page_index+1:]
        ifnext_page_or_question_candidates:
            inactive_questions=user_input._get_inactive_conditional_questions()
            triggering_answer_by_question,triggered_questions_by_answer,selected_answers=user_input._get_conditional_values()
            ifself.questions_layout=='page_per_question':
                next_active_question=any(next_questionnotininactive_questionsfornext_questioninnext_page_or_question_candidates)
                is_triggering_question=any(triggering_answerintriggered_questions_by_answer.keys()fortriggering_answerinpage_or_question.suggested_answer_ids)
                returnnot(next_active_questionoris_triggering_question)
            elifself.questions_layout=='page_per_section':
                is_triggering_section=False
                forquestioninpage_or_question.question_ids:
                    ifany(triggering_answerintriggered_questions_by_answer.keys()fortriggering_answerin
                           question.suggested_answer_ids):
                        is_triggering_section=True
                        break
                next_active_question=False
                forsectioninnext_page_or_question_candidates:
                    next_active_question=any(next_questionnotininactive_questionsfornext_questioninsection.question_ids)
                    ifnext_active_question:
                        break
                returnnot(next_active_questionoris_triggering_section)

        returnTrue

    def_get_survey_questions(self,answer=None,page_id=None,question_id=None):
        """Returnsatuplecontaining:thesurveyquestionandthepassedquestion_id/page_id
        basedonthequestion_layoutandthefactthatit'sasessionornot.

        Breakdownofusecases:
        -Wearecurrentlyrunningasession
          Wereturnthecurrentsessionquestionandit'sid
        -Thelayoutispage_per_section
          Wereturnthequestionsforthatpageandthepassedpage_id
        -Thelayoutispage_per_question
          Wereturnthequestionforthepassedquestion_idandthequestion_id
        -Thelayoutisone_page
          WereturnallthequestionsofthesurveyandNone

        Inaddition,wecrossthereturnedquestionswiththeanswer.predefined_question_ids,
        thatallowstohandletherandomizationofquestions."""

        questions,page_or_question_id=None,None

        ifanswerandanswer.is_session_answer:
            returnself.session_question_id,self.session_question_id.id
        ifself.questions_layout=='page_per_section':
            ifnotpage_id:
                raiseValueError("Pageidisneededforquestionlayout'page_per_section'")
            page_id=int(page_id)
            questions=self.env['survey.question'].sudo().search([('survey_id','=',self.id),('page_id','=',page_id)])
            page_or_question_id=page_id
        elifself.questions_layout=='page_per_question':
            ifnotquestion_id:
                raiseValueError("Questionidisneededforquestionlayout'page_per_question'")
            question_id=int(question_id)
            questions=self.env['survey.question'].sudo().browse(question_id)
            page_or_question_id=question_id
        else:
            questions=self.question_ids

        #weneedtheintersectionofthequestionsofthispageANDthequestionspreparedforthatuser_input
        #(becauserandomizedsurveysdonotuseallthequestionsofeverypage)
        ifanswer:
            questions=questions&answer.predefined_question_ids
        returnquestions,page_or_question_id

    #------------------------------------------------------------
    #CONDITIONALQUESTIONSMANAGEMENT
    #------------------------------------------------------------

    def_get_conditional_maps(self):
        triggering_answer_by_question={}
        triggered_questions_by_answer={}
        forquestioninself.question_ids:
            triggering_answer_by_question[question]=question.is_conditionalandquestion.triggering_answer_id

            ifquestion.is_conditional:
                ifquestion.triggering_answer_idintriggered_questions_by_answer:
                    triggered_questions_by_answer[question.triggering_answer_id]|=question
                else:
                    triggered_questions_by_answer[question.triggering_answer_id]=question
        returntriggering_answer_by_question,triggered_questions_by_answer

    #------------------------------------------------------------
    #SESSIONSMANAGEMENT
    #------------------------------------------------------------

    def_session_open(self):
        """Thesessionstartissudo'edtoallowsurveyusertomanagesessionsofsurveys
        theydonotown.

        Weflushafterwritingtomakesureit'supdatedbeforebustakesover."""

        ifself.env.user.has_group('survey.group_survey_user'):
            self.sudo().write({'session_state':'in_progress'})
            self.sudo().flush(['session_state'])

    def_get_session_next_question(self):
        self.ensure_one()

        ifnotself.question_idsornotself.env.user.has_group('survey.group_survey_user'):
            return

        most_voted_answers=self._get_session_most_voted_answers()
        returnself._get_next_page_or_question(
            most_voted_answers,
            self.session_question_id.idifself.session_question_idelse0)

    def_get_session_most_voted_answers(self):
        """Insessionsofsurveythathasconditionalquestions,asthesurveyispassedatthesametimeby
        manyusers,weneedtoextractthemostchosenanswers,todeterminethenextquestionstodisplay."""

        #getuser_inputsfromcurrentsession
        current_user_inputs=self.user_input_ids.filtered(lambdainput:input.create_date>self.session_start_time)
        current_user_input_lines=current_user_inputs.mapped('user_input_line_ids').filtered(lambdaanswer:answer.suggested_answer_id)

        #countthenumberofvoteperanswer
        votes_by_answer=dict.fromkeys(current_user_input_lines.mapped('suggested_answer_id'),0)
        foranswerincurrent_user_input_lines:
            votes_by_answer[answer.suggested_answer_id]+=1

        #extractmostvotedanswerforeachquestion
        most_voted_answer_by_questions=dict.fromkeys(current_user_input_lines.mapped('question_id'))
        forquestioninmost_voted_answer_by_questions.keys():
            foranswerinvotes_by_answer.keys():
                ifanswer.question_id!=question:
                    continue
                most_voted_answer=most_voted_answer_by_questions[question]
                ifnotmost_voted_answerorvotes_by_answer[most_voted_answer]<votes_by_answer[answer]:
                    most_voted_answer_by_questions[question]=answer

        #returnafake'audience'user_input
        fake_user_input=self.env['survey.user_input'].new({
            'survey_id':self.id,
            'predefined_question_ids':[(6,0,self._prepare_user_input_predefined_questions().ids)]
        })

        fake_user_input_lines=self.env['survey.user_input.line']
        forquestion,answerinmost_voted_answer_by_questions.items():
            fake_user_input_lines|=self.env['survey.user_input.line'].new({
                'question_id':question.id,
                'suggested_answer_id':answer.id,
                'survey_id':self.id,
                'user_input_id':fake_user_input.id
            })

        returnfake_user_input

    def_prepare_leaderboard_values(self):
        """"Theleaderboardisdescendingandtakesthetotaloftheattendeepointsminusthe
        currentquestionscore.
        Weneedboththetotalandthecurrentquestionpointstobeabletoshowtheattendees
        leaderboardandshifttheirpositionbasedonthescoretheyhaveonthecurrentquestion.
        Thispreparesastructurecontainingallthenecessarydatafortheanimationsdoneon
        thefrontendside.
        Theleaderboardissortedbasedonattendeesscore*before*thecurrentquestion.
        Thefrontendwillshiftpositionsaroundaccordingly."""

        self.ensure_one()

        leaderboard=self.env['survey.user_input'].search_read([
            ('survey_id','=',self.id),
            ('create_date','>=',self.session_start_time)
        ],[
            'id',
            'nickname',
            'scoring_total',
        ],limit=15,order="scoring_totaldesc")

        ifleaderboardandself.session_state=='in_progress'and\
           any(answer.answer_scoreforanswerinself.session_question_id.suggested_answer_ids):
            question_scores={}
            input_lines=self.env['survey.user_input.line'].search_read(
                    [('user_input_id','in',[score['id']forscoreinleaderboard]),
                        ('question_id','=',self.session_question_id.id)],
                    ['user_input_id','answer_score'])
            forinput_lineininput_lines:
                question_scores[input_line['user_input_id'][0]]=\
                    question_scores.get(input_line['user_input_id'][0],0)+input_line['answer_score']

            score_position=0
            forleaderboard_iteminleaderboard:
                question_score=question_scores.get(leaderboard_item['id'],0)
                leaderboard_item.update({
                    'updated_score':leaderboard_item['scoring_total'],
                    'scoring_total':leaderboard_item['scoring_total']-question_score,
                    'leaderboard_position':score_position,
                    'max_question_score':sum(
                        scoreforscoreinself.session_question_id.suggested_answer_ids.mapped('answer_score')
                        ifscore>0
                    )or1,
                    'question_score':question_score
                })
                score_position+=1
            leaderboard=sorted(
                leaderboard,
                key=lambdascore:score['scoring_total'],
                reverse=True)

        returnleaderboard


    #------------------------------------------------------------
    #ACTIONS
    #------------------------------------------------------------

    defaction_draft(self):
        self.write({'state':'draft'})

    defaction_open(self):
        self.write({'state':'open'})

    defaction_close(self):
        self.write({'state':'closed'})

    defaction_send_survey(self):
        """Openawindowtocomposeanemail,pre-filledwiththesurveymessage"""
        #Ensurethatthissurveyhasatleastonequestion.
        ifnotself.question_ids:
            raiseUserError(_('Youcannotsendaninvitationforasurveythathasnoquestions.'))

        #Ensurethatthissurveyhasatleastonesectionwithquestion(s),ifquestionlayoutis'Onepagepersection'.
        ifself.questions_layout=='page_per_section':
            ifnotself.page_ids:
                raiseUserError(_('Youcannotsendaninvitationfora"Onepagepersection"surveyifthesurveyhasnosections.'))
            ifnotself.page_ids.mapped('question_ids'):
                raiseUserError(_('Youcannotsendaninvitationfora"Onepagepersection"surveyifthesurveyonlycontainsemptysections.'))

        ifself.state=='closed':
            raiseexceptions.UserError(_("Youcannotsendinvitationsforclosedsurveys."))

        template=self.env.ref('survey.mail_template_user_input_invite',raise_if_not_found=False)

        local_context=dict(
            self.env.context,
            default_survey_id=self.id,
            default_use_template=bool(template),
            default_template_id=templateandtemplate.idorFalse,
            notif_layout='mail.mail_notification_light',
        )
        return{
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'survey.invite',
            'target':'new',
            'context':local_context,
        }

    defaction_start_survey(self,answer=None):
        """Openthewebsitepagewiththesurveyform"""
        self.ensure_one()
        url='%s?%s'%(self.get_start_url(),werkzeug.urls.url_encode({'answer_token':answerandanswer.access_tokenorNone}))
        return{
            'type':'ir.actions.act_url',
            'name':"StartSurvey",
            'target':'self',
            'url':url,
        }

    defaction_print_survey(self,answer=None):
        """Openthewebsitepagewiththesurveyprintableview"""
        self.ensure_one()
        url='%s?%s'%(self.get_print_url(),werkzeug.urls.url_encode({'answer_token':answerandanswer.access_tokenorNone}))
        return{
            'type':'ir.actions.act_url',
            'name':"PrintSurvey",
            'target':'self',
            'url':url
        }

    defaction_result_survey(self):
        """Openthewebsitepagewiththesurveyresultsview"""
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'name':"ResultsoftheSurvey",
            'target':'self',
            'url':'/survey/results/%s'%self.id
        }

    defaction_test_survey(self):
        '''Openthewebsitepagewiththesurveyformintotestmode'''
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'name':"TestSurvey",
            'target':'self',
            'url':'/survey/test/%s'%self.access_token,
        }

    defaction_survey_user_input_completed(self):
        action=self.env['ir.actions.act_window']._for_xml_id('survey.action_survey_user_input')
        ctx=dict(self.env.context)
        ctx.update({'search_default_survey_id':self.ids[0],
                    'search_default_completed':1,
                    'search_default_not_test':1})
        action['context']=ctx
        returnaction

    defaction_survey_user_input_certified(self):
        action=self.env['ir.actions.act_window']._for_xml_id('survey.action_survey_user_input')
        ctx=dict(self.env.context)
        ctx.update({'search_default_survey_id':self.ids[0],
                    'search_default_scoring_success':1,
                    'search_default_not_test':1})
        action['context']=ctx
        returnaction

    defaction_survey_user_input(self):
        action=self.env['ir.actions.act_window']._for_xml_id('survey.action_survey_user_input')
        ctx=dict(self.env.context)
        ctx.update({'search_default_survey_id':self.ids[0],
                    'search_default_not_test':1})
        action['context']=ctx
        returnaction

    defaction_survey_preview_certification_template(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'target':'_blank',
            'url':'/survey/%s/get_certification_preview'%(self.id)
        }

    defaction_start_session(self):
        """Setsthenecessaryfieldsforthesessiontotakeplaceandstartsit.
        Thewriteissudo'edbecauseasurveyusercanstartasessionevenifit's
        nothisownsurvey."""

        ifnotself.env.user.has_group('survey.group_survey_user'):
            raiseAccessError(_('Onlysurveyuserscanmanagesessions.'))

        self.ensure_one()
        self.sudo().write({
            'questions_layout':'page_per_question',
            'session_start_time':fields.Datetime.now(),
            'session_question_id':None,
            'session_state':'ready'
        })
        returnself.action_open_session_manager()

    defaction_open_session_manager(self):
        self.ensure_one()

        return{
            'type':'ir.actions.act_url',
            'name':"OpenSessionManager",
            'target':'self',
            'url':'/survey/session/manage/%s'%self.access_token
        }

    defaction_end_session(self):
        """Thewriteissudo'edbecauseasurveyusercanendasessionevenifit's
        nothisownsurvey."""

        ifnotself.env.user.has_group('survey.group_survey_user'):
            raiseAccessError(_('Onlysurveyuserscanmanagesessions.'))

        self.sudo().write({'session_state':False})
        self.user_input_ids.sudo().write({'state':'done'})
        self.env['bus.bus'].sendone(self.access_token,{'type':'end_session'})

    defget_start_url(self):
        return'/survey/start/%s'%self.access_token

    defget_start_short_url(self):
        """Seecontrollermethoddocstringformoredetails."""
        return'/s/%s'%self.access_token[:6]

    defget_print_url(self):
        return'/survey/print/%s'%self.access_token

    #------------------------------------------------------------
    #GRAPH/RESULTS
    #------------------------------------------------------------

    def_prepare_statistics(self,user_input_lines=None):
        ifuser_input_lines:
            user_input_domain=[
                ('survey_id','in',self.ids),
                ('id','in',user_input_lines.mapped('user_input_id').ids)
            ]
        else:
            user_input_domain=[
                ('survey_id','in',self.ids),
                ('state','=','done'),
                ('test_entry','=',False)
            ]
        count_data=self.env['survey.user_input'].sudo().read_group(user_input_domain,['scoring_success','id:count_distinct'],['scoring_success'])

        scoring_success_count=0
        scoring_failed_count=0
        forcount_data_itemincount_data:
            ifcount_data_item['scoring_success']:
                scoring_success_count+=count_data_item['scoring_success_count']
            else:
                scoring_failed_count+=count_data_item['scoring_success_count']

        success_graph=json.dumps([{
            'text':_('Passed'),
            'count':scoring_success_count,
            'color':'#2E7D32'
        },{
            'text':_('Missed'),
            'count':scoring_failed_count,
            'color':'#C62828'
        }])

        total=scoring_success_count+scoring_failed_count
        return{
            'global_success_rate':round((scoring_success_count/total)*100,1)iftotal>0else0,
            'global_success_graph':success_graph
        }

    #------------------------------------------------------------
    #GAMIFICATION/BADGES
    #------------------------------------------------------------

    def_prepare_challenge_category(self):
        return'certification'

    def_create_certification_badge_trigger(self):
        self.ensure_one()
        goal=self.env['gamification.goal.definition'].create({
            'name':self.title,
            'description':_("%scertificationpassed",self.title),
            'domain':"['&',('survey_id','=',%s),('scoring_success','=',True)]"%self.id,
            'computation_mode':'count',
            'display_mode':'boolean',
            'model_id':self.env.ref('survey.model_survey_user_input').id,
            'condition':'higher',
            'batch_mode':True,
            'batch_distinctive_field':self.env.ref('survey.field_survey_user_input__partner_id').id,
            'batch_user_expression':'user.partner_id.id'
        })
        challenge=self.env['gamification.challenge'].create({
            'name':_('%schallengecertification',self.title),
            'reward_id':self.certification_badge_id.id,
            'state':'inprogress',
            'period':'once',
            'challenge_category':self._prepare_challenge_category(),
            'reward_realtime':True,
            'report_message_frequency':'never',
            'user_domain':[('karma','>',0)],
            'visibility_mode':'personal'
        })
        self.env['gamification.challenge.line'].create({
            'definition_id':goal.id,
            'challenge_id':challenge.id,
            'target_goal':1
        })

    def_handle_certification_badges(self,vals):
        ifvals.get('certification_give_badge'):
            #Ifbadgealreadysetonrecords,reactivatetheonesthatarenotactive.
            surveys_with_badge=self.filtered(lambdasurvey:survey.certification_badge_idandnotsurvey.certification_badge_id.active)
            surveys_with_badge.mapped('certification_badge_id').action_unarchive()
            #(re-)createchallengeandgoal
            forsurveyinself:
                survey._create_certification_badge_trigger()
        else:
            #ifbadgewithowner:archivethem,elsedeleteeverything(badge,challenge,goal)
            badges=self.mapped('certification_badge_id')
            challenges_to_delete=self.env['gamification.challenge'].search([('reward_id','in',badges.ids)])
            goals_to_delete=challenges_to_delete.mapped('line_ids').mapped('definition_id')
            badges.action_archive()
            #deleteallchallengesandgoalsbecausenotneededanymore(challengelinesaredeletedincascade)
            challenges_to_delete.unlink()
            goals_to_delete.unlink()
