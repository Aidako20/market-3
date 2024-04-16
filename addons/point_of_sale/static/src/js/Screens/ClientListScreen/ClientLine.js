flectra.define('point_of_sale.ClientLine',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classClientLineextendsPosComponent{
        gethighlight(){
            returnthis.props.partner!==this.props.selectedClient?'':'highlight';
        }
    }
    ClientLine.template='ClientLine';

    Registries.Component.add(ClientLine);

    returnClientLine;
});
