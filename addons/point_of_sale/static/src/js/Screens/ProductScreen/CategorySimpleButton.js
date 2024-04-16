flectra.define('point_of_sale.CategorySimpleButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classCategorySimpleButtonextendsPosComponent{}
    CategorySimpleButton.template='CategorySimpleButton';

    Registries.Component.add(CategorySimpleButton);

    returnCategorySimpleButton;
});
