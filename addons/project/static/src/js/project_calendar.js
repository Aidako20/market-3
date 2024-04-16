flectra.define('project.ProjectCalendarView',function(require){
"usestrict";

constCalendarController=require('web.CalendarController');
constCalendarView=require('web.CalendarView');
constviewRegistry=require('web.view_registry');

constProjectCalendarController=CalendarController.extend({
    _renderButtonsParameters(){
        return_.extend({},this._super(...arguments), {scaleDrop:true});
    },
});

constProjectCalendarView=CalendarView.extend({
        config:_.extend({},CalendarView.prototype.config,{
            Controller:ProjectCalendarController,
        }),
    });

viewRegistry.add('project_calendar',ProjectCalendarView);
returnProjectCalendarView;
});
