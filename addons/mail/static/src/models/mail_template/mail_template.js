flectra.define('mail/static/src/models/mail_template/mail_template.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr,many2many}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classMailTemplateextendsdependencies['mail.model']{

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *@param{mail.activity}activity
         */
        preview(activity){
            constaction={
                name:this.env._t("ComposeEmail"),
                type:'ir.actions.act_window',
                res_model:'mail.compose.message',
                views:[[false,'form']],
                target:'new',
                context:{
                    default_res_id:activity.thread.id,
                    default_model:activity.thread.model,
                    default_use_template:true,
                    default_template_id:this.id,
                    force_email:true,
                },
            };
            this.env.bus.trigger('do-action',{
                action,
                options:{
                    on_close:()=>{
                        activity.thread.refresh();
                    },
                },
            });
        }

        /**
         *@param{mail.activity}activity
         */
        asyncsend(activity){
            awaitthis.async(()=>this.env.services.rpc({
                model:activity.thread.model,
                method:'activity_send_mail',
                args:[[activity.thread.id],this.id],
            }));
            activity.thread.refresh();
        }

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *@override
         */
        static_createRecordLocalId(data){
            return`${this.modelName}_${data.id}`;
        }

    }

    MailTemplate.fields={
        activities:many2many('mail.activity',{
            inverse:'mailTemplates',
        }),
        id:attr(),
        name:attr(),
    };

    MailTemplate.modelName='mail.mail_template';

    returnMailTemplate;
}

registerNewModel('mail.mail_template',factory);

});
