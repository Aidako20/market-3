flectra.define('pos_epson_printer.pos_epson_printer',function(require){
"usestrict";

varmodels=require('point_of_sale.models');
varEpsonPrinter=require('pos_epson_printer.Printer');

varposmodel_super=models.PosModel.prototype;
models.PosModel=models.PosModel.extend({
    after_load_server_data:function(){
        varself=this;
        returnposmodel_super.after_load_server_data.apply(this,arguments).then(function(){
            if(self.config.other_devices&&self.config.epson_printer_ip){
                self.proxy.printer=newEpsonPrinter(self.config.epson_printer_ip,self);
            }
        });
    },
});

});
