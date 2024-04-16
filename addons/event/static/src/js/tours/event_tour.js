flectra.define('event.event_steps',function(require){
"usestrict";

varcore=require('web.core');

varEventAdditionalTourSteps=core.Class.extend({

    _get_website_event_steps:function(){
        return[false];
    },

});

returnEventAdditionalTourSteps;

});

flectra.define('event.event_tour',function(require){
"usestrict";

varcore=require('web.core');
var_t=core._t;

vartour=require('web_tour.tour');
varEventAdditionalTourSteps=require('event.event_steps');

tour.register('event_tour',{
    url:'/web',
    rainbowManMessage:_t("Great!Nowallyouhavetodoiswaitforyourattendeestoshowup!"),
    sequence:210,
},[tour.stepUtils.showAppsMenuItem(),{
    trigger:'.o_app[data-menu-xmlid="event.event_main_menu"]',
    content:_t("Readyto<b>organizeevents</b>inafewminutes?Let'sgetstarted!"),
    position:'bottom',
    edition:'enterprise',
},{
    trigger:'.o_app[data-menu-xmlid="event.event_main_menu"]',
    content:_t("Readyto<b>organizeevents</b>inafewminutes?Let'sgetstarted!"),
    edition:'community',
},{
    trigger:'.o-kanban-button-new',
    extra_trigger:'.o_event_kanban_view',
    content:_t("Let'screateyourfirst<b>event</b>."),
    position:'bottom',
    width:175,
},{
    trigger:'.o_event_form_viewinput[name="name"]',
    content:_t("Thisisthe<b>name</b>yourguestswillseewhenregistering."),
    run:'textFlectraExperience2020',
},{
    trigger:'.o_event_form_viewinput[name="date_end"]',
    content:_t("Whenwillyoureventtakeplace?<b>Select</b>thestartandenddates<b>andclickApply</b>."),
    run:function(){
        $('input[name="date_begin"]').val('09/30/202008:00:00').change();
        $('input[name="date_end"]').val('10/02/202023:00:00').change();
    },
},{
    trigger:'.o_event_form_viewdiv[name="event_ticket_ids"].o_field_x2many_list_row_adda',
    content:_t("Tickettypesallowyoutodistinguishyourattendees.Let's<b>create</b>anewone."),
},...newEventAdditionalTourSteps()._get_website_event_steps(),{
    trigger:'.o_event_form_viewdiv[name="stage_id"]',
    extra_trigger:'div.o_form_buttons_view:not(.o_hidden)',
    content:_t("Nowthatyoureventisready,clickheretomoveittoanotherstage."),
    position:'bottom',
},{
    trigger:'ol.breadcrumbli.breadcrumb-item:first',
    extra_trigger:'.o_event_form_viewdiv[name="stage_id"]',
    content:_t("Usethe<b>breadcrumbs</b>togobacktoyourkanbanoverview."),
    position:'bottom',
    run:'click',
},{
    trigger:'.o_event_kanban_viewdiv.o_quick_create_folded',
    content:_t("Thispipelinecanbecustomizedontheflytofityourorganizationalneeds.Forexample,let'screateanewstage."),
    position:'bottom',
    run:function(actions){
        actions.click();
        $('div.o_kanban_headerinput[type="text"]').val('NewStage');
    },
},{
    trigger:'.o_event_kanban_viewbutton.o_kanban_add',
    content:_t("Click<b>add</b>tocreateanewstage."),
    position:'bottom',
    width:200,
    run:'click',
}].filter(Boolean));

});
