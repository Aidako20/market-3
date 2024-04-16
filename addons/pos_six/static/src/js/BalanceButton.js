flectra.define('pos_six.BalanceButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classBalanceButtonextendsPosComponent{
        sendBalance(){
            this.env.pos.payment_methods.map(pm=>{
                if(pm.use_payment_terminal==='six'){
                    pm.payment_terminal.send_balance();
                }
            });
        }
    }
    BalanceButton.template='BalanceButton';

    Registries.Component.add(BalanceButton);

    returnBalanceButton;
});
