flectra.define('point_of_sale.tour.SelectionPopupTourMethods',function(require){
    'usestrict';

    const{createTourMethods}=require('point_of_sale.tour.utils');

    classDo{
        clickItem(name){
            return[
                {
                    content:`clickselection'${name}'`,
                    trigger:`.selection-item:contains("${name}")`,
                },
            ];
        }
    }

    classCheck{
        hasSelectionItem(name){
            return[
                {
                    content:`selectionpopuphas'${name}'`,
                    trigger:`.selection-item:contains("${name}")`,
                    run:()=>{},
                },
            ];
        }
        isShown(){
            return[
                {
                    content:'selectionpopupisshown',
                    trigger:'.modal-dialog.popup-selection',
                    run:()=>{},
                },
            ];
        }
    }

    returncreateTourMethods('SelectionPopup',Do,Check);
});
