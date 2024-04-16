flectra.define('website_event_meet.website_event_create_room_button',function(require){
'usestrict';

constpublicWidget=require('web.public.widget');
constcore=require('web.core');
constQWeb=core.qweb;

publicWidget.registry.websiteEventCreateMeetingRoom=publicWidget.Widget.extend({
    selector:'.o_wevent_create_room_button',
    xmlDependencies:['/website_event_meet/static/src/xml/website_event_meeting_room.xml'],
    events:{
        'click':'_onClickCreate',
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    _onClickCreate:asyncfunction(){
        if(!this.$createModal){
            constlangs=awaitthis._rpc({
                route:"/event/active_langs",
            });

            this.$createModal=$(QWeb.render(
                'event_meet_create_room_modal',
                {
                    csrf_token:flectra.csrf_token,
                    eventId:this.$el.data("eventId"),
                    defaultLangCode:this.$el.data("defaultLangCode"),
                    langs:langs,
                }
            ));

            this.$createModal.appendTo(this.$el.parentNode);
        }

        this.$createModal.modal('show');
    },

    //--------------------------------------------------------------------------
    //Override
    //--------------------------------------------------------------------------

    /**
     *RemovethecreatemodalfromtheDOM,toavoidissuewheneditingthetemplate
     *withthewebsiteeditor.
     *
     *@override
     */
    destroy:function(){
        $('.o_wevent_create_meeting_room_modal').remove();
        this._super.apply(this,arguments);
    },
});

returnpublicWidget.registry.websiteEventMeetingRoom;

});
