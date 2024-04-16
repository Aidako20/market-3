flectra.define('mail/static/src/components/activity_box/activity_box.js',function(require){
'usestrict';

constcomponents={
    Activity:require('mail/static/src/components/activity/activity.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classActivityBoxextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constchatter=this.env.models['mail.chatter'].get(props.chatterLocalId);
            constthread=chatter&&chatter.thread;
            return{
                chatter:chatter?chatter.__state:undefined,
                thread:thread&&thread.__state,
            };
        });
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{Chatter}
     */
    getchatter(){
        returnthis.env.models['mail.chatter'].get(this.props.chatterLocalId);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onClickTitle(ev){
        ev.preventDefault();
        this.chatter.toggleActivityBoxVisibility();
    }

}

Object.assign(ActivityBox,{
    components,
    props:{
        chatterLocalId:String,
    },
    template:'mail.ActivityBox',
});

returnActivityBox;

});
