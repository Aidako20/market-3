flectra.define('pos_restaurant.EditBar',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');
    const{useState}=owl.hooks;

    classEditBarextendsPosComponent{
        constructor(){
            super(...arguments);
            this.state=useState({isColorPicker:false})
        }
    }
    EditBar.template='EditBar';

    Registries.Component.add(EditBar);

    returnEditBar;
});
