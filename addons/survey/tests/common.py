#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre

fromcollectionsimportCounter
fromcontextlibimportcontextmanager

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.testsimportcommon


classSurveyCase(common.SavepointCase):
    defsetUp(self):
        super(SurveyCase,self).setUp()

        """Somecustomstufftomakethematchingbetweenquestionsandanswers
          :paramdict_type_match:dict
            key:questiontype
            value:(answertype,answerfield_name)
        """
        self._type_match={
            'text_box':('text_box','value_text_box'),
            'char_box':('char_box','value_char_box'),
            'numerical_box':('numerical_box','value_numerical_box'),
            'date':('date','value_date'),
            'simple_choice':('suggestion','suggested_answer_id'), #TDE:stillunclear
            'multiple_choice':('suggestion','suggested_answer_id'), #TDE:stillunclear
            'matrix':('suggestion',('suggested_answer_id','matrix_row_id')), #TDE:stillunclear
        }

    #------------------------------------------------------------
    #ASSERTS
    #------------------------------------------------------------

    defassertAnswer(self,answer,state,page):
        self.assertEqual(answer.state,state)
        self.assertEqual(answer.last_displayed_page_id,page)

    defassertAnswerLines(self,page,answer,answer_data):
        """Checkanswerlines.

          :paramdictanswer_data:
            key=questionID
            value={'value':[userinput]}
        """
        lines=answer.user_input_line_ids.filtered(lambdal:l.page_id==page)
        answer_count=sum(len(user_input['value'])foruser_inputinanswer_data.values())
        self.assertEqual(len(lines),answer_count)
        forqid,user_inputinanswer_data.items():
            answer_lines=lines.filtered(lambdal:l.question_id.id==qid)
            question=answer_lines[0].question_id #TDEnote:mighthaveseveralanswersforagivenquestion
            ifquestion.question_type=='multiple_choice':
                values=user_input['value']
                answer_fname=self._type_match[question.question_type][1]
                self.assertEqual(
                    Counter(getattr(line,answer_fname).idforlineinanswer_lines),
                    Counter(values))
            elifquestion.question_type=='simple_choice':
                [value]=user_input['value']
                answer_fname=self._type_match[question.question_type][1]
                self.assertEqual(getattr(answer_lines,answer_fname).id,value)
            elifquestion.question_type=='matrix':
                [value_col,value_row]=user_input['value']
                answer_fname_col=self._type_match[question.question_type][1][0]
                answer_fname_row=self._type_match[question.question_type][1][1]
                self.assertEqual(getattr(answer_lines,answer_fname_col).id,value_col)
                self.assertEqual(getattr(answer_lines,answer_fname_row).id,value_row)
            else:
                [value]=user_input['value']
                answer_fname=self._type_match[question.question_type][1]
                ifquestion.question_type=='numerical_box':
                    self.assertEqual(getattr(answer_lines,answer_fname),float(value))
                else:
                    self.assertEqual(getattr(answer_lines,answer_fname),value)

    defassertResponse(self,response,status_code,text_bits=None):
        self.assertEqual(response.status_code,status_code)
        fortextintext_bitsor[]:
            self.assertIn(text,response.text)

    #------------------------------------------------------------
    #DATACREATION
    #------------------------------------------------------------

    def_add_question(self,page,name,qtype,**kwargs):
        constr_mandatory=kwargs.pop('constr_mandatory',True)
        constr_error_msg=kwargs.pop('constr_error_msg','TestError')

        sequence=kwargs.pop('sequence',False)
        ifnotsequence:
            sequence=page.question_ids[-1].sequence+1ifpage.question_idselsepage.sequence+1

        base_qvalues={
            'sequence':sequence,
            'title':name,
            'question_type':qtype,
            'constr_mandatory':constr_mandatory,
            'constr_error_msg':constr_error_msg,
        }
        ifqtypein('simple_choice','multiple_choice'):
            base_qvalues['suggested_answer_ids']=[
                (0,0,{
                    'value':label['value'],
                    'answer_score':label.get('answer_score',0),
                    'is_correct':label.get('is_correct',False)
                })forlabelinkwargs.pop('labels')
            ]
        elifqtype=='matrix':
            base_qvalues['matrix_subtype']=kwargs.pop('matrix_subtype','simple')
            base_qvalues['suggested_answer_ids']=[
                (0,0,{'value':label['value'],'answer_score':label.get('answer_score',0)})
                forlabelinkwargs.pop('labels')
            ]
            base_qvalues['matrix_row_ids']=[
                (0,0,{'value':label['value'],'answer_score':label.get('answer_score',0)})
                forlabelinkwargs.pop('labels_2')
            ]
        else:
            pass
        base_qvalues.update(kwargs)
        question=self.env['survey.question'].create(base_qvalues)
        returnquestion

    def_add_answer(self,survey,partner,**kwargs):
        base_avals={
            'survey_id':survey.id,
            'partner_id':partner.idifpartnerelseFalse,
            'email':kwargs.pop('email',False),
        }
        base_avals.update(kwargs)
        returnself.env['survey.user_input'].create(base_avals)

    def_add_answer_line(self,question,answer,answer_value,**kwargs):
        qtype=self._type_match.get(question.question_type,(False,False))
        answer_type=kwargs.pop('answer_type',qtype[0])
        answer_fname=kwargs.pop('answer_fname',qtype[1])

        base_alvals={
            'user_input_id':answer.id,
            'question_id':question.id,
            'skipped':False,
            'answer_type':answer_type,
        }
        base_alvals[answer_fname]=answer_value
        base_alvals.update(kwargs)
        returnself.env['survey.user_input.line'].create(base_alvals)

    #------------------------------------------------------------
    #UTILS/CONTROLLERENDPOINTSFLOWS
    #------------------------------------------------------------

    def_access_start(self,survey):
        returnself.url_open('/survey/start/%s'%survey.access_token)

    def_access_page(self,survey,token):
        returnself.url_open('/survey/%s/%s'%(survey.access_token,token))

    def_access_begin(self,survey,token):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url=base_url+'/survey/begin/%s/%s'%(survey.access_token,token)
        returnself.opener.post(url=url,json={})

    def_access_submit(self,survey,token,post_data):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url=base_url+'/survey/submit/%s/%s'%(survey.access_token,token)
        returnself.opener.post(url=url,json={'params':post_data})

    def_find_csrf_token(self,text):
        csrf_token_re=re.compile("(input.+csrf_token.+value=\")([a-f0-9]{40}o[0-9]*)",re.MULTILINE)
        returncsrf_token_re.search(text).groups()[1]

    def_prepare_post_data(self,question,answers,post_data):
        values=answersifisinstance(answers,list)else[answers]
        ifquestion.question_type=='multiple_choice':
            forvalueinvalues:
                value=str(value)
                ifquestion.idinpost_data:
                    ifisinstance(post_data[question.id],list):
                        post_data[question.id].append(value)
                    else:
                        post_data[question.id]=[post_data[question.id],value]
                else:
                    post_data[question.id]=value
        else:
            [values]=values
            post_data[question.id]=str(values)
        returnpost_data

    def_answer_question(self,question,answer,answer_token,csrf_token,button_submit='next'):
        #Employeesubmitsthequestionanswer
        post_data=self._format_submission_data(question,answer,{'csrf_token':csrf_token,'token':answer_token,'button_submit':button_submit})
        response=self._access_submit(question.survey_id,answer_token,post_data)
        self.assertResponse(response,200)

        #Employeeisredirectedonnextquestion
        response=self._access_page(question.survey_id,answer_token)
        self.assertResponse(response,200)

    def_answer_page(self,page,answers,answer_token,csrf_token):
        post_data={}
        forquestion,answerinanswers.items():
            post_data[question.id]=answer.id
        post_data['page_id']=page.id
        post_data['csrf_token']=csrf_token
        post_data['token']=answer_token
        response=self._access_submit(page.survey_id,answer_token,post_data)
        self.assertResponse(response,200)
        response=self._access_page(page.survey_id,answer_token)
        self.assertResponse(response,200)

    def_format_submission_data(self,question,answer,additional_post_data):
        post_data={}
        post_data['question_id']=question.id
        post_data.update(self._prepare_post_data(question,answer,post_data))
        ifquestion.page_id:
            post_data['page_id']=question.page_id.id
        post_data.update(**additional_post_data)
        returnpost_data

    #------------------------------------------------------------
    #UTILS/TOOLS
    #------------------------------------------------------------

    def_assert_skipped_question(self,question,survey_user):
        statistics=question._prepare_statistics(survey_user.user_input_line_ids)
        question_data=next(
            (question_data
            forquestion_datainstatistics
            ifquestion_data.get('question')==question),
            False
        )
        self.assertTrue(bool(question_data))
        self.assertEqual(len(question_data.get('answer_input_skipped_ids')),1)

    def_create_one_question_per_type(self):
        all_questions=self.env['survey.question']
        for(question_type,text)inself.env['survey.question']._fields['question_type'].selection:
            kwargs={}
            ifquestion_type=='multiple_choice':
                kwargs['labels']=[{'value':'MChoice0'},{'value':'MChoice1'}]
            elifquestion_type=='simple_choice':
                kwargs['labels']=[]
            elifquestion_type=='matrix':
                kwargs['labels']=[{'value':'Column0'},{'value':'Column1'}]
                kwargs['labels_2']=[{'value':'Row0'},{'value':'Row1'}]
            all_questions|=self._add_question(self.page_0,'Q0',question_type,**kwargs)

        returnall_questions


