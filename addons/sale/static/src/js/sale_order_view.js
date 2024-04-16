flectra.define('sale.SaleOrderView',function(require){
    "usestrict";

    constFormController=require('web.FormController');
    constFormView=require('web.FormView');
    constviewRegistry=require('web.view_registry');
    constDialog=require('web.Dialog');
    constcore=require('web.core');
    const_t=core._t;

    constSaleOrderFormController=FormController.extend({
        custom_events:_.extend({},FormController.prototype.custom_events,{
            open_discount_wizard:'_onOpenDiscountWizard',
        }),

        //-------------------------------------------------------------------------
        //Handlers
        //-------------------------------------------------------------------------

        /**
         *Handlercalledifuserchangesthediscountfieldinthesaleorderline.
         *Thewizardwillopenonlyif
         * (1)Saleorderlineis3ormore
         * (2)Firstsaleorderlineischangedtodiscount
         * (3)Discountisthesameinallsaleorderline
         */
        _onOpenDiscountWizard(ev){
            constorderLines=this.renderer.state.data.order_line.data.filter(line=>!line.data.display_type);
            constrecordData=ev.target.recordData;
            if(recordData.discount===orderLines[0].data.discount)return;
            constisEqualDiscount=orderLines.slice(1).every(line=>line.data.discount===recordData.discount);
            if(orderLines.length>=3&&recordData.sequence===orderLines[0].data.sequence&&isEqualDiscount){
                Dialog.confirm(this,_t("Doyouwanttoapplythisdiscounttoallorderlines?"),{
                    confirm_callback:()=>{
                        orderLines.slice(1).forEach((line)=>{
                            this.trigger_up('field_changed',{
                                dataPointID:this.renderer.state.id,
                                changes:{order_line:{operation:"UPDATE",id:line.id,data:{discount:orderLines[0].data.discount}}},
                            });
                        });
                    },
                });
            }
        },
    });

    constSaleOrderView=FormView.extend({
        config:_.extend({},FormView.prototype.config,{
            Controller:SaleOrderFormController,
        }),
    });

    viewRegistry.add('sale_discount_form',SaleOrderView);

    returnSaleOrderView;

});
