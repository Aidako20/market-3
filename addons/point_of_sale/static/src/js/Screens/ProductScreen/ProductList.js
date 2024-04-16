flectra.define('point_of_sale.ProductList',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classProductListextendsPosComponent{}
    ProductList.template='ProductList';

    Registries.Component.add(ProductList);

    returnProductList;
});
