flectra.define('sale_product_configurator.ProductConfiguratorFormRenderer',function(require){
"usestrict";

varFormRenderer=require('web.FormRenderer');
varVariantMixin=require('sale.VariantMixin');

varProductConfiguratorFormRenderer=FormRenderer.extend(VariantMixin,{

    events:_.extend({},FormRenderer.prototype.events,VariantMixin.events,{
        'clickbutton.js_add_cart_json':'onClickAddCartJSON',
    }),

    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        this.pricelistId=this.state.context.default_pricelist_id||0;
    },
    /**
     *@override
     */
    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            self.$el.append($('<div>',{class:'configurator_container'}));
            self.renderConfigurator(self.configuratorHtml);
            self._checkMode();
        });
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Renderstheproductconfiguratorwithintheform
     *
     *Willalso:
     *
     *-addeventshandlingforvariantchanges
     *-triggervariantchangetocomputethepriceandother
     *  variantspecificchanges
     *
     *@param{string}configuratorHtmltheevaluatedtemplateof
     *  theproductconfigurator
     */
    renderConfigurator:function(configuratorHtml){
        var$configuratorContainer=this.$('.configurator_container');
        $configuratorContainer.empty();

        var$configuratorHtml=$(configuratorHtml);
        $configuratorHtml.appendTo($configuratorContainer);

        this.triggerVariantChange($configuratorContainer);
        this._applyCustomValues();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *IftheconfiguratorModeinthegivencontextis'edit',weneedto
     *hidetheregular'Add'buttontoreplaceitwithan'EDIT'button.
     *
     *IftheconfiguratorModeissetto'options',wewilldirectlyopenthe
     *optionsmodal.
     *
     *@private
     */
    _checkMode:function(){
        if(this.state.context.configuratorMode==='edit'){
            this.$('.o_sale_product_configurator_add').hide();
            this.$('.o_sale_product_configurator_edit').css('display','inline-block');
        }elseif(this.state.context.configuratorMode==='options'){
            this.trigger_up('handle_add');
        }
    },

    /**
     *Togglestheaddbuttondependingonthepossibilityofthecurrent
     *combination.
     *
     *@override
     */
    _toggleDisable:function($parent,isCombinationPossible){
        VariantMixin._toggleDisable.apply(this,arguments);
        $parent.parents('.modal').find('.o_sale_product_configurator_add').toggleClass('disabled',!isCombinationPossible);
    },

    /**
     *Willfillthecustomvaluesinputbasedontheprovidedinitialconfiguration.
     *
     *@private
     */
    _applyCustomValues:function(){
        varself=this;
        varcustomValueIds=this.state.data.product_custom_attribute_value_ids;
        if(customValueIds){
            _.each(customValueIds.data,function(customValue){
                if(customValue.data.custom_value){
                    varattributeValueId=customValue.data.custom_product_template_attribute_value_id.data.id;
                    var$input=self._findRelatedAttributeValueInput(attributeValueId);
                    $input
                        .closest('li[data-attribute_id]')
                        .find('.variant_custom_value')
                        .val(customValue.data.custom_value);
                }
            });
        }
    },

    /**
     *Findthe$.Elementinput/selectrelatedtothatproduct.attribute.value
     *
     *@param{integer}attributeValueId
     *
     *@private
     */
    _findRelatedAttributeValueInput:function(attributeValueId){
        varselectors=[
            'ul.js_add_cart_variantsinput[data-value_id="'+attributeValueId+'"]',
            'ul.js_add_cart_variantsoption[data-value_id="'+attributeValueId+'"]'
        ];

        returnthis.$(selectors.join(','));
    }
});

returnProductConfiguratorFormRenderer;

});
