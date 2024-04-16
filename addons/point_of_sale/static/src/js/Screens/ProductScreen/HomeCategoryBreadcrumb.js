flectra.define('point_of_sale.HomeCategoryBreadcrumb',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');
    const{useListener}=require('web.custom_hooks');

    classHomeCategoryBreadcrumbextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('categ-popup',this._categPopup);
        }
        getselectedCategoryId(){
            returnthis.env.pos.get('selectedCategoryId');
        }
        async_categPopup(){
            letselectionList=[{
                id:0,
                label:'AllItems',
                isSelected:0===this.env.pos.get('selectedCategoryId'),
                item:{id:0,name:'AllItems'},
            }];
            letsubs=this.props.subcategories.map(category=>({
                id:category.id,
                label:category.name,
                isSelected:category.id===this.env.pos.get('selectedCategoryId'),
                item:category,
            }));
            selectionList=selectionList.concat(subs);
            const{confirmed,payload:selectedCategory}=awaitthis.showPopup(
                'SelectionPopup',
                {
                    title:this.env._t('Selectthecategory'),
                    list:selectionList,
                }
            );
            if(confirmed){
                this.trigger('switch-category',selectedCategory.id);
            }
        }
    }
    HomeCategoryBreadcrumb.template='HomeCategoryBreadcrumb';

    Registries.Component.add(HomeCategoryBreadcrumb);

    returnHomeCategoryBreadcrumb;
});
