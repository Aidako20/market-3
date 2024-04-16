flectra.define('website_event_meet.website_event_meet_meeting_room',function(require){
'usestrict';

constpublicWidget=require('web.public.widget');
constcore=require('web.core');
constDialog=require('web.Dialog');
const_t=core._t;

publicWidget.registry.websiteEventMeetingRoom=publicWidget.Widget.extend({
    selector:'.o_wevent_meeting_room_card',
    xmlDependencies:['/website_event_meet/static/src/xml/website_event_meeting_room.xml'],
    events:{
        'click.o_wevent_meeting_room_delete':'_onDeleteClick',
        'click.o_wevent_meeting_room_duplicate':'_onDuplicateClick',
        'click.o_wevent_meeting_room_is_pinned':'_onPinClick',
    },

    start:function(){
        this._super.apply(this,arguments);
        this.meetingRoomId=parseInt(this.$el.data('meeting-room-id'));
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
      *Deletethemeetingroom.
      *
      *@private
      */
    _onDeleteClick:asyncfunction(event){
        event.preventDefault();
        event.stopPropagation();

        Dialog.confirm(
            this,
            _t("Areyousureyouwanttoclosethisroom?"),
            {
                confirm_callback:async()=>{
                    awaitthis._rpc({
                        model:'event.meeting.room',
                        method:'write',
                        args:[this.meetingRoomId,{is_published:false}],
                        context:this.context,
                    });

                    //removetheelementsowedonotneedtorefreshthepage
                    this.$el.remove();
                }
            },
        );
    },

    /**
      *Duplicatetheroom.
      *
      *@private
      */
    _onDuplicateClick:function(event){
        event.preventDefault();
        event.stopPropagation();
        Dialog.confirm(
            this,
            _t("Areyousureyouwanttoduplicatethisroom?"),
            {
                confirm_callback:async()=>{
                    awaitthis._rpc({
                        model:'event.meeting.room',
                        method:'copy',
                        args:[this.meetingRoomId],
                        context:this.context,
                    });

                    window.location.reload();
                }
            },
        );
    },

    /**
      *Pin/unpintheroom.
      *
      *@private
      */
    _onPinClick:asyncfunction(event){
        event.preventDefault();
        event.stopPropagation();

        constpinnedButtonClass="o_wevent_meeting_room_pinned";
        constisPinned=event.currentTarget.classList.contains(pinnedButtonClass);

        awaitthis._rpc({
            model:'event.meeting.room',
            method:'write',
            args:[this.meetingRoomId,{is_pinned:!isPinned}],
            context:this.context,
        });

        //TDEFIXME:addclass?
        if(isPinned){
            event.currentTarget.classList.remove(pinnedButtonClass);
        }else{
            event.currentTarget.classList.add(pinnedButtonClass);
        }
    }
});

returnpublicWidget.registry.websiteEventMeetingRoom;

});
