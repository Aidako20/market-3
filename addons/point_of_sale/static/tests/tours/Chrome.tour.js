flectra.define('point_of_sale.tour.Chrome',function(require){
    'usestrict';

    const{ProductScreen}=require('point_of_sale.tour.ProductScreenTourMethods');
    const{ReceiptScreen}=require('point_of_sale.tour.ReceiptScreenTourMethods');
    const{PaymentScreen}=require('point_of_sale.tour.PaymentScreenTourMethods');
    const{TicketScreen}=require('point_of_sale.tour.TicketScreenTourMethods');
    const{Chrome}=require('point_of_sale.tour.ChromeTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    varTour=require('web_tour.tour');

    startSteps();

    //Order1isatProductScreen
    ProductScreen.do.clickHomeCategory();
    ProductScreen.exec.addOrderline('DeskPad','1','2','2.0');
    Chrome.do.clickTicketButton();
    TicketScreen.check.checkStatus('-0001','Ongoing');

    //Order2isatPaymentScreen
    TicketScreen.do.clickNewTicket();
    ProductScreen.exec.addOrderline('MonitorStand','3','4','12.0');
    ProductScreen.do.clickPayButton();
    PaymentScreen.check.isShown();
    Chrome.do.clickTicketButton();
    TicketScreen.check.checkStatus('-0002','Payment');

    //Order3isatReceiptScreen
    TicketScreen.do.clickNewTicket();
    ProductScreen.exec.addOrderline('WhiteboardPen','5','6','30.0');
    ProductScreen.do.clickPayButton();
    PaymentScreen.do.clickPaymentMethod('Bank');
    PaymentScreen.check.remainingIs('0.0');
    PaymentScreen.check.validateButtonIsHighlighted(true);
    PaymentScreen.do.clickValidate();
    ReceiptScreen.check.isShown();
    Chrome.do.clickTicketButton();
    TicketScreen.check.checkStatus('-0003','Receipt');

    //Selectorder1,shouldbeatProductScreen
    TicketScreen.do.selectOrder('-0001');
    ProductScreen.check.productIsDisplayed('DeskPad');
    ProductScreen.check.selectedOrderlineHas('DeskPad','1.0','2.0');

    //Selectorder2,shouldbeatPaymentScreen
    Chrome.do.clickTicketButton();
    TicketScreen.do.selectOrder('-0002');
    PaymentScreen.check.emptyPaymentlines('12.0');
    PaymentScreen.check.validateButtonIsHighlighted(false);

    //Selectorder3,shouldbeatReceiptScreen
    Chrome.do.clickTicketButton();
    TicketScreen.do.selectOrder('-0003');
    ReceiptScreen.check.totalAmountContains('30.0');

    //Payorder1,withchange
    Chrome.do.clickTicketButton();
    TicketScreen.do.selectOrder('-0001');
    ProductScreen.do.clickPayButton();
    PaymentScreen.do.clickPaymentMethod('Cash');
    PaymentScreen.do.pressNumpad('20');
    PaymentScreen.check.remainingIs('0.0');
    PaymentScreen.check.validateButtonIsHighlighted(true);
    PaymentScreen.do.clickValidate();
    ReceiptScreen.check.totalAmountContains('2.0');

    //Order1nowshouldhaveReceiptstatus
    Chrome.do.clickTicketButton();
    TicketScreen.check.checkStatus('-0001','Receipt');

    //Selectorder3,shouldstillbeatReceiptScreen
    //andthetotalamountdoesn'tchange.
    TicketScreen.do.selectOrder('-0003');
    ReceiptScreen.check.totalAmountContains('30.0');

    //clicknextscreenonorder3
    //thendeletethenewemptyorder
    ReceiptScreen.do.clickNextOrder();
    ProductScreen.check.orderIsEmpty();
    Chrome.do.clickTicketButton();
    TicketScreen.do.deleteOrder('-0004');
    TicketScreen.do.deleteOrder('-0001');

    //Afterdeletingorder1above,order2became
    //the2nd-roworderandithaspaymentstatus
    TicketScreen.check.nthRowContains(2,'Payment')
    TicketScreen.do.deleteOrder('-0002');
    Chrome.do.confirmPopup();
    TicketScreen.do.clickNewTicket();

    //Invoiceanorder
    ProductScreen.exec.addOrderline('WhiteboardPen','5','6');
    ProductScreen.do.clickCustomerButton();
    ProductScreen.do.clickCustomer('NicoleFord');
    ProductScreen.do.clickSetCustomer();
    ProductScreen.do.clickPayButton();
    PaymentScreen.do.clickPaymentMethod('Bank');
    PaymentScreen.do.clickInvoiceButton();
    PaymentScreen.do.clickValidate();
    ReceiptScreen.check.isShown();

    Tour.register('ChromeTour',{test:true,url:'/pos/ui'},getSteps());
});
