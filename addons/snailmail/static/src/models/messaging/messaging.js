flectra.define('snailmail/static/src/models/messaging/messaging.js',function(require){
'usestrict';

const{
    registerInstancePatchModel,
    registerFieldPatchModel,
}=require('mail/static/src/model/model_core.js');
const{attr}=require('mail/static/src/model/model_field.js');

registerInstancePatchModel('mail.messaging','snailmail/static/src/models/messaging/messaging.js',{
    asyncfetchSnailmailCreditsUrl(){
        constsnailmail_credits_url=awaitthis.async(()=>this.env.services.rpc({
            model:'iap.account',
            method:'get_credits_url',
            args:['snailmail'],
        }));
        this.update({
            snailmail_credits_url,
        });
    },
    asyncfetchSnailmailCreditsUrlTrial(){
        constsnailmail_credits_url_trial=awaitthis.async(()=>this.env.services.rpc({
            model:'iap.account',
            method:'get_credits_url',
            args:['snailmail','',0,true],
        }));
        this.update({
            snailmail_credits_url_trial,
        });
    },
});

registerFieldPatchModel('mail.messaging','snailmail/static/src/models/messaging/messaging.js',{
    snailmail_credits_url:attr(),
    snailmail_credits_url_trial:attr(),
});

});
