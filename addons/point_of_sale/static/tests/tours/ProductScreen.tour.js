flectra.define('point_of_sale.tour.ProductScreen',function(require){
    'usestrict';

    const{ProductScreen}=require('point_of_sale.tour.ProductScreenTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    varTour=require('web_tour.tour');

    //signaltostartgeneratingsteps
    //whenfinished,stepscanbetakenfromgetSteps
    startSteps();

    //Gobydefaulttohomecategory
    ProductScreen.do.clickHomeCategory();

    //Clickingproductmultipletimesshouldincrementquantity
    ProductScreen.do.clickDisplayedProduct('DeskOrganizer');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','1.0','5.10');
    ProductScreen.do.clickDisplayedProduct('DeskOrganizer');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','2.0','10.20');

    //Clickingproductshouldaddneworderlineandselecttheorderline
    //Iforderlineexists,incrementthequantity
    ProductScreen.do.clickDisplayedProduct('LetterTray');
    ProductScreen.check.selectedOrderlineHas('LetterTray','1.0','4.80');
    ProductScreen.do.clickDisplayedProduct('DeskOrganizer');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','3.0','15.30');

    //Checkeffectsofclickingnumpadbuttons
    ProductScreen.do.clickOrderline('LetterTray','1');
    ProductScreen.check.selectedOrderlineHas('LetterTray','1.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('LetterTray','0.0','0.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','3','15.30');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','0.0','0.0');
    ProductScreen.do.pressNumpad('1');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','1.0','5.1');
    ProductScreen.do.pressNumpad('2');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','12.0','61.2');
    ProductScreen.do.pressNumpad('3');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','123.0','627.3');
    ProductScreen.do.pressNumpad('.5');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','123.5','629.85');
    ProductScreen.do.pressNumpad('Price');
    ProductScreen.do.pressNumpad('1');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','123.5','123.5');
    ProductScreen.do.pressNumpad('1.');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','123.5','1,358.5');
    ProductScreen.do.pressNumpad('Disc');
    ProductScreen.do.pressNumpad('5.');
    ProductScreen.check.selectedOrderlineHas('DeskOrganizer','123.5','1,290.58');
    ProductScreen.do.pressNumpad('Qty');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.orderIsEmpty();

    //Checkdifferentsubcategories
    ProductScreen.do.clickSubcategory('Desks');
    ProductScreen.check.productIsDisplayed('DeskPad');
    ProductScreen.do.clickHomeCategory();
    ProductScreen.do.clickSubcategory('Miscellaneous');
    ProductScreen.check.productIsDisplayed('WhiteboardPen');
    ProductScreen.do.clickHomeCategory();
    ProductScreen.do.clickSubcategory('Chairs');
    ProductScreen.check.productIsDisplayed('LetterTray');
    ProductScreen.do.clickHomeCategory();

    //Addmultipleorderlinesthendeleteeachofthemuntilempty
    ProductScreen.do.clickDisplayedProduct('WhiteboardPen');
    ProductScreen.do.clickDisplayedProduct('WallShelfUnit');
    ProductScreen.do.clickDisplayedProduct('SmallShelf');
    ProductScreen.do.clickDisplayedProduct('MagneticBoard');
    ProductScreen.do.clickDisplayedProduct('MonitorStand');
    ProductScreen.do.clickOrderline('WhiteboardPen','1.0');
    ProductScreen.check.selectedOrderlineHas('WhiteboardPen','1.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('WhiteboardPen','0.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('MonitorStand','1.0');
    ProductScreen.do.clickOrderline('WallShelfUnit','1.0');
    ProductScreen.check.selectedOrderlineHas('WallShelfUnit','1.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('WallShelfUnit','0.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('MonitorStand','1.0');
    ProductScreen.do.clickOrderline('SmallShelf','1.0');
    ProductScreen.check.selectedOrderlineHas('SmallShelf','1.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('SmallShelf','0.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('MonitorStand','1.0');
    ProductScreen.do.clickOrderline('MagneticBoard','1.0');
    ProductScreen.check.selectedOrderlineHas('MagneticBoard','1.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('MagneticBoard','0.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('MonitorStand','1.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.selectedOrderlineHas('MonitorStand','0.0');
    ProductScreen.do.pressNumpad('Backspace');
    ProductScreen.check.orderIsEmpty();

    Tour.register('ProductScreenTour',{test:true,url:'/pos/ui'},getSteps());

    startSteps();

    ProductScreen.do.clickHomeCategory();
    ProductScreen.do.clickDisplayedProduct('TestProduct');
    ProductScreen.check.totalAmountIs('100.00');
    ProductScreen.do.changeFiscalPosition('NoTax');
    ProductScreen.check.noDiscountApplied("100.00");
    ProductScreen.check.totalAmountIs('86.96');

    Tour.register('FiscalPositionNoTax',{test:true,url:'/pos/ui'},getSteps());
});

flectra.define('point_of_sale.tour.FixedPriceNegativeQty',function(require){
    'usestrict';

    const{ProductScreen}=require('point_of_sale.tour.ProductScreenTourMethods');
    const{PaymentScreen}=require('point_of_sale.tour.PaymentScreenTourMethods');
    const{ReceiptScreen}=require('point_of_sale.tour.ReceiptScreenTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    varTour=require('web_tour.tour');

    startSteps();

    ProductScreen.do.clickHomeCategory();

    ProductScreen.do.clickDisplayedProduct('ZeroAmountProduct');
    ProductScreen.check.selectedOrderlineHas('ZeroAmountProduct','1.0','1.0');
    ProductScreen.do.pressNumpad('+/-1');
    ProductScreen.check.selectedOrderlineHas('ZeroAmountProduct','-1.0','-1.0');

    ProductScreen.do.clickPayButton();
    PaymentScreen.do.clickPaymentMethod('Bank');
    PaymentScreen.check.remainingIs('0.00');
    PaymentScreen.do.clickValidate();

    ReceiptScreen.check.receiptIsThere();

    Tour.register('FixedTaxNegativeQty',{test:true,url:'/pos/ui'},getSteps());
});
