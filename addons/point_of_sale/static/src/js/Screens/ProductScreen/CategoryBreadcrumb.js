flectra.define('point_of_sale.CategoryBreadcrumb',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classCategoryBreadcrumbextendsPosComponent{}
    CategoryBreadcrumb.template='CategoryBreadcrumb';

    Registries.Component.add(CategoryBreadcrumb);

    returnCategoryBreadcrumb;
});
