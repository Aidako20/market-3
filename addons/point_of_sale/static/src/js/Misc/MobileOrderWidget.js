flectra.define('point_of_sale.MobileOrderWidget',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classMobileOrderWidgetextendsPosComponent{
        constructor(){
            super(...arguments);
            this.pane=this.props.pane;
            this.update();
        }
        getorder(){
            returnthis.env.pos.get_order();
        }
        mounted(){
          this.order.on('change',()=>{
              this.update();
              this.render();
          });
          this.order.orderlines.on('change',()=>{
              this.update();
              this.render();
          });
        }
        update(){
            consttotal=this.order?this.order.get_total_with_tax():0;
            consttax=this.order?total-this.order.get_total_without_tax():0;
            this.total=this.env.pos.format_currency(total);
            this.items_number=this.order?this.order.orderlines.reduce((items_number,line)=>items_number+line.quantity,0):0;
        }
    }

    MobileOrderWidget.template='MobileOrderWidget';

    Registries.Component.add(MobileOrderWidget);

    returnMobileOrderWidget;
});
