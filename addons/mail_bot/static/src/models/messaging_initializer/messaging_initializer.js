flectra.define('mail_bot/static/src/models/messaging_initializer/messaging_initializer.js',function(require){
'usestrict';

const{registerInstancePatchModel}=require('mail/static/src/model/model_core.js');

registerInstancePatchModel('mail.messaging_initializer','mail_bot/static/src/models/messaging_initializer/messaging_initializer.js',{
    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    async_initializeFlectraBot(){
        constdata=awaitthis.async(()=>this.env.services.rpc({
            model:'mail.channel',
            method:'init_flectrabot',
        }));
        if(!data){
            return;
        }
        this.env.session.flectrabot_initialized=true;
    },

    /**
     *@override
     */
    asyncstart(){
        awaitthis.async(()=>this._super());

        if('flectrabot_initialized'inthis.env.session&&!this.env.session.flectrabot_initialized){
            this._initializeFlectraBot();
        }
    },
});

});
