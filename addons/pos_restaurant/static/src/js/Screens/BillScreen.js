flectra.define('pos_restaurant.BillScreen',function(require){
    'usestrict';

    constReceiptScreen=require('point_of_sale.ReceiptScreen');
    constRegistries=require('point_of_sale.Registries');

    constBillScreen=(ReceiptScreen)=>{
        classBillScreenextendsReceiptScreen{
            confirm(){
                this.props.resolve({confirmed:true,payload:null});
                this.trigger('close-temp-screen');
            }
            whenClosing(){
                this.confirm();
            }
            /**
             *@override
             */
            asyncprintReceipt(){
                awaitsuper.printReceipt();
                this.currentOrder._printed=false;
            }
        }
        BillScreen.template='BillScreen';
        returnBillScreen;
    };

    Registries.Component.addByExtending(BillScreen,ReceiptScreen);

    returnBillScreen;
});
