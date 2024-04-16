flectra.define('point_of_sale.tour.PaymentScreen',function(require){
    'usestrict';

    const{ProductScreen}=require('point_of_sale.tour.ProductScreenTourMethods');
    const{PaymentScreen}=require('point_of_sale.tour.PaymentScreenTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    varTour=require('web_tour.tour');

    startSteps();

    ProductScreen.exec.addOrderline('LetterTray','10');
    ProductScreen.check.selectedOrderlineHas('LetterTray','10.0');
    ProductScreen.do.clickPayButton();
    PaymentScreen.check.emptyPaymentlines('52.8');

    PaymentScreen.do.clickPaymentMethod('Cash');
    PaymentScreen.do.pressNumpad('11');
    PaymentScreen.check.selectedPaymentlineHas('Cash','11.00');
    PaymentScreen.check.remainingIs('41.8');
    PaymentScreen.check.changeIs('0.0');
    PaymentScreen.check.validateButtonIsHighlighted(false);
    //removetheselectedpaymentlinewithmultiplebackspacepresses
    PaymentScreen.do.pressNumpad('BackspaceBackspace');
    PaymentScreen.check.selectedPaymentlineHas('Cash','0.00');
    PaymentScreen.do.pressNumpad('Backspace');
    PaymentScreen.check.emptyPaymentlines('52.8');

    //Paywithbank,theselectedlineshouldhavefullamount
    PaymentScreen.do.clickPaymentMethod('Bank');
    PaymentScreen.check.remainingIs('0.0');
    PaymentScreen.check.changeIs('0.0');
    PaymentScreen.check.validateButtonIsHighlighted(true);
    //removethelineusingthedeletebutton
    PaymentScreen.do.clickPaymentlineDelButton('Bank','52.8');

    //Use+10and+50toincrementtheamountofthepaymentline
    PaymentScreen.do.clickPaymentMethod('Cash');
    PaymentScreen.do.pressNumpad('+10');
    PaymentScreen.check.remainingIs('42.8');
    PaymentScreen.check.changeIs('0.0');
    PaymentScreen.check.validateButtonIsHighlighted(false);
    PaymentScreen.do.pressNumpad('+50');
    PaymentScreen.check.remainingIs('0.0');
    PaymentScreen.check.changeIs('7.2');
    PaymentScreen.check.validateButtonIsHighlighted(true);
    PaymentScreen.do.clickPaymentlineDelButton('Cash','60.0');

    //Multiplepaymentlines
    PaymentScreen.do.clickPaymentMethod('Cash');
    PaymentScreen.do.pressNumpad('1');
    PaymentScreen.check.remainingIs('51.8');
    PaymentScreen.check.changeIs('0.0');
    PaymentScreen.check.validateButtonIsHighlighted(false);
    PaymentScreen.do.clickPaymentMethod('Cash');
    PaymentScreen.do.pressNumpad('5');
    PaymentScreen.check.remainingIs('46.8');
    PaymentScreen.check.changeIs('0.0');
    PaymentScreen.check.validateButtonIsHighlighted(false);
    PaymentScreen.do.clickPaymentMethod('Bank');
    PaymentScreen.do.pressNumpad('20');
    PaymentScreen.check.remainingIs('26.8');
    PaymentScreen.check.changeIs('0.0');
    PaymentScreen.check.validateButtonIsHighlighted(false);
    PaymentScreen.do.clickPaymentMethod('Bank');
    PaymentScreen.check.remainingIs('0.0');
    PaymentScreen.check.changeIs('0.0');
    PaymentScreen.check.validateButtonIsHighlighted(true);

    Tour.register('PaymentScreenTour',{test:true,url:'/pos/ui'},getSteps());
});
