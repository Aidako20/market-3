flectra.define('mail/static/src/components/notification_group/notification_group.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;
const{useRef}=owl.hooks;

classNotificationGroupextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constgroup=this.env.models['mail.notification_group'].get(props.notificationGroupLocalId);
            return{
                group:group?group.__state:undefined,
            };
        });
        /**
         *Referenceofthe"markasread"button.Usefultodisablethe
         *top-levelclickhandlerwhenclickingonthisspecificbutton.
         */
        this._markAsReadRef=useRef('markAsRead');
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.notification_group}
     */
    getgroup(){
        returnthis.env.models['mail.notification_group'].get(this.props.notificationGroupLocalId);
    }

    /**
     *@returns{string|undefined}
     */
    image(){
        if(this.group.notification_type==='email'){
            return'/mail/static/src/img/smiley/mailfailure.jpg';
        }
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClick(ev){
        constmarkAsRead=this._markAsReadRef.el;
        if(markAsRead&&markAsRead.contains(ev.target)){
            //handledin`_onClickMarkAsRead`
            return;
        }
        this.group.openDocuments();
        if(!this.env.messaging.device.isMobile){
            this.env.messaging.messagingMenu.close();
        }
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickMarkAsRead(ev){
        this.group.openCancelAction();
        if(!this.env.messaging.device.isMobile){
            this.env.messaging.messagingMenu.close();
        }
    }

}

Object.assign(NotificationGroup,{
    props:{
        notificationGroupLocalId:String,
    },
    template:'mail.NotificationGroup',
});

returnNotificationGroup;

});