classTestSurveyCommon(SurveyCase):
    defsetUp(self):
        super(TestSurveyCommon,self).setUp()

        """Createtestdata:asurveywithsomepre-definedquestionsandvarioustestusersforACL"""
        self.survey_manager=mail_new_test_user(
            self.env,name='GustaveDoré',login='survey_manager',email='survey.manager@example.com',
            groups='survey.group_survey_manager,base.group_user'
        )

        self.survey_user=mail_new_test_user(
            self.env,name='LukasPeeters',login='survey_user',email='survey.user@example.com',
            groups='survey.group_survey_user,base.group_user'
        )

        self.user_emp=mail_new_test_user(
            self.env,name='EglantineEmployee',login='user_emp',email='employee@example.com',
            groups='base.group_user',password='user_emp'
        )

        self.user_portal=mail_new_test_user(
            self.env,name='PatrickPortal',login='user_portal',email='portal@example.com',
            groups='base.group_portal'
        )

        self.user_public=mail_new_test_user(
            self.env,name='PaulinePublic',login='user_public',email='public@example.com',
            groups='base.group_public'
        )

        self.customer=self.env['res.partner'].create({
            'name':'CarolineCustomer',
            'email':'customer@example.com',
        })

        self.survey=self.env['survey.survey'].with_user(self.survey_manager).create({
            'title':'TestSurvey',
            'access_mode':'public',
            'users_login_required':True,
            'users_can_go_back':False,
            'state':'open',
        })
        self.page_0=self.env['survey.question'].with_user(self.survey_manager).create({
            'title':'Firstpage',
            'survey_id':self.survey.id,
            'sequence':1,
            'is_page':True,
        })
        self.question_ft=self.env['survey.question'].with_user(self.survey_manager).create({
            'title':'TestFreeText',
            'survey_id':self.survey.id,
            'sequence':2,
            'question_type':'text_box',
        })
        self.question_num=self.env['survey.question'].with_user(self.survey_manager).create({
            'title':'TestNUmericalBox',
            'survey_id':self.survey.id,
            'sequence':3,
            'question_type':'numerical_box',
        })
