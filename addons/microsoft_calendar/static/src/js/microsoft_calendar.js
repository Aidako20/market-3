flectra.define('microsoft_calendar.CalendarView',function(require){
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

constMicrosoftCalendarModel=CalendarModel.include({

    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        this.microsoft_is_sync=true;
        this.microsoft_pending_sync=false;
    },

    /**
     *@override
     */
    __get:function(){
        varresult=this._super.apply(this,arguments);
        result.microsoft_is_sync=this.microsoft_is_sync;
        returnresult;
    },

    /**
     *@override
     *@returns{Promise}
     */
    async_loadCalendar(){
        const_super=this._super.bind(this);
        //Whenthecalendarsynchronizationtakessometime,preventsretriggeringthesyncwhilenavigatingthecalendar.
        if(this.microsoft_pending_sync){
            return_super(...arguments);
        }
        try{
            awaitPromise.race([
                newPromise(resolve=>setTimeout(resolve,1000)),
                this._syncMicrosoftCalendar(true)
            ]);
        }catch(error){
            if(error.event){
                error.event.preventDefault();
            }
            console.error("CouldnotsynchronizeOutlookeventsnow.",error);
            this.microsoft_pending_sync=false;
        }
        return_super(...arguments);
    },

    _syncMicrosoftCalendar(shadow=false){
        varself=this;
        this.microsoft_pending_sync=true;
        returnthis._rpc({
            route:'/microsoft_calendar/sync_data',
            params:{
                model:this.modelName,
                fromurl:window.location.href,
            }
        },{shadow}).then(function(result){
            if(result.status==="need_config_from_admin"||result.status==="need_auth"){
                self.microsoft_is_sync=false;
            }elseif(result.status==="no_new_event_from_microsoft"||result.status==="need_refresh"){
                self.microsoft_is_sync=true;
            }
            self.microsoft_pending_sync=false;
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
});

constMicrosoftCalendarController=CalendarController.include({
    custom_events:_.extend({},CalendarController.prototype.custom_events,{
        syncMicrosoftCalendar:'_onSyncMicrosoftCalendar',
        archiveRecord:'_onArchiveRecord',
    }),


    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *TrytosyncthecalendarwithMicrosoftCalendar.Accordingtotheresult
     *fromMicrosoftAPI,thisfunctionmayrequireanactionoftheuserbythe
     *meanofadialog.
     *
     *@private
     *@returns{FlectraEvent}event
     */
    _onSyncMicrosoftCalendar:function(event){
        varself=this;

        returnthis.model._syncMicrosoftCalendar().then(function(o){
            if(o.status==="need_auth"){
                Dialog.alert(self,_t("YouwillberedirectedtoOutlooktoauthorizetheaccesstoyourcalendar."),{
                    confirm_callback:function(){
                        framework.redirect(o.url);
                    },
                    title:_t('Redirection'),
                });
            }elseif(o.status==="need_config_from_admin"){
                if(!_.isUndefined(o.action)&&parseInt(o.action)){
                    Dialog.confirm(self,_t("TheOutlookSynchronizationneedstobeconfiguredbeforeyoucanuseit,doyouwanttodoitnow?"),{
                        confirm_callback:function(){
                            self.do_action(o.action);
                        },
                        title:_t('Configuration'),
                    });
                }else{
                    Dialog.alert(self,_t("AnadministratorneedstoconfigureOutlookSynchronizationbeforeyoucanuseit!"),{
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

constMicrosoftCalendarRenderer=CalendarRenderer.include({
    events:_.extend({},CalendarRenderer.prototype.events,{
        'click.o_microsoft_sync_button':'_onSyncMicrosoftCalendar',
    }),
    custom_events:_.extend({},CalendarRenderer.prototype.custom_events,{
        archive_event:'_onArchiveEvent',
    }),

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *AddstheSyncwithOutlookbuttoninthesidebar
     *
     *@private
     */
    _initSidebar:function(){
        varself=this;
        this._super.apply(this,arguments);
        this.$microsoftButton=$();
        if(this.model==="calendar.event"){
            if(this.state.microsoft_is_sync){
                this.$microsoftButton=$('<span/>',{html:_t("SynchedwithOutlook")})
                                .addClass('o_microsoft_syncbadgebadge-pillbadge-success')
                                .prepend($('<i/>',{class:"famr-2fa-check"}))
                                .appendTo(self.$sidebar);
            }else{
                this.$microsoftButton=$('<button/>',{type:'button',html:_t("Syncwith<b>Outlook</b>")})
                                .addClass('o_microsoft_sync_buttonoe_buttonbtnbtn-secondary')
                                .appendTo(self.$sidebar);
            }
        }
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *RequeststosyncthecalendarwithMicrosoftCalendar
     *
     *@private
     */
    _onSyncMicrosoftCalendar:function(){
        varself=this;
        varcontext=this.getSession().user_context;
        this.$microsoftButton.prop('disabled',true);
        this.trigger_up('syncMicrosoftCalendar',{
            on_always:function(){
                self.$microsoftButton.prop('disabled',false);
            },
        });
    },

    _onArchiveEvent:function(ev){
        this._unselectEvent();
        this.trigger_up('archiveRecord',{id:parseInt(ev.data.id,10)});
    },
});

return{
    MicrosoftCalendarController,
    MicrosoftCalendarModel,
    MicrosoftCalendarRenderer,
};

});
