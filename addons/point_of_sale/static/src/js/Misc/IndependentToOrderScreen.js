flectra.define('point_of_sale.IndependentToOrderScreen',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');

    classIndependentToOrderScreenextendsPosComponent{
        /**
         *AliastheforceTriggerSelectedOrdermethodasitalso
         *means'closing'thisscreen.
         */
        close(){
            this.forceTriggerSelectedOrder();
        }
        forceTriggerSelectedOrder(){
            //Callingthismethodforcefullytriggerchange
            //ontheselectedOrderattribute,whichthenshowsthescreenofthe
            //currentorder,essentiallyclosingthisscreen.
            this.env.pos.trigger('change:selectedOrder',this.env.pos,this.env.pos.get_order());
        }
    }

    returnIndependentToOrderScreen;
});
