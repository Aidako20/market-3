flectra.define('pos_restaurant.tour.TextInputPopupTourMethods',function(require){
    'usestrict';

    const{createTourMethods}=require('point_of_sale.tour.utils');

    classDo{
        inputText(val){
            return[
                {
                    content:`inputtext'${val}'`,
                    trigger:`.modal-dialog.popup-textinputinput`,
                    run:`text${val}`,
                },
            ];
        }
        clickConfirm(){
            return[
                {
                    content:'confirmtextinputpopup',
                    trigger:'.modal-dialog.confirm',
                },
            ];
        }
    }

    classCheck{
        isShown(){
            return[
                {
                    content:'textinputpopupisshown',
                    trigger:'.modal-dialog.popup-textinput',
                    run:()=>{},
                },
            ];
        }
    }

    returncreateTourMethods('TextInputPopup',Do,Check);
});
