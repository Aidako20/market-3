flectra.define('mail/static/src/components/discuss_sidebar_item/discuss_sidebar_item.js',function(require){
'usestrict';

constcomponents={
    EditableText:require('mail/static/src/components/editable_text/editable_text.js'),
    ThreadIcon:require('mail/static/src/components/thread_icon/thread_icon.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');
const{isEventHandled}=require('mail/static/src/utils/utils.js');

constDialog=require('web.Dialog');

const{Component}=owl;

classDiscussSidebarItemextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constdiscuss=this.env.messaging.discuss;
            constthread=this.env.models['mail.thread'].get(props.threadLocalId);
            constcorrespondent=thread?thread.correspondent:undefined;
            return{
                correspondentName:correspondent&&correspondent.name,
                discussIsRenamingThread:discuss&&discuss.renamingThreads.includes(thread),
                isDiscussThread:discuss&&discuss.thread===thread,
                starred:this.env.messaging.starred,
                thread,
                threadChannelType:thread&&thread.channel_type,
                threadCounter:thread&&thread.counter,
                threadDisplayName:thread&&thread.displayName,
                threadGroupBasedSubscription:thread&&thread.group_based_subscription,
                threadLocalMessageUnreadCounter:thread&&thread.localMessageUnreadCounter,
                threadMassMailing:thread&&thread.mass_mailing,
                threadMessageNeedactionCounter:thread&&thread.message_needaction_counter,
                threadModel:thread&&thread.model,
            };
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Getthecounterofthisdiscussitem,whichisbasedonthethreadtype.
     *
     *@returns{integer}
     */
    getcounter(){
        if(this.thread.model==='mail.box'){
            returnthis.thread.counter;
        }elseif(this.thread.channel_type==='channel'){
            returnthis.thread.message_needaction_counter;
        }elseif(this.thread.channel_type==='chat'){
            returnthis.thread.localMessageUnreadCounter;
        }
        return0;
    }

    /**
     *@returns{mail.discuss}
     */
    getdiscuss(){
        returnthis.env.messaging&&this.env.messaging.discuss;
    }

    /**
     *@returns{boolean}
     */
    hasUnpin(){
        returnthis.thread.channel_type==='chat';
    }

    /**
     *@returns{mail.thread}
     */
    getthread(){
        returnthis.env.models['mail.thread'].get(this.props.threadLocalId);
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@returns{Promise}
     */
    _askAdminConfirmation(){
        returnnewPromise(resolve=>{
            Dialog.confirm(this,
                this.env._t("Youaretheadministratorofthischannel.Areyousureyouwanttoleave?"),
                {
                    buttons:[
                        {
                            text:this.env._t("Leave"),
                            classes:'btn-primary',
                            close:true,
                            click:resolve
                        },
                        {
                            text:this.env._t("Discard"),
                            close:true
                        }
                    ]
                }
            );
        });
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     */
    _onCancelRenaming(ev){
        this.discuss.cancelThreadRenaming(this.thread);
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClick(ev){
        if(isEventHandled(ev,'EditableText.click')){
            return;
        }
        this.thread.open();
    }

    /**
     *Stoppropagationtopreventselectingthisitem.
     *
     *@private
     *@param{CustomEvent}ev
     */
    _onClickedEditableText(ev){
        ev.stopPropagation();
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    async_onClickLeave(ev){
        ev.stopPropagation();
        if(this.thread.creator===this.env.messaging.currentUser){
            awaitthis._askAdminConfirmation();
        }
        this.thread.unsubscribe();
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickRename(ev){
        ev.stopPropagation();
        this.discuss.setThreadRenaming(this.thread);
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickSettings(ev){
        ev.stopPropagation();
        returnthis.env.bus.trigger('do-action',{
            action:{
                type:'ir.actions.act_window',
                res_model:this.thread.model,
                res_id:this.thread.id,
                views:[[false,'form']],
                target:'current'
            },
        });
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickUnpin(ev){
        ev.stopPropagation();
        this.thread.unsubscribe();
    }

    /**
     *@private
     *@param{CustomEvent}ev
     *@param{Object}ev.detail
     *@param{string}ev.detail.newName
     */
    _onValidateEditableText(ev){
        ev.stopPropagation();
        this.discuss.renameThread(this.thread,ev.detail.newName);
    }

}

Object.assign(DiscussSidebarItem,{
    components,
    props:{
        threadLocalId:String,
    },
    template:'mail.DiscussSidebarItem',
});

returnDiscussSidebarItem;

});
