flectra.define('pos_restaurant.tour.SplitBillScreen',function(require){
    'usestrict';

    const{PaymentScreen}=require('point_of_sale.tour.PaymentScreenTourMethods');
    const{Chrome}=require('pos_restaurant.tour.ChromeTourMethods');
    const{FloorScreen}=require('pos_restaurant.tour.FloorScreenTourMethods');
    const{ProductScreen}=require('pos_restaurant.tour.ProductScreenTourMethods');
    const{SplitBillScreen}=require('pos_restaurant.tour.SplitBillScreenTourMethods');
    const{TicketScreen}=require('point_of_sale.tour.TicketScreenTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    varTour=require('web_tour.tour');

    //signaltostartgeneratingsteps
    //whenfinished,stepscanbetakenfromgetSteps
    startSteps();

    FloorScreen.do.clickTable('T2');
    ProductScreen.exec.addOrderline('Water','5','2','10.0');
    ProductScreen.exec.addOrderline('MinuteMaid','3','2','6.0');
    ProductScreen.exec.addOrderline('Coca-Cola','1','2','2.0');
    ProductScreen.do.clickSplitBillButton();

    //Checkifthescreencontainsalltheorderlines
    SplitBillScreen.check.orderlineHas('Water','5','0');
    SplitBillScreen.check.orderlineHas('MinuteMaid','3','0');
    SplitBillScreen.check.orderlineHas('Coca-Cola','1','0');

    //split3waterand1coca-cola
    SplitBillScreen.do.clickOrderline('Water');
    SplitBillScreen.check.orderlineHas('Water','5','1');
    SplitBillScreen.do.clickOrderline('Water');
    SplitBillScreen.do.clickOrderline('Water');
    SplitBillScreen.check.orderlineHas('Water','5','3');
    SplitBillScreen.check.subtotalIs('6.0')
    SplitBillScreen.do.clickOrderline('Coca-Cola');
    SplitBillScreen.check.orderlineHas('Coca-Cola','1','1');
    SplitBillScreen.check.subtotalIs('8.0')

    //clickpaytosplit,gobacktocheckthelines
    SplitBillScreen.do.clickPay();
    PaymentScreen.do.clickBack();
    ProductScreen.do.clickOrderline('Water','3.0')
    ProductScreen.do.clickOrderline('Coca-Cola','1.0')

    //gobacktotheoriginalorderandseeiftheorderischanged
    Chrome.do.clickTicketButton();
    TicketScreen.do.selectOrder('-0001');
    ProductScreen.do.clickOrderline('Water','2.0')
    ProductScreen.do.clickOrderline('MinuteMaid','3.0')

    Tour.register('SplitBillScreenTour',{test:true,url:'/pos/ui'},getSteps());

    startSteps();

    FloorScreen.do.clickTable('T2');
    ProductScreen.exec.addOrderline('Water','1','2.0');
    ProductScreen.exec.addOrderline('MinuteMaid','1','2.0');
    ProductScreen.exec.addOrderline('Coca-Cola','1','2.0');
    Chrome.do.backToFloor();
    FloorScreen.do.clickTable('T2');
    ProductScreen.do.clickSplitBillButton();

    SplitBillScreen.do.clickOrderline('Water');
    SplitBillScreen.do.clickOrderline('Coca-Cola');
    SplitBillScreen.do.clickPay();
    PaymentScreen.do.clickBack();
    Chrome.do.clickTicketButton();
    TicketScreen.do.selectOrder('-0002');
    ProductScreen.do.clickOrderline('Water','1.0');
    ProductScreen.do.clickOrderline('Coca-Cola','1.0');
    ProductScreen.check.totalAmountIs('4.40');
    Chrome.do.clickTicketButton();
    TicketScreen.do.selectOrder('-0001');
    ProductScreen.do.clickOrderline('MinuteMaid','1.0');
    ProductScreen.check.totalAmountIs('2.20');

    Tour.register('SplitBillScreenTour2',{test:true,url:'/pos/ui'},getSteps());
});
