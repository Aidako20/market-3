flectra.define('survey.test_survey_session_create_tour',function(require){
"usestrict";

vartour=require('web_tour.tour');
varsurveySessionTools=require('survey.session_tour_tools');

/**
 *Smalltourthatwillsimplystartthesessionandwaitforattendees.
 */
tour.register('test_survey_session_create_tour',{
    url:"/web",
    test:true,
},[].concat(surveySessionTools.accessSurveySteps,[{
    trigger:'button[name="action_start_session"]',
},{
    trigger:'.o_survey_session_attendees_count:contains("0")',
    run:function(){}//checksessioniscorrectlystarted
}]));

});
