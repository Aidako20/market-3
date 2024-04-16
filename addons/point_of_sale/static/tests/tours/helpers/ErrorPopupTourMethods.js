flectra.define('point_of_sale.tour.ErrorPopupTourMethods',function(require){
    'usestrict';

    const{createTourMethods}=require('point_of_sale.tour.utils');

    classDo{
        clickConfirm(){
            return[
                {
                    content:'clickconfirmbutton',
                    trigger:'.popup-error.footer.cancel',
                },
            ];
        }
    }

    classCheck{
        isShown(){
            return[
                {
                    content:'errorpopupisshown',
                    trigger:'.modal-dialog.popup-error',
                    run:()=>{},
                },
            ];
        }
    }

    returncreateTourMethods('ErrorPopup',Do,Check);
});
