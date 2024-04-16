flectra.define('web.Loading',function(require){
"usestrict";

/**
 *LoadingIndicator
 *
 *Whentheuserperformsanaction,itisgoodtogivehimsomefeedbackthat
 *somethingiscurrentlyhappening. ThepurposeoftheLoadingIndicatoristo
 *displayasmallrectangleonthebottomrightofthescreenwithjustthe
 *text'Loading'andthenumberofcurrentlyrunningrpcs.
 *
 *Afteradelayof3s,ifarpcisstillnotcompleted,wealsoblocktheUI.
 */

varconfig=require('web.config');
varcore=require('web.core');
varframework=require('web.framework');
varWidget=require('web.Widget');

var_t=core._t;

varLoading=Widget.extend({
    template:"Loading",

    init:function(parent){
        this._super(parent);
        this.count=0;
        this.blocked_ui=false;
    },
    start:function(){
        core.bus.on('rpc_request',this,this.request_call);
        core.bus.on("rpc_response",this,this.response_call);
        core.bus.on("rpc_response_failed",this,this.response_call);
    },
    destroy:function(){
        this.on_rpc_event(-this.count);
        this._super();
    },
    request_call:function(){
        this.on_rpc_event(1);
    },
    response_call:function(){
        this.on_rpc_event(-1);
    },
    on_rpc_event:function(increment){
        varself=this;
        if(!this.count&&increment===1){
            //BlockUIafter3s
            this.long_running_timer=setTimeout(function(){
                self.blocked_ui=true;
                framework.blockUI();
            },3000);
        }

        this.count+=increment;
        if(this.count>0){
            if(config.isDebug()){
                this.$el.text(_.str.sprintf(_t("Loading(%d)"),this.count));
            }else{
                this.$el.text(_t("Loading"));
            }
            this.$el.show();
            this.getParent().$el.addClass('oe_wait');
        }else{
            this.count=0;
            clearTimeout(this.long_running_timer);
            //Don'tunblockifblockedbysomebodyelse
            if(self.blocked_ui){
                this.blocked_ui=false;
                framework.unblockUI();
            }
            this.$el.fadeOut();
            this.getParent().$el.removeClass('oe_wait');
        }
    }
});

returnLoading;
});

