#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime
importjson
importwerkzeug

fromdateutil.relativedeltaimportrelativedelta
fromwerkzeug.exceptionsimportNotFound

fromflectraimportfields,http
fromflectra.httpimportrequest
fromflectra.toolsimportis_html_empty


classUserInputSession(http.Controller):
    def_fetch_from_token(self,survey_token):
        """Checkthatgivensurvey_tokenmatchesasurvey'access_token'.
        Unliketheregularsurveycontroller,usertryingtoaccessthesurveymusthavefullaccessrights!"""
        returnrequest.env['survey.survey'].search([('access_token','=',survey_token)])

    def_fetch_from_session_code(self,session_code):
        """Matchesasurveyagainstapassedsession_code.
        Weforcethesession_statetobereachable(ready/in_progress)toavoidpeople
        usingthisroutetoaccessother(private)surveys.
        Welimittosessionsopenedwithinthelast7daystoavoidpotentialabuses."""
        ifsession_code:
            matching_survey=request.env['survey.survey'].sudo().search([
                ('state','=','open'),
                ('session_state','in',['ready','in_progress']),
                ('session_start_time','>',fields.Datetime.now()-relativedelta(days=7)),
                ('session_code','=',session_code),
            ],limit=1)
            ifmatching_survey:
                returnmatching_survey

        returnFalse

    #------------------------------------------------------------
    #SURVEYSESSIONMANAGEMENT
    #------------------------------------------------------------

    @http.route('/survey/session/manage/<string:survey_token>',type='http',auth='user',website=True)
    defsurvey_session_manage(self,survey_token,**kwargs):
        """Mainrouteusedbythehostto'manager'thesession.
        -Ifthestateofthesessionis'ready'
          Werenderatemplateallowingthehosttoshowcasethedifferentoptionsofthesession
          andtoactuallystartthesession.
        -Ifthestateofthesessionis'in_progress'
          Werenderatemplateallowingthehosttoshowthequestionresults,displaytheattendees
          leaderboardorgotothenextquestionofthesession."""

        survey=self._fetch_from_token(survey_token)

        ifnotsurveyornotsurvey.session_state:
            #noopensession
            returnNotFound()

        ifsurvey.session_state=='ready':
            returnrequest.render('survey.user_input_session_open',{
                'survey':survey
            })
        else:
            template_values=self._prepare_manage_session_values(survey)
            returnrequest.render('survey.user_input_session_manage',template_values)

    @http.route('/survey/session/next_question/<string:survey_token>',type='json',auth='user',website=True)
    defsurvey_session_next_question(self,survey_token,**kwargs):
        """Thisrouteiscalledwhenthehostgoestothenextquestionofthesession.

        It'snotaregular'request.render'routebecausewehandlethetransitionbetween
        questionsusingaAJAXcalltobeabletodisplayabioutifulfadein/outeffect.

        Ittriggersthenextquestionofthesession.

        Weartificiallyadd1secondtothe'current_question_start_time'toaccountforserverdelay.
        Asthetimingcaninfluencetheattendeesscore,wetrytobefairwitheveryonebygivingthem
        anextrasecondbeforewestartcountingdown.

        Frontendshouldtakethedelayintoaccountbydisplayingtheappropriateanimations.

        Writingthenextquestiononthesurveyissudo'edtoavoidpotentialaccessrightissues.
        e.g:asurveyusercancreatealivesessionfromanysurveybuthecanonlywrite
        onitsownsurvey."""

        survey=self._fetch_from_token(survey_token)

        ifnotsurveyornotsurvey.session_state:
            #noopensession
            return''

        ifsurvey.session_state=='ready':
            survey._session_open()

        next_question=survey._get_session_next_question()

        #usingdatetime.datetimebecausewewantthemillisportion
        ifnext_question:
            now=datetime.datetime.now()
            survey.sudo().write({
                'session_question_id':next_question.id,
                'session_question_start_time':fields.Datetime.now()+relativedelta(seconds=1)
            })
            request.env['bus.bus'].sendone(survey.access_token,{
                'question_start':now.timestamp(),
                'type':'next_question'
            })

            template_values=self._prepare_manage_session_values(survey)
            template_values['is_rpc_call']=True
            returnrequest.env.ref('survey.user_input_session_manage_content')._render(template_values)
        else:
            returnFalse

    @http.route('/survey/session/results/<string:survey_token>',type='json',auth='user',website=True)
    defsurvey_session_results(self,survey_token,**kwargs):
        """Thisrouteiscalledwhenthehostshowsthecurrentquestion'sresults.

        It'snotaregular'request.render'routebecausewehandlethedisplayofresultsusing
        anAJAXrequesttobeabletoincludetheresultsinthecurrentlydisplayedpage."""

        survey=self._fetch_from_token(survey_token)

        ifnotsurveyorsurvey.session_state!='in_progress':
            #noopensession
            returnFalse

        user_input_lines=request.env['survey.user_input.line'].search([
            ('survey_id','=',survey.id),
            ('question_id','=',survey.session_question_id.id),
            ('create_date','>=',survey.session_start_time)
        ])

        returnself._prepare_question_results_values(survey,user_input_lines)

    @http.route('/survey/session/leaderboard/<string:survey_token>',type='json',auth='user',website=True)
    defsurvey_session_leaderboard(self,survey_token,**kwargs):
        """Thisrouteiscalledwhenthehostshowsthecurrentquestion'sattendeesleaderboard.

        It'snotaregular'request.render'routebecausewehandlethedisplayoftheleaderboard
        usinganAJAXrequesttobeabletoincludetheresultsinthecurrentlydisplayedpage."""

        survey=self._fetch_from_token(survey_token)

        ifnotsurveyorsurvey.session_state!='in_progress':
            #noopensession
            return''

        returnrequest.env.ref('survey.user_input_session_leaderboard')._render({
            'animate':True,
            'leaderboard':survey._prepare_leaderboard_values()
        })

    #------------------------------------------------------------
    #QUICKACCESSSURVEYROUTES
    #------------------------------------------------------------

    @http.route('/s',type='http',auth='public',website=True,sitemap=False)
    defsurvey_session_code(self,**post):
        """Rendersthesurveysessioncodepageroute.
        Thispageallowstheusertoenterthesessioncodeofthesurvey.
        Itismainlyusedtoeasesurveyaccessforattendeesinsessionmode."""
        returnrequest.render("survey.survey_session_code")

    @http.route('/s/<string:session_code>',type='http',auth='public',website=True)
    defsurvey_start_short(self,session_code):
        """"Redirectsto'survey_start'routeusingashortenedlink&token.
        Wematchthesession_codeforopensurveys.
        Thisrouteisusedinsurveysessionswhereweneedshortlinksforpeopletotype."""

        survey=self._fetch_from_session_code(session_code)
        ifsurvey:
            returnwerkzeug.utils.redirect("/survey/start/%s"%survey.access_token)

        returnwerkzeug.utils.redirect("/s")

    @http.route('/survey/check_session_code/<string:session_code>',type='json',auth='public',website=True)
    defsurvey_check_session_code(self,session_code):
        """Checksifthegivencodeismatchingasurveysession_code.
        Ifyes,redirectto/s/coderoute.
        Ifnot,returnerror.Theuserisinvitedtotypeagainthecode."""
        survey=self._fetch_from_session_code(session_code)
        ifsurvey:
            return{"survey_url":"/survey/start/%s"%survey.access_token}

        return{"error":"survey_wrong"}

    def_prepare_manage_session_values(self,survey):
        is_last_question=False
        ifsurvey.question_ids:
            most_voted_answers=survey._get_session_most_voted_answers()
            is_last_question=survey._is_last_page_or_question(most_voted_answers,survey.session_question_id)

        values={
            'survey':survey,
            'is_last_question':is_last_question,
        }

        values.update(self._prepare_question_results_values(survey,request.env['survey.user_input.line']))

        returnvalues

    def_prepare_question_results_values(self,survey,user_input_lines):
        """Preparesusefullvaluestodisplayduringthehostsession:

        -question_statistics_graph
          Thegraphdatatodisplaythebarchartforquestionsoftype'choice'
        -input_lines_values
          Theanswervaluestotext/date/datetimequestions
        -answers_validity
          Anarraycontainingtheis_correctvalueforallquestionanswers.
          WeneedthisspecialvariablebecauseofChartjsdatastructure.
          Thelibrarydeterminestheparameters(color/label/...)byonlypassingtheanswer'index'
          (andnottheidoranythingelsewecanidentify).
          Inotherwords,weneedtoknowiftheansweratindex2iscorrectornot.
        -answer_count
          Thenumberofanswerstothecurrentquestion."""

        question=survey.session_question_id
        answers_validity=[]
        if(any(answer.is_correctforanswerinquestion.suggested_answer_ids)):
            answers_validity=[answer.is_correctforanswerinquestion.suggested_answer_ids]
            ifquestion.comment_count_as_answer:
                answers_validity.append(False)

        full_statistics=question._prepare_statistics(user_input_lines)[0]
        input_line_values=[]
        ifquestion.question_typein['char_box','date','datetime']:
            input_line_values=[{
                'id':line.id,
                'value':line['value_%s'%question.question_type]
            }forlineinfull_statistics.get('table_data',request.env['survey.user_input.line'])[:100]]

        return{
            'is_html_empty':is_html_empty,
            'question_statistics_graph':full_statistics.get('graph_data'),
            'input_line_values':input_line_values,
            'answers_validity':json.dumps(answers_validity),
            'answer_count':survey.session_question_answer_count,
            'attendees_count':survey.session_answer_count,
        }
