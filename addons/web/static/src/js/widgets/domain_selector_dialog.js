flectra.define("web.DomainSelectorDialog",function(require){
"usestrict";

varcore=require("web.core");
varDialog=require("web.Dialog");
varDomainSelector=require("web.DomainSelector");

var_t=core._t;

/**
 *@classDomainSelectorDialog
 */
returnDialog.extend({
    init:function(parent,model,domain,options){
        this.model=model;
        this.options=_.extend({
            readonly:true,
            debugMode:false,
        },options||{});

        varbuttons;
        if(this.options.readonly){
            buttons=[
                {text:_t("Close"),close:true},
            ];
        }else{
            buttons=[
                {text:_t("Save"),classes:"btn-primary",close:true,click:function(){
                    this.trigger_up("domain_selected",{domain:this.domainSelector.getDomain()});
                }},
                {text:_t("Discard"),close:true},
            ];
        }

        this._super(parent,_.extend({},{
            title:_t("Domain"),
            buttons:buttons,
        },options||{}));

        this.domainSelector=newDomainSelector(this,model,domain,options);
    },
    start:function(){
        varself=this;
        this.opened().then(function(){
            //thisrestoresdefaultmodalheight(bootstrap)andallowsfieldselectortooverflow
            self.$el.css('overflow','visible').closest('.modal-dialog').css('height','auto');
        });
        returnPromise.all([
            this._super.apply(this,arguments),
            this.domainSelector.appendTo(this.$el)
        ]);
    },
});
});
