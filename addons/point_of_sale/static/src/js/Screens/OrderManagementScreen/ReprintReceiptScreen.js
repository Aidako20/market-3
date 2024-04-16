flectra.define('point_of_sale.ReprintReceiptScreen',function(require){
    'usestrict';

    constAbstractReceiptScreen=require('point_of_sale.AbstractReceiptScreen');
    constRegistries=require('point_of_sale.Registries');

    constReprintReceiptScreen=(AbstractReceiptScreen)=>{
        classReprintReceiptScreenextendsAbstractReceiptScreen{
            mounted(){
                this.printReceipt();
            }
            confirm(){
                this.showScreen('OrderManagementScreen');
            }
            asyncprintReceipt(){
                if(this.env.pos.proxy.printer&&this.env.pos.config.iface_print_skip_screen){
                    letresult=awaitthis._printReceipt();
                    if(result)
                        this.showScreen('OrderManagementScreen');
                }
            }
            asynctryReprint(){
                awaitthis._printReceipt();
            }
        }
        ReprintReceiptScreen.template='ReprintReceiptScreen';
        returnReprintReceiptScreen;
    };
    Registries.Component.addByExtending(ReprintReceiptScreen,AbstractReceiptScreen);

    returnReprintReceiptScreen;
});
