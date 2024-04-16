flectra.define('mail/static/src/components/activity_mark_done_popover/activity_mark_done_popover.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;
const{useRef}=owl.hooks;

classActivityMarkDonePopoverextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constactivity=this.env.models['mail.activity'].get(props.activityLocalId);
            return{
                activity:activity?activity.__state:undefined,
            };
        });
        this._feedbackTextareaRef=useRef('feedbackTextarea');
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    mounted(){
        this._feedbackTextareaRef.el.focus();
        if(this.activity.feedbackBackup){
            this._feedbackTextareaRef.el.value=this.activity.feedbackBackup;
        }
    }

    /**
     *@returns{mail.activity}
     */
    getactivity(){
        returnthis.env.models['mail.activity'].get(this.props.activityLocalId);
    }

    /**
     *@returns{string}
     */
    getDONE_AND_SCHEDULE_NEXT(){
        returnthis.env._t("Done&ScheduleNext");
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _close(){
        this.trigger('o-popover-close');
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onBlur(){
        this.activity.update({
            feedbackBackup:this._feedbackTextareaRef.el.value,
        });
    }

    /**
     *@private
     */
    _onClickDiscard(){
        this._close();
    }

    /**
     *@private
     */
    async_onClickDone(){
        awaitthis.activity.markAsDone({
            feedback:this._feedbackTextareaRef.el.value,
        });
        this.trigger('reload',{keepChanges:true});
    }

    /**
     *@private
     */
    async_onClickDoneAndScheduleNext(){
        awaitthis.activity.markAsDoneAndScheduleNext({
            feedback:this._feedbackTextareaRef.el.value,
        });
        this.trigger('reload',{keepChanges:true});
    }

    /**
     *@private
     */
    _onKeydown(ev){
        if(ev.key==='Escape'){
            this._close();
        }
    }

}

Object.assign(ActivityMarkDonePopover,{
    props:{
        activityLocalId:String,
    },
    template:'mail.ActivityMarkDonePopover',
});

returnActivityMarkDonePopover;

});
