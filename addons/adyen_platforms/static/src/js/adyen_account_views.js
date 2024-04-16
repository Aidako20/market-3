flectra.define('adyen_platforms.account_views',function(require){
"usestrict";

varcore=require('web.core');
varDialog=require('web.Dialog');
varFormController=require('web.FormController');
varFormView=require('web.FormView');
varviewRegistry=require('web.view_registry');

var_t=core._t;
varQWeb=core.qweb;

varAdyenAccountFormController=FormController.extend({
    _saveRecord:function(recordID,options){
        if(this.model.isNew(this.handle)&&this.canBeSaved()){
            var_super=this._super.bind(this,recordID,options);
            varbuttons=[
                {
                    text:_t("Create"),
                    classes:'btn-primaryo_adyen_confirm',
                    close:true,
                    disabled:true,
                    click:function(){
                        this.close();
                        _super();
                    },
                },
                {
                    text:_t("Cancel"),
                    close:true,
                }
            ];

            vardialog=newDialog(this,{
                size:'extra-large',
                buttons:buttons,
                title:_t("ConfirmyourAdyenAccountCreation"),
                $content:QWeb.render('AdyenAccountCreationConfirmation',{
                    data:this.model.get(this.handle).data,
                }),
            });

            dialog.open().opened(function(){
                dialog.$el.on('change','.opt_in_checkbox',function(ev){
                    ev.preventDefault();
                    dialog.$footer.find('.o_adyen_confirm')[0].disabled=!ev.currentTarget.checked;
                });
            });
        }elseif(!this.model.isNew(this.handle)){
            returnthis._super.apply(this,arguments);
        }
    },
});

varAdyenAccountFormView=FormView.extend({
    config:_.extend({},FormView.prototype.config,{
        Controller:AdyenAccountFormController,
    }),
});

viewRegistry.add('adyen_account_form',AdyenAccountFormView);

});
