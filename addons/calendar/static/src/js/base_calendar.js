flectra.define('base_calendar.base_calendar',function(require){
"usestrict";

varBasicModel=require('web.BasicModel');
varfieldRegistry=require('web.field_registry');
varNotification=require('web.Notification');
varrelationalFields=require('web.relational_fields');
varsession=require('web.session');
varWebClient=require('web.WebClient');

varFieldMany2ManyTags=relationalFields.FieldMany2ManyTags;

varCalendarNotification=Notification.extend({
    template:"CalendarNotification",
    xmlDependencies:(Notification.prototype.xmlDependencies||[])
        .concat(['/calendar/static/src/xml/notification_calendar.xml']),

    init:function(parent,params){
        this._super(parent,params);
        this.eid=params.eventID;
        this.sticky=true;

        this.events=_.extend(this.events||{},{
            'click.link2event':function(){
                varself=this;

                this._rpc({
                        route:'/web/action/load',
                        params:{
                            action_id:'calendar.action_calendar_event_notify',
                        },
                    })
                    .then(function(r){
                        r.res_id=self.eid;
                        returnself.do_action(r);
                    });
            },

            'click.link2recall':function(){
                this.close();
            },

            'click.link2showed':function(){
                this._rpc({route:'/calendar/notify_ack'})
                    .then(this.close.bind(this,false),this.close.bind(this,false));
            },
        });
    },
});

WebClient.include({
    display_calendar_notif:function(notifications){
        varself=this;
        varlast_notif_timer=0;

        //Clearpreviouslysettimeoutsanddestroycurrentlydisplayedcalendarnotifications
        clearTimeout(this.get_next_calendar_notif_timeout);
        _.each(this.calendar_notif_timeouts,clearTimeout);
        this.calendar_notif_timeouts={};

        //Foreachnotification,setatimeouttodisplayit
        _.each(notifications,function(notif){
            varkey=notif.event_id+','+notif.alarm_id;
            if(keyinself.calendar_notif){
                return;
            }
            self.calendar_notif_timeouts[key]=setTimeout(function(){
                varnotificationID=self.call('notification','notify',{
                    Notification:CalendarNotification,
                    title:notif.title,
                    message:notif.message,
                    eventID:notif.event_id,
                    onClose:function(){
                        deleteself.calendar_notif[key];
                    },
                });
                self.calendar_notif[key]=notificationID;
            },notif.timer*1000);
            last_notif_timer=Math.max(last_notif_timer,notif.timer);
        });

        //Setatimeouttogetthenextnotificationswhenthelastonehasbeendisplayed
        if(last_notif_timer>0){
            this.get_next_calendar_notif_timeout=setTimeout(this.get_next_calendar_notif.bind(this),last_notif_timer*1000);
        }
    },
    get_next_calendar_notif:function(){
        session.rpc("/calendar/notify",{},{shadow:true})
            .then(this.display_calendar_notif.bind(this))
            .guardedCatch(function(reason){//
                varerr=reason.message;
                varev=reason.event;
                if(err.code===-32098){
                    //PreventtheCrashManagertodisplayanerror
                    //incaseofanxhrerrornotduetoaservererror
                    ev.preventDefault();
                }
            });
    },
    show_application:function(){
        //Aneventistriggeredonthebuseachtimeacalendareventwithalarm
        //inwhichthecurrentuserisinvolvediscreated,editedordeleted
        this.calendar_notif_timeouts={};
        this.calendar_notif={};
        this.call('bus_service','onNotification',this,function(notifications){
            _.each(notifications,(function(notification){
                if(notification[0][1]==='calendar.alarm'){
                    this.display_calendar_notif(notification[1]);
                }
            }).bind(this));
        });
        returnthis._super.apply(this,arguments).then(this.get_next_calendar_notif.bind(this));
    },
});

BasicModel.include({
    /**
     *@private
     *@param{Object}record
     *@param{string}fieldName
     *@returns{Promise}
     */
    _fetchSpecialAttendeeStatus:function(record,fieldName){
        varcontext=record.getContext({fieldName:fieldName});
        varattendeeIDs=record.data[fieldName]?this.localData[record.data[fieldName]].res_ids:[];
        varmeetingID=_.isNumber(record.res_id)?record.res_id:false;
        returnthis._rpc({
            model:'res.partner',
            method:'get_attendee_detail',
            args:[attendeeIDs,meetingID],
            context:context,
        }).then(function(result){
            return_.map(result,function(d){
                return_.object(['id','display_name','status','color'],d);
            });
        });
    },
});

varMany2ManyAttendee=FieldMany2ManyTags.extend({
    //asthiswidgetismodeldependant(rpconres.partner),useitinanother
    //contextprobablywon'twork
    //supportedFieldTypes:['many2many'],
    tag_template:"Many2ManyAttendeeTag",
    specialData:"_fetchSpecialAttendeeStatus",

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _getRenderTagsContext:function(){
        varresult=this._super.apply(this,arguments);
        result.attendeesData=this.record.specialData.partner_ids;
        returnresult;
    },
});

fieldRegistry.add('many2manyattendee',Many2ManyAttendee);

});
