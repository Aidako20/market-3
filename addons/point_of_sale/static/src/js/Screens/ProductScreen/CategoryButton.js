flectra.define('point_of_sale.CategoryButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classCategoryButtonextendsPosComponent{
        getimageUrl(){
            constcategory=this.props.category
            return`/web/image?model=pos.category&field=image_128&id=${category.id}&write_date=${category.write_date}&unique=1`;
        }
    }
    CategoryButton.template='CategoryButton';

    Registries.Component.add(CategoryButton);

    returnCategoryButton;
});
