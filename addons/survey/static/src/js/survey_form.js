flectra.define('survey.form',function(require){
'usestrict';

varfield_utils=require('web.field_utils');
varpublicWidget=require('web.public.widget');
vartime=require('web.time');
varcore=require('web.core');
varDialog=require('web.Dialog');
vardom=require('web.dom');
varutils=require('web.utils');

var_t=core._t;

publicWidget.registry.SurveyFormWidget=publicWidget.Widget.extend({
    selector:'.o_survey_form',
    events:{
        'change.o_survey_form_choice_item':'_onChangeChoiceItem',
        'click.o_survey_matrix_btn':'_onMatrixBtnClick',
        'clickbutton[type="submit"]':'_onSubmit',
    },
    custom_events:{
        'breadcrumb_click':'_onBreadcrumbClick',
    },

    //--------------------------------------------------------------------------
    //Widget
    //--------------------------------------------------------------------------

    /**
    *@override
    */
    start:function(){
        varself=this;
        this.fadeInOutDelay=400;
        returnthis._super.apply(this,arguments).then(function(){
            self.options=self.$target.find('form').data();
            self.readonly=self.options.readonly;
            self.selectedAnswers=self.options.selectedAnswers;

            //AddSurveycookietoretrievethesurveyifyouquitthepageandrestartthesurvey.
            if(!utils.get_cookie('survey_'+self.options.surveyToken)){
                utils.set_cookie('survey_'+self.options.surveyToken,self.options.answerToken,60*60*24);
            }

            //Initfields
            if(!self.options.isStartScreen&&!self.readonly){
                self._initTimer();
                self._initBreadcrumb();
            }
            self.$('div.o_survey_form_date').each(function(){
                self._initDateTimePicker($(this));
            });
            self._initChoiceItems();
            self._initTextArea();
            self._focusOnFirstInput();
            //Initeventlistener
            if(!self.readonly){
                $(document).on('keydown',self._onKeyDown.bind(self));
            }
            if(self.options.sessionInProgress&&
                (self.options.isStartScreen||self.options.hasAnswered||self.options.isPageDescription)){
                self.preventEnterSubmit=true;
            }
            self._initSessionManagement();

            //Needsglobalselectorasprogress/navigationarenotwithinthesurveyform,butneed
            //tobeupdatedatthesametime
            self.$surveyProgress=$('.o_survey_progress_wrapper');
            self.$surveyNavigation=$('.o_survey_navigation_wrapper');
            self.$surveyNavigation.find('.o_survey_navigation_submit').on('click',self._onSubmit.bind(self));
        });
    },

    //-------------------------------------------------------------------------
    //Private
    //-------------------------------------------------------------------------

    //Handlers
    //-------------------------------------------------------------------------

    /**
     *Handlekeyboardnavigation:
     *-'enter'or'arrow-right'=>submitform
     *-'arrow-left'=>submitform(butgobackbackwards)
     *-otheralphabeticalcharacter('a','b',...)
     *  Selecttherelatedoptionintheform(ifavailable)
     *
     *@param{Event}event
     */
    _onKeyDown:function(event){
        //Ifuserisansweringatextinput,donothandlekeydown
        if(this.$("textarea").is(":focus")||this.$('input').is(':focus')){
            return;
        }
        //Ifinsessionmodeandquestionalreadyanswered,donothandlekeydown
        if(this.$('fieldset[disabled="disabled"]').length!==0){
            return;
        }

        varself=this;
        varkeyCode=event.keyCode;
        varletter=String.fromCharCode(keyCode).toUpperCase();

        //HandleStart/Next/Submit
        if(keyCode===13||keyCode===39){ //Enterorarrow-right:goNext
            event.preventDefault();
            if(!this.preventEnterSubmit){
                varisFinish=this.$('button[value="finish"]').length!==0;
                this._submitForm({isFinish:isFinish});
            }
        }elseif(keyCode===37){ //arrow-left:previous(ifavailable)
            //It'seasiertoactuallyclickonthebutton(ifintheDOM)asitcontainsnecessary
            //datathatareusedintheeventhandler.
            //Again,globalselectornecessarysincethenavigationisoutsideoftheform.
            $('.o_survey_navigation_submit[value="previous"]').click();
        }elseif(self.options.questionsLayout==='page_per_question'
                   &&letter.match(/[a-z]/i)){
            var$choiceInput=this.$(`input[data-selection-key=${letter}]`);
            if($choiceInput.length===1){
                $choiceInput.prop("checked",!$choiceInput.prop("checked")).trigger('change');

                //Avoidselectionkeytobetypedintothetextboxif'other'isselectedbykey
                event.preventDefault();
            }
        }
    },

    /**
    *Checks,ifthe'other'choiceischecked.Appliesonlyifthecommentcountasanswer.
    *  Ifnotchecked:Clearthecommenttextarea,hideanddisableit
    *  Ifchecked:enablethecommenttextarea,showandfocusonit
    *
    *@private
    *@param{Event}event
    */
    _onChangeChoiceItem:function(event){
        varself=this;
        var$target=$(event.currentTarget);
        var$choiceItemGroup=$target.closest('.o_survey_form_choice');
        var$otherItem=$choiceItemGroup.find('.o_survey_js_form_other_comment');
        var$commentInput=$choiceItemGroup.find('textarea[type="text"]');

        if($otherItem.prop('checked')||$commentInput.hasClass('o_survey_comment')){
            $commentInput.enable();
            $commentInput.closest('.o_survey_comment_container').removeClass('d-none');
            if($otherItem.prop('checked')){
                $commentInput.focus();
            }
        }else{
            $commentInput.val('');
            $commentInput.closest('.o_survey_comment_container').addClass('d-none');
            $commentInput.enable(false);
        }

        var$matrixBtn=$target.closest('.o_survey_matrix_btn');
        if($target.attr('type')==='radio'){
            varisQuestionComplete=false;
            if($matrixBtn.length>0){
                $matrixBtn.closest('tr').find('td').removeClass('o_survey_selected');
                $matrixBtn.addClass('o_survey_selected');
                if(this.options.questionsLayout==='page_per_question'){
                    varsubQuestionsIds=$matrixBtn.closest('table').data('subQuestions');
                    varcompletedQuestions=[];
                    subQuestionsIds.forEach(function(id){
                        if(self.$('tr#'+id).find('input:checked').length!==0){
                            completedQuestions.push(id);
                        }
                    });
                    isQuestionComplete=completedQuestions.length===subQuestionsIds.length;
                }
            }else{
                varpreviouslySelectedAnswer=$choiceItemGroup.find('label.o_survey_selected');
                previouslySelectedAnswer.removeClass('o_survey_selected');

                varnewlySelectedAnswer=$target.closest('label');
                if(newlySelectedAnswer.find('input').val()!==previouslySelectedAnswer.find('input').val()){
                    newlySelectedAnswer.addClass('o_survey_selected');
                    isQuestionComplete=this.options.questionsLayout==='page_per_question';
                }

                //Conditionaldisplay
                if(this.options.questionsLayout!=='page_per_question'){
                    vartreatedQuestionIds=[]; //Neededtoavoidshow(1st'if')thenimmediatelyhide(2nd'if')questionduringconditionalpropagationcascade
                    if(Object.keys(this.options.triggeredQuestionsByAnswer).includes(previouslySelectedAnswer.find('input').val())){
                        //Hideandcleardependingquestion
                        this.options.triggeredQuestionsByAnswer[previouslySelectedAnswer.find('input').val()].forEach(function(questionId){
                            vardependingQuestion=$('.js_question-wrapper#'+questionId);

                            dependingQuestion.addClass('d-none');
                            self._clearQuestionInputs(dependingQuestion);

                            treatedQuestionIds.push(questionId);
                        });
                        //Removeanswerfromselectedanswer
                        self.selectedAnswers.splice(self.selectedAnswers.indexOf(parseInt($target.val())),1);
                    }
                    if(Object.keys(this.options.triggeredQuestionsByAnswer).includes($target.val())){
                        //Displaydependingquestion
                        this.options.triggeredQuestionsByAnswer[$target.val()].forEach(function(questionId){
                            if(!treatedQuestionIds.includes(questionId)){
                                vardependingQuestion=$('.js_question-wrapper#'+questionId);
                                dependingQuestion.removeClass('d-none');

                                //Addanswertoselectedanswer
                                self.selectedAnswers.push(parseInt($target.val()));
                            }
                        });
                    }
                }
            }
            //AutoSubmitForm
            varisLastQuestion=this.$('button[value="finish"]').length!==0;
            varquestionHasComment=$target.closest('.o_survey_form_choice').find('.o_survey_comment').length!==0
                                        ||$target.hasClass('o_survey_js_form_other_comment');
            if(!isLastQuestion&&this.options.usersCanGoBack&&isQuestionComplete&&!questionHasComment){
                this._submitForm({});
            }
        }else{ //$target.attr('type')==='checkbox'
            if($matrixBtn.length>0){
                $matrixBtn.toggleClass('o_survey_selected',!$matrixBtn.hasClass('o_survey_selected'));
            }else{
                var$label=$target.closest('label');
                $label.toggleClass('o_survey_selected',!$label.hasClass('o_survey_selected'));

                //Conditionaldisplay
                if(this.options.questionsLayout!=='page_per_question'&&Object.keys(this.options.triggeredQuestionsByAnswer).includes($target.val())){
                    varisInputSelected=$label.hasClass('o_survey_selected');
                    //Hideandclearordisplaydependingquestion
                    this.options.triggeredQuestionsByAnswer[$target.val()].forEach(function(questionId){
                        vardependingQuestion=$('.js_question-wrapper#'+questionId);
                        dependingQuestion.toggleClass('d-none',!isInputSelected);
                        if(!isInputSelected){
                            self._clearQuestionInputs(dependingQuestion);
                        }
                    });
                    //Add/removeanswerto/fromselectedanswer
                    if(!isInputSelected){
                        self.selectedAnswers.splice(self.selectedAnswers.indexOf(parseInt($target.val())),1);
                    }else{
                        self.selectedAnswers.push(parseInt($target.val()));
                    }
                }
            }
        }
    },

    _onMatrixBtnClick:function(event){
        if(this.readonly){
            return;
        }

        var$target=$(event.currentTarget);
        var$input=$target.find('input');
        if($input.attr('type')==='radio'){
            $input.prop("checked",true).trigger('change');
        }else{
            $input.prop("checked",!$input.prop("checked")).trigger('change');
        }
    },

    _onSubmit:function(event){
        event.preventDefault();
        varoptions={};
        var$target=$(event.currentTarget);
        if($target.val()==='previous'){
            options.previousPageId=$target.data('previousPageId');
        }elseif($target.val()==='finish'){
            options.isFinish=true;
        }
        this._submitForm(options);
    },

    //CustomEvents
    //-------------------------------------------------------------------------

    _onBreadcrumbClick:function(event){
        this._submitForm({'previousPageId':event.data.previousPageId});
    },

    /**
     *Welistento'next_question'and'end_session'eventstoloadthenext
     *pageofthesurveyautomatically,basedonthehostpacing.
     *
     *Ifthetriggeris'next_question',wehandlesomeextracomputationtofind
     *asuitable"fadeInOutDelay"basedonthedelaybetweenthetimeofthequestion
     *changebythehostandthetimeofreceptionoftheevent.
     *Thiswillallowustoaccountforalittlebitofserverlag(upto1second)
     *whilegivingeveryoneafairexperienceonthequiz.
     *
     *e.g1:
     *-Thehostswitchesthequestion
     *-Wereceivetheevent200mslaterduetoserverlag
     *-->ThefadeInOutDelaywillbe400ms(200msdelay+400ms*2fadeinfadeout)
     *
     *e.g2:
     *-Thehostswitchesthequestion
     *-Wereceivetheevent600mslaterduetobiggerserverlag
     *-->ThefadeInOutDelaywillbe200ms(600msdelay+200ms*2fadeinfadeout)
     *
     *@private
     *@param{Array[]}notificationsstructuredasspecifiedbythebusfeature
     */
    _onNotification:function(notifications){
        varnextPageEvent=false;
        if(notifications&&notifications.length!==0){
            notifications.forEach(function(notification){
                if(notification.length>=2){
                    varevent=notification[1];
                    if(event.type==='next_question'||
                        event.type==='end_session'){
                        nextPageEvent=event;
                    }
                }
            });
        }

        if(this.options.isStartScreen&&nextPageEvent.type==='end_session'){
            //canhappenwhentriggeringthesamesurveysessionmultipletimes
            //wereceivedan"old"end_sessioneventthatneedstobeignored
            return;
        }

        if(nextPageEvent){
            if(nextPageEvent.type==='next_question'){
                varserverDelayMS=moment.utc().valueOf()-moment.unix(nextPageEvent.question_start).utc().valueOf();
                if(serverDelayMS<0){
                    serverDelayMS=0;
                }elseif(serverDelayMS>1000){
                    serverDelayMS=1000;
                }
                this.fadeInOutDelay=(1000-serverDelayMS)/2;
            }else{
                this.fadeInOutDelay=400;
            }

            this.$('.o_survey_main_title:visible').fadeOut(400);

            this.preventEnterSubmit=false;
            this.readonly=false;
            this._nextScreen(
                this._rpc({
                    route:`/survey/next_question/${this.options.surveyToken}/${this.options.answerToken}`,
                }),{
                    initTimer:true,
                    isFinish:nextPageEvent.type==='end_session'
                }
            );
        }
    },

    //SUBMIT
    //-------------------------------------------------------------------------

    /**
    *Thisfunctionwillsendajsonrpccalltotheserverto
    *-startthesurvey(ifweareonstartscreen)
    *-submittheanswersofthecurrentpage
    *Beforesubmittingtheanswers,theyarefirstvalidatedtoavoidlatencyfromtheserver
    *andallowafadeout/fadeintransitionofthenextquestion.
    *
    *@param{Array}[options]
    *@param{Integer}[options.previousPageId]navigatestopageid
    *@param{Boolean}[options.skipValidation]skipsJSvalidation
    *@param{Boolean}[options.initTime]willforcethere-initofthetimerafternext
    *  screentransition
    *@param{Boolean}[options.isFinish]fadesoutbreadcrumbandtimer
    *@private
    */
    _submitForm:function(options){
        varself=this;
        varparams={};
        if(options.previousPageId){
            params.previous_page_id=options.previousPageId;
        }
        varroute="/survey/submit";

        if(this.options.isStartScreen){
            route="/survey/begin";
            //Hidesurveytitlein'page_per_question'layout:ittakestoomuchspace
            if(this.options.questionsLayout==='page_per_question'){
                this.$('.o_survey_main_title').fadeOut(400);
            }
        }else{
            var$form=this.$('form');
            varformData=newFormData($form[0]);

            if(!options.skipValidation){
                //Validationpresubmit
                if(!this._validateForm($form,formData)){
                    return;
                }
            }

            this._prepareSubmitValues(formData,params);
        }

        //preventuserfromsubmittingmoretimesusingenterkey
        this.preventEnterSubmit=true;

        if(this.options.sessionInProgress){
            //resetthefadeInOutDelaywhenattendeeissubmittingform
            this.fadeInOutDelay=400;
            //preventuserfromclickingonmatrixoptionswhenformissubmitted
            this.readonly=true;
        }

        varsubmitPromise=self._rpc({
            route:_.str.sprintf('%s/%s/%s',route,self.options.surveyToken,self.options.answerToken),
            params:params,
        });
        this._nextScreen(submitPromise,options);
    },

    /**
     *Willfadeout/fadeinthenextscreenbasedonpassedpromiseandoptions.
     *
     *@param{Promise}nextScreenPromise
     *@param{Object}optionssee'_submitForm'fordetails
     */
    _nextScreen:function(nextScreenPromise,options){
        varself=this;

        varresolveFadeOut;
        varfadeOutPromise=newPromise(function(resolve,reject){resolveFadeOut=resolve;});

        varselectorsToFadeout=['.o_survey_form_content'];
        if(options.isFinish){
            selectorsToFadeout.push('.breadcrumb','.o_survey_timer');
            utils.set_cookie('survey_'+self.options.surveyToken,'',-1); //deletecookie
        }
        self.$(selectorsToFadeout.join(',')).fadeOut(this.fadeInOutDelay,function(){
            resolveFadeOut();
        });

        Promise.all([fadeOutPromise,nextScreenPromise]).then(function(results){
            returnself._onNextScreenDone(results[1],options);
        });
    },

    /**
     *Handleserversidevalidationanddisplayeventualerrormessages.
     *
     *@param{string}resulttheHTMLresultofthescreentodisplay
     *@param{Object}optionssee'_submitForm'fordetails
     */
   _onNextScreenDone:function(result,options){
        varself=this;

        if(!(options&&options.isFinish)
            &&!this.options.sessionInProgress){
            this.preventEnterSubmit=false;
        }

        if(result&&!result.error){
            this.$(".o_survey_form_content").empty();
            this.$(".o_survey_form_content").html(result.survey_content);

            if(result.survey_progress&&this.$surveyProgress.length!==0){
                this.$surveyProgress.html(result.survey_progress);
            }elseif(options.isFinish&&this.$surveyProgress.length!==0){
                this.$surveyProgress.remove();
            }

            if(result.survey_navigation&&this.$surveyNavigation.length!==0){
                this.$surveyNavigation.html(result.survey_navigation);
                this.$surveyNavigation.find('.o_survey_navigation_submit').on('click',self._onSubmit.bind(self));
            }

            //Hidetimerifendscreen(ifpage_per_questionincaseofconditionalquestions)
            if(self.options.questionsLayout==='page_per_question'&&this.$('.o_survey_finished').length>0){
                options.isFinish=true;
            }

            this.$('div.o_survey_form_date').each(function(){
                self._initDateTimePicker($(this));
            });
            if(this.options.isStartScreen||(options&&options.initTimer)){
                this._initTimer();
                this.options.isStartScreen=false;
            }else{
                if(this.options.sessionInProgress&&this.surveyTimerWidget){
                    this.surveyTimerWidget.destroy();
                }
            }
            if(options&&options.isFinish){
                this._initResultWidget();
                if(this.surveyBreadcrumbWidget){
                    this.$('.o_survey_breadcrumb_container').addClass('d-none');
                    this.surveyBreadcrumbWidget.destroy();
                }
                if(this.surveyTimerWidget){
                    this.surveyTimerWidget.destroy();
                }
            }else{
                this._updateBreadcrumb();
            }
            self._initChoiceItems();
            self._initTextArea();

            if(this.options.sessionInProgress&&this.$('.o_survey_form_content_data').data('isPageDescription')){
                //prevententersubmitifwe'reonapagedescription(thereisnothingtosubmit)
                this.preventEnterSubmit=true;
            }

            this.$('.o_survey_form_content').fadeIn(this.fadeInOutDelay);
            $("html,body").animate({scrollTop:0},this.fadeInOutDelay);
            self._focusOnFirstInput();
        }
        elseif(result&&result.fields&&result.error==='validation'){
            this.$('.o_survey_form_content').fadeIn(0);
            this._showErrors(result.fields);
        }else{
            var$errorTarget=this.$('.o_survey_error');
            $errorTarget.removeClass("d-none");
            this._scrollToError($errorTarget);
        }
    },

    //VALIDATIONTOOLS
    //-------------------------------------------------------------------------
    /**
    *Validationisdoneinfrontendbeforesubmittoavoidlatencyfromtheserver.
    *Ifthevalidationisincorrect,theerrorsaredisplayedbeforesubmittingand
    *fadein/outofsubmitisavoided.
    *
    *Eachquestiontypegetsitsownvalidationprocess.
    *
    *Thereisaspecialusecaseforthe'required'questions,whereweusetheconstraint
    *errormessagethatcomesfromthequestionconfiguration('constr_error_msg'field).
    *
    *@private
    */
    _validateForm:function($form,formData){
        varself=this;
        varerrors={};
        varvalidationEmailMsg=_t("Thisanswermustbeanemailaddress.");
        varvalidationDateMsg=_t("Thisisnotadate");

        this._resetErrors();

        vardata={};
        formData.forEach(function(value,key){
            data[key]=value;
        });

        varinactiveQuestionIds=this.options.sessionInProgress?[]:this._getInactiveConditionalQuestionIds();

        $form.find('[data-question-type]').each(function(){
            var$input=$(this);
            var$questionWrapper=$input.closest(".js_question-wrapper");
            varquestionId=$questionWrapper.attr('id');

            //Ifquestionisinactive,skipvalidation.
            if(inactiveQuestionIds.includes(parseInt(questionId))){
                return;
            }

            varquestionRequired=$questionWrapper.data('required');
            varconstrErrorMsg=$questionWrapper.data('constrErrorMsg');
            varvalidationErrorMsg=$questionWrapper.data('validationErrorMsg');
            switch($input.data('questionType')){
                case'char_box':
                    if(questionRequired&&!$input.val()){
                        errors[questionId]=constrErrorMsg;
                    }elseif($input.val()&&$input.attr('type')==='email'&&!self._validateEmail($input.val())){
                        errors[questionId]=validationEmailMsg;
                    }else{
                        varlengthMin=$input.data('validationLengthMin');
                        varlengthMax=$input.data('validationLengthMax');
                        varlength=$input.val().length;
                        if(lengthMin&&(lengthMin>length||length>lengthMax)){
                            errors[questionId]=validationErrorMsg;
                        }
                    }
                    break;
                case'numerical_box':
                    if(questionRequired&&!data[questionId]){
                        errors[questionId]=constrErrorMsg;
                    }else{
                        varfloatMin=$input.data('validationFloatMin');
                        varfloatMax=$input.data('validationFloatMax');
                        varvalue=parseFloat($input.val());
                        if(floatMin&&(floatMin>value||value>floatMax)){
                            errors[questionId]=validationErrorMsg;
                        }
                    }
                    break;
                case'date':
                case'datetime':
                    if(questionRequired&&!data[questionId]){
                        errors[questionId]=constrErrorMsg;
                    }elseif(data[questionId]){
                        vardatetimepickerFormat=$input.data('questionType')==='datetime'?time.getLangDatetimeFormat():time.getLangDateFormat();
                        varmomentDate=moment($input.val(),datetimepickerFormat);
                        if(!momentDate.isValid()){
                            errors[questionId]=validationDateMsg;
                        }else{
                            var$dateDiv=$questionWrapper.find('.o_survey_form_date');
                            varmaxDate=$dateDiv.data('maxdate');
                            varminDate=$dateDiv.data('mindate');
                            if((maxDate&&momentDate.isAfter(moment(maxDate)))
                                    ||(minDate&&momentDate.isBefore(moment(minDate)))){
                                errors[questionId]=validationErrorMsg;
                            }
                        }
                    }
                    break;
                case'simple_choice_radio':
                case'multiple_choice':
                    if(questionRequired){
                        var$textarea=$questionWrapper.find('textarea');
                        if(!data[questionId]){
                            errors[questionId]=constrErrorMsg;
                        }elseif(data[questionId]==='-1'&&!$textarea.val()){
                            //ifotherhasbeencheckedandvalueisnull
                            errors[questionId]=constrErrorMsg;
                        }
                    }
                    break;
                case'matrix':
                    if(questionRequired){
                        varsubQuestionsIds=$questionWrapper.find('table').data('subQuestions');
                        subQuestionsIds.forEach(function(id){
                            if(!((questionId+'_'+id)indata)){
                                errors[questionId]=constrErrorMsg;
                            }
                        });
                    }
                    break;
            }
        });
        if(_.keys(errors).length>0){
            this._showErrors(errors);
            returnfalse;
        }
        returntrue;
    },

    /**
    *Checkiftheemailhasan'@',aleftpartandarightpart
    *@private
    */
    _validateEmail:function(email){
        varemailParts=email.split('@');
        returnemailParts.length===2&&emailParts[0]&&emailParts[1];
    },

    //PREPARESUBMITTOOLS
    //-------------------------------------------------------------------------
    /**
    *Foreachtypeofquestion,extracttheanswerfrominputsortextarea(commentoranswer)
    *
    *
    *@private
    *@param{Event}event
    */
    _prepareSubmitValues:function(formData,params){
        varself=this;
        formData.forEach(function(value,key){
            switch(key){
                case'csrf_token':
                case'token':
                case'page_id':
                case'question_id':
                    params[key]=value;
                    break;
            }
        });

        //Getallquestionanswersbyquestiontype
        this.$('[data-question-type]').each(function(){
            switch($(this).data('questionType')){
                case'text_box':
                case'char_box':
                case'numerical_box':
                    params[this.name]=this.value;
                    break;
                case'date':
                    params=self._prepareSubmitDates(params,this.name,this.value,false);
                    break;
                case'datetime':
                    params=self._prepareSubmitDates(params,this.name,this.value,true);
                    break;
                case'simple_choice_radio':
                case'multiple_choice':
                    params=self._prepareSubmitChoices(params,$(this),$(this).data('name'));
                    break;
                case'matrix':
                    params=self._prepareSubmitAnswersMatrix(params,$(this));
                    break;
            }
        });
    },

    /**
    *  Preparedateanswerbeforesubmittingform.
    *  ConvertdatevaluefromclientcurrenttimezonetoUTCDatetocorrespondtotheserverformat.
    *  returnparams={'dateQuestionId':'2019-05-23','datetimeQuestionId':'2019-05-2314:05:12'}
    */
    _prepareSubmitDates:function(params,questionId,value,isDateTime){
        varmomentDate=isDateTime?field_utils.parse.datetime(value,null,{timezone:true}):field_utils.parse.date(value);
        varformattedDate=momentDate?momentDate.toJSON():'';
        params[questionId]=formattedDate;
        returnparams;
    },

    /**
    *  Preparechoiceanswerbeforesubmittingform.
    *  Iftheanswerisnotthe'commentselection'(=Other),callsthe_prepareSubmitAnswermethodtoaddtheanswertotheparams
    *  Ifthereisacommentlinkedtothatquestion,callsthe_prepareSubmitCommentmethodtoaddthecommenttotheparams
    */
    _prepareSubmitChoices:function(params,$parent,questionId){
        varself=this;
        $parent.find('input:checked').each(function(){
            if(this.value!=='-1'){
                params=self._prepareSubmitAnswer(params,questionId,this.value);
            }
        });
        params=self._prepareSubmitComment(params,$parent,questionId,false);
        returnparams;
    },


    /**
    *  Preparematrixanswersbeforesubmittingform.
    *  Thismethodaddsmatrixanswersonebyoneandaddcommentifanytoaparamskey,valuelike:
    *  params={'matrixQuestionId':{'rowId1':[colId1,colId2,...],'rowId2':[colId1,colId3,...],'comment':comment}}
    */
    _prepareSubmitAnswersMatrix:function(params,$matrixTable){
        varself=this;
        $matrixTable.find('input:checked').each(function(){
            params=self._prepareSubmitAnswerMatrix(params,$matrixTable.data('name'),$(this).data('rowId'),this.value);
        });
        params=self._prepareSubmitComment(params,$matrixTable.closest('.js_question-wrapper'),$matrixTable.data('name'),true);
        returnparams;
    },

    /**
    *  Prepareanswerbeforesubmittingformifquestiontypeismatrix.
    *  Thismethodregroupsanswersbyquestionandbyrowtomakeanobjectlike:
    *  params={'matrixQuestionId':{'rowId1':[colId1,colId2,...],'rowId2':[colId1,colId3,...]}}
    */
    _prepareSubmitAnswerMatrix:function(params,questionId,rowId,colId,isComment){
        varvalue=questionIdinparams?params[questionId]:{};
        if(isComment){
            value['comment']=colId;
        }else{
            if(rowIdinvalue){
                value[rowId].push(colId);
            }else{
                value[rowId]=[colId];
            }
        }
        params[questionId]=value;
        returnparams;
    },

    /**
    *  Prepareanswerbeforesubmittingform(anykindofanswer-exceptMatrix-).
    *  Thismethodregroupsanswersbyquestion.
    *  LonelyansweraredirectlyassignedtoquestionId.Multipleanswersareregroupedinanarray:
    *  params={'questionId1':lonelyAnswer,'questionId2':[multipleAnswer1,multipleAnswer2,...]}
    */
    _prepareSubmitAnswer:function(params,questionId,value){
        if(questionIdinparams){
            if(params[questionId].constructor===Array){
                params[questionId].push(value);
            }else{
                params[questionId]=[params[questionId],value];
            }
        }else{
            params[questionId]=value;
        }
        returnparams;
    },

    /**
    *  Preparecommentbeforesubmittingform.
    *  Thismethodextractthecomment,encapsulateitinadictandcallsthe_prepareSubmitAnswermethods
    *  withthenewvalue.Attheend,theresultlookslike:
    *  params={'questionId1':{'comment':commentValue},'questionId2':[multipleAnswer1,{'comment':commentValue},...]}
    */
    _prepareSubmitComment:function(params,$parent,questionId,isMatrix){
        varself=this;
        $parent.find('textarea').each(function(){
            if(this.value){
                varvalue={'comment':this.value};
                if(isMatrix){
                    params=self._prepareSubmitAnswerMatrix(params,questionId,this.name,this.value,true);
                }else{
                    params=self._prepareSubmitAnswer(params,questionId,value);
                }
            }
        });
        returnparams;
    },

    //INITFIELDSTOOLS
    //-------------------------------------------------------------------------

   /**
    *Willallowthetextareatoresizeoncarriagereturninsteadofshowingscrollbar.
    */
    _initTextArea:function(){
        this.$('textarea').each(function(){
            dom.autoresize($(this));
        });
    },

    _initChoiceItems:function(){
        this.$("input[type='radio'],input[type='checkbox']").each(function(){
            varmatrixBtn=$(this).parents('.o_survey_matrix_btn');
            if($(this).prop("checked")){
                var$target=matrixBtn.length>0?matrixBtn:$(this).closest('label');
                $target.addClass('o_survey_selected');
            }
        });
    },

    /**
     *Willinitializethebreadcrumbwidgetthathandlesnavigationtoapreviouslyfilledinpage.
     *
     *@private
     */
    _initBreadcrumb:function(){
        var$breadcrumb=this.$('.o_survey_breadcrumb_container');
        varpageId=this.$('input[name=page_id]').val();
        if($breadcrumb.length){
            this.surveyBreadcrumbWidget=newpublicWidget.registry.SurveyBreadcrumbWidget(this,{
                'canGoBack':$breadcrumb.data('canGoBack'),
                'currentPageId':pageId?parseInt(pageId):0,
                'pages':$breadcrumb.data('pages'),
            });
            this.surveyBreadcrumbWidget.appendTo($breadcrumb);
            $breadcrumb.removeClass('d-none'); //hiddenbydefaulttoavoidhavingghostdivinstartscreen
        }
    },

    /**
     *Calledaftersurveysubmittoupdatethebreadcrumbtotherightpage.
     */
    _updateBreadcrumb:function(){
        if(this.surveyBreadcrumbWidget){
            varpageId=this.$('input[name=page_id]').val();
            this.surveyBreadcrumbWidget.updateBreadcrumb(parseInt(pageId));
        }else{
            this._initBreadcrumb();
        }
    },

    /**
     *Willhandlebusspecificbehaviorforsurvey'sessions'
     *
     *@private
     */
    _initSessionManagement:function(){
        varself=this;
        if(this.options.surveyToken&&this.options.sessionInProgress){
            this.call('bus_service','addChannel',this.options.surveyToken);
            this.call('bus_service','startPolling');

            if(!this._checkIsMasterTab()){
                this.shouldReloadMasterTab=true;
                this.masterTabCheckInterval=setInterval(function(){
                     if(self._checkIsMasterTab()){
                        clearInterval(self.masterTabCheckInterval);
                     }
                },2000);
            }

            this.call('bus_service','onNotification',this,this._onNotification);
        }
    },

    _initTimer:function(){
        if(this.surveyTimerWidget){
            this.surveyTimerWidget.destroy();
        }

        varself=this;
        var$timerData=this.$('.o_survey_form_content_data');
        varquestionTimeLimitReached=$timerData.data('questionTimeLimitReached');
        vartimeLimitMinutes=$timerData.data('timeLimitMinutes');
        varhasAnswered=$timerData.data('hasAnswered');
        constserverTime=$timerData.data('serverTime');

        if(!questionTimeLimitReached&&!hasAnswered&&timeLimitMinutes){
            vartimer=$timerData.data('timer');
            var$timer=$('<span>',{
                class:'o_survey_timer'
            });
            this.$('.o_survey_timer_container').append($timer);
            this.surveyTimerWidget=newpublicWidget.registry.SurveyTimerWidget(this,{
                'serverTime':serverTime,
                'timer':timer,
                'timeLimitMinutes':timeLimitMinutes
            });
            this.surveyTimerWidget.attachTo($timer);
            this.surveyTimerWidget.on('time_up',this,function(ev){
                self._submitForm({
                    'skipValidation':true,
                    'isFinish':!this.options.sessionInProgress
                });
            });
        }
    },

    /**
    *Initializedatetimepickerincorrectformatandwithconstraints
    */
    _initDateTimePicker:function($dateGroup){
        vardisabledDates=[];
        varquestionType=$dateGroup.find('input').data('questionType');
        varminDateData=$dateGroup.data('mindate');
        varmaxDateData=$dateGroup.data('maxdate');

        vardatetimepickerFormat=questionType==='datetime'?time.getLangDatetimeFormat():time.getLangDateFormat();

        varminDate=minDateData
            ?this._formatDateTime(minDateData,datetimepickerFormat)
            :moment({y:1000});

        varmaxDate=maxDateData
            ?this._formatDateTime(maxDateData,datetimepickerFormat)
            :moment().add(200,"y");

        if(questionType==='date'){
            //Includeminandmaxdateinselectablevalues
            maxDate=moment(maxDate).add(1,"d");
            minDate=moment(minDate).subtract(1,"d");
            disabledDates=[minDate,maxDate];
        }

        $dateGroup.datetimepicker({
            format:datetimepickerFormat,
            minDate:minDate,
            maxDate:maxDate,
            disabledDates:disabledDates,
            useCurrent:false,
            viewDate:moment(newDate()).hours(minDate.hours()).minutes(minDate.minutes()).seconds(minDate.seconds()).milliseconds(minDate.milliseconds()),
            calendarWeeks:true,
            icons:{
                time:'fafa-clock-o',
                date:'fafa-calendar',
                next:'fafa-chevron-right',
                previous:'fafa-chevron-left',
                up:'fafa-chevron-up',
                down:'fafa-chevron-down',
            },
            locale:moment.locale(),
            allowInputToggle:true,
        });
        $dateGroup.on('error.datetimepicker',function(err){
            if(err.date){
                if(err.date<minDate){
                    Dialog.alert(this,_t('Thedateyouselectedislowerthantheminimumdate:')+minDate.format(datetimepickerFormat));
                }

                if(err.date>maxDate){
                    Dialog.alert(this,_t('Thedateyouselectedisgreaterthanthemaximumdate:')+maxDate.format(datetimepickerFormat));
                }
            }
            returnfalse;
        });
    },

    _formatDateTime:function(datetimeValue,format){
        returnmoment(field_utils.format.datetime(moment(datetimeValue),null,{timezone:true}),format);
    },

    _initResultWidget:function(){
        var$result=this.$('.o_survey_result');
        if($result.length){
            this.surveyResultWidget=newpublicWidget.registry.SurveyResultWidget(this);
            this.surveyResultWidget.attachTo($result);
            $result.fadeIn(this.fadeInOutDelay);
        }
    },

   /**
    *Willautomaticallyfocusonthefirstinputtoallowtheusertocompletedirectlythesurvey,
    *withouthavingtomanuallygetthefocus(onlyiftheinputhastherighttype-canwritesomethinginside-)
    */
    _focusOnFirstInput:function(){
        var$firstTextInput=this.$('.js_question-wrapper').first() //Takefirstquestion
                              .find("input[type='text'],input[type='number'],textarea") //get'text'inputs
                              .filter('.form-control') //neededfortheauto-resize
                              .not('.o_survey_comment'); //removeinputsforcommentsthatdoesnotcountasanswers
        if($firstTextInput.length>0){
            $firstTextInput.focus();
        }
    },

    /**
    *Thismethodcheckifthecurrenttabisthemastertabatthebuslevel.
    *Ifnot,thesurveycouldnotreceivenextquestionnotificationanymorefromsessionmanager.
    *Wethenasktheparticipanttocloseallothertabsonthesamehostnamebeforelettingthemcontinue.
    *
    *@private
    */
    _checkIsMasterTab:function(){
        varisMasterTab=this.call('bus_service','isMasterTab');
        var$errorModal=this.$('#MasterTabErrorModal');
        if(isMasterTab){
            //Forcereloadthepagewhensurveyisreadytobefollowed,toforcerestartlongpolling
            if(this.shouldReloadMasterTab){
                window.location.reload();
            }
           returntrue;
        }elseif(!$errorModal.modal._isShown){
            $errorModal.find('.text-danger').text(window.location.hostname);
            $errorModal.modal('show');
        }
        returnfalse;
    },

    //CONDITIONALQUESTIONSMANAGEMENTTOOLS
    //-------------------------------------------------------------------------

    /**
    *Clear/Un-selectalltheinputfromthegivenquestion
    *+propagateconditionalhierarchybytriggeringchangeonchoiceinputs.
    *
    *@private
    */
    _clearQuestionInputs:function(question){
        question.find('input').each(function(){
            if($(this).attr('type')==='text'||$(this).attr('type')==='number'){
                $(this).val('');
            }elseif($(this).prop('checked')){
                $(this).prop('checked',false).change();
            }
        });
        question.find('textarea').val('');
    },

    /**
    *Getquestionsthatarenotsupposedtobeansweredbytheuser.
    *Thosearetheonestriggeredbyanswersthattheuserdidnotselected.
    *
    *@private
    */
    _getInactiveConditionalQuestionIds:function(){
        varself=this;
        varinactiveQuestionIds=[];
        if(this.options.triggeredQuestionsByAnswer){
            Object.keys(this.options.triggeredQuestionsByAnswer).forEach(function(answerId){
                if(!self.selectedAnswers.includes(parseInt(answerId))){
                     self.options.triggeredQuestionsByAnswer[answerId].forEach(function(questionId){
                        inactiveQuestionIds.push(questionId);
                     });
                }
            });
        }
        returninactiveQuestionIds;
    },

    //ERRORSTOOLS
    //-------------------------------------------------------------------------

    _showErrors:function(errors){
        varself=this;
        varerrorKeys=_.keys(errors);
        _.each(errorKeys,function(key){
            self.$("#"+key+'>.o_survey_question_error').append($('<p>',{text:errors[key]})).addClass("slide_in");
            if(errorKeys[0]===key){
                self._scrollToError(self.$('.js_question-wrapper#'+key));
            }
        });
    },

    _scrollToError:function($target){
        varscrollLocation=$target.offset().top;
        varnavbarHeight=$('.o_main_navbar').height();
        if(navbarHeight){
            //Inoverflowauto,scrollLocationoftargetcanbenegativeiftargetisoutofscreen(upside)
            scrollLocation=scrollLocation>=0?scrollLocation-navbarHeight:scrollLocation+navbarHeight;
        }
        varscrollinside=$("#wrapwrap").scrollTop();
        $('#wrapwrap').animate({
            scrollTop:scrollinside+scrollLocation
        },500);
    },

    /**
    *CleanallformerrorsinordertocleanDOMbeforeanewvalidation
    */
    _resetErrors:function(){
        this.$('.o_survey_question_error').empty().removeClass('slide_in');
        this.$('.o_survey_error').addClass('d-none');
    },

});

returnpublicWidget.registry.SurveyFormWidget;

});
