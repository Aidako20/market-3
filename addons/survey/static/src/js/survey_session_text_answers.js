flectra.define('survey.session_text_answers',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
varcore=require('web.core');
vartime=require('web.time');
varSESSION_CHART_COLORS=require('survey.session_colors');

varQWeb=core.qweb;

publicWidget.registry.SurveySessionTextAnswers=publicWidget.Widget.extend({
    xmlDependencies:['/survey/static/src/xml/survey_session_text_answer_template.xml'],
    init:function(parent,options){
        this._super.apply(this,arguments);

        this.answerIds=[];
        this.questionType=options.questionType;
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Addstheattendeesanswersonthescreen.
     *Thisisusedforchar_box/dateanddatetimequestions.
     *
     *WeusesometrickswithjQueryforwoweffect:
     *-forceawidthontheexternaldivcontainer,toreservespaceforthatanswer
     *-settheactualwidthoftheanswer,andenableacsswidthanimation
     *-settheopacityto1,andenableacssopacityanimation
     *
     *@param{Array}inputLineValuesarrayofsurvey.user_input.linerecordsintheform
     *  {id:line.id,value:line.[value_char_box/value_date/value_datetime]}
     */
    updateTextAnswers:function(inputLineValues){
        varself=this;

        inputLineValues.forEach(function(inputLineValue){
            if(!self.answerIds.includes(inputLineValue.id)&&inputLineValue.value){
                vartextValue=inputLineValue.value;
                if(self.questionType==='char_box'){
                    textValue=textValue.length>25?
                        textValue.substring(0,22)+'...':
                        textValue;
                }elseif(self.questionType==='date'){
                    textValue=moment(textValue).format(time.getLangDateFormat());
                }elseif(self.questionType==='datetime'){
                    textValue=moment(textValue).format(time.getLangDatetimeFormat());
                }

                var$textAnswer=$(QWeb.render('survey.survey_session_text_answer',{
                    value:textValue,
                    borderColor:`rgb(${SESSION_CHART_COLORS[self.answerIds.length%10]})`
                }));
                self.$el.append($textAnswer);
                varspanWidth=$textAnswer.find('span').width();
                varcalculatedWidth=`calc(${spanWidth}px+1.2rem)`;
                $textAnswer.css('width',calculatedWidth);
                setTimeout(function(){
                    //setTimeouttoforcejQueryrendering
                    $textAnswer.find('.o_survey_session_text_answer_container')
                        .css('width',calculatedWidth)
                        .css('opacity','1');
                },1);
                self.answerIds.push(inputLineValue.id);
            }
        });
    },
});

returnpublicWidget.registry.SurveySessionTextAnswers;

});
