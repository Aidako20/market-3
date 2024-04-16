flectra.define('pos_restaurant.tour.FloorScreen',function(require){
    'usestrict';

    const{Chrome}=require('pos_restaurant.tour.ChromeTourMethods');
    const{FloorScreen}=require('pos_restaurant.tour.FloorScreenTourMethods');
    const{TextInputPopup}=require('pos_restaurant.tour.TextInputPopupTourMethods');
    const{NumberPopup}=require('point_of_sale.tour.NumberPopupTourMethods');
    const{ProductScreen}=require('pos_restaurant.tour.ProductScreenTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    varTour=require('web_tour.tour');

    //signaltostartgeneratingsteps
    //whenfinished,stepscanbetakenfromgetSteps
    startSteps();

    //checkfloorsiftheycontaintheircorrespondingtables
    FloorScreen.check.selectedFloorIs('MainFloor');
    FloorScreen.check.hasTable('T2');
    FloorScreen.check.hasTable('T4');
    FloorScreen.check.hasTable('T5');
    FloorScreen.do.clickFloor('SecondFloor');
    FloorScreen.check.hasTable('T3');
    FloorScreen.check.hasTable('T1');

    //clickingtableinactivemodedoesnotopenproductscreen
    //instead,tableisselected
    FloorScreen.do.clickEdit();
    FloorScreen.check.editModeIsActive(true);
    FloorScreen.do.clickTable('T3');
    FloorScreen.check.selectedTableIs('T3');
    FloorScreen.do.clickTable('T1');
    FloorScreen.check.selectedTableIs('T1');

    //switchingfloorineditmodedeactivateseditmode
    FloorScreen.do.clickFloor('MainFloor');
    FloorScreen.check.editModeIsActive(false);
    FloorScreen.do.clickEdit();
    FloorScreen.check.editModeIsActive(true);

    //testaddtable
    FloorScreen.do.clickAddTable();
    FloorScreen.check.selectedTableIs('T1');
    FloorScreen.do.clickRename();
    TextInputPopup.check.isShown();
    TextInputPopup.do.inputText('T100');
    TextInputPopup.do.clickConfirm();
    FloorScreen.check.selectedTableIs('T100');

    //testduplicatetable
    FloorScreen.do.clickDuplicate();
    //newtableisalreadynamedT101
    FloorScreen.check.selectedTableIs('T101');
    FloorScreen.do.clickRename();
    TextInputPopup.check.isShown();
    TextInputPopup.do.inputText('T1111');
    TextInputPopup.do.clickConfirm();
    FloorScreen.check.selectedTableIs('T1111');

    //switchfloor,switchbackandcheckif
    //thenewtablesarestillthere
    FloorScreen.do.clickFloor('SecondFloor');
    FloorScreen.check.editModeIsActive(false);
    FloorScreen.check.hasTable('T3');
    FloorScreen.check.hasTable('T1');

    FloorScreen.do.clickFloor('MainFloor');
    FloorScreen.check.hasTable('T2');
    FloorScreen.check.hasTable('T4');
    FloorScreen.check.hasTable('T5');
    FloorScreen.check.hasTable('T100');
    FloorScreen.check.hasTable('T1111');

    //testdeletetable
    FloorScreen.do.clickEdit();
    FloorScreen.check.editModeIsActive(true);
    FloorScreen.do.clickTable('T2');
    FloorScreen.check.selectedTableIs('T2');
    FloorScreen.do.clickTrash();
    Chrome.do.confirmPopup();

    //changenumberofseats
    FloorScreen.do.clickTable('T4');
    FloorScreen.check.selectedTableIs('T4');
    FloorScreen.do.clickSeats();
    NumberPopup.do.pressNumpad('Backspace9');
    NumberPopup.check.inputShownIs('9');
    NumberPopup.do.clickConfirm();
    FloorScreen.check.tableSeatIs('T4','9');

    //changeshape
    FloorScreen.do.changeShapeTo('round');

    //Openingproductscreeninmainfloorshouldgobacktomainfloor
    FloorScreen.do.clickEdit();
    FloorScreen.check.editModeIsActive(false);
    FloorScreen.check.tableIsNotSelected('T4');
    FloorScreen.do.clickTable('T4');
    ProductScreen.check.isShown();
    Chrome.check.backToFloorTextIs('MainFloor','T4');
    Chrome.do.backToFloor();

    //Openingproductscreeninsecondfloorshouldgobacktosecondfloor
    FloorScreen.do.clickFloor('SecondFloor');
    FloorScreen.check.hasTable('T3');
    FloorScreen.do.clickTable('T3');
    Chrome.check.backToFloorTextIs('SecondFloor','T3');

    Tour.register('FloorScreenTour',{test:true,url:'/pos/ui'},getSteps());
});
