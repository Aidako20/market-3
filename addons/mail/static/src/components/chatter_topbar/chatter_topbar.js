flectra.define('mail/static/src/components/chatter_topbar/chatter_topbar.js',function(require){
'usestrict';

constcomponents={
    FollowButton:require('mail/static/src/components/follow_button/follow_button.js'),
    FollowerListMenu:require('mail/static/src/components/follower_list_menu/follower_list_menu.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classChatterTopbarextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constchatter=this.env.models['mail.chatter'].get(props.chatterLocalId);
            constthread=chatter?chatter.thread:undefined;
            constthreadAttachments=thread?thread.allAttachments:[];
            return{
                areThreadAttachmentsLoaded:thread&&thread.areAttachmentsLoaded,
                chatter:chatter?chatter.__state:undefined,
                composerIsLog:chatter&&chatter.composer&&chatter.composer.isLog,
                threadAttachmentsAmount:threadAttachments.length,
            };
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.chatter}
     */
    getchatter(){
        returnthis.env.models['mail.chatter'].get(this.props.chatterLocalId);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickAttachments(ev){
        this.chatter.update({
            isAttachmentBoxVisible:!this.chatter.isAttachmentBoxVisible,
        });
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickClose(ev){
        this.trigger('o-close-chatter');
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickLogNote(ev){
        if(!this.chatter.composer){
            return;
        }
        if(this.chatter.isComposerVisible&&this.chatter.composer.isLog){
            this.chatter.update({isComposerVisible:false});
        }else{
            this.chatter.showLogNote();
        }
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickScheduleActivity(ev){
        constaction={
            type:'ir.actions.act_window',
            name:this.env._t("ScheduleActivity"),
            res_model:'mail.activity',
            view_mode:'form',
            views:[[false,'form']],
            target:'new',
            context:{
                default_res_id:this.chatter.thread.id,
                default_res_model:this.chatter.thread.model,
            },
            res_id:false,
        };
        returnthis.env.bus.trigger('do-action',{
            action,
            options:{
                on_close:()=>{
                    this.trigger('reload',{keepChanges:true});
                },
            },
        });
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickSendMessage(ev){
        if(!this.chatter.composer){
            return;
        }
        if(this.chatter.isComposerVisible&&!this.chatter.composer.isLog){
            this.chatter.update({isComposerVisible:false});
        }else{
            this.chatter.showSendMessage();
        }
    }

}

Object.assign(ChatterTopbar,{
    components,
    props:{
        chatterLocalId:String,
    },
    template:'mail.ChatterTopbar',
});

returnChatterTopbar;

});
