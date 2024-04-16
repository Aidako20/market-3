flectra.define('point_of_sale.OrderManagementButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');
    const{isRpcError}=require('point_of_sale.utils');

    classOrderManagementButtonextendsPosComponent{
        asynconClick(){
            try{
                //pingtheserver,ifnoerror,showthescreen
                awaitthis.rpc({
                    model:'pos.order',
                    method:'browse',
                    args:[[]],
                    kwargs:{context:this.env.session.user_context},
                });
                this.showScreen('OrderManagementScreen');
            }catch(error){
                if(isRpcError(error)&&error.message.code<0){
                    this.showPopup('ErrorPopup',{
                        title:this.env._t('NetworkError'),
                        body:this.env._t('Cannotaccessordermanagementscreenifoffline.'),
                    });
                }else{
                    throwerror;
                }
            }
        }
    }
    OrderManagementButton.template='OrderManagementButton';

    Registries.Component.add(OrderManagementButton);

    returnOrderManagementButton;
});
