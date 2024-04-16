flectra.define('calendar.CalendarModel',function(require){
    "usestrict";

    constModel=require('web.CalendarModel');

    constCalendarModel=Model.extend({

        /**
         *@override
         *TransformfullcalendareventobjecttoflectraDataobject
         */
        calendarEventToRecord(event){
            constdata=this._super(event);
            return_.extend({},data,{
                'recurrence_update':event.recurrenceUpdate,
            });
        }
    });

    returnCalendarModel;
});
