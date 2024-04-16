/**
 *ThisfileallowsintroducingnewJSmoduleswithoutcontaminatingotherfiles.
 *ThisisusefulwhenbugfixingrequiresaddingsuchJSmodulesinstable
 *versionsofFlectra.Anymodulethatisdefinedinthisfileshouldbeisolated
 *initsownfileinmaster.
 */
flectra.define('im_livechat/static/src/bugfix/bugfix.js',function(require){
'usestrict';

const{
    registerInstancePatchModel,
}=require('mail/static/src/model/model_core.js');

registerInstancePatchModel('mail.chat_window','im_livechat/static/src/models/chat_window/chat_window.js',{

    /**
     *@override
     */
    close({notifyServer}={}){
        if(
            this.thread&&
            this.thread.model==='mail.channel'&&
            this.thread.channel_type==='livechat'&&
            this.thread.mainCache.isLoaded&&
            this.thread.messages.length===0
        ){
            notifyServer=true;
            this.thread.unpin();
        }
        this._super({notifyServer});
    }
});

});


flectra.define('im_livechat/static/src/models/message/message.js',function(require){
'usestrict';

const{
    registerClassPatchModel,
}=require('mail/static/src/model/model_core.js');

registerClassPatchModel('mail.message','im_livechat/static/src/models/message/message.js',{
    /**
     *@override
     */
    convertData(data){
        constdata2=this._super(data);
        if('author_id'indata){
            if(data.author_id[2]){
                //fluxspecificforlivechat,a3rdparamislivechat_username
                //andmeans2ndparam(display_name)shouldbeignored
                data2.author=[
                    ['insert-and-replace',{
                        id:data.author_id[0],
                        livechat_username:data.author_id[2],
                    }],
                ];
            }
        }
        returndata2;
    },
});

});

flectra.define('im_livechat/static/src/models/composer/composer.js',function(require){
'usestrict';

const{registerInstancePatchModel}=require('mail/static/src/model/model_core.js');

registerInstancePatchModel('mail.composer','im_livechat/static/src/models/composer/composer.js',{
    /**
     *@override
     */
    _computeHasDropZone(){
        if(this.thread&&this.thread.channel_type==='livechat'){
            returnfalse;
        }
        returnthis._super();
    },
});

});
