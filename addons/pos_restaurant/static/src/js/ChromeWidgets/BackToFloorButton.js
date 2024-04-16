flectra.define('pos_restaurant.BackToFloorButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');
    const{posbus}=require('point_of_sale.utils');

    classBackToFloorButtonextendsPosComponent{
        mounted(){
            posbus.on('table-set',this,this.render);
        }
        willUnmount(){
            posbus.on('table-set',this);
        }
        gettable(){
            return(this.env.pos&&this.env.pos.table)||null;
        }
        getfloor(){
            consttable=this.table;
            returntable?table.floor:null;
        }
        gethasTable(){
            returnthis.table!==null;
        }
        backToFloorScreen(){
            this.showScreen('FloorScreen',{floor:this.floor});
        }
    }
    BackToFloorButton.template='BackToFloorButton';

    Registries.Component.add(BackToFloorButton);

    returnBackToFloorButton;
});
