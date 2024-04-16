flectra.define('survey.session_tour_tools',function(require){
'usestrict';

vartour=require('web_tour.tour');

/**
 *Toolthatgatherscommonstepstoevery'surveysession'tours.
 */
return{
    accessSurveySteps:[tour.stepUtils.showAppsMenuItem(),{
        trigger:'.o_app[data-menu-xmlid="survey.menu_surveys"]',
        edition:'community'
    },{
        trigger:'.o_app[data-menu-xmlid="survey.menu_surveys"]',
        edition:'enterprise'
    },{
        trigger:'.oe_kanban_card:contains("UserSessionSurvey")',
    }]
};

});
