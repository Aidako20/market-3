flectra.define('point_of_sale.OfflineErrorPopup',function(require){
    'usestrict';

    constErrorPopup=require('point_of_sale.ErrorPopup');
    constRegistries=require('point_of_sale.Registries');

    /**
     *Thisisaspecialkindoferrorpopupasitintroduces
     *anoptiontonotshowitagain.
     */
    classOfflineErrorPopupextendsErrorPopup{
        dontShowAgain(){
            this.constructor.dontShow=true;
            this.cancel();
        }
    }
    OfflineErrorPopup.template='OfflineErrorPopup';
    OfflineErrorPopup.dontShow=false;
    OfflineErrorPopup.defaultProps={
        confirmText:'Ok',
        cancelText:'Cancel',
        title:'OfflineError',
        body:'Eithertheserverisinaccessibleorbrowserisnotconnectedonline.',
    };

    Registries.Component.add(OfflineErrorPopup);

    returnOfflineErrorPopup;
});
