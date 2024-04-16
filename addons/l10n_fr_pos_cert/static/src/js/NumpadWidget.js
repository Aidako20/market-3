flectra.define('l10n_fr_pos_cert.NumpadWidget',function(require){
    'usestrict';

    constNumpadWidget=require('point_of_sale.NumpadWidget');
    constRegistries=require('point_of_sale.Registries');

    constPosFrNumpadWidget=NumpadWidget=>classextendsNumpadWidget{
        gethasPriceControlRights(){
            if(this.env.pos.is_french_country()){
                returnfalse;
            }else{
                returnsuper.hasPriceControlRights;
            }
        }
    };

    Registries.Component.extend(NumpadWidget,PosFrNumpadWidget);

    returnNumpadWidget;
 });
