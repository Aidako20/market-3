flectra.define('mail/static/src/components/follow_button/follow_button.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;
const{useState}=owl.hooks;

classFollowButtonextendsComponent{
    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        this.state=useState({
            /**
             *Determinewhethertheunfollowbuttonishighlightedornot.
             */
            isUnfollowButtonHighlighted:false,
        });
        useStore(props=>{
            constthread=this.env.models['mail.thread'].get(props.threadLocalId);
            return{
                threadIsCurrentPartnerFollowing:thread&&thread.isCurrentPartnerFollowing,
            };
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@return{mail.thread}
     */
    getthread(){
        returnthis.env.models['mail.thread'].get(this.props.threadLocalId);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickFollow(ev){
        this.thread.follow();
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    async_onClickUnfollow(ev){
        awaitthis.thread.unfollow();
        this.trigger('reload',{fieldNames:['message_follower_ids'],keepChanges:true});
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onMouseLeaveUnfollow(ev){
        this.state.isUnfollowButtonHighlighted=false;
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onMouseEnterUnfollow(ev){
        this.state.isUnfollowButtonHighlighted=true;
    }

}

Object.assign(FollowButton,{
    defaultProps:{
        isDisabled:false,
    },
    props:{
        isDisabled:Boolean,
        threadLocalId:String,
    },
    template:'mail.FollowButton',
});

returnFollowButton;

});
