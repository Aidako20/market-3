flectra.define('point_of_sale.Orderline',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classOrderlineextendsPosComponent{
        selectLine(){
            this.trigger('select-line',{orderline:this.props.line});
        }
        lotIconClicked(){
            this.trigger('edit-pack-lot-lines',{orderline:this.props.line});
        }
        getaddedClasses(){
            return{
                selected:this.props.line.selected,
            };
        }
    }
    Orderline.template='Orderline';

    Registries.Component.add(Orderline);

    returnOrderline;
});
