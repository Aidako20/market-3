flectra.define('mail/static/src/components/chatter_container/chatter_container.js',function(require){
'usestrict';

constcomponents={
    Chatter:require('mail/static/src/components/chatter/chatter.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');
constuseUpdate=require('mail/static/src/component_hooks/use_update/use_update.js');
const{clear}=require('mail/static/src/model/model_field_command.js');

const{Component}=owl;

/**
 *Thiscomponentabstractschattercomponenttoitsparent,sothatitcanbe
 *mountedandreceivechatterdataevenwhenachattercomponentcannotbe
 *created.Indeed,inordertocreateachattercomponent,wemustcreate
 *achatterrecord,thelatterrequiringmessagingtobeinitialized.Theview
 *mayattempttocreateachatterbeforemessaginghasbeeninitialized,so
 *thiscomponentdelaysthemountingofchatteruntilitbecomesinitialized.
 */
classChatterContainerextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        this.chatter=undefined;
        this._wasMessagingInitialized=false;
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constisMessagingInitialized=this.env.isMessagingInitialized();
            //Delaycreationofchatterrecorduntilmessagingisinitialized.
            //Ideallyshouldobservemodelsdirectlytodetectchangeinstead
            //ofusing`useStore`.
            if(!this._wasMessagingInitialized&&isMessagingInitialized){
                this._wasMessagingInitialized=true;
                this._insertFromProps(props);
            }
            return{chatter:this.chatter};
        });
        useUpdate({func:()=>this._update()});
    }

    /**
     *@override
     */
    willUpdateProps(nextProps){
        if(this.env.isMessagingInitialized()){
            this._insertFromProps(nextProps);
        }
        returnsuper.willUpdateProps(...arguments);
    }

    /**
     *@override
     */
    destroy(){
        super.destroy();
        if(this.chatter){
            this.chatter.delete();
        }
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _insertFromProps(props){
        constvalues=Object.assign({},props);
        if(values.threadId===undefined){
            values.threadId=clear();
        }
        if(!this.chatter){
            this.chatter=this.env.models['mail.chatter'].create(values);
        }else{
            this.chatter.update(values);
        }
    }

    /**
     *@private
     */
    _update(){
        if(this.chatter){
            this.chatter.refresh();
        }
    }

}

Object.assign(ChatterContainer,{
    components,
    props:{
        hasActivities:{
            type:Boolean,
            optional:true,
        },
        hasExternalBorder:{
            type:Boolean,
            optional:true,
        },
        hasFollowers:{
            type:Boolean,
            optional:true,
        },
        hasMessageList:{
            type:Boolean,
            optional:true,
        },
        hasMessageListScrollAdjust:{
            type:Boolean,
            optional:true,
        },
        hasTopbarCloseButton:{
            type:Boolean,
            optional:true,
        },
        isAttachmentBoxVisibleInitially:{
            type:Boolean,
            optional:true,
        },
        threadId:{
            type:Number,
            optional:true,
        },
        threadModel:String,
    },
    template:'mail.ChatterContainer',
});


returnChatterContainer;

});
