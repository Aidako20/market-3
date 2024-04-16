flectra.define('stock.InventoryReportListController',function(require){
"usestrict";

varcore=require('web.core');
varListController=require('web.ListController');

varqweb=core.qweb;


varInventoryReportListController=ListController.extend({

    //-------------------------------------------------------------------------
    //Public
    //-------------------------------------------------------------------------

    init:function(parent,model,renderer,params){
        this.context=renderer.state.getContext();
        returnthis._super.apply(this,arguments);
    },

    /**
     *@override
     */
    renderButtons:function($node){
        this._super.apply(this,arguments);
        if(this.context.no_at_date){
            return;
        }
        var$buttonToDate=$(qweb.render('InventoryReport.Buttons'));
        $buttonToDate.on('click',this._onOpenWizard.bind(this));
        this.$buttons.prepend($buttonToDate);
    },

    //-------------------------------------------------------------------------
    //Handlers
    //-------------------------------------------------------------------------

    /**
     *Handlercalledwhentheuserclickedonthe'InventoryatDate'button.
     *Openswizardtodisplay,atchoice,theproductsinventoryoracomputed
     *inventoryatagivendate.
     */
    _onOpenWizard:function(){
        varstate=this.model.get(this.handle,{raw:true});
        varstateContext=state.getContext();
        varcontext={
            active_model:this.modelName,
        };
        if(stateContext.default_product_id){
            context.product_id=stateContext.default_product_id;
        }elseif(stateContext.product_tmpl_id){
            context.product_tmpl_id=stateContext.product_tmpl_id;
        }
        this.do_action({
            res_model:'stock.quantity.history',
            views:[[false,'form']],
            target:'new',
            type:'ir.actions.act_window',
            context:context,
        });
    },
});

returnInventoryReportListController;

});
