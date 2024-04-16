flectra.define('survey.session_manage',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
varSurveySessionChart=require('survey.session_chart');
varSurveySessionTextAnswers=require('survey.session_text_answers');
varSurveySessionLeaderBoard=require('survey.session_leaderboard');
varcore=require('web.core');
var_t=core._t;

publicWidget.registry.SurveySessionManage=publicWidget.Widget.extend({
    selector:'.o_survey_session_manage',
    events:{
        'click.o_survey_session_copy':'_onCopySessionLink',
        'click.o_survey_session_navigation_next,.o_survey_session_start':'_onNext',
        'click.o_survey_session_navigation_previous':'_onBack',
        'click.o_survey_session_close':'_onEndSessionClick',
    },

    /**
     *Overriddentosetafewpropertiesthatcomefromthepythontemplaterendering.
     *
     *WealsohandlethetimerIFwe'renot"transitioning",meaningafadeoutoftheprevious
     *$eltothenextquestion(thefactthatwe'retransitioningisintheisRpcCalldata).
     *Ifwe'retransitioning,thetimerishandledmanuallyattheendofthetransition.
     */
    start:function(){
        varself=this;
        this.fadeInOutTime=500;
        returnthis._super.apply(this,arguments).then(function(){
            //generalsurveyprops
            self.surveyId=self.$el.data('surveyId');
            self.surveyAccessToken=self.$el.data('surveyAccessToken');
            self.isStartScreen=self.$el.data('isStartScreen');
            self.isLastQuestion=self.$el.data('isLastQuestion');
            //scoringprops
            self.isScoredQuestion=self.$el.data('isScoredQuestion');
            self.sessionShowLeaderboard=self.$el.data('sessionShowLeaderboard');
            self.hasCorrectAnswers=self.$el.data('hasCorrectAnswers');
            //displayprops
            self.showBarChart=self.$el.data('showBarChart');
            self.showTextAnswers=self.$el.data('showTextAnswers');

            varisRpcCall=self.$el.data('isRpcCall');
            if(!isRpcCall){
                self._startTimer();
                $(document).on('keydown',self._onKeyDown.bind(self));
            }

            self._setupIntervals();
            self._setupCurrentScreen();
            varsetupPromises=[];
            setupPromises.push(self._setupTextAnswers());
            setupPromises.push(self._setupChart());
            setupPromises.push(self._setupLeaderboard());

            returnPromise.all(setupPromises);
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *CopiesthesurveyURLlinktotheclipboard.
     *Weuse'ClipboardJS'toavoidhavingtoprinttheURLinastandardtextinput
     *
     *@param{MouseEvent}ev
     */
    _onCopySessionLink:function(ev){
        varself=this;
        ev.preventDefault();

        var$clipboardBtn=this.$('.o_survey_session_copy');

        $clipboardBtn.popover({
            placement:'right',
            container:'body',
            offset:'0,3',
            content:function(){
                return_t("Copied!");
            }
        });

        varclipboard=newClipboardJS('.o_survey_session_copy',{
            text:function(){
                returnself.$('.o_survey_session_copy_url').val();
            },
            container:this.el
        });

        clipboard.on('success',function(){
            clipboard.destroy();
            $clipboardBtn.popover('show');
            _.delay(function(){
                $clipboardBtn.popover('hide');
            },800);
        });

        clipboard.on('error',function(e){
            clipboard.destroy();
        });
    },

    /**
     *Listenersforkeyboardarrow/spacebarkeys.
     *
     *-39=arrow-right
     *-32=spacebar
     *-37=arrow-left
     *
     *@param{KeyboardEvent}ev
     */
    _onKeyDown:function(ev){
        varkeyCode=ev.keyCode;

        if(keyCode===39||keyCode===32){
            this._onNext(ev);
        }elseif(keyCode===37){
            this._onBack(ev);
        }
    },

    /**
     *Handlesthe"nextscreen"behavior.
     *Ithappenswhenthehostusesthekeyboardkey/buttontogotothenextscreen.
     *Theresultdependsonthecurrentscreenwe'reon.
     *
     *Possiblevaluesofthe"nextscreen"todisplayare:
     *-'userInputs'whengoingfromaquestiontothedisplayofattendees'survey.user_input.line
     *  forthatquestion.
     *-'results'whengoingfromtheinputstotheactualcorrect/incorrectanswersofthat
     *  question.Onlyusedforscoredsimple/multiplechoicequestions.
     *-'leaderboard'(or'leaderboardFinal')whengoingfromthecorrectanswersofaquestionto
     *  theleaderboardofattendees.Onlyusedforscoredsimple/multiplechoicequestions.
     *-Ifit'snotoneoftheabove:wegotothenextquestion,orendthesessionifwe'reon
     *  thelastquestionofthissession.
     *
     *See'_getNextScreen'foradetailedlogic.
     *
     *@param{Event}ev
     */
    _onNext:function(ev){
        ev.preventDefault();

        varscreenToDisplay=this._getNextScreen();

        if(screenToDisplay==='userInputs'){
            this._setShowInputs(true);
            this.$('.o_survey_session_navigation_previous').removeClass('d-none');
        }elseif(screenToDisplay==='results'){
            this._setShowAnswers(true);
            //whenshowingresults,stoprefreshinganswers
            clearInterval(this.resultsRefreshInterval);
            deletethis.resultsRefreshInterval;
            this.$('.o_survey_session_navigation_previous').removeClass('d-none');
        }elseif(['leaderboard','leaderboardFinal'].includes(screenToDisplay)
                   &&!['leaderboard','leaderboardFinal'].includes(this.currentScreen)){
            if(this.isLastQuestion){
                this.$('.o_survey_session_navigation_next').addClass('d-none');
            }
            this.leaderBoard.showLeaderboard(true,this.isScoredQuestion);
        }else{
            if(!this.isLastQuestion){
                this._nextQuestion();
            }elseif(!this.sessionShowLeaderboard){
                //Ifwehavenoleaderboardtoshow,directlyendthesession
                this.$('.o_survey_session_close').click();
            }
        }

        this.currentScreen=screenToDisplay;
    },

    /**
     *Reversebehaviorof'_onNext'.
     *
     *@param{Event}ev
     */
    _onBack:function(ev){
        ev.preventDefault();

        varscreenToDisplay=this._getPreviousScreen();

        if(screenToDisplay==='question'){
            this._setShowInputs(false);
            this.$('.o_survey_session_navigation_previous').addClass('d-none');
        }elseif(screenToDisplay==='userInputs'){
            this._setShowAnswers(false);
            //resumerefreshinganswersifnecessary
            if(!this.resultsRefreshInterval){
                this.resultsRefreshInterval=setInterval(this._refreshResults.bind(this),2000);
            }
        }elseif(screenToDisplay==='results'){
            this.leaderBoard.hideLeaderboard();
            //whenshowingresults,stoprefreshinganswers
            clearInterval(this.resultsRefreshInterval);
            deletethis.resultsRefreshInterval;
        }

        this.currentScreen=screenToDisplay;
    },

    /**
     *Marksthissessionas'done'andredirectstheusertotheresultsbasedontheclickedlink.
     *
     *@param{MouseEvent}ev
     *@private
    */
    _onEndSessionClick:function(ev){
        varself=this;
        ev.preventDefault();

        this._rpc({
            model:'survey.survey',
            method:'action_end_session',
            args:[[this.surveyId]],
        }).then(function(){
            if($(ev.currentTarget).data('showResults')){
                document.location=_.str.sprintf(
                    '/survey/results/%s',
                    self.surveyId
                );
            }else{
                window.history.back();
            }
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Businesslogicthatdeterminesthe'nextscreen'basedonthecurrentscreenandthequestion
     *configuration.
     *
     *Breakdownofusecases:
     *-Ifwe'reonthe'question'screen,andthequestionisscored,wemovetothe'userInputs'
     *-Ifwe'reonthe'question'screenandit'sNOTscored,thenwemoveto
     *    -'results'ifthequestionhascorrect/incorrectanswers
     *      (butnotscored,whichiskindofacornercase)
     *    -'nextQuestion'otherwise
     *-Ifwe'reonthe'userInputs'screenandthequestionhasanswers,wemovetothe'results'
     *-Ifwe'reonthe'results'andthequestionisscored,wemovetothe'leaderboard'
     *-Inallothercases,weshowthenextquestion
     *-(Smallexceptionforthelastquestion:weshowthe"finalleaderboard")
     *
     *(Fordetailsaboutwhichscreenshowswhat,see'_onNext')
     */
    _getNextScreen:function(){
        if(this.currentScreen==='question'&&this.isScoredQuestion){
            return'userInputs';
        }elseif(this.hasCorrectAnswers&&['question','userInputs'].includes(this.currentScreen)){
            return'results';
        }elseif(this.sessionShowLeaderboard){
            if(['question','userInputs','results'].includes(this.currentScreen)&&this.isScoredQuestion){
                return'leaderboard';
            }elseif(this.isLastQuestion){
                return'leaderboardFinal';
            }
        }
        return'nextQuestion';
    },

    /**
     *Reversebehaviorof'_getNextScreen'.
     *
     *@param{Event}ev
     */
    _getPreviousScreen:function(){
        if(this.currentScreen==='userInputs'&&this.isScoredQuestion){
            return'question';
        }elseif(this.currentScreen==='results'||
                  (this.currentScreen==='leaderboard'&&!this.isScoredQuestion)){
            return'userInputs';
        }elseif(this.currentScreen==='leaderboard'&&this.isScoredQuestion){
            return'results';
        }

        returnthis.currentScreen;
    },

    /**
    *Weuseafadein/outmechanismtodisplaythenextquestionofthesession.
    *
    *Thefadeouthappensatthesamemomentasthe_rpctogetthenewquestiontemplate.
    *Whenthey'rebothfinished,weupdatetheHTMLofthiswidgetwiththenewtemplateandthen
    *fadeintheupdatedquestiontotheuser.
    *
    *Thetimer(ifconfigured)startsattheendofthefadeinanimation.
    *
    *@param{MouseEvent}ev
    *@private
    */
    _nextQuestion:function(){
        varself=this;

        this.isStartScreen=false;
        if(this.surveyTimerWidget){
            this.surveyTimerWidget.destroy();
        }

        varresolveFadeOut;
        varfadeOutPromise=newPromise(function(resolve,reject){resolveFadeOut=resolve;});
        this.$el.fadeOut(this.fadeInOutTime,function(){
            resolveFadeOut();
        });

        varnextQuestionPromise=this._rpc({
            route:_.str.sprintf('/survey/session/next_question/%s',self.surveyAccessToken)
        });

        //avoidrefreshingresultswhiletransitioning
        if(this.resultsRefreshInterval){
            clearInterval(this.resultsRefreshInterval);
            deletethis.resultsRefreshInterval;
        }

        Promise.all([fadeOutPromise,nextQuestionPromise]).then(function(results){
            if(results[1]){
                var$renderedTemplate=$(results[1]);
                self.$el.replaceWith($renderedTemplate);
                self.attachTo($renderedTemplate);
                self.$el.fadeIn(self.fadeInOutTime,function(){
                    self._startTimer();
                });
            }elseif(self.sessionShowLeaderboard){
                //Displaylastscreenifleaderboardactivated
                self.isLastQuestion=true;
                self._setupLeaderboard().then(function(){
                    self.$('.o_survey_session_leaderboard_title').text(_t('FinalLeaderboard'));
                    self.$('.o_survey_session_navigation_next').addClass('d-none');
                    self.$('.o_survey_leaderboard_buttons').removeClass('d-none');
                    self.leaderBoard.showLeaderboard(false,false);
                });
            }else{
                self.$('.o_survey_session_close').click();
            }
        });
    },

    /**
     *Willstartthequestiontimersothatthehostmayknowwhenthequestionisdonetodisplay
     *theresultsandtheleaderboard.
     *
     *Ifthequestionisscored,thetimerendingtriggersthedisplayofattendeesinputs.
     */
    _startTimer:function(){
        varself=this;
        var$timer=this.$('.o_survey_timer');

        if($timer.length){
            vartimeLimitMinutes=this.$el.data('timeLimitMinutes');
            vartimer=this.$el.data('timer');
            this.surveyTimerWidget=newpublicWidget.registry.SurveyTimerWidget(this,{
                'timer':timer,
                'timeLimitMinutes':timeLimitMinutes
            });
            this.surveyTimerWidget.attachTo($timer);
            this.surveyTimerWidget.on('time_up',this,function(){
                if(self.currentScreen==='question'&&this.isScoredQuestion){
                    self.$('.o_survey_session_navigation_next').click();
                }
            });
        }
    },

    /**
     *Refreshesthequestionresults.
     *
     *Whatwegetfromthiscall:
     *-The'questionstatistics'usedtodisplaythebarchartwhenappropriate
     *-The'userinputlines'thatareusedtodisplaytext/date/datetimeanswersonthescreen
     *-Thenumberofanswers,usefulforrefreshingtheprogressbar
     */
    _refreshResults:function(){
        varself=this;

        returnthis._rpc({
            route:_.str.sprintf('/survey/session/results/%s',self.surveyAccessToken)
        }).then(function(questionResults){
            if(questionResults){
                self.attendeesCount=questionResults.attendees_count;

                if(self.resultsChart&&questionResults.question_statistics_graph){
                    self.resultsChart.updateChart(JSON.parse(questionResults.question_statistics_graph));
                }elseif(self.textAnswers){
                    self.textAnswers.updateTextAnswers(questionResults.input_line_values);
                }

                varmax=self.attendeesCount>0?self.attendeesCount:1;
                varpercentage=Math.min(Math.round((questionResults.answer_count/max)*100),100);
                self.$('.progress-bar').css('width',`${percentage}%`);

                if(self.attendeesCount&&self.attendeesCount>0){
                    varanswerCount=Math.min(questionResults.answer_count,self.attendeesCount);
                    self.$('.o_survey_session_answer_count').text(answerCount);
                    self.$('.progress-bar.o_survey_session_progress_smallspan').text(
                        `${answerCount}/${self.attendeesCount}`
                    );
                }
            }

            returnPromise.resolve();
        },function(){
            //onfailure,stoprefreshing
            clearInterval(self.resultsRefreshInterval);
            deleteself.resultsRefreshInterval;
        });
    },

    /**
     *Werefreshtheattendeescountevery2secondswhiletheuserisonthestartscreen.
     *
     */
    _refreshAttendeesCount:function(){
        varself=this;

        returnself._rpc({
            model:'survey.survey',
            method:'read',
            args:[[self.surveyId],['session_answer_count']],
        }).then(function(result){
            if(result&&result.length===1){
                self.$('.o_survey_session_attendees_count').text(
                    result[0].session_answer_count
                );
            }
        },function(){
            //onfailure,stoprefreshing
            clearInterval(self.attendeesRefreshInterval);
        });
    },

    /**
     *Forsimple/multiplechoicequestions,wedisplayabarchartwith:
     *
     *-answersofattendees
     *-correct/incorrectanswerswhenrelevant
     *
     *seeSurveySessionChartwidgetdocformoreinformation.
     *
     */
    _setupChart:function(){
        if(this.resultsChart){
            this.resultsChart.setElement(null);
            this.resultsChart.destroy();
            deletethis.resultsChart;
        }

        if(!this.isStartScreen&&this.showBarChart){
            this.resultsChart=newSurveySessionChart(this,{
                questionType:this.$el.data('questionType'),
                answersValidity:this.$el.data('answersValidity'),
                hasCorrectAnswers:this.hasCorrectAnswers,
                questionStatistics:this.$el.data('questionStatistics'),
                showInputs:this.showInputs
            });

            returnthis.resultsChart.attachTo(this.$('.o_survey_session_chart'));
        }else{
            returnPromise.resolve();
        }
    },

    /**
     *Leaderboardofalltheattendeesbasedontheirscore.
     *seeSurveySessionLeaderBoardwidgetdocformoreinformation.
     *
     */
    _setupLeaderboard:function(){
        if(this.leaderBoard){
            this.leaderBoard.setElement(null);
            this.leaderBoard.destroy();
            deletethis.leaderBoard;
        }

        if(this.isScoredQuestion||this.isLastQuestion){
            this.leaderBoard=newSurveySessionLeaderBoard(this,{
                surveyAccessToken:this.surveyAccessToken,
                sessionResults:this.$('.o_survey_session_results')
            });

            returnthis.leaderBoard.attachTo(this.$('.o_survey_session_leaderboard'));
        }else{
            returnPromise.resolve();
        }
    },

    /**
     *Showsattendeesanswersforchar_box/dateanddatetimequestions.
     *seeSurveySessionTextAnswerswidgetdocformoreinformation.
     *
     */
    _setupTextAnswers:function(){
        if(this.textAnswers){
            this.textAnswers.setElement(null);
            this.textAnswers.destroy();
            deletethis.textAnswers;
        }

        if(!this.isStartScreen&&this.showTextAnswers){
            this.textAnswers=newSurveySessionTextAnswers(this,{
                questionType:this.$el.data('questionType')
            });

            returnthis.textAnswers.attachTo(this.$('.o_survey_session_text_answers_container'));
        }else{
            returnPromise.resolve();
        }
    },

    /**
     *Setupthe2refreshintervalsof2secondsforourwidget:
     *-Therefreshofattendeescount(onlyonthestartscreen)
     *-Therefreshofresults(usedforchart/textanswers/progressbar)
     */
    _setupIntervals:function(){
        this.attendeesCount=this.$el.data('attendeesCount')?this.$el.data('attendeesCount'):0;

        if(this.isStartScreen){
            this.attendeesRefreshInterval=setInterval(this._refreshAttendeesCount.bind(this),2000);
        }else{
            if(this.attendeesRefreshInterval){
                clearInterval(this.attendeesRefreshInterval);
            }

            if(!this.resultsRefreshInterval){
                this.resultsRefreshInterval=setInterval(this._refreshResults.bind(this),2000);
            }
        }
    },

    /**
     *Setupcurrentscreenbasedonquestionproperties.
     *Ifit'sanon-scoredquestionwithachart,wedirectlydisplaytheuserinputs.
     */
    _setupCurrentScreen:function(){
        if(this.isStartScreen){
            this.currentScreen='startScreen';
        }elseif(!this.isScoredQuestion&&this.showBarChart){
            this.currentScreen='userInputs';
        }else{
            this.currentScreen='question';
        }

        this._setShowInputs(this.currentScreen==='userInputs');
    },

    /**
     *Whenwegofromthe'question'screentothe'userInputs'screen,wetogglethisboolean
     *andsendtheinformationtothechart.
     *Thechartwillshowattendeessurvey.user_input.lines.
     *
     *@param{Boolean}showInputs
     */
    _setShowInputs(showInputs){
        this.showInputs=showInputs;

        if(this.resultsChart){
            this.resultsChart.setShowInputs(showInputs);
            this.resultsChart.updateChart();
        }
    },

    /**
     *Whenwegofromthe'userInputs'screentothe'results'screen,wetogglethisboolean
     *andsendtheinformationtothechart.
     *Thechartwillshowthequestionsurvey.question.answers.
     *(Onlyusedforsimple/multiplechoicequestions).
     *
     *@param{Boolean}showAnswers
     */
    _setShowAnswers(showAnswers){
        this.showAnswers=showAnswers;

        if(this.resultsChart){
            this.resultsChart.setShowAnswers(showAnswers);
            this.resultsChart.updateChart();
        }
    }
});

returnpublicWidget.registry.SurveySessionManage;

});
