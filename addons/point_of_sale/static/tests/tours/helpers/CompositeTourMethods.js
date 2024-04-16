flectra.define('point_of_sale.tour.CompositeTourMethods',function(require){
    'usestrict';

    const{ProductScreen}=require('point_of_sale.tour.ProductScreenTourMethods');
    const{ReceiptScreen}=require('point_of_sale.tour.ReceiptScreenTourMethods');
    const{PaymentScreen}=require('point_of_sale.tour.PaymentScreenTourMethods');
    const{ClientListScreen}=require('point_of_sale.tour.ClientListScreenTourMethods');

    functionmakeFullOrder({orderlist,customer,payment,ntimes=1}){
        for(leti=0;i<ntimes;i++){
            ProductScreen.exec.addMultiOrderlines(...orderlist);
            if(customer){
                ProductScreen.do.clickCustomerButton();
                ClientListScreen.exec.setClient(customer);
            }
            ProductScreen.do.clickPayButton();
            PaymentScreen.exec.pay(...payment);
            ReceiptScreen.exec.nextOrder();
        }
    }

    return{makeFullOrder};
});
