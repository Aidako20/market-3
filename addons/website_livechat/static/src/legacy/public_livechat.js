flectra.define('website_livechat.legacy.website_livechat.livechat_request',function(require){
"usestrict";

varutils=require('web.utils');
varLivechatButton=require('im_livechat.legacy.im_livechat.im_livechat').LivechatButton;


LivechatButton.include({

    /**
     *@override
     *Checkifachatrequestisopenedforthisvisitor
     *ifyes,replacethesessioncookieandstarttheconversationimmediately.
     *Dothisbeforecallingsupertohaveeverythingreadybeforeexecutingexistingstartlogic.
     *Thisisusedforchatrequestmechanism,whenanoperatorsendachatrequest
     *frombackendtoawebsitevisitor.
     */
    willStart:function(){
        if(this.options.chat_request_session){
            utils.set_cookie('im_livechat_session',JSON.stringify(this.options.chat_request_session),60*60);
        }
        returnthis._super();
    },
});

return{
    LivechatButton:LivechatButton,
};

});
