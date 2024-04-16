flectra.define('sale_product_configurator.ProductConfiguratorFormController',function(require){
"usestrict";

varcore=require('web.core');
var_t=core._t;
varFormController=require('web.FormController');
varOptionalProductsModal=require('sale_product_configurator.OptionalProductsModal');

varProductConfiguratorFormController=FormController.extend({
    custom_events:_.extend({},FormController.prototype.custom_events,{
        field_changed:'_onFieldChanged',
        handle_add:'_handleAdd'
    }),
    /**
     *@override
     */
    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            self.$el.addClass('o_product_configurator');
        });
    },
    /**
     *Weneedtofirstloadthetemplateoftheselectedproductandthenrenderthecontent
     *toavoidaflickerwhenthemodalisopened.
     *
     *@override
     */
    willStart:function(){
        vardef=this._super.apply(this,arguments);
        if(this.initialState.data.product_template_id){
            returnthis._configureProduct(
                this.initialState.data.product_template_id.data.id
            ).then(function(){
                returndef;
            });
        }

        returndef;
    },
    /**
     *ShowingthiswindowisuselessforconfiguratorMode'options'asthisformview
     *isusedasabridgebetweenSOlinesandoptionalproducts.
     *
     *Placedherebecauseit'stheonlymethodthatiscalledafterthemodalisrendered.
     *
     *@override
     */
    renderButtons:function(){
        this._super.apply(this,arguments);

        if(this.renderer.state.context.configuratorMode==='options'){
            this.$el.closest('.modal').addClass('d-none');
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------


    /**
    *Weneedtooverridethedefaultclickbehaviorforour"Add"button
    *becausethereisapossibilitythatthisproducthasoptionalproducts.
    *Ifso,weneedtodisplayanextramodaltochoosetheoptions.
    *
    *@override
    */
    _onButtonClicked:function(event){
        if(event.stopPropagation){
            event.stopPropagation();
        }
        varattrs=event.data.attrs;
        if(attrs.special==='cancel'){
            this._super.apply(this,arguments);
        }else{
            if(!this.$el
                    .parents('.modal')
                    .find('.o_sale_product_configurator_add')
                    .hasClass('disabled')){
                this._handleAdd();
            }
        }
    },
    /**
     *Thisisoverriddentoallowcatchingthe"select"eventonourproducttemplateselectfield.
     *
     *@override
     *@private
     */
    _onFieldChanged:function(event){
        this._super.apply(this,arguments);

        varself=this;
        varproductId=event.data.changes.product_template_id.id;

        //checktopreventtracebackwhenemptyingthefield
        if(!productId){
            return;
        }

        this._configureProduct(event.data.changes.product_template_id.id)
            .then(function(){
                self.renderer.renderConfigurator(self.renderer.configuratorHtml);
            });
    },

    /**
     *Rendersthe"variants"partofthewizard
     *
     *@param{integer}productTemplateId
     */
    _configureProduct:function(productTemplateId){
        varself=this;
        varinitialProduct=this.initialState.data.product_template_id;
        varchanged=initialProduct&&initialProduct.data.id!==productTemplateId;
        vardata=this.renderer.state.data;
        varquantity=initialProduct.context&&initialProduct.context.default_quantity?initialProduct.context.default_quantity:data.quantity;
        returnthis._rpc({
            route:'/sale_product_configurator/configure',
            params:{
                product_template_id:productTemplateId,
                pricelist_id:this.renderer.pricelistId,
                add_qty:quantity,
                product_template_attribute_value_ids:changed?[]:this._getAttributeValueIds(
                    data.product_template_attribute_value_ids
                ),
                product_no_variant_attribute_value_ids:changed?[]:this._getAttributeValueIds(
                    data.product_no_variant_attribute_value_ids
                )
            }
        }).then(function(configurator){
            self.renderer.configuratorHtml=configurator;
        });
    },
    /**
    *Whentheuseraddsaproductthathasoptionalproducts,weneedtodisplay
    *awindowtoallowtheusertochoosetheseextraoptions.
    *
    *Thiswillalsocreatetheproductifit'sin"dynamic"mode
    *(seeproduct_attribute.create_variant)
    *
    *If"self.renderer.state.context.configuratorMode"is'edit',thiswillonlysend
    *themainproductwithitschanges.
    *
    *Asopposedtothe'add'modethatwilladdthemainproductANDalltheconfiguredoptionalproducts.
    *
    *Athirdmode,'options',isavailableforproductsthatdon'thaveaconfigurationbuthave
    *optionalproductstoselect.Thiswillbypasstheconfigurationstepandopenthe
    *optionsmodaldirectly.
    *
    *@private
    */
    _handleAdd:function(){
        varself=this;
        var$modal=this.$el;
        varproductSelector=[
            'input[type="hidden"][name="product_id"]',
            'input[type="radio"][name="product_id"]:checked'
        ];

        varproductId=parseInt($modal.find(productSelector.join(',')).first().val(),10);
        varproductTemplateId=$modal.find('.product_template_id').val();
        this.renderer.selectOrCreateProduct(
            $modal,
            productId,
            productTemplateId,
            false
        ).then(function(productId){
            $modal.find(productSelector.join(',')).val(productId);

            varvariantValues=self
                .renderer
                .getSelectedVariantValues($modal.find('.js_product'));

            varproductCustomVariantValues=self
                .renderer
                .getCustomVariantValues($modal.find('.js_product'));

            varnoVariantAttributeValues=self
                .renderer
                .getNoVariantAttributeValues($modal.find('.js_product'));

            self.rootProduct={
                product_id:productId,
                product_template_id:parseInt(productTemplateId),
                quantity:parseFloat($modal.find('input[name="add_qty"]').val()||1),
                variant_values:variantValues,
                product_custom_attribute_values:productCustomVariantValues,
                no_variant_attribute_values:noVariantAttributeValues
            };

            if(self.renderer.state.context.configuratorMode==='edit'){
                //editmodeonlytakescareofmainproduct
                self._onAddRootProductOnly();
                return;
            }

            self.optionalProductsModal=newOptionalProductsModal($('body'),{
                rootProduct:self.rootProduct,
                pricelistId:self.renderer.pricelistId,
                okButtonText:_t('Confirm'),
                cancelButtonText:_t('Back'),
                title:_t('Configure'),
                context:self.initialState.context,
                previousModalHeight:self.$el.closest('.modal-content').height()
            }).open();

            self.optionalProductsModal.on('options_empty',null,
                //nooptionalproductsfoundforthisproduct,onlyaddtherootproduct
                self._onAddRootProductOnly.bind(self));

            self.optionalProductsModal.on('update_quantity',null,
                self._onOptionsUpdateQuantity.bind(self));

            self.optionalProductsModal.on('confirm',null,
                self._onModalConfirm.bind(self));

            self.optionalProductsModal.on('closed',null,
                self._onModalClose.bind(self));
        });
    },

    /**
     *Addrootproductonlyandforgetoptionalproducts.
     *Usedwhenproducthasnooptionalproductsandin'edit'mode.
     *
     *@private
     */
    _onAddRootProductOnly:function(){
        this._addProducts([this.rootProduct]);
    },

    /**
     *Addallselectedproducts
     *
     *@private
     */
    _onModalConfirm:function(){
        this._wasConfirmed=true;
        this._addProducts(this.optionalProductsModal.getSelectedProducts());
    },

    /**
     *Whentheoptionalproductsmodalisclosed(andnotconfirmed)on'options'mode,
     *thiswindowshouldalsobeclosedimmediately.
     *
     *@private
     */
    _onModalClose:function(){
        if(this.renderer.state.context.configuratorMode==='options'
            &&this._wasConfirmed!==true){
              this.do_action({type:'ir.actions.act_window_close'});
        }
    },

    /**
     *Updateproductconfiguratorform
     *whenquantityisupdatedintheoptionalproductswindow
     *
     *@private
     *@param{integer}quantity
     */
    _onOptionsUpdateQuantity:function(quantity){
        this.$el
            .find('input[name="add_qty"]')
            .val(quantity)
            .trigger('change');
    },

    /**
    *Thistriggersthecloseactionforthewindowand
    *addstheproductasthe"infos"parameter.
    *Itwillallowthecaller(typicallytheproduct_configuratorwidget)ofthiswindow
    *tohandletheaddedproducts.
    *
    *@private
    *@param{Array}productsthelistofaddedproducts
    *  {integer}products.product_id:theidoftheproduct
    *  {integer}products.quantity:theaddedquantityforthisproduct
    *  {Array}products.product_custom_attribute_values:
    *    seevariant_mixin.getCustomVariantValues
    *  {Array}products.no_variant_attribute_values:
    *    seevariant_mixin.getNoVariantAttributeValues
    */
    _addProducts:function(products){
        this.do_action({type:'ir.actions.act_window_close',infos:{
            mainProduct:products[0],
            options:products.slice(1)
        }});
    },
    /**
     *ExtractstheidsfromthepassedattributeValueIdsandreturnsthem
     *asaplainarray.
     *
     *@param{Array}attributeValueIds
     */
    _getAttributeValueIds:function(attributeValueIds){
        if(!attributeValueIds||attributeValueIds.length===0){
            returnfalse;
        }

        varresult=[];
        _.each(attributeValueIds.data,function(attributeValue){
            result.push(attributeValue.data.id);
        });

        returnresult;
    }
});

returnProductConfiguratorFormController;

});
