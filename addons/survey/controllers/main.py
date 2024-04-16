#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importlogging
importwerkzeug

fromdatetimeimportdatetime,timedelta
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportfields,http,SUPERUSER_ID,_
fromflectra.addons.base.models.ir_ui_viewimportkeep_query
fromflectra.exceptionsimportUserError
fromflectra.httpimportrequest,content_disposition
fromflectra.osvimportexpression
fromflectra.toolsimportformat_datetime,format_date,is_html_empty

fromflectra.addons.web.controllers.mainimportBinary

_logger=logging.getLogger(__name__)


classSurvey(http.Controller):

    #------------------------------------------------------------
    #ACCESS
    #------------------------------------------------------------

    def_fetch_from_access_token(self,survey_token,answer_token):
        """Checkthatgiventokenmatchesananswerfromthegivensurvey_id.
        Returnsasudo-edbrowserecordofsurveyinordertoavoidaccessrights
        issuesnowthataccessisgrantedthroughtoken."""
        survey_sudo=request.env['survey.survey'].with_context(active_test=False).sudo().search([('access_token','=',survey_token)])
        ifnotanswer_token:
            answer_sudo=request.env['survey.user_input'].sudo()
        else:
            answer_sudo=request.env['survey.user_input'].sudo().search([
                ('survey_id','=',survey_sudo.id),
                ('access_token','=',answer_token)
            ],limit=1)
        returnsurvey_sudo,answer_sudo

    def_check_validity(self,survey_token,answer_token,ensure_token=True,check_partner=True):
        """Checksurveyisopenandcanbetaken.Thisdoesnotchecksfor
        securityrules,onlyfunctional/businessrules.Itreturnsastringkey
        allowingfurthermanipulationofvalidityissues

         *survey_wrong:surveydoesnotexist;
         *survey_auth:authenticationisrequired;
         *survey_closed:surveyisclosedanddoesnotacceptinputanymore;
         *survey_void:surveyisvoidandshouldnotbetaken;
         *token_wrong:giventokennotrecognized;
         *token_required:notokengivenalthoughitisnecessarytoaccessthe
           survey;
         *answer_deadline:tokenlinkedtoanexpiredanswer;

        :paramensure_token:whetheruserinputexistencebasedongivenaccesstoken
          shouldbeenforcedornot,dependingontherouterequestingatokenor
          allowingexternalworldcalls;

        :paramcheck_partner:Whetherwemustcheckthatthepartnerassociatedtothetarget
          answercorrespondstotheactiveuser.
        """
        survey_sudo,answer_sudo=self._fetch_from_access_token(survey_token,answer_token)

        ifnotsurvey_sudo.exists():
            return'survey_wrong'

        ifanswer_tokenandnotanswer_sudo:
            return'token_wrong'

        ifnotanswer_sudoandensure_token:
            return'token_required'
        ifnotanswer_sudoandsurvey_sudo.access_mode=='token':
            return'token_required'

        ifsurvey_sudo.users_login_requiredandrequest.env.user._is_public():
            return'survey_auth'

        if(survey_sudo.state=='closed'orsurvey_sudo.state=='draft'ornotsurvey_sudo.active)and(notanswer_sudoornotanswer_sudo.test_entry):
            return'survey_closed'

        if(notsurvey_sudo.page_idsandsurvey_sudo.questions_layout=='page_per_section')ornotsurvey_sudo.question_ids:
            return'survey_void'

        ifanswer_sudoandcheck_partner:
            ifrequest.env.user._is_public()andanswer_sudo.partner_idandnotanswer_token:
                #answersfrompublicusershouldnothaveanypartner_id;thisindicatesprobablyacookieissue
                return'answer_wrong_user'
            ifnotrequest.env.user._is_public()andanswer_sudo.partner_idandanswer_sudo.partner_id!=request.env.user.partner_id:
                #partnermismatch,probablyacookieissue
                return'answer_wrong_user'

        ifanswer_sudoandanswer_sudo.deadlineandanswer_sudo.deadline<datetime.now():
            return'answer_deadline'

        returnTrue

    def_get_access_data(self,survey_token,answer_token,ensure_token=True,check_partner=True):
        """Getbackdatarelatedtosurveyanduserinput,giventheIDandaccess
        tokenprovidedbytheroute.

         :paramensure_token:whetheruserinputexistenceshouldbeenforcedornot(see``_check_validity``)
         :paramcheck_partner:whetherthepartnerofthetargetanswershouldbechecked(see``_check_validity``)
        """
        survey_sudo,answer_sudo=request.env['survey.survey'].sudo(),request.env['survey.user_input'].sudo()
        has_survey_access,can_answer=False,False

        validity_code=self._check_validity(survey_token,answer_token,ensure_token=ensure_token,check_partner=check_partner)
        ifvalidity_code!='survey_wrong':
            survey_sudo,answer_sudo=self._fetch_from_access_token(survey_token,answer_token)
            try:
                survey_user=survey_sudo.with_user(request.env.user)
                survey_user.check_access_rights(self,'read',raise_exception=True)
                survey_user.check_access_rule(self,'read')
            except:
                pass
            else:
                has_survey_access=True
            can_answer=bool(answer_sudo)
            ifnotcan_answer:
                can_answer=survey_sudo.access_mode=='public'

        return{
            'survey_sudo':survey_sudo,
            'answer_sudo':answer_sudo,
            'has_survey_access':has_survey_access,
            'can_answer':can_answer,
            'validity_code':validity_code,
        }

    def_redirect_with_error(self,access_data,error_key):
        survey_sudo=access_data['survey_sudo']
        answer_sudo=access_data['answer_sudo']

        iferror_key=='survey_void'andaccess_data['can_answer']:
            returnrequest.render("survey.survey_void_content",{'survey':survey_sudo,'answer':answer_sudo})
        eliferror_key=='survey_closed'andaccess_data['can_answer']:
            returnrequest.render("survey.survey_closed_expired",{'survey':survey_sudo})
        eliferror_key=='survey_auth':
            ifnotanswer_sudo: #surveyisnotevenstarted
                redirect_url='/web/login?redirect=/survey/start/%s'%survey_sudo.access_token
            elifanswer_sudo.access_token: #surveyisstartedbutuserisnotloggedinanymore.
                ifanswer_sudo.partner_idand(answer_sudo.partner_id.user_idsorsurvey_sudo.users_can_signup):
                    ifanswer_sudo.partner_id.user_ids:
                        answer_sudo.partner_id.signup_cancel()
                    else:
                        answer_sudo.partner_id.signup_prepare(expiration=fields.Datetime.now()+relativedelta(days=1))
                    redirect_url=answer_sudo.partner_id._get_signup_url_for_action(url='/survey/start/%s?answer_token=%s'%(survey_sudo.access_token,answer_sudo.access_token))[answer_sudo.partner_id.id]
                else:
                    redirect_url='/web/login?redirect=%s'%('/survey/start/%s?answer_token=%s'%(survey_sudo.access_token,answer_sudo.access_token))
            returnrequest.render("survey.survey_auth_required",{'survey':survey_sudo,'redirect_url':redirect_url})
        eliferror_key=='answer_deadline'andanswer_sudo.access_token:
            returnrequest.render("survey.survey_closed_expired",{'survey':survey_sudo})

        returnwerkzeug.utils.redirect("/")

    #------------------------------------------------------------
    #TEST/RETRYSURVEYROUTES
    #------------------------------------------------------------

    @http.route('/survey/test/<string:survey_token>',type='http',auth='user',website=True)
    defsurvey_test(self,survey_token,**kwargs):
        """Testmodeforsurveys:createatestanswer,onlyformanagersorofficers
        testingtheirsurveys"""
        survey_sudo,dummy=self._fetch_from_access_token(survey_token,False)
        try:
            answer_sudo=survey_sudo._create_answer(user=request.env.user,test_entry=True)
        except:
            returnwerkzeug.utils.redirect('/')
        returnrequest.redirect('/survey/start/%s?%s'%(survey_sudo.access_token,keep_query('*',answer_token=answer_sudo.access_token)))

    @http.route('/survey/retry/<string:survey_token>/<string:answer_token>',type='http',auth='public',website=True)
    defsurvey_retry(self,survey_token,answer_token,**post):
        """Thisrouteiscalledwhenevertheuserhasattemptsleftandhitsthe'Retry'button
        afterfailingthesurvey."""
        access_data=self._get_access_data(survey_token,answer_token,ensure_token=True)
        ifaccess_data['validity_code']isnotTrue:
            returnself._redirect_with_error(access_data,access_data['validity_code'])

        survey_sudo,answer_sudo=access_data['survey_sudo'],access_data['answer_sudo']
        ifnotanswer_sudo:
            #attemptsto'retry'withouthavingtriedfirst
            returnwerkzeug.utils.redirect("/")

        try:
            retry_answer_sudo=survey_sudo._create_answer(
                user=request.env.user,
                partner=answer_sudo.partner_id,
                email=answer_sudo.email,
                invite_token=answer_sudo.invite_token,
                test_entry=answer_sudo.test_entry,
                **self._prepare_retry_additional_values(answer_sudo)
            )
        except:
            returnwerkzeug.utils.redirect("/")
        returnrequest.redirect('/survey/start/%s?%s'%(survey_sudo.access_token,keep_query('*',answer_token=retry_answer_sudo.access_token)))

    def_prepare_retry_additional_values(self,answer):
        return{
            'deadline':answer.deadline,
        }

    def_prepare_survey_finished_values(self,survey,answer,token=False):
        values={'survey':survey,'answer':answer}
        iftoken:
            values['token']=token
        ifsurvey.scoring_type!='no_scoring'andsurvey.certification:
            values['graph_data']=json.dumps(answer._prepare_statistics()[0])
        returnvalues

    #------------------------------------------------------------
    #TAKINGSURVEYROUTES
    #------------------------------------------------------------

    @http.route('/survey/start/<string:survey_token>',type='http',auth='public',website=True)
    defsurvey_start(self,survey_token,answer_token=None,email=False,**post):
        """Startasurveybyproviding
         *atokenlinkedtoasurvey;
         *atokenlinkedtoananswerorgenerateanewtokenifaccessisallowed;
        """
        #Getthecurrentanswertokenfromcookie
        answer_from_cookie=False
        ifnotanswer_token:
            answer_token=request.httprequest.cookies.get('survey_%s'%survey_token)
            answer_from_cookie=bool(answer_token)

        access_data=self._get_access_data(survey_token,answer_token,ensure_token=False)

        ifanswer_from_cookieandaccess_data['validity_code']in('answer_wrong_user','token_wrong'):
            #Ifthecookiehadbeengeneratedforanotheruserordoesnotcorrespondtoanyexistinganswerobject
            #(probablybecauseithasbeendeleted),ignoreitandredothecheck.
            #ThecookiewillbereplacedbyalegitvaluewhenresolvingtheURL,sowedon'tcleanitfurtherhere.
            access_data=self._get_access_data(survey_token,None,ensure_token=False)

        ifaccess_data['validity_code']isnotTrue:
            returnself._redirect_with_error(access_data,access_data['validity_code'])

        survey_sudo,answer_sudo=access_data['survey_sudo'],access_data['answer_sudo']
        ifnotanswer_sudo:
            try:
                answer_sudo=survey_sudo._create_answer(user=request.env.user,email=email)
            exceptUserError:
                answer_sudo=False

        ifnotanswer_sudo:
            try:
                survey_sudo.with_user(request.env.user).check_access_rights('read')
                survey_sudo.with_user(request.env.user).check_access_rule('read')
            except:
                returnwerkzeug.utils.redirect("/")
            else:
                returnrequest.render("survey.survey_403_page",{'survey':survey_sudo})

        returnrequest.redirect('/survey/%s/%s'%(survey_sudo.access_token,answer_sudo.access_token))

    def_prepare_survey_data(self,survey_sudo,answer_sudo,**post):
        """Thismethodpreparesallthedataneededfortemplaterendering,infunctionofthesurveyuserinputstate.
            :parampost:
                -previous_page_id:comefromthebreadcrumborthebackbuttonandforcethenextquestionstoload
                                     tobethepreviousones."""
        data={
            'is_html_empty':is_html_empty,
            'survey':survey_sudo,
            'answer':answer_sudo,
            'breadcrumb_pages':[{
                'id':page.id,
                'title':page.title,
            }forpageinsurvey_sudo.page_ids],
            'format_datetime':lambdadt:format_datetime(request.env,dt,dt_format=False),
            'format_date':lambdadate:format_date(request.env,date)
        }
        ifsurvey_sudo.questions_layout!='page_per_question':
            triggering_answer_by_question,triggered_questions_by_answer,selected_answers=answer_sudo._get_conditional_values()
            data.update({
                'triggering_answer_by_question':{
                    question.id:triggering_answer_by_question[question].idforquestionintriggering_answer_by_question.keys()
                    iftriggering_answer_by_question[question]
                },
                'triggered_questions_by_answer':{
                    answer.id:triggered_questions_by_answer[answer].ids
                    foranswerintriggered_questions_by_answer.keys()
                },
                'selected_answers':selected_answers.ids
            })

        ifnotanswer_sudo.is_session_answerandsurvey_sudo.is_time_limitedandanswer_sudo.start_datetime:
            data.update({
                'server_time':fields.Datetime.now(),
                'timer_start':answer_sudo.start_datetime.isoformat(),
                'time_limit_minutes':survey_sudo.time_limit
            })

        page_or_question_key='question'ifsurvey_sudo.questions_layout=='page_per_question'else'page'

        #Bypassallifpage_idisspecified(comesfrombreadcrumborpreviousbutton)
        if'previous_page_id'inpost:
            previous_page_or_question_id=int(post['previous_page_id'])
            new_previous_id=survey_sudo._get_next_page_or_question(answer_sudo,previous_page_or_question_id,go_back=True).id
            page_or_question=request.env['survey.question'].sudo().browse(previous_page_or_question_id)
            data.update({
                page_or_question_key:page_or_question,
                'previous_page_id':new_previous_id,
                'has_answered':answer_sudo.user_input_line_ids.filtered(lambdaline:line.question_id.id==new_previous_id),
                'can_go_back':survey_sudo._can_go_back(answer_sudo,page_or_question),
            })
            returndata

        ifanswer_sudo.state=='in_progress':
            ifanswer_sudo.is_session_answer:
                next_page_or_question=survey_sudo.session_question_id
            else:
                next_page_or_question=survey_sudo._get_next_page_or_question(
                    answer_sudo,
                    answer_sudo.last_displayed_page_id.idifanswer_sudo.last_displayed_page_idelse0)

                ifnext_page_or_question:
                    data.update({
                        'survey_last':survey_sudo._is_last_page_or_question(answer_sudo,next_page_or_question)
                    })

            ifanswer_sudo.is_session_answerandnext_page_or_question.is_time_limited:
                data.update({
                    'timer_start':survey_sudo.session_question_start_time.isoformat(),
                    'time_limit_minutes':next_page_or_question.time_limit/60
                })

            data.update({
                page_or_question_key:next_page_or_question,
                'has_answered':answer_sudo.user_input_line_ids.filtered(lambdaline:line.question_id==next_page_or_question),
                'can_go_back':survey_sudo._can_go_back(answer_sudo,next_page_or_question),
            })
            ifsurvey_sudo.questions_layout!='one_page':
                data.update({
                    'previous_page_id':survey_sudo._get_next_page_or_question(answer_sudo,next_page_or_question.id,go_back=True).id
                })
        elifanswer_sudo.state=='done'oranswer_sudo.survey_time_limit_reached:
            #Displaysuccessmessage
            returnself._prepare_survey_finished_values(survey_sudo,answer_sudo)

        returndata

    def_prepare_question_html(self,survey_sudo,answer_sudo,**post):
        """SurveypagenavigationisdoneinAJAX.Thisfunctionpreparethe'nextpage'todisplayinhtml
        andsendbackthishtmltothesurvey_formwidgetthatwillinjectitintothepage."""
        survey_data=self._prepare_survey_data(survey_sudo,answer_sudo,**post)

        survey_content=False
        ifanswer_sudo.state=='done':
            survey_content=request.env.ref('survey.survey_fill_form_done')._render(survey_data)
        else:
            survey_content=request.env.ref('survey.survey_fill_form_in_progress')._render(survey_data)

        survey_progress=False
        ifanswer_sudo.state=='in_progress'andnotsurvey_data.get('question',request.env['survey.question']).is_page:
            ifsurvey_sudo.questions_layout=='page_per_section':
                page_ids=survey_sudo.page_ids.ids
                survey_progress=request.env.ref('survey.survey_progression')._render({
                    'survey':survey_sudo,
                    'page_ids':page_ids,
                    'page_number':page_ids.index(survey_data['page'].id)+(1ifsurvey_sudo.progression_mode=='number'else0)
                })
            elifsurvey_sudo.questions_layout=='page_per_question':
                page_ids=(answer_sudo.predefined_question_ids.ids
                            ifnotanswer_sudo.is_session_answerandsurvey_sudo.questions_selection=='random'
                            elsesurvey_sudo.question_ids.ids)
                survey_progress=request.env.ref('survey.survey_progression')._render({
                    'survey':survey_sudo,
                    'page_ids':page_ids,
                    'page_number':page_ids.index(survey_data['question'].id)
                })

        return{
            'survey_content':survey_content,
            'survey_progress':survey_progress,
            'survey_navigation':request.env.ref('survey.survey_navigation')._render(survey_data),
        }

    @http.route('/survey/<string:survey_token>/<string:answer_token>',type='http',auth='public',website=True)
    defsurvey_display_page(self,survey_token,answer_token,**post):
        access_data=self._get_access_data(survey_token,answer_token,ensure_token=True)
        ifaccess_data['validity_code']isnotTrue:
            returnself._redirect_with_error(access_data,access_data['validity_code'])

        answer_sudo=access_data['answer_sudo']
        ifanswer_sudo.state!='done'andanswer_sudo.survey_time_limit_reached:
            answer_sudo._mark_done()

        returnrequest.render('survey.survey_page_fill',
            self._prepare_survey_data(access_data['survey_sudo'],answer_sudo,**post))

    @http.route('/survey/get_background_image/<string:survey_token>/<string:answer_token>',type='http',auth="public",website=True,sitemap=False)
    defsurvey_get_background(self,survey_token,answer_token):
        access_data=self._get_access_data(survey_token,answer_token,ensure_token=True)
        ifaccess_data['validity_code']isnotTrue:
            returnwerkzeug.exceptions.Forbidden()

        survey_sudo,answer_sudo=access_data['survey_sudo'],access_data['answer_sudo']

        status,headers,image_base64=request.env['ir.http'].sudo().binary_content(
            model='survey.survey',id=survey_sudo.id,field='background_image',
            default_mimetype='image/png')

        returnBinary._content_image_get_response(status,headers,image_base64)

    @http.route('/survey/get_question_image/<string:survey_token>/<string:answer_token>/<int:question_id>/<int:suggested_answer_id>',type='http',auth="public",website=True,sitemap=False)
    defsurvey_get_question_image(self,survey_token,answer_token,question_id,suggested_answer_id):
        access_data=self._get_access_data(survey_token,answer_token,ensure_token=True)
        ifaccess_data['validity_code']isnotTrue:
            returnwerkzeug.exceptions.Forbidden()

        survey_sudo,answer_sudo=access_data['survey_sudo'],access_data['answer_sudo']

        ifnotsurvey_sudo.question_ids.filtered(lambdaq:q.id==question_id)\
                          .suggested_answer_ids.filtered(lambdaa:a.id==suggested_answer_id):
            returnwerkzeug.exceptions.NotFound()

        status,headers,image_base64=request.env['ir.http'].sudo().binary_content(
            model='survey.question.answer',id=suggested_answer_id,field='value_image',
            default_mimetype='image/png')

        returnBinary._content_image_get_response(status,headers,image_base64)

    #----------------------------------------------------------------
    #JSONROUTEStobegin/continuesurvey(ajaxnavigation)+Tools
    #----------------------------------------------------------------

    @http.route('/survey/begin/<string:survey_token>/<string:answer_token>',type='json',auth='public',website=True)
    defsurvey_begin(self,survey_token,answer_token,**post):
        """Routeusedtostartthesurveyuserinputanddisplaythefirstsurveypage."""
        access_data=self._get_access_data(survey_token,answer_token,ensure_token=True)
        ifaccess_data['validity_code']isnotTrue:
            return{'error':access_data['validity_code']}
        survey_sudo,answer_sudo=access_data['survey_sudo'],access_data['answer_sudo']

        ifanswer_sudo.state!="new":
            return{'error':_("Thesurveyhasalreadystarted.")}

        answer_sudo._mark_in_progress()
        returnself._prepare_question_html(survey_sudo,answer_sudo,**post)

    @http.route('/survey/next_question/<string:survey_token>/<string:answer_token>',type='json',auth='public',website=True)
    defsurvey_next_question(self,survey_token,answer_token,**post):
        """Methodusedtodisplaythenextsurveyquestioninanongoingsession.
        Triggeredonallattendeesscreenswhenthehostgoestothenextquestion."""
        access_data=self._get_access_data(survey_token,answer_token,ensure_token=True)
        ifaccess_data['validity_code']isnotTrue:
            return{'error':access_data['validity_code']}
        survey_sudo,answer_sudo=access_data['survey_sudo'],access_data['answer_sudo']

        ifanswer_sudo.state=='new'andanswer_sudo.is_session_answer:
            answer_sudo._mark_in_progress()

        returnself._prepare_question_html(survey_sudo,answer_sudo,**post)

    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>',type='json',auth='public',website=True)
    defsurvey_submit(self,survey_token,answer_token,**post):
        """Submitapagefromthesurvey.
        Thiswilltakeintoaccountthevalidationerrorsandstoretheanswerstothequestions.
        Ifthetimelimitisreached,errorswillbeskipped,answerswillbeignoredand
        surveystatewillbeforcedto'done'"""
        #SurveyValidation
        access_data=self._get_access_data(survey_token,answer_token,ensure_token=True)
        ifaccess_data['validity_code']isnotTrue:
            return{'error':access_data['validity_code']}
        survey_sudo,answer_sudo=access_data['survey_sudo'],access_data['answer_sudo']

        ifanswer_sudo.state=='done':
            return{'error':'unauthorized'}

        questions,page_or_question_id=survey_sudo._get_survey_questions(answer=answer_sudo,
                                                                           page_id=post.get('page_id'),
                                                                           question_id=post.get('question_id'))

        ifnotanswer_sudo.test_entryandnotsurvey_sudo._has_attempts_left(answer_sudo.partner_id,answer_sudo.email,answer_sudo.invite_token):
            #preventcheatingwithuserscreatingmultiple'user_input'beforetheirlastattempt
            return{'error':'unauthorized'}

        ifanswer_sudo.survey_time_limit_reachedoranswer_sudo.question_time_limit_reached:
            ifanswer_sudo.question_time_limit_reached:
                time_limit=survey_sudo.session_question_start_time+relativedelta(
                    seconds=survey_sudo.session_question_id.time_limit
                )
                time_limit+=timedelta(seconds=3)
            else:
                time_limit=answer_sudo.start_datetime+timedelta(minutes=survey_sudo.time_limit)
                time_limit+=timedelta(seconds=10)
            iffields.Datetime.now()>time_limit:
                #preventcheatingwithusersblockingtheJStimerandtakingalltheirtimetoanswer
                return{'error':'unauthorized'}

        errors={}
        #Prepareanswers/commentbyquestion,validateandsaveanswers
        forquestioninquestions:
            inactive_questions=request.env['survey.question']ifanswer_sudo.is_session_answerelseanswer_sudo._get_inactive_conditional_questions()
            ifquestionininactive_questions: #ifquestionisinactive,skipvalidationandsave
                continue
            answer,comment=self._extract_comment_from_answers(question,post.get(str(question.id)))
            errors.update(question.validate_question(answer,comment))
            ifnoterrors.get(question.id):
                answer_sudo.save_lines(question,answer,comment)

        iferrorsandnot(answer_sudo.survey_time_limit_reachedoranswer_sudo.question_time_limit_reached):
            return{'error':'validation','fields':errors}

        ifnotanswer_sudo.is_session_answer:
            answer_sudo._clear_inactive_conditional_answers()

        ifanswer_sudo.survey_time_limit_reachedorsurvey_sudo.questions_layout=='one_page':
            answer_sudo._mark_done()
        elif'previous_page_id'inpost:
            #Gobacktospecificpageusingthebreadcrumb.Linesaresavedandsurveycontinues
            returnself._prepare_question_html(survey_sudo,answer_sudo,**post)
        else:
            vals={'last_displayed_page_id':page_or_question_id}
            ifnotanswer_sudo.is_session_answer:
                next_page=survey_sudo._get_next_page_or_question(answer_sudo,page_or_question_id)
                ifnotnext_page:
                    answer_sudo._mark_done()

            answer_sudo.write(vals)

        returnself._prepare_question_html(survey_sudo,answer_sudo)

    def_extract_comment_from_answers(self,question,answers):
        """Answersisacustomstructuredependingofthequestiontype
        thatcancontainquestionanswersbutalsocommentsthatneedtobe
        extractedbeforevalidatingandsavinganswers.
        Ifmultipleanswers,theyarelistedinanarray,exceptformatrix
        whereanswersarestructureddifferently.Seeinputandoutputfor
        moreinfoondatastructures.
        :paramquestion:survey.question
        :paramanswers:
          *question_type:free_text,text_box,numerical_box,date,datetime
            answersisastringcontainingthevalue
          *question_type:simple_choicewithnocomment
            answersisastringcontainingthevalue('question_id_1')
          *question_type:simple_choicewithcomment
            ['question_id_1',{'comment':str}]
          *question_type:multiplechoice
            ['question_id_1','question_id_2']+[{'comment':str}]ifholdsacomment
          *question_type:matrix
            {'matrix_row_id_1':['question_id_1','question_id_2'],
             'matrix_row_id_2':['question_id_1','question_id_2']
            }+{'comment':str}ifholdsacomment
        :return:tuple(
          samestructurewithoutcomment,
          extractedcommentforgivenquestion
        )"""
        comment=None
        answers_no_comment=[]
        ifanswers:
            ifquestion.question_type=='matrix':
                if'comment'inanswers:
                    comment=answers['comment'].strip()
                    answers.pop('comment')
                answers_no_comment=answers
            else:
                ifnotisinstance(answers,list):
                    answers=[answers]
                foranswerinanswers:
                    ifisinstance(answer,dict)and'comment'inanswer:
                        comment=answer['comment'].strip()
                    else:
                        answers_no_comment.append(answer)
                iflen(answers_no_comment)==1:
                    answers_no_comment=answers_no_comment[0]
        returnanswers_no_comment,comment

    #------------------------------------------------------------
    #COMPLETEDSURVEYROUTES
    #------------------------------------------------------------

    @http.route('/survey/print/<string:survey_token>',type='http',auth='public',website=True,sitemap=False)
    defsurvey_print(self,survey_token,review=False,answer_token=None,**post):
        '''Displayansurveyinprintableview;if<answer_token>isset,itwill
        grabtheanswersoftheuser_input_idthathas<answer_token>.'''
        access_data=self._get_access_data(survey_token,answer_token,ensure_token=False,check_partner=False)
        ifaccess_data['validity_code']isnotTrueand(
                access_data['has_survey_access']or
                access_data['validity_code']notin['token_required','survey_closed','survey_void']):
            returnself._redirect_with_error(access_data,access_data['validity_code'])

        survey_sudo,answer_sudo=access_data['survey_sudo'],access_data['answer_sudo']

        returnrequest.render('survey.survey_page_print',{
            'is_html_empty':is_html_empty,
            'review':review,
            'survey':survey_sudo,
            'answer':answer_sudoifsurvey_sudo.scoring_type!='scoring_without_answers'elseanswer_sudo.browse(),
            'questions_to_display':answer_sudo._get_print_questions(),
            'scoring_display_correction':survey_sudo.scoring_type=='scoring_with_answers'andanswer_sudo,
            'format_datetime':lambdadt:format_datetime(request.env,dt,dt_format=False),
            'format_date':lambdadate:format_date(request.env,date),
        })

    @http.route(['/survey/<model("survey.survey"):survey>/get_certification_preview'],type="http",auth="user",methods=['GET'],website=True)
    defsurvey_get_certification_preview(self,survey,**kwargs):
        ifnotrequest.env.user.has_group('survey.group_survey_user'):
            raisewerkzeug.exceptions.Forbidden()

        fake_user_input=survey._create_answer(user=request.env.user,test_entry=True)
        response=self._generate_report(fake_user_input,download=False)
        fake_user_input.sudo().unlink()
        returnresponse

    @http.route(['/survey/<int:survey_id>/get_certification'],type='http',auth='user',methods=['GET'],website=True)
    defsurvey_get_certification(self,survey_id,**kwargs):
        """Thecertificationdocumentcanbedownloadedaslongastheuserhassucceededthecertification"""
        survey=request.env['survey.survey'].sudo().search([
            ('id','=',survey_id),
            ('certification','=',True)
        ])

        ifnotsurvey:
            #nocertificationfound
            returnwerkzeug.utils.redirect("/")

        succeeded_attempt=request.env['survey.user_input'].sudo().search([
            ('partner_id','=',request.env.user.partner_id.id),
            ('survey_id','=',survey_id),
            ('scoring_success','=',True)
        ],limit=1)

        ifnotsucceeded_attempt:
            raiseUserError(_("Theuserhasnotsucceededthecertification"))

        returnself._generate_report(succeeded_attempt,download=True)

    #------------------------------------------------------------
    #REPORTINGSURVEYROUTESANDTOOLS
    #------------------------------------------------------------

    @http.route('/survey/results/<model("survey.survey"):survey>',type='http',auth='user',website=True)
    defsurvey_report(self,survey,answer_token=None,**post):
        """DisplaysurveyResults&Statisticsforgivensurvey.

        Newstructure:{
            'survey':currentsurveybrowserecord,
            'question_and_page_data':see``SurveyQuestion._prepare_statistics()``,
            'survey_data'=see``SurveySurvey._prepare_statistics()``
            'search_filters':[],
            'search_finished':eitherfilteronfinishedinputsonlyornot,
        }
        """
        user_input_lines,search_filters=self._extract_filters_data(survey,post)
        survey_data=survey._prepare_statistics(user_input_lines)
        question_and_page_data=survey.question_and_page_ids._prepare_statistics(user_input_lines)

        template_values={
            #surveyanditsstatistics
            'survey':survey,
            'question_and_page_data':question_and_page_data,
            'survey_data':survey_data,
            #search
            'search_filters':search_filters,
            'search_finished':post.get('finished')=='true',
        }

        ifsurvey.session_show_leaderboard:
            template_values['leaderboard']=survey._prepare_leaderboard_values()

        returnrequest.render('survey.survey_page_statistics',template_values)

    def_generate_report(self,user_input,download=True):
        report=request.env.ref('survey.certification_report').with_user(SUPERUSER_ID)._render_qweb_pdf([user_input.id],data={'report_type':'pdf'})[0]

        report_content_disposition=content_disposition('Certification.pdf')
        ifnotdownload:
            content_split=report_content_disposition.split(';')
            content_split[0]='inline'
            report_content_disposition=';'.join(content_split)

        returnrequest.make_response(report,headers=[
            ('Content-Type','application/pdf'),
            ('Content-Length',len(report)),
            ('Content-Disposition',report_content_disposition),
        ])

    def_get_user_input_domain(self,survey,line_filter_domain,**post):
        user_input_domain=['&',('test_entry','=',False),('survey_id','=',survey.id)]
        ifline_filter_domain:
            matching_line_ids=request.env['survey.user_input.line'].sudo().search(line_filter_domain).ids
            user_input_domain=expression.AND([
                [('user_input_line_ids','in',matching_line_ids)],
                user_input_domain
            ])
        ifpost.get('finished'):
            user_input_domain=expression.AND([[('state','=','done')],user_input_domain])
        else:
            user_input_domain=expression.AND([[('state','!=','new')],user_input_domain])
        returnuser_input_domain

    def_extract_filters_data(self,survey,post):
        search_filters=[]
        line_filter_domain,line_choices=[],[]
        fordatainpost.get('filters','').split('|'):
            try:
                row_id,answer_id=(int(item)foritemindata.split(','))
            except:
                pass
            else:
                ifrow_idandanswer_id:
                    line_filter_domain=expression.AND([
                        ['&',('matrix_row_id','=',row_id),('suggested_answer_id','=',answer_id)],
                        line_filter_domain
                    ])
                    answers=request.env['survey.question.answer'].browse([row_id,answer_id])
                elifanswer_id:
                    line_choices.append(answer_id)
                    answers=request.env['survey.question.answer'].browse([answer_id])
                ifanswer_id:
                    question_id=answers[0].matrix_question_idoranswers[0].question_id
                    search_filters.append({
                        'question':question_id.title,
                        'answers':'%s%s'%(answers[0].value,':%s'%answers[1].valueiflen(answers)>1else'')
                    })
        ifline_choices:
            line_filter_domain=expression.AND([[('suggested_answer_id','in',line_choices)],line_filter_domain])

        user_input_domain=self._get_user_input_domain(survey,line_filter_domain,**post)
        user_input_lines=request.env['survey.user_input'].sudo().search(user_input_domain).mapped('user_input_line_ids')

        returnuser_input_lines,search_filters
