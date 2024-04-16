flectra.define('point_of_sale.CashierName',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    //PreviouslyUsernameWidget
    classCashierNameextendsPosComponent{
        getusername(){
            constcashier=this.env.pos.get_cashier();
            if(cashier){
                returncashier.name;
            }else{
                return'';
            }
        }
    }
    CashierName.template='CashierName';

    Registries.Component.add(CashierName);

    returnCashierName;
});
