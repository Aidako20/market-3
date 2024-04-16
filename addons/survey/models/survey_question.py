#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importcollections
importjson
importitertools
importoperator

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportValidationError


classSurveyQuestion(models.Model):
    """Questionsthatwillbeaskedinasurvey.

        Eachquestioncanhaveoneofmoresuggestedanswers(eg.incaseof
        multi-answercheckboxes,radiobuttons...).

        Technicalnote:

        survey.questionisalsothemodelusedforthesurvey'spages(withthe"is_page"fieldsettoTrue).

        Apagecorrespondstoa"section"intheinterface,andthefactthatitseparatesthesurveyin
        actualpagesintheinterfacedependsonthe"questions_layout"parameteronthesurvey.surveymodel.
        Pagesarealsousedwhenrandomizingquestions.Therandomizationcanhappenwithina"page".

        Usingthesamemodelforquestionsandpagesallowstoputallthepagesandquestionstogetherinao2mfield
        (seesurvey.survey.question_and_page_ids)ontheviewsideandeasilyreorganizeyoursurveybydraggingthe
        itemsaround.

        Italsoremovesonlevelofencodingbydirectlyhaving'Addapage'and'Addaquestion'
        linksonthetreeviewofquestions,enablingafasterencoding.

        However,thishasthedownsideofmakingthecodereadingalittlebitmorecomplicated.
        Effortsweremadeatthemodelleveltocreatecomputedfieldssothattheuseofthesemodels
        stillseemssomewhatlogical.Thatmeans:
        -Asurveystillhas"page_ids"(question_and_page_idsfilteredonis_page=True)
        -These"page_ids"stillhavequestion_ids(questionslocatedbetweenthispageandthenext)
        -These"question_ids"stillhavea"page_id"

        Thatmakestheuseanddisplayoftheseinformationatviewandcontrollerlevelseasiertounderstand.
    """
    _name='survey.question'
    _description='SurveyQuestion'
    _rec_name='title'
    _order='sequence,id'

    @api.model
    defdefault_get(self,fields):
        defaults=super(SurveyQuestion,self).default_get(fields)
        if(notfieldsor'question_type'infields):
            defaults['question_type']=Falseifdefaults.get('is_page')==Trueelse'text_box'
        returndefaults

    #questiongenericdata
    title=fields.Char('Title',required=True,translate=True)
    description=fields.Html(
        'Description',translate=True,sanitize=False, #TDETODO:sanitizebutfindawaytokeepyoutubeiframemediastuff
        help="Usethisfieldtoaddadditionalexplanationsaboutyourquestionortoillustrateitwithpicturesoravideo")
    survey_id=fields.Many2one('survey.survey',string='Survey',ondelete='cascade')
    scoring_type=fields.Selection(related='survey_id.scoring_type',string='ScoringType',readonly=True)
    sequence=fields.Integer('Sequence',default=10)
    #pagespecific
    is_page=fields.Boolean('Isapage?')
    question_ids=fields.One2many('survey.question',string='Questions',compute="_compute_question_ids")
    questions_selection=fields.Selection(
        related='survey_id.questions_selection',readonly=True,
        help="Ifrandomizedisselected,addthenumberofrandomquestionsnexttothesection.")
    random_questions_count=fields.Integer(
        'Randomquestionscount',default=1,
        help="UsedonrandomizedsectionstotakeXrandomquestionsfromallthequestionsofthatsection.")
    #questionspecific
    page_id=fields.Many2one('survey.question',string='Page',compute="_compute_page_id",store=True)
    question_type=fields.Selection([
        ('text_box','MultipleLinesTextBox'),
        ('char_box','SingleLineTextBox'),
        ('numerical_box','NumericalValue'),
        ('date','Date'),
        ('datetime','Datetime'),
        ('simple_choice','Multiplechoice:onlyoneanswer'),
        ('multiple_choice','Multiplechoice:multipleanswersallowed'),
        ('matrix','Matrix')],string='QuestionType',
        compute='_compute_question_type',readonly=False,store=True)
    is_scored_question=fields.Boolean(
        'Scored',compute='_compute_is_scored_question',
        readonly=False,store=True,copy=True,
        help="Includethisquestionaspartofquizscoring.Requiresananswerandanswerscoretobetakenintoaccount.")
    #--scoreable/answerablesimpleanswer_types:numerical_box/date/datetime
    answer_numerical_box=fields.Float('Correctnumericalanswer',help="Correctnumberanswerforthisquestion.")
    answer_date=fields.Date('Correctdateanswer',help="Correctdateanswerforthisquestion.")
    answer_datetime=fields.Datetime('Correctdatetimeanswer',help="Correctdateandtimeanswerforthisquestion.")
    answer_score=fields.Float('Score',help="Scorevalueforacorrectanswertothisquestion.")
    #--char_box
    save_as_email=fields.Boolean(
        "Saveasuseremail",compute='_compute_save_as_email',readonly=False,store=True,copy=True,
        help="Ifchecked,thisoptionwillsavetheuser'sanswerasitsemailaddress.")
    save_as_nickname=fields.Boolean(
        "Saveasusernickname",compute='_compute_save_as_nickname',readonly=False,store=True,copy=True,
        help="Ifchecked,thisoptionwillsavetheuser'sanswerasitsnickname.")
    #--simplechoice/multiplechoice/matrix
    suggested_answer_ids=fields.One2many(
        'survey.question.answer','question_id',string='Typesofanswers',copy=True,
        help='Labelsusedforproposedchoices:simplechoice,multiplechoiceandcolumnsofmatrix')
    allow_value_image=fields.Boolean('Imagesonanswers',help='Displayimagesinadditiontoanswerlabel.Validonlyforsimple/multiplechoicequestions.')
    #--matrix
    matrix_subtype=fields.Selection([
        ('simple','Onechoiceperrow'),
        ('multiple','Multiplechoicesperrow')],string='MatrixType',default='simple')
    matrix_row_ids=fields.One2many(
        'survey.question.answer','matrix_question_id',string='MatrixRows',copy=True,
        help='Labelsusedforproposedchoices:rowsofmatrix')
    #--display&timingoptions
    column_nb=fields.Selection([
        ('12','1'),('6','2'),('4','3'),('3','4'),('2','6')],
        string='Numberofcolumns',default='12',
        help='Theseoptionsrefertocol-xx-[12|6|4|3|2]classesinBootstrapfordropdown-basedsimpleandmultiplechoicequestions.')
    is_time_limited=fields.Boolean("Thequestionislimitedintime",
        help="Currentlyonlysupportedforlivesessions.")
    time_limit=fields.Integer("Timelimit(seconds)")
    #--comments(simplechoice,multiplechoice,matrix(withoutcountasananswer))
    comments_allowed=fields.Boolean('ShowCommentsField')
    comments_message=fields.Char('CommentMessage',translate=True,default=lambdaself:_("Ifother,pleasespecify:"))
    comment_count_as_answer=fields.Boolean('CommentFieldisanAnswerChoice')
    #questionvalidation
    validation_required=fields.Boolean('Validateentry')
    validation_email=fields.Boolean('Inputmustbeanemail')
    validation_length_min=fields.Integer('MinimumTextLength',default=0)
    validation_length_max=fields.Integer('MaximumTextLength',default=0)
    validation_min_float_value=fields.Float('Minimumvalue',default=0.0)
    validation_max_float_value=fields.Float('Maximumvalue',default=0.0)
    validation_min_date=fields.Date('MinimumDate')
    validation_max_date=fields.Date('MaximumDate')
    validation_min_datetime=fields.Datetime('MinimumDatetime')
    validation_max_datetime=fields.Datetime('MaximumDatetime')
    validation_error_msg=fields.Char('ValidationErrormessage',translate=True,default=lambdaself:_("Theansweryouenteredisnotvalid."))
    constr_mandatory=fields.Boolean('MandatoryAnswer')
    constr_error_msg=fields.Char('Errormessage',translate=True,default=lambdaself:_("Thisquestionrequiresananswer."))
    #answers
    user_input_line_ids=fields.One2many(
        'survey.user_input.line','question_id',string='Answers',
        domain=[('skipped','=',False)],groups='survey.group_survey_user')

    #Conditionaldisplay
    is_conditional=fields.Boolean(
        string='ConditionalDisplay',copy=False,help="""Ifchecked,thisquestionwillbedisplayedonly
        ifthespecifiedconditionalanswerhavebeenselectedinapreviousquestion""")
    triggering_question_id=fields.Many2one(
        'survey.question',string="TriggeringQuestion",copy=False,compute="_compute_triggering_question_id",
        store=True,readonly=False,help="Questioncontainingthetriggeringanswertodisplaythecurrentquestion.",
        domain="""[('survey_id','=',survey_id),
                 '&',('question_type','in',['simple_choice','multiple_choice']),
                 '|',
                     ('sequence','<',sequence),
                     '&',('sequence','=',sequence),('id','<',id)]""")
    triggering_answer_id=fields.Many2one(
        'survey.question.answer',string="TriggeringAnswer",copy=False,compute="_compute_triggering_answer_id",
        store=True,readonly=False,help="Answerthatwilltriggerthedisplayofthecurrentquestion.",
        domain="[('question_id','=',triggering_question_id)]")

    _sql_constraints=[
        ('positive_len_min','CHECK(validation_length_min>=0)','Alengthmustbepositive!'),
        ('positive_len_max','CHECK(validation_length_max>=0)','Alengthmustbepositive!'),
        ('validation_length','CHECK(validation_length_min<=validation_length_max)','Maxlengthcannotbesmallerthanminlength!'),
        ('validation_float','CHECK(validation_min_float_value<=validation_max_float_value)','Maxvaluecannotbesmallerthanminvalue!'),
        ('validation_date','CHECK(validation_min_date<=validation_max_date)','Maxdatecannotbesmallerthanmindate!'),
        ('validation_datetime','CHECK(validation_min_datetime<=validation_max_datetime)','Maxdatetimecannotbesmallerthanmindatetime!'),
        ('positive_answer_score','CHECK(answer_score>=0)','Ananswerscoreforanon-multiplechoicequestioncannotbenegative!'),
        ('scored_datetime_have_answers',"CHECK(is_scored_question!=TrueORquestion_type!='datetime'ORanswer_datetimeisnotnull)",
            'All"Isascoredquestion=True"and"QuestionType:Datetime"questionsneedananswer'),
        ('scored_date_have_answers',"CHECK(is_scored_question!=TrueORquestion_type!='date'ORanswer_dateisnotnull)",
            'All"Isascoredquestion=True"and"QuestionType:Date"questionsneedananswer')
    ]

    @api.depends('is_page')
    def_compute_question_type(self):
        forquestioninself:
            ifnotquestion.question_typeorquestion.is_page:
                question.question_type=False

    @api.depends('survey_id.question_and_page_ids.is_page','survey_id.question_and_page_ids.sequence')
    def_compute_question_ids(self):
        """Willtakeallquestionsofthesurveyforwhichtheindexishigherthantheindexofthispage
        andlowerthantheindexofthenextpage."""
        forquestioninself:
            ifquestion.is_page:
                next_page_index=False
                forpageinquestion.survey_id.page_ids:
                    ifpage._index()>question._index():
                        next_page_index=page._index()
                        break

                question.question_ids=question.survey_id.question_ids.filtered(
                    lambdaq:q._index()>question._index()and(notnext_page_indexorq._index()<next_page_index)
                )
            else:
                question.question_ids=self.env['survey.question']

    @api.depends('survey_id.question_and_page_ids.is_page','survey_id.question_and_page_ids.sequence')
    def_compute_page_id(self):
        """Willfindthepagetowhichthisquestionbelongstobylookinginsidethecorrespondingsurvey"""
        forquestioninself:
            ifquestion.is_page:
                question.page_id=None
            else:
                page=None
                forqinquestion.survey_id.question_and_page_ids.sorted():
                    ifq==question:
                        break
                    ifq.is_page:
                        page=q
                question.page_id=page

    @api.depends('question_type','validation_email')
    def_compute_save_as_email(self):
        forquestioninself:
            ifquestion.question_type!='char_box'ornotquestion.validation_email:
                question.save_as_email=False

    @api.depends('question_type')
    def_compute_save_as_nickname(self):
        forquestioninself:
            ifquestion.question_type!='char_box':
                question.save_as_nickname=False

    @api.depends('is_conditional')
    def_compute_triggering_question_id(self):
        """Usedasan'onchange':Resetthetriggeringquestionifuseruncheck'ConditionalDisplay'
            AvoidCacheMiss:setthevaluetoFalseifthevalueisnotsetyet."""
        forquestioninself:
            ifnotquestion.is_conditionalorquestion.triggering_question_idisNone:
                question.triggering_question_id=False

    @api.depends('triggering_question_id')
    def_compute_triggering_answer_id(self):
        """Usedasan'onchange':Resetthetriggeringanswerifuserunsetorchangethetriggeringquestion
            oruncheck'ConditionalDisplay'.
            AvoidCacheMiss:setthevaluetoFalseifthevalueisnotsetyet."""
        forquestioninself:
            ifnotquestion.triggering_question_id\
                    orquestion.triggering_question_id!=question.triggering_answer_id.question_id\
                    orquestion.triggering_answer_idisNone:
                question.triggering_answer_id=False

    @api.depends('question_type','scoring_type','answer_date','answer_datetime','answer_numerical_box')
    def_compute_is_scored_question(self):
        """Computeswhetheraquestion"isscored"ornot.Handlesfollowingcases:
          -inconsistentBoolean=Noneedgecasethatbreakstests=>False
          -surveyisnotscored=>False
          -'date'/'datetime'/'numerical_box'questiontypesw/correctanswer=>True
            (impliedwithoutuserhavingtoactivate,exceptfornumericalwhosecorrectvalueis0.0)
          -'simple_choice/multiple_choice':settoTrueeveniflogicisabitdifferent(comingfromanswers)
          -question_typeisn'tscoreable(note:choicequestionsscoringlogichandledseparately)=>False
        """
        forquestioninself:
            ifquestion.is_scored_questionisNoneorquestion.scoring_type=='no_scoring':
                question.is_scored_question=False
            elifquestion.question_type=='date':
                question.is_scored_question=bool(question.answer_date)
            elifquestion.question_type=='datetime':
                question.is_scored_question=bool(question.answer_datetime)
            elifquestion.question_type=='numerical_box'andquestion.answer_numerical_box:
                question.is_scored_question=True
            elifquestion.question_typein['simple_choice','multiple_choice']:
                question.is_scored_question=True
            else:
                question.is_scored_question=False

    #------------------------------------------------------------
    #VALIDATION
    #------------------------------------------------------------

    defvalidate_question(self,answer,comment=None):
        """Validatequestion,dependingonquestiontypeandparameters
         forsimplechoice,text,dateandnumber,answerissimplytheanswerofthequestion.
         Forothermultiplechoicesquestions,answerisalistofanswers(theselectedchoices
         oralistofselectedanswersperquestion-formatrixtype-):
            -Simpleanswer:answer='example'or2orquestion_answer_idor2019/10/10
            -Multiplechoice:answer=[question_answer_id1,question_answer_id2,question_answer_id3]
            -Matrix:answer={'rowId1':[colId1,colId2,...],'rowId2':[colId1,colId3,...]}

         returndict{question.id(int):error(str)}->emptydictifnovalidationerror.
         """
        self.ensure_one()
        ifisinstance(answer,str):
            answer=answer.strip()
        #Emptyanswertomandatoryquestion
        ifself.constr_mandatoryandnotanswerandself.question_typenotin['simple_choice','multiple_choice']:
            return{self.id:self.constr_error_msg}

        #becauseinchoicesquestiontypes,commentcancountasanswer
        ifanswerorself.question_typein['simple_choice','multiple_choice']:
            ifself.question_type=='char_box':
                returnself._validate_char_box(answer)
            elifself.question_type=='numerical_box':
                returnself._validate_numerical_box(answer)
            elifself.question_typein['date','datetime']:
                returnself._validate_date(answer)
            elifself.question_typein['simple_choice','multiple_choice']:
                returnself._validate_choice(answer,comment)
            elifself.question_type=='matrix':
                returnself._validate_matrix(answer)
        return{}

    def_validate_char_box(self,answer):
        #Emailformatvalidation
        #allthestringsoftheform"<something>@<anything>.<extension>"willbeaccepted
        ifself.validation_email:
            ifnottools.email_normalize(answer):
                return{self.id:_('Thisanswermustbeanemailaddress')}

        #Answervalidation(ifproperlydefined)
        #Lengthoftheanswermustbeinarange
        ifself.validation_required:
            ifnot(self.validation_length_min<=len(answer)<=self.validation_length_max):
                return{self.id:self.validation_error_msg}
        return{}

    def_validate_numerical_box(self,answer):
        try:
            floatanswer=float(answer)
        exceptValueError:
            return{self.id:_('Thisisnotanumber')}

        ifself.validation_required:
            #Answerisnotintherightrange
            withtools.ignore(Exception):
                ifnot(self.validation_min_float_value<=floatanswer<=self.validation_max_float_value):
                    return{self.id:self.validation_error_msg}
        return{}

    def_validate_date(self,answer):
        isDatetime=self.question_type=='datetime'
        #Checksifuserinputisadate
        try:
            dateanswer=fields.Datetime.from_string(answer)ifisDatetimeelsefields.Date.from_string(answer)
        exceptValueError:
            return{self.id:_('Thisisnotadate')}
        ifself.validation_required:
            #Checkifanswerisintherightrange
            ifisDatetime:
                min_date=fields.Datetime.from_string(self.validation_min_datetime)
                max_date=fields.Datetime.from_string(self.validation_max_datetime)
                dateanswer=fields.Datetime.from_string(answer)
            else:
                min_date=fields.Date.from_string(self.validation_min_date)
                max_date=fields.Date.from_string(self.validation_max_date)
                dateanswer=fields.Date.from_string(answer)

            if(min_dateandmax_dateandnot(min_date<=dateanswer<=max_date))\
                    or(min_dateandnotmin_date<=dateanswer)\
                    or(max_dateandnotdateanswer<=max_date):
                return{self.id:self.validation_error_msg}
        return{}

    def_validate_choice(self,answer,comment):
        #Emptycomment
        ifself.constr_mandatory\
                andnotanswer\
                andnot(self.comments_allowedandself.comment_count_as_answerandcomment):
            return{self.id:self.constr_error_msg}
        return{}

    def_validate_matrix(self,answers):
        #Validatethateachlinehasbeenanswered
        ifself.constr_mandatoryandlen(self.matrix_row_ids)!=len(answers):
            return{self.id:self.constr_error_msg}
        return{}

    def_index(self):
        """Wewouldnormallyjustusethe'sequence'fieldofquestionsBUT,ifthepagesandquestionsare
        createdwithoutevermovingrecordsaround,thesequencefieldcanbesetto0forallthequestions.

        However,theorderoftherecordsetisalwayscorrectsowecanrelyontheindexmethod."""
        self.ensure_one()
        returnlist(self.survey_id.question_and_page_ids).index(self)

    #------------------------------------------------------------
    #STATISTICS/REPORTING
    #------------------------------------------------------------

    def_prepare_statistics(self,user_input_lines):
        """Computestatisticaldataforquestionsbycountingnumberofvoteperchoiceonbasisoffilter"""
        all_questions_data=[]
        forquestioninself:
            question_data={'question':question,'is_page':question.is_page}

            ifquestion.is_page:
                all_questions_data.append(question_data)
                continue

            #fetchanswerlines,separatecommentsfromrealanswers
            all_lines=user_input_lines.filtered(lambdaline:line.question_id==question)
            ifquestion.question_typein['simple_choice','multiple_choice','matrix']:
                answer_lines=all_lines.filtered(
                    lambdaline:line.answer_type=='suggestion'or(
                        line.skippedandnotline.answer_type)or(
                        line.answer_type=='char_box'andquestion.comment_count_as_answer)
                    )
                comment_line_ids=all_lines.filtered(lambdaline:line.answer_type=='char_box')
            else:
                answer_lines=all_lines
                comment_line_ids=self.env['survey.user_input.line']
            skipped_lines=answer_lines.filtered(lambdaline:line.skipped)
            done_lines=answer_lines-skipped_lines
            question_data.update(
                answer_line_ids=answer_lines,
                answer_line_done_ids=done_lines,
                answer_input_done_ids=done_lines.mapped('user_input_id'),
                answer_input_skipped_ids=skipped_lines.mapped('user_input_id'),
                comment_line_ids=comment_line_ids)
            question_data.update(question._get_stats_summary_data(answer_lines))

            #preparetableandgraphdata
            table_data,graph_data=question._get_stats_data(answer_lines)
            question_data['table_data']=table_data
            question_data['graph_data']=json.dumps(graph_data)

            all_questions_data.append(question_data)
        returnall_questions_data

    def_get_stats_data(self,user_input_lines):
        ifself.question_type=='simple_choice':
            returnself._get_stats_data_answers(user_input_lines)
        elifself.question_type=='multiple_choice':
            table_data,graph_data=self._get_stats_data_answers(user_input_lines)
            returntable_data,[{'key':self.title,'values':graph_data}]
        elifself.question_type=='matrix':
            returnself._get_stats_graph_data_matrix(user_input_lines)
        return[lineforlineinuser_input_lines],[]

    def_get_stats_data_answers(self,user_input_lines):
        """Statisticsforquestion.answerbasedquestions(simplechoice,multiple
        choice.).Acornercasewithavoidrecordsurvey.question.answerisadded
        tocountcommentsthatshouldbeconsideredasvalidanswers.Thissmallhack
        allowtohaveeverythingavailableinthesamestandardstructure."""
        suggested_answers=[answerforanswerinself.mapped('suggested_answer_ids')]
        ifself.comment_count_as_answer:
            suggested_answers+=[self.env['survey.question.answer']]

        count_data=dict.fromkeys(suggested_answers,0)
        forlineinuser_input_lines:
            ifline.suggested_answer_idincount_data\
               or(line.value_char_boxandself.comment_count_as_answer):
                count_data[line.suggested_answer_id]+=1

        table_data=[{
            'value':_('Other(seecomments)')ifnotsug_answerelsesug_answer.value,
            'suggested_answer':sug_answer,
            'count':count_data[sug_answer]
            }
            forsug_answerinsuggested_answers]
        graph_data=[{
            'text':_('Other(seecomments)')ifnotsug_answerelsesug_answer.value,
            'count':count_data[sug_answer]
            }
            forsug_answerinsuggested_answers]

        returntable_data,graph_data

    def_get_stats_graph_data_matrix(self,user_input_lines):
        suggested_answers=self.mapped('suggested_answer_ids')
        matrix_rows=self.mapped('matrix_row_ids')

        count_data=dict.fromkeys(itertools.product(matrix_rows,suggested_answers),0)
        forlineinuser_input_lines:
            ifline.matrix_row_idandline.suggested_answer_id:
                count_data[(line.matrix_row_id,line.suggested_answer_id)]+=1

        table_data=[{
            'row':row,
            'columns':[{
                'suggested_answer':sug_answer,
                'count':count_data[(row,sug_answer)]
            }forsug_answerinsuggested_answers],
        }forrowinmatrix_rows]
        graph_data=[{
            'key':sug_answer.value,
            'values':[{
                'text':row.value,
                'count':count_data[(row,sug_answer)]
                }
                forrowinmatrix_rows
            ]
        }forsug_answerinsuggested_answers]

        returntable_data,graph_data

    def_get_stats_summary_data(self,user_input_lines):
        stats={}
        ifself.question_typein['simple_choice','multiple_choice']:
            stats.update(self._get_stats_summary_data_choice(user_input_lines))
        elifself.question_type=='numerical_box':
            stats.update(self._get_stats_summary_data_numerical(user_input_lines))

        ifself.question_typein['numerical_box','date','datetime']:
            stats.update(self._get_stats_summary_data_scored(user_input_lines))
        returnstats

    def_get_stats_summary_data_choice(self,user_input_lines):
        right_inputs,partial_inputs=self.env['survey.user_input'],self.env['survey.user_input']
        right_answers=self.suggested_answer_ids.filtered(lambdalabel:label.is_correct)
        ifself.question_type=='multiple_choice':
            foruser_input,linesintools.groupby(user_input_lines,operator.itemgetter('user_input_id')):
                user_input_answers=self.env['survey.user_input.line'].concat(*lines).filtered(lambdal:l.answer_is_correct).mapped('suggested_answer_id')
                ifuser_input_answersanduser_input_answers<right_answers:
                    partial_inputs+=user_input
                elifuser_input_answers:
                    right_inputs+=user_input
        else:
            right_inputs=user_input_lines.filtered(lambdaline:line.answer_is_correct).mapped('user_input_id')
        return{
            'right_answers':right_answers,
            'right_inputs_count':len(right_inputs),
            'partial_inputs_count':len(partial_inputs),
        }

    def_get_stats_summary_data_numerical(self,user_input_lines):
        all_values=user_input_lines.filtered(lambdaline:notline.skipped).mapped('value_numerical_box')
        lines_sum=sum(all_values)
        return{
            'numerical_max':max(all_values,default=0),
            'numerical_min':min(all_values,default=0),
            'numerical_average':round(lines_sum/(len(all_values)or1),2),
        }

    def_get_stats_summary_data_scored(self,user_input_lines):
        return{
            'common_lines':collections.Counter(
                user_input_lines.filtered(lambdaline:notline.skipped).mapped('value_%s'%self.question_type)
            ).most_common(5)ifself.question_type!='datetime'else[],
            'right_inputs_count':len(user_input_lines.filtered(lambdaline:line.answer_is_correct).mapped('user_input_id'))
        }


