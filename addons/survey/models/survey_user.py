#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importuuid

fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError
fromflectra.toolsimportfloat_is_zero

_logger=logging.getLogger(__name__)


classSurveyUserInput(models.Model):
    """Metadataforasetofoneuser'sanswerstoaparticularsurvey"""
    _name="survey.user_input"
    _rec_name='survey_id'
    _description='SurveyUserInput'

    #answerdescription
    survey_id=fields.Many2one('survey.survey',string='Survey',required=True,readonly=True,ondelete='cascade')
    scoring_type=fields.Selection(string="Scoring",related="survey_id.scoring_type")
    start_datetime=fields.Datetime('Startdateandtime',readonly=True)
    deadline=fields.Datetime('Deadline',help="Datetimeuntilcustomercanopenthesurveyandsubmitanswers")
    state=fields.Selection([
        ('new','Notstartedyet'),
        ('in_progress','InProgress'),
        ('done','Completed')],string='Status',default='new',readonly=True)
    test_entry=fields.Boolean(readonly=True)
    last_displayed_page_id=fields.Many2one('survey.question',string='Lastdisplayedquestion/page')
    #attemptsmanagement
    is_attempts_limited=fields.Boolean("Limitednumberofattempts",related='survey_id.is_attempts_limited')
    attempts_limit=fields.Integer("Numberofattempts",related='survey_id.attempts_limit')
    attempts_number=fields.Integer("Attemptn°",compute='_compute_attempts_number')
    survey_time_limit_reached=fields.Boolean("SurveyTimeLimitReached",compute='_compute_survey_time_limit_reached')
    #identification/access
    access_token=fields.Char('Identificationtoken',default=lambdaself:str(uuid.uuid4()),readonly=True,required=True,copy=False)
    invite_token=fields.Char('Invitetoken',readonly=True,copy=False) #nouniqueconstraint,asitidentifiesapoolofattempts
    partner_id=fields.Many2one('res.partner',string='Partner',readonly=True)
    email=fields.Char('Email',readonly=True)
    nickname=fields.Char('Nickname',help="Attendeenickname,mainlyusedtoidentifyhiminthesurveysessionleaderboard.")
    #questions/answers
    user_input_line_ids=fields.One2many('survey.user_input.line','user_input_id',string='Answers',copy=True)
    predefined_question_ids=fields.Many2many('survey.question',string='PredefinedQuestions',readonly=True)
    scoring_percentage=fields.Float("Score(%)",compute="_compute_scoring_values",store=True,compute_sudo=True) #storedforperfreasons
    scoring_total=fields.Float("TotalScore",compute="_compute_scoring_values",store=True,compute_sudo=True) #storedforperfreasons
    scoring_success=fields.Boolean('QuizzPassed',compute='_compute_scoring_success',store=True,compute_sudo=True) #storedforperfreasons
    #livesessions
    is_session_answer=fields.Boolean('IsinaSession',help="Isthatuserinputpartofasurveysessionornot.")
    question_time_limit_reached=fields.Boolean("QuestionTimeLimitReached",compute='_compute_question_time_limit_reached')

    _sql_constraints=[
        ('unique_token','UNIQUE(access_token)','Anaccesstokenmustbeunique!'),
    ]

    @api.depends('user_input_line_ids.answer_score','user_input_line_ids.question_id','predefined_question_ids.answer_score')
    def_compute_scoring_values(self):
        foruser_inputinself:
            #sum(multi-choicequestionscores)+sum(simpleanswer_typescores)
            total_possible_score=0
            forquestioninuser_input.predefined_question_ids:
                ifquestion.question_type=='simple_choice':
                    total_possible_score+=max([scoreforscoreinquestion.mapped('suggested_answer_ids.answer_score')ifscore>0],default=0)
                elifquestion.question_type=='multiple_choice':
                    total_possible_score+=sum(scoreforscoreinquestion.mapped('suggested_answer_ids.answer_score')ifscore>0)
                elifquestion.is_scored_question:
                    total_possible_score+=question.answer_score

            iftotal_possible_score==0:
                user_input.scoring_percentage=0
                user_input.scoring_total=0
            else:
                score_total=sum(user_input.user_input_line_ids.mapped('answer_score'))
                user_input.scoring_total=score_total
                score_percentage=(score_total/total_possible_score)*100
                user_input.scoring_percentage=round(score_percentage,2)ifscore_percentage>0else0

    @api.depends('scoring_percentage','survey_id')
    def_compute_scoring_success(self):
        foruser_inputinself:
            user_input.scoring_success=user_input.scoring_percentage>=user_input.survey_id.scoring_success_min

    @api.depends(
        'start_datetime',
        'survey_id.is_time_limited',
        'survey_id.time_limit')
    def_compute_survey_time_limit_reached(self):
        """Checksthattheuser_inputisnotexceedingthesurvey'stimelimit."""
        foruser_inputinself:
            ifnotuser_input.is_session_answeranduser_input.start_datetime:
                start_time=user_input.start_datetime
                time_limit=user_input.survey_id.time_limit
                user_input.survey_time_limit_reached=user_input.survey_id.is_time_limitedand\
                    fields.Datetime.now()>=start_time+relativedelta(minutes=time_limit)
            else:
                user_input.survey_time_limit_reached=False

    @api.depends(
        'survey_id.session_question_id.time_limit',
        'survey_id.session_question_id.is_time_limited',
        'survey_id.session_question_start_time')
    def_compute_question_time_limit_reached(self):
        """Checksthattheuser_inputisnotexceedingthequestion'stimelimit.
        Onlyusedinthecontextofsurveysessions."""
        foruser_inputinself:
            ifuser_input.is_session_answeranduser_input.survey_id.session_question_start_time:
                start_time=user_input.survey_id.session_question_start_time
                time_limit=user_input.survey_id.session_question_id.time_limit
                user_input.question_time_limit_reached=user_input.survey_id.session_question_id.is_time_limitedand\
                    fields.Datetime.now()>=start_time+relativedelta(seconds=time_limit)
            else:
                user_input.question_time_limit_reached=False

    @api.depends('state','test_entry','survey_id.is_attempts_limited','partner_id','email','invite_token')
    def_compute_attempts_number(self):
        attempts_to_compute=self.filtered(
            lambdauser_input:user_input.state=='done'andnotuser_input.test_entryanduser_input.survey_id.is_attempts_limited
        )

        foruser_inputin(self-attempts_to_compute):
            user_input.attempts_number=1

        ifattempts_to_compute:
            self.env.cr.execute("""SELECTuser_input.id,(COUNT(previous_user_input.id)+1)ASattempts_number
                FROMsurvey_user_inputuser_input
                LEFTOUTERJOINsurvey_user_inputprevious_user_input
                ONuser_input.survey_id=previous_user_input.survey_id
                ANDprevious_user_input.state='done'
                ANDprevious_user_input.test_entryISNOTTRUE
                ANDprevious_user_input.id<user_input.id
                AND(user_input.invite_tokenISNULLORuser_input.invite_token=previous_user_input.invite_token)
                AND(user_input.partner_id=previous_user_input.partner_idORuser_input.email=previous_user_input.email)
                WHEREuser_input.idIN%s
                GROUPBYuser_input.id;
            """,(tuple(attempts_to_compute.ids),))

            attempts_count_results=self.env.cr.dictfetchall()

            foruser_inputinattempts_to_compute:
                attempts_number=1
                forattempts_count_resultinattempts_count_results:
                    ifattempts_count_result['id']==user_input.id:
                        attempts_number=attempts_count_result['attempts_number']
                        break

                user_input.attempts_number=attempts_number

    @api.model_create_multi
    defcreate(self,vals_list):
        forvalsinvals_list:
            if'predefined_question_ids'notinvals:
                suvey_id=vals.get('survey_id',self.env.context.get('default_survey_id'))
                survey=self.env['survey.survey'].browse(suvey_id)
                vals['predefined_question_ids']=[(6,0,survey._prepare_user_input_predefined_questions().ids)]
        returnsuper(SurveyUserInput,self).create(vals_list)

    #------------------------------------------------------------
    #ACTIONS/BUSINESS
    #------------------------------------------------------------

    defaction_resend(self):
        partners=self.env['res.partner']
        emails=[]
        foruser_answerinself:
            ifuser_answer.partner_id:
                partners|=user_answer.partner_id
            elifuser_answer.email:
                emails.append(user_answer.email)

        returnself.survey_id.with_context(
            default_existing_mode='resend',
            default_partner_ids=partners.ids,
            default_emails=','.join(emails)
        ).action_send_survey()

    defaction_print_answers(self):
        """Openthewebsitepagewiththesurveyform"""
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'name':"ViewAnswers",
            'target':'self',
            'url':'/survey/print/%s?answer_token=%s'%(self.survey_id.access_token,self.access_token)
        }

    @api.model
    def_generate_invite_token(self):
        returnstr(uuid.uuid4())

    def_mark_in_progress(self):
        """marksthestateas'in_progress'andupdatesthestart_datetimeaccordingly."""
        self.write({
            'start_datetime':fields.Datetime.now(),
            'state':'in_progress'
        })

    def_mark_done(self):
        """Thismethodwill:
        1.markthestateas'done'
        2.sendthecertificationemailwithattacheddocumentif
        -Thesurveyisacertification
        -Ithasacertification_mail_template_idset
        -Theusersucceededthetest
        WillalsorunchallengeCrontogivethecertificationbadgeifany."""
        self.write({'state':'done'})
        Challenge=self.env['gamification.challenge'].sudo()
        badge_ids=[]
        foruser_inputinself:
            ifuser_input.survey_id.certificationanduser_input.scoring_success:
                ifuser_input.survey_id.certification_mail_template_idandnotuser_input.test_entry:
                    user_input.survey_id.certification_mail_template_id.send_mail(user_input.id,notif_layout="mail.mail_notification_light")
                ifuser_input.survey_id.certification_give_badge:
                    badge_ids.append(user_input.survey_id.certification_badge_id.id)

            #Updatepredefined_question_idtoremoveinactivequestions
            user_input.predefined_question_ids-=user_input._get_inactive_conditional_questions()

        ifbadge_ids:
            challenges=Challenge.search([('reward_id','in',badge_ids)])
            ifchallenges:
                Challenge._cron_update(ids=challenges.ids,commit=False)

    defget_start_url(self):
        self.ensure_one()
        return'%s?answer_token=%s'%(self.survey_id.get_start_url(),self.access_token)

    defget_print_url(self):
        self.ensure_one()
        return'%s?answer_token=%s'%(self.survey_id.get_print_url(),self.access_token)

    #------------------------------------------------------------
    #CREATE/UPDATELINESFROMSURVEYFRONTENDINPUT
    #------------------------------------------------------------

    defsave_lines(self,question,answer,comment=None):
        """Saveanswerstoquestions,dependingonquestiontype

            Ifanansweralreadyexistsforquestionanduser_input_id,itwillbe
            overwritten(ordeletedfor'choice'questions)(inordertomaintaindataconsistency).
        """
        old_answers=self.env['survey.user_input.line'].search([
            ('user_input_id','=',self.id),
            ('question_id','=',question.id)
        ])

        ifquestion.question_typein['char_box','text_box','numerical_box','date','datetime']:
            self._save_line_simple_answer(question,old_answers,answer)
            ifquestion.save_as_emailandanswer:
                self.write({'email':answer})
            ifquestion.save_as_nicknameandanswer:
                self.write({'nickname':answer})

        elifquestion.question_typein['simple_choice','multiple_choice']:
            self._save_line_choice(question,old_answers,answer,comment)
        elifquestion.question_type=='matrix':
            self._save_line_matrix(question,old_answers,answer,comment)
        else:
            raiseAttributeError(question.question_type+":Thistypeofquestionhasnosavingfunction")

    def_save_line_simple_answer(self,question,old_answers,answer):
        vals=self._get_line_answer_values(question,answer,question.question_type)
        ifold_answers:
            old_answers.write(vals)
            returnold_answers
        else:
            returnself.env['survey.user_input.line'].create(vals)

    def_save_line_choice(self,question,old_answers,answers,comment):
        ifnot(isinstance(answers,list)):
            answers=[answers]

        ifnotanswers:
            #addaFalseanswertoforcesavingaskippedline
            #thiswillmakethisquestioncorrectlyconsideredasskippedinstatistics
            answers=[False]

        vals_list=[]

        ifquestion.question_type=='simple_choice':
            ifnotquestion.comment_count_as_answerornotquestion.comments_allowedornotcomment:
                vals_list=[self._get_line_answer_values(question,answer,'suggestion')foranswerinanswers]
        elifquestion.question_type=='multiple_choice':
            vals_list=[self._get_line_answer_values(question,answer,'suggestion')foranswerinanswers]

        ifcomment:
            vals_list.append(self._get_line_comment_values(question,comment))

        old_answers.sudo().unlink()
        returnself.env['survey.user_input.line'].create(vals_list)

    def_save_line_matrix(self,question,old_answers,answers,comment):
        vals_list=[]

        ifnotanswersandquestion.matrix_row_ids:
            #addaFalseanswertoforcesavingaskippedline
            #thiswillmakethisquestioncorrectlyconsideredasskippedinstatistics
            answers={question.matrix_row_ids[0].id:[False]}

        ifanswers:
            forrow_key,row_answerinanswers.items():
                foranswerinrow_answer:
                    vals=self._get_line_answer_values(question,answer,'suggestion')
                    vals['matrix_row_id']=int(row_key)
                    vals_list.append(vals.copy())

        ifcomment:
            vals_list.append(self._get_line_comment_values(question,comment))

        old_answers.sudo().unlink()
        returnself.env['survey.user_input.line'].create(vals_list)

    def_get_line_answer_values(self,question,answer,answer_type):
        vals={
            'user_input_id':self.id,
            'question_id':question.id,
            'skipped':False,
            'answer_type':answer_type,
        }
        ifnotansweror(isinstance(answer,str)andnotanswer.strip()):
            vals.update(answer_type=None,skipped=True)
            returnvals

        ifanswer_type=='suggestion':
            vals['suggested_answer_id']=int(answer)
        elifanswer_type=='numerical_box':
            vals['value_numerical_box']=float(answer)
        else:
            vals['value_%s'%answer_type]=answer
        returnvals

    def_get_line_comment_values(self,question,comment):
        return{
            'user_input_id':self.id,
            'question_id':question.id,
            'skipped':False,
            'answer_type':'char_box',
            'value_char_box':comment,
        }

    #------------------------------------------------------------
    #STATISTICS/RESULTS
    #------------------------------------------------------------

    def_prepare_statistics(self):
        res=dict((user_input,{
            'correct':0,
            'incorrect':0,
            'partial':0,
            'skipped':0,
        })foruser_inputinself)

        scored_questions=self.mapped('predefined_question_ids').filtered(lambdaquestion:question.is_scored_question)

        forquestioninscored_questions:
            ifquestion.question_typein['simple_choice','multiple_choice']:
                question_correct_suggested_answers=question.suggested_answer_ids.filtered(lambdaanswer:answer.is_correct)
            foruser_inputinself:
                user_input_lines=user_input.user_input_line_ids.filtered(lambdaline:line.question_id==question)
                ifquestion.question_typein['simple_choice','multiple_choice']:
                    res[user_input][self._choice_question_answer_result(user_input_lines,question_correct_suggested_answers)]+=1
                else:
                    res[user_input][self._simple_question_answer_result(user_input_lines)]+=1

        return[[
            {'text':_("Correct"),'count':res[user_input]['correct']},
            {'text':_("Partially"),'count':res[user_input]['partial']},
            {'text':_("Incorrect"),'count':res[user_input]['incorrect']},
            {'text':_("Unanswered"),'count':res[user_input]['skipped']}
        ]foruser_inputinself]

    def_choice_question_answer_result(self,user_input_lines,question_correct_suggested_answers):
        correct_user_input_lines=user_input_lines.filtered(lambdaline:line.answer_is_correctandnotline.skipped).mapped('suggested_answer_id')
        incorrect_user_input_lines=user_input_lines.filtered(lambdaline:notline.answer_is_correctandnotline.skipped)
        ifquestion_correct_suggested_answersandcorrect_user_input_lines==question_correct_suggested_answers:
            return'correct'
        elifcorrect_user_input_linesandcorrect_user_input_lines<question_correct_suggested_answers:
            return'partial'
        elifnotcorrect_user_input_linesandincorrect_user_input_lines:
            return'incorrect'
        else:
            return'skipped'

    def_simple_question_answer_result(self,user_input_line):
        ifuser_input_line.skipped:
            return'skipped'
        elifuser_input_line.answer_is_correct:
            return'correct'
        else:
            return'incorrect'

    #------------------------------------------------------------
    #ConditionalQuestionsManagement
    #------------------------------------------------------------

    def_get_conditional_values(self):
        """Forsurveycontainingconditionalquestions,weneedatriggered_questions_by_answermapthatcontains
                {key:answer,value:thequestionthattheanswertriggers,ifselected},
         Theideaistobeabletoverify,oneveryanswercheck,ifthisansweristriggeringthedisplay
         ofanotherquestion.
         Ifanswerisnotintheconditionalmap:
            -nothinghappens.
         Iftheanswerisintheconditionalmap:
            -IfweareinONEPAGEsurvey:(handledatCLIENTside)
                ->displayimmediatelythedependingquestion
            -IfweareinPAGEPERSECTION:(handledatCLIENTside)
                -Ifrelatedquestionisonthesamepage:
                    ->displayimmediatelythedependingquestion
                -Iftherelatedquestionisnotonthesamepage:
                    ->keeptheanswersinmemoryandcheckatnextpageloadifthedependingquestionisinthereand
                       displayit,ifso.
            -IfweareinPAGEPERQUESTION:(handledatSERVERside)
                ->Duringsubmit,determinewhichisthenextquestiontodisplaygettingthenextquestion
                   thatisthenextinsequenceandthatiseithernottriggeredbyanotherquestion'sanswer,orthat
                   istriggeredbyanalreadyselectedanswer.
         Todoallthis,weneedtoreturn:
            -listofallselectedanswers:[answer_id1,answer_id2,...](forsurveyreloading,otherwise,thislistis
              updatedatclientside)
            -triggered_questions_by_answer:dict->foragivenanswer,listofquestionstriggeredbythisanswer;
                Usedmainlyfordynamicshow/hidebehaviouratclientside
            -triggering_answer_by_question:dict->foragivenquestion,theanswerthattriggersit
                Usedmainlytoeasetemplaterendering
        """
        triggering_answer_by_question,triggered_questions_by_answer={},{}
        #Ignoreconditionalconfigurationifrandomisedquestionsselection
        ifself.survey_id.questions_selection!='random':
            triggering_answer_by_question,triggered_questions_by_answer=self.survey_id._get_conditional_maps()
        selected_answers=self._get_selected_suggested_answers()

        returntriggering_answer_by_question,triggered_questions_by_answer,selected_answers

    def_get_selected_suggested_answers(self):
        """
        Fornow,onlysimpleandmultiplechoicesquestiontypearehandledbytheconditionalquestionsfeature.
        Mappingallthesuggestedanswersselectedbytheuserwillalsoincludeanswersfrommatrixquestiontype,
        Thoseoneswon'tbeused.
        Maybesomeday,conditionalquestionsfeaturewillbeextendedtoworkwithmatrixquestion.
        :return:allthesuggestedanswerselectedbytheuser.
        """
        returnself.mapped('user_input_line_ids.suggested_answer_id')

    def_clear_inactive_conditional_answers(self):
        """
        Cleaneventualanswersonconditionalquestionsthatshouldnothavebeendisplayedtouser.
        Thismethodisusedmainlyforpageperquestionsurvey,asimilarmethoddoesthesametreatment
        atclientsidefortheothersurveylayouts.
        E.g.:ifdependinganswerwasuncheckafteransweringconditionalquestion,weneedtoclearanswers
              ofthatconditionalquestion,fortworeasons:
              -ensurecorrectscoring
              -iftheselectedanswertriggersanotherquestionlaterinthesurvey,iftheanswerisnotcleared,
                aquestionthatshouldnotbedisplayedtotheuserwillbe.
        
        TODODBE:Maybethiscanbetheonlycleaningmethod,evenforsection_per_pageorone_pagewhere
        conditionalquestionsare,fornow,clearedinJSdirectly.Butthiscanbeannoyingifusertypedalong
        answer,changedhisminduncheckingdependinganswerandchangedagainhismindbyrecheckingthedepending
        answer->Fornow,thelonganswerwillbelost.Ifweusethisasthemastercleaningmethod,
        longanswerwillbeclearedonlyduringsubmit.
        """
        inactive_questions=self._get_inactive_conditional_questions()

        #deleteuser.input.lineonquestionthatshouldnotbeanswered.
        answers_to_delete=self.user_input_line_ids.filtered(lambdaanswer:answer.question_idininactive_questions)
        answers_to_delete.unlink()

    def_get_inactive_conditional_questions(self):
        triggering_answer_by_question,triggered_questions_by_answer,selected_answers=self._get_conditional_values()

        #getquestionsthatshouldnotbeanswered
        inactive_questions=self.env['survey.question']
        foranswerintriggered_questions_by_answer.keys():
            ifanswernotinselected_answers:
                forquestionintriggered_questions_by_answer[answer]:
                    inactive_questions|=question
        returninactive_questions

    def_get_print_questions(self):
        """Getthequestionstodisplay:theonesthatshouldhavebeenanswered=activequestions
            Incaseofsession,activequestionsarebasedonmostvotedanswers
        :return:activesurvey.questionbrowserecords
        """
        survey=self.survey_id
        ifself.is_session_answer:
            most_voted_answers=survey._get_session_most_voted_answers()
            inactive_questions=most_voted_answers._get_inactive_conditional_questions()
        else:
            inactive_questions=self._get_inactive_conditional_questions()
        returnsurvey.question_ids-inactive_questions


