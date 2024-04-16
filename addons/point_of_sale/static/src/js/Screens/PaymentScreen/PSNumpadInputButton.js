flectra.define('point_of_sale.PSNumpadInputButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classPSNumpadInputButtonextendsPosComponent{
        get_class(){
            returnthis.props.changeClassTo||'input-buttonnumber-char';
        }
    }
    PSNumpadInputButton.template='PSNumpadInputButton';

    Registries.Component.add(PSNumpadInputButton);

    returnPSNumpadInputButton;
});
