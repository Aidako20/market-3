flectra.define('calendar.systray.ActivityMenu',function(require){
"usestrict";

varActivityMenu=require('mail.systray.ActivityMenu');
varfieldUtils=require('web.field_utils');

ActivityMenu.include({

    //-----------------------------------------
    //Private
    //-----------------------------------------

    /**
     *parsedatetoservervalue
     *
     *@private
     *@override
     */
    _getActivityData:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            varmeeting=_.find(self._activities,{type:'meeting'});
            if(meeting&&meeting.meetings) {
                _.each(meeting.meetings,function(res){
                    res.start=fieldUtils.parse.datetime(res.start,false,{isUTC:true});
                });
            }
        });
    },

    //-----------------------------------------
    //Handlers
    //-----------------------------------------

    /**
     *@private
     *@override
     */
    _onActivityFilterClick:function(ev){
        var$el=$(ev.currentTarget);
        vardata=_.extend({},$el.data());
        if(data.res_model==="calendar.event"&&data.filter==="my"){
            this.do_action('calendar.action_calendar_event',{
                additional_context:{
                    default_mode:'day',
                    search_default_mymeetings:1,
                },
               clear_breadcrumbs:true,
            });
        }else{
            this._super.apply(this,arguments);
        }
    },
});

});
