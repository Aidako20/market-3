flectra.define('point_of_sale.tour.ReceiptScreen',function(require){
    'usestrict';

    const{ProductScreen}=require('point_of_sale.tour.ProductScreenTourMethods');
    const{ReceiptScreen}=require('point_of_sale.tour.ReceiptScreenTourMethods');
    const{PaymentScreen}=require('point_of_sale.tour.PaymentScreenTourMethods');
    const{NumberPopup}=require('point_of_sale.tour.NumberPopupTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    constTour=require('web_tour.tour');

    startSteps();

    //pressclosebuttoninreceiptscreen
    ProductScreen.exec.addOrderline('LetterTray','10','5');
    ProductScreen.check.selectedOrderlineHas('LetterTray','10');
    ProductScreen.do.clickPayButton();
    PaymentScreen.do.clickPaymentMethod('Bank');
    PaymentScreen.check.validateButtonIsHighlighted(true);
    PaymentScreen.do.clickValidate();
    ReceiptScreen.check.receiptIsThere();
    //lettertrayhas10%tax(searchSRC)
    ReceiptScreen.check.totalAmountContains('55.0');
    ReceiptScreen.do.clickNextOrder();

    //sendemailinreceiptscreen
    ProductScreen.do.clickHomeCategory();
    ProductScreen.exec.addOrderline('DeskPad','6','5','30.0');
    ProductScreen.exec.addOrderline('WhiteboardPen','6','6','36.0');
    ProductScreen.exec.addOrderline('MonitorStand','6','1','6.0');
    ProductScreen.do.clickPayButton();
    PaymentScreen.do.clickPaymentMethod('Cash');
    PaymentScreen.do.pressNumpad('70');
    PaymentScreen.check.remainingIs('2.0');
    PaymentScreen.do.pressNumpad('0');
    PaymentScreen.check.remainingIs('0.00');
    PaymentScreen.check.changeIs('628.0');
    PaymentScreen.do.clickValidate();
    ReceiptScreen.check.receiptIsThere();
    ReceiptScreen.check.totalAmountContains('72.0');
    ReceiptScreen.do.setEmail('test@receiptscreen.com');
    ReceiptScreen.do.clickSend();
    ReceiptScreen.check.emailIsSuccessful();
    ReceiptScreen.do.clickNextOrder();

    //orderwithtip
    //checkiftipamountisdisplayed
    ProductScreen.exec.addOrderline('DeskPad','6','5');
    ProductScreen.do.clickPayButton();
    PaymentScreen.do.clickTipButton();
    NumberPopup.do.pressNumpad('1');
    NumberPopup.check.inputShownIs('1');
    NumberPopup.do.clickConfirm();
    PaymentScreen.check.emptyPaymentlines('31.0');
    PaymentScreen.do.clickPaymentMethod('Cash');
    PaymentScreen.do.clickValidate();
    ReceiptScreen.check.receiptIsThere();
    ReceiptScreen.check.totalAmountContains('$30.00+$1.00tip');
    ReceiptScreen.do.clickNextOrder();

    Tour.register('ReceiptScreenTour',{test:true,url:'/pos/ui'},getSteps());

    startSteps();

    ProductScreen.do.clickHomeCategory();
    ProductScreen.exec.addOrderline('TestProduct','1');
    ProductScreen.do.clickPricelistButton();
    ProductScreen.do.selectPriceList('special_pricelist');
    ProductScreen.check.discountOriginalPriceIs('7.0');
    ProductScreen.do.clickPayButton();
    PaymentScreen.do.clickPaymentMethod('Cash');
    PaymentScreen.do.clickValidate();
    ReceiptScreen.check.discountAmountIs('0.7');

    Tour.register('ReceiptScreenDiscountWithPricelistTour',{test:true,url:'/pos/ui'},getSteps());
});
