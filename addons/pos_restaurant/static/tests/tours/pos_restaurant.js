flectra.define('pos_reataurant.tour.synchronized_table_management',function(require){
    'usestrict';

    const{PaymentScreen}=require('point_of_sale.tour.PaymentScreenTourMethods');
    const{ReceiptScreen}=require('point_of_sale.tour.ReceiptScreenTourMethods');
    const{Chrome}=require('pos_restaurant.tour.ChromeTourMethods');
    const{FloorScreen}=require('pos_restaurant.tour.FloorScreenTourMethods');
    const{ProductScreen}=require('pos_restaurant.tour.ProductScreenTourMethods');
    const{TicketScreen}=require('point_of_sale.tour.TicketScreenTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    constTour=require('web_tour.tour');

    startSteps();

    FloorScreen.do.clickTable('T5');

    //Createfirstorder
    ProductScreen.do.clickDisplayedProduct('Coca-Cola');
    ProductScreen.check.selectedOrderlineHas('Coca-Cola');
    ProductScreen.do.clickDisplayedProduct('Water');
    ProductScreen.check.selectedOrderlineHas('Water');
    ProductScreen.check.totalAmountIs('4.40');

    //Create2ndorder(paid)
    Chrome.do.clickTicketButton();
    TicketScreen.do.clickNewTicket();
    ProductScreen.do.clickDisplayedProduct('Coca-Cola');
    ProductScreen.check.selectedOrderlineHas('Coca-Cola');
    ProductScreen.do.clickDisplayedProduct('MinuteMaid');
    ProductScreen.check.selectedOrderlineHas('MinuteMaid');
    ProductScreen.check.totalAmountIs('4.40');
    ProductScreen.do.clickPayButton();
    PaymentScreen.do.clickPaymentMethod('Cash');
    PaymentScreen.do.clickValidate();
    ReceiptScreen.do.clickNextOrder();

    //Afterclickingnextorder,floorscreenisshown.
    //Itshouldhave1asnumberofdraftsyncedorder.
    FloorScreen.check.orderCountSyncedInTableIs('T5','1');
    FloorScreen.do.clickTable('T5');
    ProductScreen.check.totalAmountIs('4.40');

    //Createanotherdraftorderandgobacktofloor
    Chrome.do.clickTicketButton();
    TicketScreen.do.clickNewTicket();
    ProductScreen.do.clickDisplayedProduct('Coca-Cola');
    ProductScreen.check.selectedOrderlineHas('Coca-Cola');
    ProductScreen.do.clickDisplayedProduct('MinuteMaid');
    ProductScreen.check.selectedOrderlineHas('MinuteMaid');
    Chrome.do.backToFloor();

    //Atfloorscreen,thereshouldbe2synceddraftorders
    FloorScreen.check.orderCountSyncedInTableIs('T5','2');

    //Deletethefirstorderthengobacktofloor
    FloorScreen.do.clickTable('T5');
    ProductScreen.check.isShown();
    Chrome.do.clickTicketButton();
    TicketScreen.do.deleteOrder('-0001');
    Chrome.do.confirmPopup();
    TicketScreen.do.selectOrder('-0003');
    Chrome.do.backToFloor();

    //Thereshouldbe1synceddraftorder.
    FloorScreen.check.orderCountSyncedInTableIs('T5','1');

    Tour.register('pos_restaurant_sync',{test:true,url:'/pos/ui'},getSteps());

    startSteps();

    /*pos_restaurant_sync_second_login
     *
     *Thistourshouldberunafterthefirsttourisdone.
     */

    //Thereisonedraftsyncedorderfromtheprevioustour
    FloorScreen.check.orderCountSyncedInTableIs('T5','1');
    FloorScreen.do.clickTable('T5');
    ProductScreen.check.totalAmountIs('4.40');

    //Testtransferinganorder
    ProductScreen.do.clickTransferButton();
    FloorScreen.do.clickTable('T4');

    //Testifproductsstillgetmergedaftertransferingtheorder
    ProductScreen.do.clickDisplayedProduct('Coca-Cola');
    ProductScreen.check.selectedOrderlineHas('Coca-Cola','2.0');
    ProductScreen.check.totalAmountIs('6.60');
    ProductScreen.do.pressNumpad('1');
    ProductScreen.check.totalAmountIs('4.40');
    ProductScreen.do.clickPayButton();
    PaymentScreen.do.clickPaymentMethod('Cash');
    PaymentScreen.do.clickValidate();
    ReceiptScreen.do.clickNextOrder();
    //Atthispoint,therearenodraftorders.

    FloorScreen.do.clickTable('T2');
    ProductScreen.check.isShown();
    ProductScreen.check.orderIsEmpty();
    ProductScreen.do.clickTransferButton();
    FloorScreen.do.clickTable('T4');
    ProductScreen.do.clickDisplayedProduct('Coca-Cola');
    ProductScreen.check.totalAmountIs('2.20');
    Chrome.do.backToFloor();
    FloorScreen.check.orderCountSyncedInTableIs('T4','1');

    Tour.register('pos_restaurant_sync_second_login',{test:true,url:'/pos/ui'},getSteps());
});
