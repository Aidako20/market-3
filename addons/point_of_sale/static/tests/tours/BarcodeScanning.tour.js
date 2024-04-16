flectra.define('point_of_sale.tour.BarcodeScanning',function(require){
    'usestrict';

    const{ProductScreen}=require('point_of_sale.tour.ProductScreenTourMethods');
    const{getSteps,startSteps}=require('point_of_sale.tour.utils');
    constTour=require('web_tour.tour');

    startSteps();


    //Addaproductwithitsbarcode
    ProductScreen.do.scan_barcode("0123456789");
    ProductScreen.check.selectedOrderlineHas('MonitorStand');
    ProductScreen.do.scan_barcode("0123456789");
    ProductScreen.check.selectedOrderlineHas('MonitorStand',2);

    //Test"Pricesproduct"EAN-13`23.....{NNNDD}`barcodepattern
    ProductScreen.do.scan_ean13_barcode("2305000000004");
    ProductScreen.check.selectedOrderlineHas('MagneticBoard',1,"0.00");
    ProductScreen.do.scan_ean13_barcode("2305000123454");
    ProductScreen.check.selectedOrderlineHas('MagneticBoard',1,"123.45");

    //Test"Weightedproduct"EAN-13`21.....{NNDDD}`barcodepattern
    ProductScreen.do.scan_ean13_barcode("2100005000000");
    ProductScreen.check.selectedOrderlineHas('WallShelfUnit',0,"0.00");
    ProductScreen.do.scan_ean13_barcode("2100005080000");
    ProductScreen.check.selectedOrderlineHas('WallShelfUnit',8);


    Tour.register('BarcodeScanningTour',{test:true,url:'/pos/ui'},getSteps());
});
