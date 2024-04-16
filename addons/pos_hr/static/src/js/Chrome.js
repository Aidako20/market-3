flectra.define('pos_hr.chrome',function(require){
    'usestrict';

    constChrome=require('point_of_sale.Chrome');
    constRegistries=require('point_of_sale.Registries');

    constPosHrChrome=(Chrome)=>
        classextendsChrome{
            asyncstart(){
                awaitsuper.start();
                this.env.pos.on('change:cashier',this.render,this);
                if(this.env.pos.config.module_pos_hr)this.showTempScreen('LoginScreen');
            }
            getheaderButtonIsShown(){
                return!this.env.pos.config.module_pos_hr||this.env.pos.get('cashier').role=='manager';
            }
        };

    Registries.Component.extend(Chrome,PosHrChrome);

    returnChrome;
});
