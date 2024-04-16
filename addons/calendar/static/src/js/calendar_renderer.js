flectra.define('calendar.CalendarRenderer',function(require){
"usestrict";

constCalendarRenderer=require('web.CalendarRenderer');
constCalendarPopover=require('web.CalendarPopover');
constsession=require('web.session');


constAttendeeCalendarPopover=CalendarPopover.extend({
    template:'Calendar.attendee.status.popover',
    events:_.extend({},CalendarPopover.prototype.events,{
        'click.o-calendar-attendee-status.dropdown-item':'_onClickAttendeeStatus'
    }),
    /**
     *@constructor
     */
    init:function(){
        varself=this;
        this._super.apply(this,arguments);
        //Showstatusdropdownifuserisinattendeeslist
        if(this.isCurrentPartnerAttendee()){
            this.statusColors={accepted:'text-success',declined:'text-danger',tentative:'text-muted',needsAction:'text-dark'};
            this.statusInfo={};
            _.each(this.fields.attendee_status.selection,function(selection){
                self.statusInfo[selection[0]]={text:selection[1],color:self.statusColors[selection[0]]};
            });
            this.selectedStatusInfo=this.statusInfo[this.event.extendedProps.record.attendee_status];
        }
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@return{boolean}
     */
    isCurrentPartnerAttendee(){
        returnthis.event.extendedProps.record.partner_ids.includes(session.partner_id);
    },
    /**
     *@override
     *@return{boolean}
     */
    isEventDeletable(){
        returnthis._super()&&(this._isEventPrivate()?this.isCurrentPartnerAttendee():true);
    },
    /**
     *@override
     *@return{boolean}
     */
    isEventDetailsVisible(){
        returnthis._isEventPrivate()?this.isCurrentPartnerAttendee():this._super();
    },
    /**
     *@override
     *@return{boolean}
     */
    isEventEditable(){
        returnthis._isEventPrivate()?this.isCurrentPartnerAttendee():this._super();
    },
     /**
     *@return{boolean}
     */
    displayAttendeeAnswerChoice(){
        //checkifweareapartnerandifwearetheonlyattendee.
        //Thisavoidtodisplayattendeeanwserdropdownforsingleuserattendees
        constisCurrentpartner=(currentValue)=>currentValue===session.partner_id;
        constonlyAttendee=this.event.extendedProps.record.partner_ids.every(isCurrentpartner);
        returnthis.isCurrentPartnerAttendee()&&!onlyAttendee;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@return{boolean}
     */
    _isEventPrivate(){
        returnthis.event.extendedProps.record.privacy==='private';
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickAttendeeStatus:function(ev){
        ev.preventDefault();
        varself=this;
        varselectedStatus=$(ev.currentTarget).attr('data-action');
        this._rpc({
            model:'calendar.event',
            method:'change_attendee_status',
            args:[parseInt(this.event.id),selectedStatus],
        }).then(function(){
            self.event.extendedProps.record.attendee_status=selectedStatus; //FIXEME:Maybewehavetoreloadview
            self.$('.o-calendar-attendee-status-text').text(self.statusInfo[selectedStatus].text);
            self.$('.o-calendar-attendee-status-icon').removeClass(_.values(self.statusColors).join('')).addClass(self.statusInfo[selectedStatus].color);
        });
    },
});


constAttendeeCalendarRenderer=CalendarRenderer.extend({
	config:_.extend({},CalendarRenderer.prototype.config,{
		CalendarPopover:AttendeeCalendarPopover,
	}),
});

returnAttendeeCalendarRenderer

});
