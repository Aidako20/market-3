flectra.define('purchase_stock.purchase_steps',function(require){
"usestrict";

varcore=require('web.core');

var_t=core._t;
varPurchaseAdditionalTourSteps=require('purchase.purchase_steps');

PurchaseAdditionalTourSteps.include({

    init:function(){
        this._super.apply(this,arguments);
    },

    _get_purchase_stock_steps:function(){
        this._super.apply(this,arguments);
        return[{
            trigger:".oe_button_boxbutton[name='action_view_picking']",
            extra_trigger:".oe_button_boxbutton[name='action_view_picking']",
            content:_t("Receivetheorderedproducts."),
            position:"bottom",
            run:'click',
        },{
            trigger:".o_statusbar_buttonsbutton[name='button_validate']",
            content:_t("Validatethereceiptofallorderedproducts."),
            position:"bottom",
            run:'click',
        },{
            trigger:".modal-footer.btn-primary",
            extra_trigger:".modal-dialog",
            content:_t("Processallthereceiptquantities."),
            position:"bottom",
        },{
            trigger:".o_back_buttona,.breadcrumb-item:not('.active'):last",
            content:_t('Gobacktothepurchaseordertogeneratethevendorbill.'),
            position:'bottom',
        },{
            trigger:".o_statusbar_buttonsbutton[name='action_create_invoice']",
            content:_t("Generatethedraftvendorbill."),
            position:"bottom",
            run:'click',
        }
        ];
    }
});

returnPurchaseAdditionalTourSteps;

});
