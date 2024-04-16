flectra.define('pos_restaurant.tour.OrderManagementScreen',function(require){
    'usestrict';

    //ThistourteststheintegrationofOrderManagementScreen
    //tosomepos_restaurantfeatures.

    const{makeFullOrder}=require('point_of_sale.tour.CompositeTourMethods');
    const{Chrome}=require('pos_restaurant.tour.ChromeTourMethods');
    const{
        OrderManagementScreen,
    }=require('point_of_sale.tour.OrderManagementScreenTourMethods');
    const{FloorScreen}=require('pos_restaurant.tour.FloorScreenTourMethods');
    const{ProductScreen}=require('pos_restaurant.tour.ProductScreenTourMethods');
    const{TicketScreen}=require('point_of_sale.tour.TicketScreenTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    varTour=require('web_tour.tour');

    //signaltostartgeneratingsteps
    //whenfinished,stepscanbetakenfromgetSteps
    startSteps();

    FloorScreen.do.clickTable('T2');

    //makeoneorderandcheckifitcanbeseenfromthemanagementscreen.
    makeFullOrder({orderlist:[['MinuteMaid','5','6']],payment:['Cash','30']});
    Chrome.do.clickOrderManagementButton();
    OrderManagementScreen.check.isShown();
    OrderManagementScreen.check.orderlistHas({orderName:'-0001',total:'30'});

    //gobacktocreatemultipleunpaidorders
    OrderManagementScreen.do.clickBack();

    //create2unpaidordersonT2(orders0002and0003)
    FloorScreen.do.clickTable('T2');
    ProductScreen.exec.addMultiOrderlines(
        ['Coca-Cola','1','2'],
        ['Water','3','4'],
        ['MinuteMaid','5','6']
    );
    Chrome.do.clickTicketButton();
    TicketScreen.do.clickNewTicket();
    ProductScreen.exec.addMultiOrderlines(['Coca-Cola','1','2'],['MinuteMaid','5','6']);
    Chrome.do.backToFloor();

    //create2unpaidordersonT5(orders0004and0005)
    FloorScreen.do.clickTable('T5');
    ProductScreen.exec.addMultiOrderlines(
        ['Coca-Cola','7','8'],
        ['Water','9','10'],
        ['MinuteMaid','11','12']
    );
    Chrome.do.clickTicketButton();
    TicketScreen.do.clickNewTicket();
    ProductScreen.exec.addMultiOrderlines(['Coca-Cola','13','14'],['MinuteMaid','15','16']);
    Chrome.do.backToFloor();

    //checkthattheunpaidordersarelistedinthemanagementscreen
    Chrome.do.clickOrderManagementButton();
    OrderManagementScreen.check.isShown();
    OrderManagementScreen.check.orderlistHas({orderName:'-0002',total:'44.0'});
    OrderManagementScreen.check.orderlistHas({orderName:'-0003',total:'32.0'});
    OrderManagementScreen.check.orderlistHas({orderName:'-0004',total:'278.0'});
    OrderManagementScreen.check.orderlistHas({orderName:'-0005',total:'422.0'});

    //selectorder0003andcheckifitisreallyinT2
    OrderManagementScreen.do.clickOrder('-0003');
    ProductScreen.check.isShown();
    ProductScreen.check.totalAmountIs('32');
    Chrome.check.backToFloorTextIs('MainFloor','T2');

    Chrome.do.clickOrderManagementButton();

    //selectorder0005andcheckititisreallyinT5
    OrderManagementScreen.check.isShown();
    OrderManagementScreen.do.clickOrder('-0005');
    ProductScreen.check.totalAmountIs('422');
    Chrome.check.backToFloorTextIs('MainFloor','T5');

    //gobacktofloorscreenandstartordermanagementfromthere
    Chrome.do.backToFloor();
    FloorScreen.check.selectedFloorIs('MainFloor');
    Chrome.do.clickOrderManagementButton();
    OrderManagementScreen.check.isShown();

    //selectorder0002andcheckifitisreallyinT2
    OrderManagementScreen.do.clickOrder('-0002');
    ProductScreen.check.isShown();
    ProductScreen.check.totalAmountIs('44');
    Chrome.check.backToFloorTextIs('MainFloor','T2');

    Chrome.do.clickOrderManagementButton();
    OrderManagementScreen.check.isShown();

    //selectorder0004andcheckifitisreallyinT5
    OrderManagementScreen.do.clickOrder('-0004');
    ProductScreen.check.isShown();
    ProductScreen.check.totalAmountIs('278');
    Chrome.check.backToFloorTextIs('MainFloor','T5');

    //transferorder0004toT2
    ProductScreen.do.clickTransferButton();
    FloorScreen.do.clickTable('T2');
    ProductScreen.check.isShown();

    Chrome.do.clickOrderManagementButton();
    OrderManagementScreen.check.isShown();

    //selectorder0004andcheckifitisnowinT2
    OrderManagementScreen.do.clickOrder('-0004',['table','T2']);
    ProductScreen.check.isShown();
    ProductScreen.check.totalAmountIs('278');
    Chrome.check.backToFloorTextIs('MainFloor','T2');

    Chrome.do.clickOrderManagementButton();
    OrderManagementScreen.check.isShown();

    //finally,selectorder0002
    OrderManagementScreen.do.clickOrder('-0002');
    ProductScreen.check.isShown();
    ProductScreen.check.totalAmountIs('44');
    Chrome.check.backToFloorTextIs('MainFloor','T2');

    Tour.register('PosResOrderManagementScreenTour',{test:true,url:'/pos/ui'},getSteps());
});
