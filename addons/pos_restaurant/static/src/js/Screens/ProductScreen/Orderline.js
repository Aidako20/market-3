flectra.define('pos_restaurant.Orderline',function(require){
    'usestrict';

    constOrderline=require('point_of_sale.Orderline');
    constRegistries=require('point_of_sale.Registries');

    constPosResOrderline=Orderline=>
        classextendsOrderline{
            /**
             *@override
             */
            getaddedClasses(){
                constres=super.addedClasses;
                Object.assign(res,{
                    dirty:this.props.line.mp_dirty,
                    skip:this.props.line.mp_skip,
                });
                returnres;
            }
            /**
             *@override
             *ifdoubleclick,changemp_dirtytomp_skip
             *
             *IMPROVEMENT:Insteadofhandlingbothdoubleclickandclickinsingle
             *method,perhapswecanseparatedoubleclickfromsingleclick.
             */
            selectLine(){
                constline=this.props.line;//theorderline
                if(this.env.pos.get_order().selected_orderline!==line){
                    this.mp_dbclk_time=newDate().getTime();
                }elseif(!this.mp_dbclk_time){
                    this.mp_dbclk_time=newDate().getTime();
                }elseif(this.mp_dbclk_time+500>newDate().getTime()){
                    line.set_skip(!line.mp_skip);
                    this.mp_dbclk_time=0;
                }else{
                    this.mp_dbclk_time=newDate().getTime();
                }
                super.selectLine();
            }
        };

    Registries.Component.extend(Orderline,PosResOrderline);

    returnOrderline;
});
