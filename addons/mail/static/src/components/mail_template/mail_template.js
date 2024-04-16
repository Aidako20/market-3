flectra.define('mail/static/src/components/mail_template/mail_template.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseStore=require('mail/static/src/component_hooks/use_store/use_store.js');

const{Component}=owl;

classMailTemplateextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props=>{
            constactivity=this.env.models['mail.activity'].get(props.activityLocalId);
            constmailTemplate=this.env.models['mail.mail_template'].get(props.mailTemplateLocalId);
            return{
                activity:activity?activity.__state:undefined,
                mailTemplate:mailTemplate?mailTemplate.__state:undefined,
            };
        });
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
     *@returns{mail.mail_template}
     */
    getmailTemplate(){
        returnthis.env.models['mail.mail_template'].get(this.props.mailTemplateLocalId);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickPreview(ev){
        ev.stopPropagation();
        ev.preventDefault();
        this.mailTemplate.preview(this.activity);
    }

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickSend(ev){
        ev.stopPropagation();
        ev.preventDefault();
        this.mailTemplate.send(this.activity);
    }

}

Object.assign(MailTemplate,{
    props:{
        activityLocalId:String,
        mailTemplateLocalId:String,
    },
    template:'mail.MailTemplate',
});

returnMailTemplate;

});
