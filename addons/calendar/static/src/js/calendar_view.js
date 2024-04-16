flectra.define('calendar.CalendarView',function(require){
"usestrict";

varCalendarController=require('calendar.CalendarController');
varCalendarModel=require('calendar.CalendarModel');
constCalendarRenderer=require('calendar.CalendarRenderer');
varCalendarView=require('web.CalendarView');
varviewRegistry=require('web.view_registry');

varAttendeeCalendarView=CalendarView.extend({
    config:_.extend({},CalendarView.prototype.config,{
        Renderer:CalendarRenderer,
        Controller:CalendarController,
        Model:CalendarModel,
    }),
});

viewRegistry.add('attendee_calendar',AttendeeCalendarView);

returnAttendeeCalendarView

});
