flectra.define('pos_restaurant.tour.BillScreenTourMethods',function(require){
    'usestrict';

    const{createTourMethods}=require('point_of_sale.tour.utils');

    classDo{
        clickBack(){
            return[
                {
                    content:`goback`,
                    trigger:`.receipt-screen.back`,
                },
            ];
        }
    }

    classCheck{
        isShown(){
            return[
                {
                    content:'Billscreenisshown',
                    trigger:'.receipt-screenh1:contains("BillPrinting")',
                    run:()=>{},
                },
            ];
        }
    }

    returncreateTourMethods('BillScreen',Do,Check);
});
