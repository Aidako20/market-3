flectra.define('website_sale.s_dynamic_snippet_products',function(require){
'usestrict';

constconfig=require('web.config');
constcore=require('web.core');
constpublicWidget=require('web.public.widget');
constDynamicSnippetCarousel=require('website.s_dynamic_snippet_carousel');

constDynamicSnippetProducts=DynamicSnippetCarousel.extend({
    selector:'.s_dynamic_snippet_products',

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Methodtobeoverriddeninchildcomponentsifadditionalconfigurationelements
     *arerequiredinordertofetchdata.
     *@override
     *@private
     */
    _isConfigComplete:function(){
        returnthis._super.apply(this,arguments)&&this.$el.get(0).dataset.productCategoryId!==undefined;
    },
    /**
     *
     *@override
     *@private
     */
    _mustMessageWarningBeHidden:function(){
        constisInitialDrop=this.$el.get(0).dataset.templateKey===undefined;
        //Thissnippethasdefaultvaluesobtainedaftertheinitialstartandrenderafterdrop.
        //Becauseofthisthereisaninitialrefreshhappeningrightafter.
        //Wewanttoavoidshowingtheincompleteconfigmessagebeforethisrefresh.
        //SincetherefreshedcallwillalwayshappenwithadefinedtemplateKey,
        //ifitisnotsetyet,weknowitisthedropcallandwecanavoidshowingthemessage.
        returnisInitialDrop||this._super.apply(this,arguments);
    },
    /**
     *Methodtobeoverriddeninchildcomponentsinordertoprovideasearch
     *domainifneeded.
     *@override
     *@private
     */
    _getSearchDomain:function(){
        constsearchDomain=this._super.apply(this,arguments);
        constproductCategoryId=parseInt(this.$el.get(0).dataset.productCategoryId);
        if(productCategoryId>=0){
            searchDomain.push(['public_categ_ids','child_of',productCategoryId]);
        }
        returnsearchDomain;
    },

});
publicWidget.registry.dynamic_snippet_products=DynamicSnippetProducts;

returnDynamicSnippetProducts;
});
