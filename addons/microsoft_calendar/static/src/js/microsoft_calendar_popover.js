flectra.define('microsoft_calendar.MicrosoftCalendarPopover',function(require){
    "usestrict";

    constCalendarPopover=require('web.CalendarPopover');

    constMicrosoftCalendarPopover=CalendarPopover.include({
        events:_.extend({},CalendarPopover.prototype.events,{
            'click.o_cw_popover_archive_m':'_onClickPopoverArchive',
        }),

        /**
         *Weonlywantone'Archive'buttoninthepopover
         *soifGoogleSyncisalsoactive,ittakesprecedence
         *overthispopvoer.
         */
        isMEventSyncedAndArchivable(){
            if(this.event.extendedProps.record.google_id===undefined){
                returnthis.event.extendedProps.record.microsoft_id;
            }
            return!this.event.extendedProps.record.google_id&&this.event.extendedProps.record.microsoft_id
        },

        isEventDeletable(){
            return!this.isMEventSyncedAndArchivable()&&this._super();
        },

        _onClickPopoverArchive:function(ev){
            ev.preventDefault();
            this.trigger_up('archive_event',{id:this.event.id});
        },
    });

    returnMicrosoftCalendarPopover;
});
