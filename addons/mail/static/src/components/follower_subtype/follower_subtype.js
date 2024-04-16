flectra.define('mail/static/src/components/follower_subtype/follower_subtype.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classFollowerSubtypeextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constfollowerSubtype=this.env.models['mail.follower_subtype'].get(props.followerSubtypeLocalId);
            return[followerSubtype?followerSubtype.__state:undefined];
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.follower|undefined}
     */
    getfollower(){
        returnthis.env.models['mail.follower'].get(this.props.followerLocalId);
    }

    /**
     *@returns{mail.follower_subtype}
     */
    getfollowerSubtype(){
        returnthis.env.models['mail.follower_subtype'].get(this.props.followerSubtypeLocalId);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhenclickingoncancelbutton.
     *
     *@private
     *@param{Event}ev
     */
    _onChangeCheckbox(ev){
        if(ev.target.checked){
            this.follower.selectSubtype(this.followerSubtype);
        }else{
            this.follower.unselectSubtype(this.followerSubtype);
        }
    }

}

Object.assign(FollowerSubtype,{
    props:{
        followerLocalId:String,
        followerSubtypeLocalId:String,
    },
    template:'mail.FollowerSubtype',
});

returnFollowerSubtype;

});
