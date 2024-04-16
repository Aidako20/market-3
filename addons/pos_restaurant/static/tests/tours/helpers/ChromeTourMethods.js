flectra.define('pos_restaurant.tour.ChromeTourMethods',function(require){
    'usestrict';

    const{createTourMethods}=require('point_of_sale.tour.utils');
    const{Do}=require('point_of_sale.tour.ChromeTourMethods');

    classDoExtextendsDo{
        backToFloor(){
            return[
                {
                    content:'backtofloor',
                    trigger:'.floor-button',
                },
            ];
        }
    }

    classCheck{
        backToFloorTextIs(floor,table){
            return[
                {
                    content:`backtofloortextis'${floor}(${table})'`,
                    trigger:`.floor-buttonspan:contains("${floor}")~.table-name:contains("${table}")`,
                    run:()=>{},
                },
            ];
        }
    }

    classExecute{}

    returncreateTourMethods('Chrome',DoExt,Check,Execute);
});
