flectra.define('survey.test_survey_session_start_tour',function(require){
"usestrict";

vartour=require('web_tour.tour');
varsurveySessionTools=require('survey.session_tour_tools');

/**
 *Smalltourthatwillopenthesessionmanagerandcheck
 *thattheattendeesareaccountedfor,thenstartthesession
 *bygoingtothefirstquestion.
 */
tour.register('test_survey_session_start_tour',{
    url:"/web",
    test:true,
},[].concat(surveySessionTools.accessSurveySteps,[{
    trigger:'button[name="action_open_session_manager"]',
},{
    trigger:'.o_survey_session_attendees_count:contains("3")',
    run:function(){}//checkattendeescount
},{
    trigger:'h1',
    run:function(){
        vare=$.Event('keydown');
        e.keyCode=39;//arrow-right
        $(document).trigger(e);//startsession
    }
},{
    trigger:'h1:contains("Nickname")',
    run:function(){}//checkfirstquestionisdisplayed
}]));

});
