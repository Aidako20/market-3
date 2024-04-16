flectra.define('point_of_sale.EditListInput',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classEditListInputextendsPosComponent{
        onKeyup(event){
            if(event.key==="Enter"&&event.target.value.trim()!==''){
                this.trigger('create-new-item');
            }
        }
    }
    EditListInput.template='EditListInput';

    Registries.Component.add(EditListInput);

    returnEditListInput;
});
