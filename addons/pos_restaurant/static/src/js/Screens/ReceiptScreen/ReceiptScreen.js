flectra.define('pos_restaurant.ReceiptScreen',function(require){
    'usestrict';

    constReceiptScreen=require('point_of_sale.ReceiptScreen');
    constRegistries=require('point_of_sale.Registries');

    constPosResReceiptScreen=ReceiptScreen=>
        classextendsReceiptScreen{
            /**
             *@override
             */
            getnextScreen(){
                if(
                    this.env.pos.config.module_pos_restaurant&&
                    this.env.pos.config.iface_floorplan
                ){
                    consttable=this.env.pos.table;
                    return{name:'FloorScreen',props:{floor:table?table.floor:null}};
                }else{
                    returnsuper.nextScreen;
                }
            }
        };

    Registries.Component.extend(ReceiptScreen,PosResReceiptScreen);

    returnReceiptScreen;
});