classSurveyQuestionAnswer(models.Model):
    """Apreconfiguredanswerforaquestion.Thismodelstoresvaluesused
    for

      *simplechoice,multiplechoice:proposedvaluesfortheselection/
        radio;
      *matrix:rowandcolumnvalues;

    """
    _name='survey.question.answer'
    _rec_name='value'
    _order='sequence,id'
    _description='SurveyLabel'

    question_id=fields.Many2one('survey.question',string='Question',ondelete='cascade')
    matrix_question_id=fields.Many2one('survey.question',string='Question(asmatrixrow)',ondelete='cascade')
    sequence=fields.Integer('LabelSequenceorder',default=10)
    value=fields.Char('Suggestedvalue',translate=True,required=True)
    value_image=fields.Image('Image',max_width=256,max_height=256)
    is_correct=fields.Boolean('Isacorrectanswer')
    answer_score=fields.Float('Scoreforthischoice',help="Apositivescoreindicatesacorrectchoice;anegativeornullscoreindicatesawronganswer")

    @api.constrains('question_id','matrix_question_id')
    def_check_question_not_empty(self):
        """Ensurethatfieldquestion_idXORfieldmatrix_question_idisnotnull"""
        forlabelinself:
            ifnotbool(label.question_id)!=bool(label.matrix_question_id):
                raiseValidationError(_("Alabelmustbeattachedtoonlyonequestion."))
