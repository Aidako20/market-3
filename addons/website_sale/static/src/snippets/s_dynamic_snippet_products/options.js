flectra.define('website_sale.s_dynamic_snippet_products_options',function(require){
'usestrict';

constoptions=require('web_editor.snippets.options');
consts_dynamic_snippet_carousel_options=require('website.s_dynamic_snippet_carousel_options');

constdynamicSnippetProductsOptions=s_dynamic_snippet_carousel_options.extend({

    /**
     *
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        this.productCategories={};
    },
    /**
     *
     *@override
     */
    onBuilt:function(){
        this._super.apply(this,arguments);
        //TODORemoveinmaster.
        this.$target[0].dataset['snippet']='s_dynamic_snippet_products';
        this._rpc({
            route:'/website_sale/snippet/options_filters'
        }).then((data)=>{
            if(data.length){
                this.$target.get(0).dataset.filterId=data[0].id;
                this.$target.get(0).dataset.numberOfRecords=this.dynamicFilters[data[0].id].limit;
                this._refreshPublicWidgets();
                //Refreshisneededbecausedefaultvaluesareobtainedafterstart()
            }
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *
     *@override
     *@private
     */
    _computeWidgetVisibility:function(widgetName,params){
        if(widgetName==='filter_opt'){
            returnfalse;
        }
        returnthis._super.apply(this,arguments);
    },
    /**
     *Fetchesproductcategories.
     *@private
     *@returns{Promise}
     */
    _fetchProductCategories:function(){
        returnthis._rpc({
            model:'product.public.category',
            method:'search_read',
            kwargs:{
                domain:[],
                fields:['id','name'],
            }
        });
    },
    /**
     *
     *@override
     *@private
     */
    _renderCustomXML:asyncfunction(uiFragment){
        awaitthis._super.apply(this,arguments);
        awaitthis._renderProductCategorySelector(uiFragment);
    },
    /**
     *RenderstheproductcategoriesoptionselectorcontentintotheprovideduiFragment.
     *@private
     *@param{HTMLElement}uiFragment
     */
    _renderProductCategorySelector:asyncfunction(uiFragment){
        constproductCategories=awaitthis._fetchProductCategories();
        for(letindexinproductCategories){
            this.productCategories[productCategories[index].id]=productCategories[index];
        }
        constproductCategoriesSelectorEl=uiFragment.querySelector('[data-name="product_category_opt"]');
        returnthis._renderSelectUserValueWidgetButtons(productCategoriesSelectorEl,this.productCategories);
    },
    /**
     *Setsdefaultoptionsvalues.
     *@override
     *@private
     */
    _setOptionsDefaultValues:function(){
        this._super.apply(this,arguments);
        consttemplateKeys=this.$el.find("we-select[data-attribute-name='templateKey']we-selection-itemswe-button");
        if(templateKeys.length>0){
            this._setOptionValue('templateKey',templateKeys.attr('data-select-data-attribute'));
        }
        constproductCategories=this.$el.find("we-select[data-attribute-name='productCategoryId']we-selection-itemswe-button");
        if(productCategories.length>0){
            this._setOptionValue('productCategoryId',productCategories.attr('data-select-data-attribute'));
        }
    },

});

options.registry.dynamic_snippet_products=dynamicSnippetProductsOptions;

returndynamicSnippetProductsOptions;
});
