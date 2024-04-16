flectra.define('pos_epson_printer_restaurant.multiprint',function(require){
"usestrict";

varmodels=require('point_of_sale.models');
varEpsonPrinter=require('pos_epson_printer.Printer');

//Theoverrideofcreate_printerneedstohappenafteritsdeclarationin
//pos_restaurant.Weneedtomakesurethatthiscodeisexecutedafterthe
//multiprintfileinpos_restaurant.
require('pos_restaurant.multiprint');

models.load_fields("restaurant.printer",["epson_printer_ip"]);

var_super_posmodel=models.PosModel.prototype;

models.PosModel=models.PosModel.extend({
    create_printer:function(config){
        if(config.printer_type==="epson_epos"){
            returnnewEpsonPrinter(config.epson_printer_ip,posmodel);
        }else{
            return_super_posmodel.create_printer.apply(this,arguments);
        }
    },
});
});
