flectra.define('pos_restaurant.SplitOrderline',function(require){
    'usestrict';

    const{useListener}=require('web.custom_hooks');
    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classSplitOrderlineextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('click',this.onClick);
        }
        getisSelected(){
            returnthis.props.split.quantity!==0;
        }
        onClick(){
            this.trigger('click-line',this.props.line);
        }
    }
    SplitOrderline.template='SplitOrderline';

    Registries.Component.add(SplitOrderline);

    returnSplitOrderline;
});
