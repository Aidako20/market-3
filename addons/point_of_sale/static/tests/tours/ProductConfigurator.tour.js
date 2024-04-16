flectra.define('point_of_sale.tour.ProductConfigurator',function(require){
    'usestrict';

    const{ProductScreen}=require('point_of_sale.tour.ProductScreenTourMethods');
    const{ProductConfigurator}=require('point_of_sale.tour.ProductConfiguratorTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    varTour=require('web_tour.tour');

    //signaltostartgeneratingsteps
    //whenfinished,stepscanbetakenfromgetSteps
    startSteps();

    //Gobydefaulttohomecategory
    ProductScreen.do.clickHomeCategory();

    //ClickonConfigurableChairproduct
    ProductScreen.do.clickDisplayedProduct('ConfigurableChair');
    ProductConfigurator.check.isShown();

    //Cancelconfiguration,notproductshouldbeinorder
    ProductConfigurator.do.cancelAttributes();
    ProductScreen.check.orderIsEmpty();

    //ClickonConfigurableChairproduct
    ProductScreen.do.clickDisplayedProduct('ConfigurableChair');
    ProductConfigurator.check.isShown();

    //PickColor
    ProductConfigurator.do.pickColor('Red');

    //PickRadio
    ProductConfigurator.do.pickSelect('Metal');

    //PickSelect
    ProductConfigurator.do.pickRadio('Other');

    //Fillincustomattribute
    ProductConfigurator.do.fillCustomAttribute('CustomFabric');

    //Confirmconfiguration
    ProductConfigurator.do.confirmAttributes();

    //Checkthattheproducthasbeenaddedtotheorderwithcorrectattributesandprice
    ProductScreen.check.selectedOrderlineHas('ConfigurableChair(Red,Metal,Other:CustomFabric)','1.0','11.0');

    //Orderlineswiththesameattributesshouldbemerged
    ProductScreen.do.clickHomeCategory();
    ProductScreen.do.clickDisplayedProduct('ConfigurableChair');
    ProductConfigurator.do.pickColor('Red');
    ProductConfigurator.do.pickSelect('Metal');
    ProductConfigurator.do.pickRadio('Other');
    ProductConfigurator.do.fillCustomAttribute('CustomFabric');
    ProductConfigurator.do.confirmAttributes();
    ProductScreen.check.selectedOrderlineHas('ConfigurableChair(Red,Metal,Other:CustomFabric)','2.0','22.0');

    //Orderlineswithdifferentattributesshouldn'tbemerged
    ProductScreen.do.clickHomeCategory();
    ProductScreen.do.clickDisplayedProduct('ConfigurableChair');
    ProductConfigurator.do.pickColor('Blue');
    ProductConfigurator.do.pickSelect('Metal');
    ProductConfigurator.do.pickRadio('Leather');
    ProductConfigurator.do.confirmAttributes();
    ProductScreen.check.selectedOrderlineHas('ConfigurableChair(Blue,Metal,Leather)','1.0','10.0');

    Tour.register('ProductConfiguratorTour',{test:true,url:'/pos/ui'},getSteps());
});
