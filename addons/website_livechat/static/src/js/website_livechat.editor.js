flectra.define('website_livechat.editor',function(require){
'usestrict';

varcore=require('web.core');
varwUtils=require('website.utils');
varWebsiteNewMenu=require('website.newMenu');

var_t=core._t;

WebsiteNewMenu.include({
    actions:_.extend({},WebsiteNewMenu.prototype.actions||{},{
        new_channel:'_createNewChannel',
    }),

    //--------------------------------------------------------------------------
    //Actions
    //--------------------------------------------------------------------------

    /**
     *Askstheuserinformationaboutanewchanneltocreate,thencreatesit
     *andredirectstheusertothisnewchannel.
     *
     *@private
     *@returns{Promise}Unresolvedifthereisaredirection
     */
    _createNewChannel:function(){
        varself=this;
        returnwUtils.prompt({
            window_title:_t("NewChannel"),
            input:_t("Name"),
        }).then(function(result){
            varname=result.val;
            if(!name){
                return;
            }
            returnself._rpc({
                model:'im_livechat.channel',
                method:'create_and_get_website_url',
                args:[[]],
                kwargs:{
                    name:name,
                },
            }).then(function(url){
                window.location.href=url;
                returnnewPromise(function(){});
            });
        });
    },
});

});