classSurveyUserInputLine(models.Model):
    _name='survey.user_input.line'
    _description='SurveyUserInputLine'
    _rec_name='user_input_id'
    _order='question_sequence,id'

    #surveydata
    user_input_id=fields.Many2one('survey.user_input',string='UserInput',ondelete='cascade',required=True)
    survey_id=fields.Many2one(related='user_input_id.survey_id',string='Survey',store=True,readonly=False)
    question_id=fields.Many2one('survey.question',string='Question',ondelete='cascade',required=True)
    page_id=fields.Many2one(related='question_id.page_id',string="Section",readonly=False)
    question_sequence=fields.Integer('Sequence',related='question_id.sequence',store=True)
    #answer
    skipped=fields.Boolean('Skipped')
    answer_type=fields.Selection([
        ('text_box','FreeText'),
        ('char_box','Text'),
        ('numerical_box','Number'),
        ('date','Date'),
        ('datetime','Datetime'),
        ('suggestion','Suggestion')],string='AnswerType')
    value_char_box=fields.Char('Textanswer')
    value_numerical_box=fields.Float('Numericalanswer')
    value_date=fields.Date('Dateanswer')
    value_datetime=fields.Datetime('Datetimeanswer')
    value_text_box=fields.Text('FreeTextanswer')
    suggested_answer_id=fields.Many2one('survey.question.answer',string="Suggestedanswer")
    matrix_row_id=fields.Many2one('survey.question.answer',string="Rowanswer")
    #scoring
    answer_score=fields.Float('Score')
    answer_is_correct=fields.Boolean('Correct')

    @api.constrains('skipped','answer_type')
    def_check_answer_type_skipped(self):
        forlineinself:
            if(line.skipped==bool(line.answer_type)):
                raiseValidationError(_('Aquestioncaneitherbeskippedoranswered,notboth.'))

            #allow0fornumericalbox
            ifline.answer_type=='numerical_box'andfloat_is_zero(line['value_numerical_box'],precision_digits=6):
                continue
            ifline.answer_type=='suggestion':
                field_name='suggested_answer_id'
            elifline.answer_type:
                field_name='value_%s'%line.answer_type
            else: #skipped
                field_name=False

            iffield_nameandnotline[field_name]:
                raiseValidationError(_('Theanswermustbeintherighttype'))

    @api.model_create_multi
    defcreate(self,vals_list):
        forvalsinvals_list:
            ifnotvals.get('answer_score'):
                score_vals=self._get_answer_score_values(vals)
                vals.update(score_vals)
        returnsuper(SurveyUserInputLine,self).create(vals_list)

    defwrite(self,vals):
        res=True
        forlineinself:
            vals_copy={**vals}
            getter_params={
                'user_input_id':line.user_input_id.id,
                'answer_type':line.answer_type,
                'question_id':line.question_id.id,
                **vals_copy
            }
            ifnotvals_copy.get('answer_score'):
                score_vals=self._get_answer_score_values(getter_params,compute_speed_score=False)
                vals_copy.update(score_vals)
            res=super(SurveyUserInputLine,line).write(vals_copy)andres
        returnres

    @api.model
    def_get_answer_score_values(self,vals,compute_speed_score=True):
        """Getvaluesfor:answer_is_correctandassociatedanswer_score.

        Requiresvalstocontain'answer_type','question_id',and'user_input_id'.
        Dependingon'answer_type'additionalvalueof'suggested_answer_id'mayalsobe
        required.

        Calculateswhetherananswer_is_correctanditsscorebasedon'answer_type'and
        correspondingquestion.Handleschoice(answer_type=='suggestion')questions
        separatelyfromotherquestiontypes.Eachselectedchoiceanswerishandledasan
        individualanswer.

        Ifscoredependsonthespeedoftheanswer,itisadjustedasfollows:
         -Iftheuseranswersinlessthan2seconds,theyreceive100%ofthepossiblepoints.
         -Ifuseranswersafterthat,theyreceive50%ofthepossiblepoints+theremaining
            50%scaledbythetimelimitandtimetakentoanswer[i.e.aminimumof50%ofthe
            possiblepointsisgiventoallcorrectanswers]

        Exampleofreturnedvalues:
            *{'answer_is_correct':False,'answer_score':0}(default)
            *{'answer_is_correct':True,'answer_score':2.0}
        """
        user_input_id=vals.get('user_input_id')
        answer_type=vals.get('answer_type')
        question_id=vals.get('question_id')
        ifnotquestion_id:
            raiseValueError(_('Computingscorerequiresaquestioninarguments.'))
        question=self.env['survey.question'].browse(int(question_id))

        #defaultandnon-scoredquestions
        answer_is_correct=False
        answer_score=0

        #recordselectedsuggestedchoiceanswer_score(canbe:pos,neg,or0)
        ifquestion.question_typein['simple_choice','multiple_choice']:
            ifanswer_type=='suggestion':
                suggested_answer_id=vals.get('suggested_answer_id')
                ifsuggested_answer_id:
                    question_answer=self.env['survey.question.answer'].browse(int(suggested_answer_id))
                    answer_score=question_answer.answer_score
                    answer_is_correct=question_answer.is_correct
        #forallotherscoredquestioncases,recordquestionanswer_score(canbe:posor0)
        elifquestion.is_scored_question:
            answer=vals.get('value_%s'%answer_type)
            ifanswer_type=='numerical_box':
                answer=float(answer)
            elifanswer_type=='date':
                answer=fields.Date.from_string(answer)
            elifanswer_type=='datetime':
                answer=fields.Datetime.from_string(answer)
            ifanswerandanswer==question['answer_%s'%answer_type]:
                answer_is_correct=True
                answer_score=question.answer_score

        ifcompute_speed_scoreandanswer_score>0:
            user_input=self.env['survey.user_input'].browse(user_input_id)
            session_speed_rating=user_input.exists()anduser_input.is_session_answeranduser_input.survey_id.session_speed_rating
            ifsession_speed_rating:
                max_score_delay=2
                time_limit=question.time_limit
                now=fields.Datetime.now()
                seconds_to_answer=(now-user_input.survey_id.session_question_start_time).total_seconds()
                question_remaining_time=time_limit-seconds_to_answer
                #ifansweredwithinthemax_score_delay=>leavescoreasis
                ifquestion_remaining_time<0: #ifnotimeleft
                    answer_score/=2
                elifseconds_to_answer>max_score_delay:
                    time_limit-=max_score_delay #weremovethemax_score_delaytohaveallpossiblevalues
                    score_proportion=(time_limit-seconds_to_answer)/time_limit
                    answer_score=(answer_score/2)*(1+score_proportion)

        return{
            'answer_is_correct':answer_is_correct,
            'answer_score':answer_score
        }
