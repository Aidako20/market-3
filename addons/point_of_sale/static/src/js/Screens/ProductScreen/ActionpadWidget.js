flectra.define('point_of_sale.ActionpadWidget',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    /**
     *@propsclient
     *@emitsclick-customer
     *@emitsclick-pay
     */
    classActionpadWidgetextendsPosComponent{
        getisLongName(){
            returnthis.client&&this.client.name.length>10;
        }
        getclient(){
            returnthis.props.client;
        }
    }
    ActionpadWidget.template='ActionpadWidget';

    Registries.Component.add(ActionpadWidget);

    returnActionpadWidget;
});
