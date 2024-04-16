flectra.define('sale_product_configurator.OptionalProductsModal',function(require){
    "usestrict";

varajax=require('web.ajax');
varDialog=require('web.Dialog');
constOwlDialog=require('web.OwlDialog');
varServicesMixin=require('web.ServicesMixin');
varVariantMixin=require('sale.VariantMixin');

varOptionalProductsModal=Dialog.extend(ServicesMixin,VariantMixin,{
    events: _.extend({},Dialog.prototype.events,VariantMixin.events,{
        'clicka.js_add,a.js_remove':'_onAddOrRemoveOption',
        'clickbutton.js_add_cart_json':'onClickAddCartJSON',
        'change.in_cartinput.js_quantity':'_onChangeQuantity',
        'change.js_raw_price':'_computePriceTotal'
    }),
    /**
     *Initializestheoptionalproductsmodal
     *
     *@override
     *@param{$.Element}parentTheparentcontainer
     *@param{Object}params
     *@param{integer}params.pricelistId
     *@param{string}params.okButtonTextThetexttoapplyonthe"ok"button,typically
     *  "Add"forthesaleorderand"Proceedtocheckout"onthewebshop
     *@param{string}params.cancelButtonTextsameas"params.okButtonText"but
     *  forthecancelbutton
     *@param{integer}params.previousModalHeightusedtoconfigureaminheightonthemodal-content.
     *  Thisparameterisprovidedbytheproductconfiguratorto"cover"itsmodalbymaking
     *  thisonebigenough.Thiswaytheusercan'tseemultiplebuttons(whichcanbeconfusing).
     *@param{Object}params.rootProductTherootproductoftheoptionalproductswindow
     *@param{integer}params.rootProduct.product_id
     *@param{integer}params.rootProduct.quantity
     *@param{Array}params.rootProduct.variant_values
     *@param{Array}params.rootProduct.product_custom_attribute_values
     *@param{Array}params.rootProduct.no_variant_attribute_values
     */
    init:function(parent,params){
        varself=this;

        varoptions=_.extend({
            size:'large',
            buttons:[{
                text:params.okButtonText,
                click:this._onConfirmButtonClick,
                classes:'btn-primary'
            },{
                text:params.cancelButtonText,
                click:this._onCancelButtonClick
            }],
            technical:!params.isWebsite,
        },params||{});

        this._super(parent,options);

        this.context=params.context;
        this.rootProduct=params.rootProduct;
        this.container=parent;
        this.pricelistId=params.pricelistId;
        this.previousModalHeight=params.previousModalHeight;
        this.dialogClass='oe_optional_products_modal';
        this._productImageField='image_128';

        this._opened.then(function(){
            if(self.previousModalHeight){
                self.$el.closest('.modal-content').css('min-height',self.previousModalHeight+'px');
            }
        });
    },
     /**
     *@override
     */
    willStart:function(){
        varself=this;

        varuri=this._getUri("/sale_product_configurator/show_optional_products");
        vargetModalContent=ajax.jsonRpc(uri,'call',{
            product_id:self.rootProduct.product_id,
            variant_values:self.rootProduct.variant_values,
            pricelist_id:self.pricelistId||false,
            add_qty:self.rootProduct.quantity,
            kwargs:{
                context:_.extend({
                    'quantity':self.rootProduct.quantity
                },this.context),
            }
        })
        .then(function(modalContent){
            if(modalContent){
                var$modalContent=$(modalContent);
                $modalContent=self._postProcessContent($modalContent);
                self.$content=$modalContent;
            }else{
                self.trigger('options_empty');
                self.preventOpening=true;
            }
        });

        varparentInit=self._super.apply(self,arguments);
        returnPromise.all([getModalContent,parentInit]);
    },

    /**
     *Thisisoverriddentoappendthemodaltotheprovidedcontainer(seeinit("parent")).
     *Weneedthistohavethemodalcontainedinthewebshopproductform.
     *Theadditionalproductsdatawillthenbecontainedintheformandsentonsubmit.
     *
     *@override
     */
    open:function(options){
        $('.tooltip').remove();//removeopentooltipifanytopreventthemstayingwhenmodalisopened

        varself=this;
        this.appendTo($('<div/>')).then(function(){
            if(!self.preventOpening){
                self.$modal.find(".modal-body").replaceWith(self.$el);
                self.$modal.attr('open',true);
                self.$modal.modal().appendTo(self.container);
                self.$modal.focus();
                self._openedResolver();

                //NotifiesOwlDialogtoadjustfocus/activepropertiesonowldialogs
                OwlDialog.display(self);
            }
        });
        if(options&&options.shouldFocusButtons){
            self._onFocusControlButton();
        }

        returnself;
    },
    /**
     *Willupdatequantityinputtosynchronizewithpreviouswindow
     *
     *@override
     */
    start:function(){
        vardef=this._super.apply(this,arguments);
        varself=this;

        this.$el.find('input[name="add_qty"]').val(this.rootProduct.quantity);

        //setauniqueidtoeachrowforoptionshierarchy
        var$products=this.$el.find('tr.js_product');
        _.each($products,function(el){
            var$el=$(el);
            varuniqueId=self._getUniqueId(el);

            varproductId=parseInt($el.find('input.product_id').val(),10);
            if(productId===self.rootProduct.product_id){
                self.rootProduct.unique_id=uniqueId;
            }else{
                el.dataset.parentUniqueId=self.rootProduct.unique_id;
            }
        });

        returndef.then(function(){
            //Thishastobetriggeredtocomputethe"outofstock"feature
            self._opened.then(function(){
                self.triggerVariantChange(self.$el);
            });
        });
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Returnsthelistofselectedproducts.
     *Therootproductisaddedontopofthelist.
     *
     *@returns{Array}products
     *  {integer}product_id
     *  {integer}quantity
     *  {Array}product_custom_variant_values
     *  {Array}no_variant_attribute_values
     *@public
     */
    getSelectedProducts:function(){
        varself=this;
        varproducts=[this.rootProduct];
        this.$modal.find('.js_product.in_cart:not(.main_product)').each(function(){
            var$item=$(this);
            varquantity=parseFloat($item.find('input[name="add_qty"]').val().replace(',','.')||1);
            varparentUniqueId=this.dataset.parentUniqueId;
            varuniqueId=this.dataset.uniqueId;
            varproductCustomVariantValues=self.getCustomVariantValues($(this));
            varnoVariantAttributeValues=self.getNoVariantAttributeValues($(this));
            products.push({
                'product_id':parseInt($item.find('input.product_id').val(),10),
                'product_template_id':parseInt($item.find('input.product_template_id').val(),10),
                'quantity':quantity,
                'parent_unique_id':parentUniqueId,
                'unique_id':uniqueId,
                'product_custom_attribute_values':productCustomVariantValues,
                'no_variant_attribute_values':noVariantAttributeValues
            });
        });

        returnproducts;
    },

    //------------------------------------------
    //Private
    //------------------------------------------

    /**
     *Addstheproductimageandupdatestheproductdescription
     *basedonattributevaluesthatareeither"novariant"or"custom".
     *
     *@private
     */
    _postProcessContent:function($modalContent){
        varproductId=this.rootProduct.product_id;
        $modalContent
            .find('img:first')
            .attr("src","/web/image/product.product/"+productId+"/image_128");

        if(this.rootProduct&&
                (this.rootProduct.product_custom_attribute_values||
                 this.rootProduct.no_variant_attribute_values)){
            var$productDescription=$modalContent
                .find('.main_product')
                .find('td.td-product_namediv.text-muted.small>div:first');
            var$updatedDescription=$('<div/>');
            $updatedDescription.append($('<p>',{
                text:$productDescription.text()
            }));

            $.each(this.rootProduct.product_custom_attribute_values,function(){
                $updatedDescription.append($('<div>',{
                    text:this.attribute_value_name+':'+this.custom_value
                }));
            });

            $.each(this.rootProduct.no_variant_attribute_values,function(){
                if(this.is_custom!=='True'){
                    $updatedDescription.append($('<div>',{
                        text:this.attribute_name+':'+this.attribute_value_name
                    }));
                }
            });

            $productDescription.replaceWith($updatedDescription);
        }

        return$modalContent;
    },

    /**
     *@private
     */
    _onConfirmButtonClick:function(){
        this.trigger('confirm');
        this.close();
    },

    /**
     *@private
     */
    _onCancelButtonClick:function(){
        this.trigger('back');
        this.close();
    },

    /**
     *Willadd/removetheoption,thatincludes:
     *-MovingittothecorrectDOMsection
     *  andpossiblyunderitsparentproduct
     *-Hidingattributevaluesselectionandshowingthequantity
     *-Creatingtheproductifit'sin"dynamic"mode(seeproduct_attribute.create_variant)
     *-Updatingthedescriptionbasedoncustom/no_createattributevalues
     *-Removingoptionalproductsifparentproductisremoved
     *-Computingthetotalprice
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onAddOrRemoveOption:function(ev){
        ev.preventDefault();
        varself=this;
        var$target=$(ev.currentTarget);
        var$modal=$target.parents('.oe_optional_products_modal');
        var$parent=$target.parents('.js_product:first');
        $parent.find("a.js_add,span.js_remove").toggleClass('d-none');
        $parent.find(".js_remove");

        varproductTemplateId=$parent.find(".product_template_id").val();
        if($target.hasClass('js_add')){
            self._onAddOption($modal,$parent,productTemplateId);
        }else{
            self._onRemoveOption($modal,$parent);
        }

        self._computePriceTotal();
    },

    /**
     *@private
     *@see_onAddOrRemoveOption
     *@param{$.Element}$modal
     *@param{$.Element}$parent
     *@param{integer}productTemplateId
     */
    _onAddOption:function($modal,$parent,productTemplateId){
        varself=this;
        var$selectOptionsText=$modal.find('.o_select_options');

        varparentUniqueId=$parent[0].dataset.parentUniqueId;
        var$optionParent=$modal.find('tr.js_product[data-unique-id="'+parentUniqueId+'"]');

        //removeattributevaluesselectionandupdate+showquantityinput
        $parent.find('.td-product_name').removeAttr("colspan");
        $parent.find('.td-qty').removeClass('d-none');

        varproductCustomVariantValues=self.getCustomVariantValues($parent);
        varnoVariantAttributeValues=self.getNoVariantAttributeValues($parent);
        if(productCustomVariantValues||noVariantAttributeValues){
            var$productDescription=$parent
                .find('td.td-product_namediv.float-left');

            var$customAttributeValuesDescription=$('<div>',{
                class:'custom_attribute_values_descriptiontext-mutedsmall'
            });
            if(productCustomVariantValues.length!==0||noVariantAttributeValues.length!==0){
                $customAttributeValuesDescription.append($('<br/>'));
            }

            $.each(productCustomVariantValues,function(){
                $customAttributeValuesDescription.append($('<div>',{
                    text:this.attribute_value_name+':'+this.custom_value
                }));
            });

            $.each(noVariantAttributeValues,function(){
                if(this.is_custom!=='True'){
                    $customAttributeValuesDescription.append($('<div>',{
                        text:this.attribute_name+':'+this.attribute_value_name
                    }));
                }
            });

            $productDescription.append($customAttributeValuesDescription);
        }

        //placeitafteritsparentanditsparentoptions
        var$tmpOptionParent=$optionParent;
        while($tmpOptionParent.length){
            $optionParent=$tmpOptionParent;
            $tmpOptionParent=$modal.find('tr.js_product.in_cart[data-parent-unique-id="'+$optionParent[0].dataset.uniqueId+'"]').last();
        }
        $optionParent.after($parent);
        $parent.addClass('in_cart');

        this.selectOrCreateProduct(
            $parent,
            $parent.find('.product_id').val(),
            productTemplateId,
            true
        ).then(function(productId){
            $parent.find('.product_id').val(productId);

            ajax.jsonRpc(self._getUri("/sale_product_configurator/optional_product_items"),'call',{
                'product_id':productId,
                'pricelist_id':self.pricelistId||false,
            }).then(function(addedItem){
                var$addedItem=$(addedItem);
                $modal.find('tr:last').after($addedItem);

                self.$el.find('input[name="add_qty"]').trigger('change');
                self.triggerVariantChange($addedItem);

                //addauniqueidtothenewproducts
                varparentUniqueId=$parent[0].dataset.uniqueId;
                varparentQty=$parent.find('input[name="add_qty"]').val();
                $addedItem.filter('.js_product').each(function(){
                    var$el=$(this);
                    varuniqueId=self._getUniqueId(this);
                    this.dataset.uniqueId=uniqueId;
                    this.dataset.parentUniqueId=parentUniqueId;
                    $el.find('input[name="add_qty"]').val(parentQty);
                });

                if($selectOptionsText.nextAll('.js_product').length===0){
                    //nomoreoptionalproductstoselect->hidetheheader
                    $selectOptionsText.hide();
                }
            });
        });
    },

    /**
     *@private
     *@see_onAddOrRemoveOption
     *@param{$.Element}$modal
     *@param{$.Element}$parent
     */
    _onRemoveOption:function($modal,$parent){
        //restoreattributevaluesselection
        varuniqueId=$parent[0].dataset.parentUniqueId;
        varqty=$modal.find('tr.js_product.in_cart[data-unique-id="'+uniqueId+'"]').find('input[name="add_qty"]').val();
        $parent.removeClass('in_cart');
        $parent.find('.td-product_name').attr("colspan",2);
        $parent.find('.td-qty').addClass('d-none');
        $parent.find('input[name="add_qty"]').val(qty);
        $parent.find('.custom_attribute_values_description').remove();

        $modal.find('.o_select_options').show();

        varproductUniqueId=$parent[0].dataset.uniqueId;
        this._removeOptionOption($modal,productUniqueId);

        $modal.find('tr:last').after($parent);
    },

    /**
     *Iftheremovedproducthadoptionalproducts,removethemaswell
     *
     *@private
     *@param{$.Element}$modal
     *@param{integer}optionUniqueIdTheremovedoptionalproductid
     */
    _removeOptionOption:function($modal,optionUniqueId){
        varself=this;
        $modal.find('tr.js_product[data-parent-unique-id="'+optionUniqueId+'"]').each(function(){
            varuniqueId=this.dataset.uniqueId;
            $(this).remove();
            self._removeOptionOption($modal,uniqueId);
        });
    },
    /**
     *@override
     */
    _onChangeCombination:function(ev,$parent,combination){
        $parent
            .find('.td-product_name.product-name')
            .first()
            .text(combination.display_name);

        VariantMixin._onChangeCombination.apply(this,arguments);

        this._computePriceTotal();
    },
    /**
     *Updatepricetotalwhenthequantityofaproductischanged
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onChangeQuantity:function(ev){
        var$product=$(ev.target.closest('tr.js_product'));
        varqty=parseFloat($(ev.currentTarget).val());

        varuniqueId=$product[0].dataset.uniqueId;
        this.$el.find('tr.js_product:not(.in_cart)[data-parent-unique-id="'+uniqueId+'"]input[name="add_qty"]').each(function(){
            $(this).val(qty);
        });

        if(this._triggerPriceUpdateOnChangeQuantity()){
            this.onChangeAddQuantity(ev);
        }
        if($product.hasClass('main_product')){
            this.rootProduct.quantity=qty;
        }
        this.trigger('update_quantity',this.rootProduct.quantity);
        this._computePriceTotal();
    },

    /**
     *Whenaproductisaddedorwhenthequantityischanged,
     *weneedtorefreshthetotalpricerow
     */
    _computePriceTotal:function(){
        if(this.$modal.find('.js_price_total').length){
            varprice=0;
            this.$modal.find('.js_product.in_cart').each(function(){
                varquantity=parseFloat($(this).find('input[name="add_qty"]').first().val().replace(',','.')||1);
                price+=parseFloat($(this).find('.js_raw_price').html())*quantity;
            });

            this.$modal.find('.js_price_total.oe_currency_value').text(
                this._priceToStr(parseFloat(price))
            );
        }
    },

    /**
     *Extensionpointforwebsite_sale
     *
     *@private
     */
    _triggerPriceUpdateOnChangeQuantity:function(){
        returntrue;
    },
    /**
     *Returnsauniqueidfor`$el`.
     *
     *@private
     *@param{Element}el
     *@returns{integer}
     */
    _getUniqueId:function(el){
        if(!el.dataset.uniqueId){
            el.dataset.uniqueId=parseInt(_.uniqueId(),10);
        }
        returnel.dataset.uniqueId;
    },
});

returnOptionalProductsModal;

});
