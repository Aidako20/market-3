flectra.define('pos_restaurant.OrderManagementScreen',function(require){
    'usestrict';

    constOrderManagementScreen=require('point_of_sale.OrderManagementScreen');
    constRegistries=require('point_of_sale.Registries');

    constPosResOrderManagementScreen=(OrderManagementScreen)=>
        classextendsOrderManagementScreen{
            /**
             *@override
             */
            _setOrder(order){
                if(this.env.pos.config.module_pos_restaurant){
                    constcurrentOrder=this.env.pos.get_order();
                    this.env.pos.set_table(order.table,order);
                    if(currentOrder&&currentOrder.uid===order.uid){
                        this.close();
                    }
                }else{
                    super._setOrder(order);
                }
            }
        };

    Registries.Component.extend(OrderManagementScreen,PosResOrderManagementScreen);

    returnOrderManagementScreen;
});
