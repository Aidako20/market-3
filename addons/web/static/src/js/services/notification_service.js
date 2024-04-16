flectra.define('web.NotificationService',function(require){
'usestrict';

varAbstractService=require('web.AbstractService');
varNotification=require('web.Notification');
varcore=require('web.core');

varid=0;

/**
 *NotificationService
 *
 *TheNotificationServiceissimplyaserviceusedtodisplaynotificationsin
 *thetop/rightpartofthescreen.
 *
 *Ifyouwanttodisplaysuchanotification,youprobablydonotwanttodoit
 *byusingthisfile.Theproperwayistousethedo_warnordo_notify
 *methodsontheWidgetclass.
 */
varNotificationService=AbstractService.extend({
    custom_events:{
        close:'_onCloseNotification',
    },

    /**
     *@override
     */
    start:function(){
        this._super.apply(this,arguments);
        this.notifications={};
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Itmaysometimesbeusefultocloseprogrammaticallyanotification.For
     *example,whenthereisastickynotificationwarningtheuseraboutsome
     *condition(connectionlost),buttheconditiondoesnotapplyanymore.
     *
     *@param{number}notificationId
     *@param{boolean}[silent=false]iftrue,thenotificationdoesnotcall
     *  onClosecallback
     */
    close:function(notificationId,silent){
        varnotification=this.notifications[notificationId];
        if(!notification){
            return;
        }
        notification.close(silent);
    },
    /**
     *Displayanotificationattheappropriatelocation,andreturnsthe
     *referenceidtothesamewidget.
     *
     *NotethatthismethoddoesnotwaitfortheappendTomethodtocomplete.
     *
     *@param{Object}params
     *@param{function}[params.Notification]javascriptclassofanotification
     *  toinstantiatebydefaultuse'web.Notification'
     *@param{string}params.titlenotificationtitle
     *@param{string}params.subtitlenotificationsubtitle
     *@param{string}params.messagenotificationmainmessage
     *@param{string}params.type'notification'or'warning'
     *@param{boolean}[params.sticky=false]iftrue,thenotificationwillstay
     *  visibleuntiltheuserclicksonit.
     *@param{string}[params.className]classNametoaddonthedom
     *@param{function}[params.onClose]callbackwhentheuserclickonthex
     *  orwhenthenotificationisautoclose(nosticky)
     *@param{Object[]}params.buttons
     *@param{function}params.buttons[0].clickcallbackonclick
     *@param{Boolean}[params.buttons[0].primary]displaythebuttonasprimary
     *@param{string}[params.buttons[0].text]buttonlabel
     *@param{string}[params.buttons[0].icon]font-awsomeclassNameorimagesrc
     *@returns{Number}notificationid
     */
    notify:function(params){
        if(!this.$el){
            this.$el=$('<divclass="o_notification_manager"/>');
            this.$el.prependTo('body');
        }
        varNotificationWidget=params.Notification||Notification;
        varnotification=this.notifications[++id]=newNotificationWidget(this,params);
        notification.appendTo(this.$el);
        returnid;
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{FlectraEvent}ev
     */
    _onCloseNotification:function(ev){
        ev.stopPropagation();
        for(varnotificationIdinthis.notifications){
            if(this.notifications[notificationId]===ev.target){
                deletethis.notifications[notificationId];
                break;
            }
        }
    },
});

core.serviceRegistry.add('notification',NotificationService);

returnNotificationService;
});
