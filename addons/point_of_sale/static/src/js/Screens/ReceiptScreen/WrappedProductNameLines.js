flectra.define('point_of_sale.WrappedProductNameLines',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classWrappedProductNameLinesextendsPosComponent{
        constructor(){
            super(...arguments);
            this.line=this.props.line;
        }
    }
    WrappedProductNameLines.template='WrappedProductNameLines';

    Registries.Component.add(WrappedProductNameLines);

    returnWrappedProductNameLines;
});
