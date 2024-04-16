flectra.define('google_calendar.GoogleCalendarPopover',function(require){
    "usestrict";

    constCalendarPopover=require('web.CalendarPopover');

    constGoogleCalendarPopover=CalendarPopover.include({
        events:_.extend({},CalendarPopover.prototype.events,{
            'click.o_cw_popover_archive_g':'_onClickPopoverGArchive',
        }),

        isGEventSyncedAndArchivable(){
            returnthis.event.extendedProps.record.google_id;
        },

        isEventDeletable(){
            return!this.isGEventSyncedAndArchivable()&&this._super();
        },

        _onClickPopoverGArchive:function(ev){
            ev.preventDefault();
            this.trigger_up('archive_event',{id:this.event.id});
        },
    })

    returnGoogleCalendarPopover;
});
