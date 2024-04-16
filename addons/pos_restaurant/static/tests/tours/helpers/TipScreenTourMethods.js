flectra.define('pos_restaurant.tour.TipScreenTourMethods',function(require){
    'usestrict';

    const{createTourMethods}=require('point_of_sale.tour.utils');

    classDo{
        clickPercentTip(percent){
            return[
                {
                    trigger:`.tip-screen.percentage:contains("${percent}")`,
                },
            ];
        }
        setCustomTip(amount){
            return[
                {
                    trigger:`.tip-screen.custom-amount-forminput`,
                    run:`text${amount}`,
                },
            ];
        }
    }

    classCheck{
        isShown(){
            return[
                {
                    trigger:'.pos.tip-screen',
                    run:()=>{},
                },
            ];
        }
        totalAmountIs(amount){
            return[
                {
                    trigger:`.tip-screen.total-amount:contains("${amount}")`,
                    run:()=>{},
                },
            ];
        }
        percentAmountIs(percent,amount){
            return[
                {
                    trigger:`.tip-screen.percentage:contains("${percent}")~.amount:contains("${amount}")`,
                    run:()=>{},
                },
            ];
        }
        inputAmountIs(amount){
            return[
                {
                    trigger:`.tip-screen.custom-amount-forminput[data-amount="${amount}"]`,
                    run:()=>{},
                }
            ]
        }
    }

    returncreateTourMethods('TipScreen',Do,Check);
});
