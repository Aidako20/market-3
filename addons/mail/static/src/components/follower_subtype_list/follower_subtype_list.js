flectra.define('mail/static/src/components/follower_subtype_list/follower_subtype_list.js',function(require){
'usestrict';

constcomponents={
    FollowerSubtype:require('mail/static/src/components/follower_subtype/follower_subtype.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component,QWeb}=owl;

classFollowerSubtypeListextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constfollowerSubtypeList=this.env.models['mail.follower_subtype_list'].get(props.localId);
            constfollower=followerSubtypeList
                ?followerSubtypeList.follower
                :undefined;
            constfollowerSubtypes=follower?follower.subtypes:[];
            return{
                follower:follower?follower.__state:undefined,
                followerSubtypeList:followerSubtypeList
                    ?followerSubtypeList.__state
                    :undefined,
                followerSubtypes:followerSubtypes.map(subtype=>subtype.__state),
            };
        },{
            compareDepth:{
                followerSubtypes:1,
            },
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.follower_subtype_list}
     */
    getfollowerSubtypeList(){
        returnthis.env.models['mail.follower_subtype_list'].get(this.props.localId);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhenclickingoncancelbutton.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onClickCancel(ev){
        this.followerSubtypeList.follower.closeSubtypes();
    }

    /**
     *Calledwhenclickingonapplybutton.
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onClickApply(ev){
        this.followerSubtypeList.follower.updateSubtypes();
    }

}

Object.assign(FollowerSubtypeList,{
    components,
    props:{
        localId:String,
    },
    template:'mail.FollowerSubtypeList',
});

QWeb.registerComponent('FollowerSubtypeList',FollowerSubtypeList);

returnFollowerSubtypeList;

});
