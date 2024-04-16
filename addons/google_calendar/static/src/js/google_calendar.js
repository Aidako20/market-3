flectra.define('google_calendar.CalendarView',function(require){
"usestrict";

varcore=require('web.core');
varDialog=require('web.Dialog');
varframework=require('web.framework');
constCalendarView=require('calendar.CalendarView');
constCalendarRenderer=require('calendar.CalendarRenderer');
constCalendarController=require('calendar.CalendarController');
constCalendarModel=require('calendar.CalendarModel');
constviewRegistry=require('web.view_registry');
constsession=require('web.session');

var_t=core._t;

constGoogleCalendarModel=CalendarModel.include({

    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        this.google_is_sync=true;
        this.google_pending_sync=false;
    },

    /**
     *@override
     */
    __get:function(){
        varresult=this._super.apply(this,arguments);
        result.google_is_sync=this.google_is_sync;
        returnresult;
    },


    /**
     *@override
     *@returns{Promise}
     */
    async_loadCalendar(){
        const_super=this._super.bind(this);
        //Whenthecalendarsynchronizationtakessometime,preventsretriggeringthesyncwhilenavigatingthecalendar.
        if(this.google_pending_sync){
            return_super(...arguments);
        }

        try{
            awaitPromise.race([
                newPromise(resolve=>setTimeout(resolve,1000)),
                this._syncGoogleCalendar(true)
            ]);
        }catch(error){
            if(error.event){
                error.event.preventDefault();
            }
            console.error("CouldnotsynchronizeGoogleeventsnow.",error);
            this.google_pending_sync=false;
        }
        return_super(...arguments);
    },

    _syncGoogleCalendar(shadow=false){
        varself=this;
        varcontext=this.getSession().user_context;
        this.google_pending_sync=true;
        returnthis._rpc({
            route:'/google_calendar/sync_data',
            params:{
                model:this.modelName,
                fromurl:window.location.href,
                local_context:context,//LULTODOremovethislocal_context
            }
        },{shadow}).then(function(result){
            if(result.status==="need_config_from_admin"||result.status==="need_auth"){
                self.google_is_sync=false;
            }elseif(result.status==="no_new_event_from_google"||result.status==="need_refresh"){
                self.google_is_sync=true;
            }
            self.google_pending_sync=false;
            returnresult
        });
    },

    archiveRecords:function(ids,model){
        returnthis._rpc({
            model:model,
            method:'action_archive',
            args:[ids],
            context:session.user_context,
        });
    },
})

constGoogleCalendarController=CalendarController.include({
    custom_events:_.extend({},CalendarController.prototype.custom_events,{
        syncGoogleCalendar:'_onGoogleSyncCalendar',
        archiveRecord:'_onArchiveRecord',
    }),


    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *TrytosyncthecalendarwithGoogleCalendar.Accordingtotheresult
     *fromGoogleAPI,thisfunctionmayrequireanactionoftheuserbythe
     *meanofadialog.
     *
     *@private
     *@returns{FlectraEvent}event
     */
    _onGoogleSyncCalendar:function(event){
        varself=this;

        returnthis.model._syncGoogleCalendar().then(function(o){
            if(o.status==="need_auth"){
                Dialog.alert(self,_t("YouwillberedirectedtoGoogletoauthorizeaccesstoyourcalendar!"),{
                    confirm_callback:function(){
                        framework.redirect(o.url);
                    },
                    title:_t('Redirection'),
                });
            }elseif(o.status==="need_config_from_admin"){
                if(!_.isUndefined(o.action)&&parseInt(o.action)){
                    Dialog.confirm(self,_t("TheGoogleSynchronizationneedstobeconfiguredbeforeyoucanuseit,doyouwanttodoitnow?"),{
                        confirm_callback:function(){
                            self.do_action(o.action);
                        },
                        title:_t('Configuration'),
                    });
                }else{
                    Dialog.alert(self,_t("AnadministratorneedstoconfigureGoogleSynchronizationbeforeyoucanuseit!"),{
                        title:_t('Configuration'),
                    });
                }
            }elseif(o.status==="need_refresh"){
                self.reload();
            }
        }).then(event.data.on_always,event.data.on_always);
    },

    _onArchiveRecord:function(ev){
        varself=this;
        Dialog.confirm(this,_t("Areyousureyouwanttoarchivethisrecord?"),{
            confirm_callback:function(){
                self.model.archiveRecords([ev.data.id],self.modelName).then(function(){
                    self.reload();
                });
            }
        });
    },
});

constGoogleCalendarRenderer=CalendarRenderer.include({
    events:_.extend({},CalendarRenderer.prototype.events,{
        'click.o_google_sync_button':'_onGoogleSyncCalendar',
    }),
    
    custom_events:_.extend({},CalendarRenderer.prototype.custom_events,{
        archive_event:'_onArchiveEvent',
    }),

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *AddstheSyncwithGooglebuttoninthesidebar
     *
     *@private
     */
    _initSidebar:function(){
        varself=this;
        this._super.apply(this,arguments);
        this.$googleButton=$();
        if(this.model==="calendar.event"){
            if(this.state.google_is_sync){
                this.$googleButton=$('<span/>',{html:_t("SynchedwithGoogle")})
                                .addClass('o_google_syncbadgebadge-pillbadge-success')
                                .prepend($('<i/>',{class:"famr-2fa-check"}))
                                .appendTo(self.$sidebar);
            }else{
                this.$googleButton=$('<button/>',{type:'button',html:_t("Syncwith<b>Google</b>")})
                                .addClass('o_google_sync_buttonoe_buttonbtnbtn-secondary')
                                .appendTo(self.$sidebar);
            }
        }
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *RequeststosyncthecalendarwithGoogleCalendar
     *
     *@private
     */
    _onGoogleSyncCalendar:function(){
        varself=this;
        varcontext=this.getSession().user_context;
        this.$googleButton.prop('disabled',true);
        this.trigger_up('syncGoogleCalendar',{
            on_always:function(){
                self.$googleButton.prop('disabled',false);
            },
        });
    },

    _onArchiveEvent:function(ev){
        this._unselectEvent();
        this.trigger_up('archiveRecord',{id:parseInt(ev.data.id,10)});
    }
});

return{
    GoogleCalendarController,
    GoogleCalendarModel,
    GoogleCalendarRenderer,
};

});
