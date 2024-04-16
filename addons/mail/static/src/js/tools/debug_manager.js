flectra.define('mail.DebugManager.Backend',function(require){
"usestrict";

varcore=require('web.core');
varDebugManager=require('web.DebugManager.Backend');

var_t=core._t;
/**
 *addsanewmethodavailableforthedebugmanager,calledbythe"ManageMessages"button.
 *
 */
DebugManager.include({
    getMailMessages:function(){
        varselectedIDs=this._controller.getSelectedIds();
        if(!selectedIDs.length){
            console.warn(_t("Nomessageavailable"));
            return;
        }
        this.do_action({
            res_model:'mail.message',
            name:_t('ManageMessages'),
            views:[[false,'list'],[false,'form']],
            type:'ir.actions.act_window',
            domain:[['res_id','=',selectedIDs[0]],['model','=',this._controller.modelName]],
            context:{
                default_res_model:this._controller.modelName,
                default_res_id:selectedIDs[0],
            },
        });
    },
});

});
