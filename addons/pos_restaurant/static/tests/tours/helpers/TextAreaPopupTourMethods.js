flectra.define('pos_restaurant.tour.TextAreaPopupTourMethods',function(require){
    'usestrict';

    const{createTourMethods}=require('point_of_sale.tour.utils');

    classDo{
        inputText(val){
            return[
                {
                    content:`inputtext'${val}'`,
                    trigger:`.modal-dialog.popup-textareatextarea`,
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
                    trigger:'.modal-dialog.popup-textarea',
                    run:()=>{},
                },
            ];
        }
    }

    returncreateTourMethods('TextAreaPopup',Do,Check);
});
