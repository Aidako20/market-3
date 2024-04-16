flectra.define('mail/static/src/components/activity/activity.js',function(require){
'usestrict';

constcomponents={
    ActivityMarkDonePopover:require('mail/static/src/components/activity_mark_done_popover/activity_mark_done_popover.js'),
    FileUploader:require('mail/static/src/components/file_uploader/file_uploader.js'),
    MailTemplate:require('mail/static/src/components/mail_template/mail_template.js'),
};
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{
    auto_str_to_date,
    getLangDateFormat,
    getLangDatetimeFormat,
}=require('web.time');

const{Component,useState}=owl;
const{useRef}=owl.hooks;

classActivityextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        this.state=useState({
            areDetailsVisible:false,
        });
        useStore(props=>{
            constactivity=this.env.models['mail.activity'].get(props.activityLocalId);
            return{
                activity:activity?activity.__state:undefined,
                assigneeNameOrDisplayName:(
                    activity&&
                    activity.assignee&&
                    activity.assignee.nameOrDisplayName
                ),
            };
        });
        /**
         *Referenceofthefileuploader.
         *Usefultoprogrammaticallypromptsthebrowserfileuploader.
         */
        this._fileUploaderRef=useRef('fileUploader');
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@returns{mail.activity}
     */
    getactivity(){
        returnthis.env.models['mail.activity'].get(this.props.activityLocalId);
    }

    /**
     *@returns{string}
     */
    getassignedUserText(){
        return_.str.sprintf(this.env._t("for%s"),this.activity.assignee.nameOrDisplayName);
    }

    /**
     *@returns{string}
     */
    getdelayLabel(){
        consttoday=moment().startOf('day');
        constmomentDeadlineDate=moment(auto_str_to_date(this.activity.dateDeadline));
        //truemeansnorounding
        constdiff=momentDeadlineDate.diff(today,'days',true);
        if(diff===0){
            returnthis.env._t("Today:");
        }elseif(diff===-1){
            returnthis.env._t("Yesterday:");
        }elseif(diff<0){
            return_.str.sprintf(this.env._t("%ddaysoverdue:"),Math.abs(diff));
        }elseif(diff===1){
            returnthis.env._t("Tomorrow:");
        }else{
            return_.str.sprintf(this.env._t("Duein%ddays:"),Math.abs(diff));
        }
    }

    /**
     *@returns{string}
     */
    getformattedCreateDatetime(){
        constmomentCreateDate=moment(auto_str_to_date(this.activity.dateCreate));
        constdatetimeFormat=getLangDatetimeFormat();
        returnmomentCreateDate.format(datetimeFormat);
    }

    /**
     *@returns{string}
     */
    getformattedDeadlineDate(){
        constmomentDeadlineDate=moment(auto_str_to_date(this.activity.dateDeadline));
        constdatetimeFormat=getLangDateFormat();
        returnmomentDeadlineDate.format(datetimeFormat);
    }

    /**
     *@returns{string}
     */
    getMARK_DONE(){
        returnthis.env._t("MarkDone");
    }

    /**
     *@returns{string}
     */
    getsummary(){
        return_.str.sprintf(this.env._t("“%s”"),this.activity.summary);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{CustomEvent}ev
     *@param{Object}ev.detail
     *@param{mail.attachment}ev.detail.attachment
     */
    async_onAttachmentCreated(ev){
        awaitthis.activity.markAsDone({attachments:[ev.detail.attachment]});
        this.trigger('o-attachments-changed');
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClick(ev){
        if(
            ev.target.tagName==='A'&&
            ev.target.dataset.oeId&&
            ev.target.dataset.oeModel
        ){
            this.env.messaging.openProfile({
                id:Number(ev.target.dataset.oeId),
                model:ev.target.dataset.oeModel,
            });
            //avoidfollowingdummyhref
            ev.preventDefault();
        }
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    async_onClickCancel(ev){
        ev.preventDefault();
        awaitthis.activity.deleteServerRecord();
        this.trigger('reload',{keepChanges:true});
    }

    /**
     *@private
     */
    _onClickDetailsButton(ev){
        ev.preventDefault();
        this.state.areDetailsVisible=!this.state.areDetailsVisible;
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    async_onClickEdit(ev){
        awaitthis.activity.edit();
        this.trigger('reload',{keepChanges:true});
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickUploadDocument(ev){
        this._fileUploaderRef.comp.openBrowserFileUploader();
    }

}

Object.assign(Activity,{
    components,
    props:{
        activityLocalId:String,
    },
    template:'mail.Activity',
});

returnActivity;

});
