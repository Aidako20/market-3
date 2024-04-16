flectra.define('mail/static/src/components/partner_im_status_icon/partner_im_status_icon.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classPartnerImStatusIconextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constpartner=this.env.models['mail.partner'].get(props.partnerLocalId);
            return{
                partner,
                partnerImStatus:partner&&partner.im_status,
                partnerRoot:this.env.messaging.partnerRoot,
            };
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.partner}
     */
    getpartner(){
        returnthis.env.models['mail.partner'].get(this.props.partnerLocalId);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClick(ev){
        if(!this.props.hasOpenChat){
            return;
        }
        this.partner.openChat();
    }

}

Object.assign(PartnerImStatusIcon,{
    defaultProps:{
        hasBackground:true,
        hasOpenChat:false,
    },
    props:{
        partnerLocalId:String,
        hasBackground:Boolean,
        /**
         *Determineswhetheraclickon`this`shouldopenachatwith
         *`this.partner`.
         */
        hasOpenChat:Boolean,
    },
    template:'mail.PartnerImStatusIcon',
});

returnPartnerImStatusIcon;

});
