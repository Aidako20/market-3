flectra.define('point_of_sale.tour.OrderManagementScreen',function(require){
    'usestrict';

    const{OrderManagementScreen}=require('point_of_sale.tour.OrderManagementScreenTourMethods');
    const{ProductScreen}=require('point_of_sale.tour.ProductScreenTourMethods');
    const{PaymentScreen}=require('point_of_sale.tour.PaymentScreenTourMethods');
    const{ClientListScreen}=require('point_of_sale.tour.ClientListScreenTourMethods');
    const{TicketScreen}=require('point_of_sale.tour.TicketScreenTourMethods');
    const{Chrome}=require('point_of_sale.tour.ChromeTourMethods');
    const{makeFullOrder}=require('point_of_sale.tour.CompositeTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    varTour=require('web_tour.tour');

    //signaltostartgeneratingsteps
    //whenfinished,stepscanbetakenfromgetSteps
    startSteps();

    //Gobydefaulttohomecategory
    ProductScreen.do.clickHomeCategory();

    //makeoneorderandcheckifitcanbeseenfromthemanagementscreen.
    //order0001
    makeFullOrder({orderlist:[['WhiteboardPen','5','6']],payment:['Cash','30']});
    Chrome.do.clickOrderManagementButton();
    OrderManagementScreen.check.isShown();
    OrderManagementScreen.check.orderlistHas({orderName:'-0001',total:'30'});

    OrderManagementScreen.do.clickBack();

    //makemultipleordersandchecktheminthemanagementscreen.
    //order0002
    makeFullOrder({
        orderlist:[
            ['DeskPad','1','2'],
            ['MonitorStand','3','4'],
            ['WhiteboardPen','5','6'],
        ],
        payment:['Bank','44'],
    });
    //order0003
    makeFullOrder({
        orderlist:[
            ['DeskPad','1','2'],
            ['WhiteboardPen','5','6'],
        ],
        customer:'ColleenDiaz',
        payment:['Cash','50'],
    });
    //order0004
    makeFullOrder({
        orderlist:[
            ['MonitorStand','3','4'],
            ['WhiteboardPen','5','6'],
        ],
        payment:['Bank','42'],
    });

    Chrome.do.clickOrderManagementButton();
    OrderManagementScreen.check.isShown();
    OrderManagementScreen.check.orderlistHas({orderName:'-0002',total:'44'});
    OrderManagementScreen.check.orderlistHas({
        orderName:'0003',
        total:'32',
        customer:'ColleenDiaz',
    });
    OrderManagementScreen.check.orderlistHas({orderName:'-0004',total:'42'});

    //clickthecurrentlyactiveorder
    OrderManagementScreen.do.clickOrder('-0005');
    ProductScreen.check.isShown();

    //Add2orders,theyshouldappearinordermanagementscreen
    //order0006
    Chrome.do.clickTicketButton();
    TicketScreen.do.clickNewTicket();
    ProductScreen.exec.addOrderline('WhiteboardPen','66','6');

    //order0007,shouldbeatpaymentscreen
    Chrome.do.clickTicketButton();
    TicketScreen.do.clickNewTicket();
    ProductScreen.exec.addOrderline('MonitorStand','55','5');
    ProductScreen.do.clickCustomerButton();
    ClientListScreen.exec.setClient('AzureInterior');
    ProductScreen.do.clickPayButton();

    Chrome.do.clickOrderManagementButton();
    OrderManagementScreen.check.orderlistHas({orderName:'-0006',total:'396'});
    OrderManagementScreen.check.orderlistHas({
        orderName:'-0007',
        total:'275',
        customer:'AzureInterior',
    });

    //selectapaidorder,orderrowshouldbehighlightedandshouldshoworderdetails
    OrderManagementScreen.do.clickOrder('-0004');
    OrderManagementScreen.check.highlightedOrderRowHas('-0004');
    OrderManagementScreen.check.orderDetailsHas({
        lines:[
            {product:'MonitorStand',quantity:'3'},
            {product:'WhiteboardPen',quantity:'5'},
        ],
        total:'42',
    });
    OrderManagementScreen.do.clickOrder('-0001');
    OrderManagementScreen.check.highlightedOrderRowHas('-0001');
    //0004shouldnotbehighlightedanymore
    OrderManagementScreen.check.orderRowIsNotHighlighted('-0004');
    OrderManagementScreen.check.orderDetailsHas({
        lines:[{product:'WhiteboardPen',quantity:'5'}],
        total:'30',
    });

    //Selectapaidordertheninvoiceit.Theselectedordershouldremainselected
    //andwillcontainanewcustomer.Afterinvoice,thecurrentcustomershouldberemoved.
    //TODO:enablethefollowingstepsoncetheissueininvoicingissolved.
    //OrderManagementScreen.do.clickInvoiceButton();
    //Chrome.do.confirmPopup();
    //ClientListScreen.check.isShown();
    //ClientListScreen.exec.setClient('JesseBrown');
    //OrderManagementScreen.check.highlightedOrderRowHas('JesseBrown');

    //Checkiforder0007isselected,itshouldbeatpaymentscreen
    OrderManagementScreen.do.clickOrder('-0007');
    PaymentScreen.check.isShown();

    Chrome.do.clickOrderManagementButton();
    OrderManagementScreen.check.isShown();
    OrderManagementScreen.do.clickOrder('-0003');
    OrderManagementScreen.do.clickPrintReceiptButton();
    OrderManagementScreen.check.reprintReceiptIsShown();
    OrderManagementScreen.check.receiptChangeIs('18.0');
    OrderManagementScreen.check.receiptOrderDataContains('-0003');
    OrderManagementScreen.check.receiptAmountIs('32.0');
    OrderManagementScreen.do.closeReceipt();
    OrderManagementScreen.check.isNotHidden();

    Tour.register('OrderManagementScreenTour',{test:true,url:'/pos/ui'},getSteps());
});
