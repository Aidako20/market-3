flectra.define('mail/static/src/components/discuss_mobile_mailbox_selection/discuss_mobile_mailbox_selection.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classDiscussMobileMailboxSelectionextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            return{
                allOrderedAndPinnedMailboxes:this.orderedMailboxes.map(mailbox=>mailbox.__state),
                discussThread:this.env.messaging.discuss.thread
                    ?this.env.messaging.discuss.thread.__state
                    :undefined,
            };
        },{
            compareDepth:{
                allOrderedAndPinnedMailboxes:1,
            },
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.thread[]}
     */
    getorderedMailboxes(){
        returnthis.env.models['mail.thread']
            .all(thread=>thread.isPinned&&thread.model==='mail.box')
            .sort((mailbox1,mailbox2)=>{
                if(mailbox1===this.env.messaging.inbox){
                    return-1;
                }
                if(mailbox2===this.env.messaging.inbox){
                    return1;
                }
                if(mailbox1===this.env.messaging.starred){
                    return-1;
                }
                if(mailbox2===this.env.messaging.starred){
                    return1;
                }
                constmailbox1Name=mailbox1.displayName;
                constmailbox2Name=mailbox2.displayName;
                mailbox1Name<mailbox2Name?-1:1;
            });
    }

    /**
     *@returns{mail.discuss}
     */
    getdiscuss(){
        returnthis.env.messaging&&this.env.messaging.discuss;
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhenclickingonamailboxselectionitem.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onClick(ev){
        const{mailboxLocalId}=ev.currentTarget.dataset;
        constmailbox=this.env.models['mail.thread'].get(mailboxLocalId);
        if(!mailbox){
            return;
        }
        mailbox.open();
    }

}

Object.assign(DiscussMobileMailboxSelection,{
    props:{},
    template:'mail.DiscussMobileMailboxSelection',
});

returnDiscussMobileMailboxSelection;

});
