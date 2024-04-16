flectra.define('website.s_dynamic_snippet_carousel',function(require){
'usestrict';

constconfig=require('web.config');
constcore=require('web.core');
constpublicWidget=require('web.public.widget');
constDynamicSnippet=require('website.s_dynamic_snippet');

constDynamicSnippetCarousel=DynamicSnippet.extend({
    selector:'.s_dynamic_snippet_carousel',
    xmlDependencies:(DynamicSnippet.prototype.xmlDependencies||[]).concat(
        ['/website/static/src/snippets/s_dynamic_snippet_carousel/000.xml']
    ),

    /**
     *
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        this.template_key='website.s_dynamic_snippet.carousel';
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _getQWebRenderOptions:function(){
        returnObject.assign(
            this._super.apply(this,arguments),
            {
                interval:parseInt(this.$target[0].dataset.carouselInterval),
            },
        );
    },
    /**
     *@deprecated
     *@todoremovemeinmaster,thiswaswronglynamedandwassupposedto
     *override_getQWebRenderOptions.Thisiskeptforpotentialcustoin
     *stable,althoughnotethatwithouthacks,callingthis._superherejust
     *crashes.
     */
    _getQWebRenderParams:function(){
        returnObject.assign(
            this._super.apply(this,arguments),
            {
                interval:parseInt(this.$target[0].dataset.carouselInterval),
            },
        );
    },
});
publicWidget.registry.dynamic_snippet_carousel=DynamicSnippetCarousel;

returnDynamicSnippetCarousel;
});
