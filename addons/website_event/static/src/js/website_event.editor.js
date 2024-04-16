flectra.define('website_event.editor',function(require){
"usestrict";

varcore=require('web.core');
varwUtils=require('website.utils');
varWebsiteNewMenu=require('website.newMenu');

var_t=core._t;

WebsiteNewMenu.include({
    actions:_.extend({},WebsiteNewMenu.prototype.actions||{},{
        new_event:'_createNewEvent',
    }),

    //--------------------------------------------------------------------------
    //Actions
    //--------------------------------------------------------------------------

    /**
     *Askstheuserinformationaboutaneweventtocreate,thencreatesit
     *andredirectstheusertothisnewevent.
     *
     *@private
     *@returns{Promise}Unresolvedifthereisaredirection
     */
    _createNewEvent:function(){
        varself=this;
        returnwUtils.prompt({
            id:"editor_new_event",
            window_title:_t("NewEvent"),
            input:_t("EventName"),
        }).then(function(result){
            vareventName=result.val;
            if(!eventName){
                return;
            }
            returnself._rpc({
                route:'/event/add_event',
                params:{
                    event_name:eventName,
                },
            }).then(function(url){
                window.location.href=url;
                returnnewPromise(function(){});
            });
        });
    },
});
});
