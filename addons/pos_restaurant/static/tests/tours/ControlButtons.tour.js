flectra.define('pos_restaurant.tour.ControlButtons',function(require){
    'usestrict';

    const{TextAreaPopup}=require('pos_restaurant.tour.TextAreaPopupTourMethods');
    const{Chrome}=require('pos_restaurant.tour.ChromeTourMethods');
    const{FloorScreen}=require('pos_restaurant.tour.FloorScreenTourMethods');
    const{ProductScreen}=require('pos_restaurant.tour.ProductScreenTourMethods');
    const{SplitBillScreen}=require('pos_restaurant.tour.SplitBillScreenTourMethods');
    const{BillScreen}=require('pos_restaurant.tour.BillScreenTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    varTour=require('web_tour.tour');

    //signaltostartgeneratingsteps
    //whenfinished,stepscanbetakenfromgetSteps
    startSteps();

    //TestTransferOrderButton
    FloorScreen.do.clickTable('T2');
    ProductScreen.exec.addOrderline('Water','5','2','10.0');
    ProductScreen.do.clickTransferButton();
    FloorScreen.do.clickTable('T4');
    ProductScreen.do.clickOrderline('Water','5','2');
    Chrome.do.backToFloor();
    FloorScreen.do.clickTable('T2');
    ProductScreen.check.orderIsEmpty();
    Chrome.do.backToFloor();
    FloorScreen.do.clickTable('T4');
    ProductScreen.do.clickOrderline('Water','5','2');

    //TestSplitBillButton
    ProductScreen.do.clickSplitBillButton();
    SplitBillScreen.do.clickBack();

    //TestOrderlineNoteButton
    ProductScreen.do.clickNoteButton();
    TextAreaPopup.check.isShown();
    TextAreaPopup.do.inputText('testnote');
    TextAreaPopup.do.clickConfirm();
    ProductScreen.check.orderlineHasNote('Water','5','testnote');
    ProductScreen.exec.addOrderline('Water','8','1','8.0');

    //TestPrintBillButton
    ProductScreen.do.clickPrintBillButton();
    BillScreen.check.isShown();
    BillScreen.do.clickBack();

    Tour.register('ControlButtonsTour',{test:true,url:'/pos/ui'},getSteps());
});
