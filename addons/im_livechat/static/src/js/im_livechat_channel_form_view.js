flectra.define('im_livechat.ImLivechatChannelFormView',function(require){
"usestrict";

constImLivechatChannelFormController=require('im_livechat.ImLivechatChannelFormController');

constFormView=require('web.FormView');
constviewRegistry=require('web.view_registry');

constImLivechatChannelFormView=FormView.extend({
    config:Object.assign({},FormView.prototype.config,{
        Controller:ImLivechatChannelFormController,
    }),
});

viewRegistry.add('im_livechat_channel_form_view_js',ImLivechatChannelFormView);

returnImLivechatChannelFormView;

});
