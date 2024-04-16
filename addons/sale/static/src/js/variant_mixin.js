flectra.define('sale.VariantMixin',function(require){
'usestrict';

varconcurrency=require('web.concurrency');
varcore=require('web.core');
varutils=require('web.utils');
varajax=require('web.ajax');
var_t=core._t;

varVariantMixin={
    events:{
        'change.css_attribute_colorinput':'_onChangeColorAttribute',
        'change.main_product:not(.in_cart)input.js_quantity':'onChangeAddQuantity',
        'change[data-attribute_exclusions]':'onChangeVariant'
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Whenavariantischanged,thiswillcheck:
     *-Iftheselectedcombinationisavailableornot
     *-Theextrapriceifapplicable
     *-Thedisplaynameoftheproduct("Customizabledesk(White,Steel)")
     *-Thenewtotalprice
     *-Theneedofaddinga"customvalue"input
     *  Ifthecustomvalueistheonlyavailablevalue
     *  (definedbyitsdata'is_single_and_custom'),
     *  thecustomvaluewillhaveit'sowninput&label
     *
     *'change'eventstriggeredbytheuserenteredcustomvaluesareignoredsincethey
     *arenotrelevant
     *
     *@param{MouseEvent}ev
     */
    onChangeVariant:function(ev){
        var$parent=$(ev.target).closest('.js_product');
        if(!$parent.data('uniqueId')){
            $parent.data('uniqueId',_.uniqueId());
        }
        this._throttledGetCombinationInfo($parent.data('uniqueId'))(ev);
    },
    /**
     *@seeonChangeVariant
     *
     *@private
     *@param{Event}ev
     *@returns{Deferred}
     */
    _getCombinationInfo:function(ev){
        varself=this;

        if($(ev.target).hasClass('variant_custom_value')){
            returnPromise.resolve();
        }

        var$parent=$(ev.target).closest('.js_product');
        varqty=$parent.find('input[name="add_qty"]').val();
        varcombination=this.getSelectedVariantValues($parent);
        varparentCombination=$parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').parent_combination;
        varproductTemplateId=parseInt($parent.find('.product_template_id').val());

        self._checkExclusions($parent,combination);

        returnajax.jsonRpc(this._getUri('/sale/get_combination_info'),'call',{
            'product_template_id':productTemplateId,
            'product_id':this._getProductId($parent),
            'combination':combination,
            'add_qty':parseInt(qty),
            'pricelist_id':this.pricelistId||false,
            'parent_combination':parentCombination,
        }).then(function(combinationData){
            self._onChangeCombination(ev,$parent,combinationData);
        });
    },

    /**
     *Willaddthe"customvalue"inputforthisattributevalueif
     *theattributevalueisconfiguredas"custom"(seeproduct_attribute_value.is_custom)
     *
     *@private
     *@param{MouseEvent}ev
     */
    handleCustomValues:function($target){
        var$variantContainer;
        var$customInput=false;
        if($target.is('input[type=radio]')&&$target.is(':checked')){
            $variantContainer=$target.closest('ul').closest('li');
            $customInput=$target;
        }elseif($target.is('select')){
            $variantContainer=$target.closest('li');
            $customInput=$target
                .find('option[value="'+$target.val()+'"]');
        }

        if($variantContainer){
            if($customInput&&$customInput.data('is_custom')==='True'){
                varattributeValueId=$customInput.data('value_id');
                varattributeValueName=$customInput.data('value_name');

                if($variantContainer.find('.variant_custom_value').length===0
                        ||$variantContainer
                              .find('.variant_custom_value')
                              .data('custom_product_template_attribute_value_id')!==parseInt(attributeValueId)){
                    $variantContainer.find('.variant_custom_value').remove();

                    var$input=$('<input>',{
                        type:'text',
                        'data-custom_product_template_attribute_value_id':attributeValueId,
                        'data-attribute_value_name':attributeValueName,
                        class:'variant_custom_valueform-control'
                    });

                    varisRadioInput=$target.is('input[type=radio]')&&
                        $target.closest('label.css_attribute_color').length===0;

                    if(isRadioInput&&$customInput.data('is_single_and_custom')!=='True'){
                        $input.addClass('custom_value_radio');
                        $target.closest('div').after($input);
                    }else{
                        $input.attr('placeholder',attributeValueName);
                        $input.addClass('custom_value_own_line');
                        $variantContainer.append($input);
                    }
                }
            }else{
                $variantContainer.find('.variant_custom_value').remove();
            }
        }
    },

    /**
     *Hacktoaddandremovefromcartwithjson
     *
     *@param{MouseEvent}ev
     */
    onClickAddCartJSON:function(ev){
        ev.preventDefault();
        var$link=$(ev.currentTarget);
        var$input=$link.closest('.input-group').find("input");
        varmin=parseFloat($input.data("min")||0);
        varmax=parseFloat($input.data("max")||Infinity);
        varpreviousQty=parseFloat($input.val()||0,10);
        varquantity=($link.has(".fa-minus").length?-1:1)+previousQty;
        varnewQty=quantity>min?(quantity<max?quantity:max):min;

        if(newQty!==previousQty){
            $input.val(newQty).trigger('change');
        }
        returnfalse;
    },

    /**
     *Whenthequantityischanged,weneedtoquerythenewpriceoftheproduct.
     *Basedonthepricelist,thepricemightchangewhenquantityexceedsX
     *
     *@param{MouseEvent}ev
     */
    onChangeAddQuantity:function(ev){
        var$parent;

        if($(ev.currentTarget).closest('.oe_optional_products_modal').length>0){
            $parent=$(ev.currentTarget).closest('.oe_optional_products_modal');
        }elseif($(ev.currentTarget).closest('form').length>0){
            $parent=$(ev.currentTarget).closest('form');
        } else{
            $parent=$(ev.currentTarget).closest('.o_product_configurator');
        }

        this.triggerVariantChange($parent);
    },

    /**
     *Triggersthepricecomputationandothervariantspecificchanges
     *
     *@param{$.Element}$container
     */
    triggerVariantChange:function($container){
        varself=this;
        $container.find('ul[data-attribute_exclusions]').trigger('change');
        $container.find('input.js_variant_change:checked,select.js_variant_change').each(function(){
            self.handleCustomValues($(this));
        });
    },

    /**
     *Willlookforusercustomattributevalues
     *intheprovidedcontainer
     *
     *@param{$.Element}$container
     *@returns{Array}arrayofcustomvalueswiththefollowingformat
     *  {integer}custom_product_template_attribute_value_id
     *  {string}attribute_value_name
     *  {string}custom_value
     */
    getCustomVariantValues:function($container){
        varvariantCustomValues=[];
        $container.find('.variant_custom_value').each(function(){
            var$variantCustomValueInput=$(this);
            if($variantCustomValueInput.length!==0){
                variantCustomValues.push({
                    'custom_product_template_attribute_value_id':$variantCustomValueInput.data('custom_product_template_attribute_value_id'),
                    'attribute_value_name':$variantCustomValueInput.data('attribute_value_name'),
                    'custom_value':$variantCustomValueInput.val(),
                });
            }
        });

        returnvariantCustomValues;
    },

    /**
     *Willlookforattributevaluesthatdonotcreateproductvariant
     *(seeproduct_attribute.create_variant"dynamic")
     *
     *@param{$.Element}$container
     *@returns{Array}arrayofattributevalueswiththefollowingformat
     *  {integer}custom_product_template_attribute_value_id
     *  {string}attribute_value_name
     *  {integer}value
     *  {string}attribute_name
     *  {boolean}is_custom
     */
    getNoVariantAttributeValues:function($container){
        varnoVariantAttributeValues=[];
        varvariantsValuesSelectors=[
            'input.no_variant.js_variant_change:checked',
            'select.no_variant.js_variant_change'
        ];

        $container.find(variantsValuesSelectors.join(',')).each(function(){
            var$variantValueInput=$(this);
            varsingleNoCustom=$variantValueInput.data('is_single')&&!$variantValueInput.data('is_custom');

            if($variantValueInput.is('select')){
                $variantValueInput=$variantValueInput.find('option[value='+$variantValueInput.val()+']');
            }

            if($variantValueInput.length!==0&&!singleNoCustom){
                noVariantAttributeValues.push({
                    'custom_product_template_attribute_value_id':$variantValueInput.data('value_id'),
                    'attribute_value_name':$variantValueInput.data('value_name'),
                    'value':$variantValueInput.val(),
                    'attribute_name':$variantValueInput.data('attribute_name'),
                    'is_custom':$variantValueInput.data('is_custom')
                });
            }
        });

        returnnoVariantAttributeValues;
    },

    /**
     *Willreturnthelistofselectedproduct.template.attribute.valueids
     *Forthemodal,the"mainproduct"'sattributevaluesarestoredinthe
     *"unchanged_value_ids"data
     *
     *@param{$.Element}$containerthecontainertolookinto
     */
    getSelectedVariantValues:function($container){
        varvalues=[];
        varunchangedValues=$container
            .find('div.oe_unchanged_value_ids')
            .data('unchanged_value_ids')||[];

        varvariantsValuesSelectors=[
            'input.js_variant_change:checked',
            'select.js_variant_change'
        ];
        _.each($container.find(variantsValuesSelectors.join(',')),function(el){
            values.push(+$(el).val());
        });

        returnvalues.concat(unchangedValues);
    },

    /**
     *Willreturnapromise:
     *
     *-Iftheproductalreadyexists,immediatelyresolvesitwiththeproduct_id
     *-Iftheproductdoesnotexistyet("dynamic"variantcreation),thismethodwill
     *  createtheproductfirstandthenresolvethepromisewiththecreatedproduct'sid
     *
     *@param{$.Element}$containerthecontainertolookinto
     *@param{integer}productIdtheproductid
     *@param{integer}productTemplateIdthecorrespondingproducttemplateid
     *@param{boolean}useAjaxwethertherpccallshouldbedoneusingajax.jsonRpcorusing_rpc
     *@returns{Promise}thepromisethatwillberesolvedwitha{integer}productId
     */
    selectOrCreateProduct:function($container,productId,productTemplateId,useAjax){
        varself=this;
        productId=parseInt(productId);
        productTemplateId=parseInt(productTemplateId);
        varproductReady=Promise.resolve();
        if(productId){
            productReady=Promise.resolve(productId);
        }else{
            varparams={
                product_template_id:productTemplateId,
                product_template_attribute_value_ids:
                    JSON.stringify(self.getSelectedVariantValues($container)),
            };

            varroute='/sale/create_product_variant';
            if(useAjax){
                productReady=ajax.jsonRpc(route,'call',params);
            }else{
                productReady=this._rpc({route:route,params:params});
            }
        }

        returnproductReady;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Willdisableattributevalue'sinputsbasedoncombinationexclusions
     *andwilldisablethe"add"buttoniftheselectedcombination
     *isnotavailable
     *
     *Thiswillcheckboththeexclusionswithintheproductitselfand
     *theexclusionscomingfromtheparentproduct(meaningthatthisproduct
     *isanoptionoftheparentproduct)
     *
     *Itwillalsocheckthattheselectedcombinationdoesnotexactly
     *matchamanuallyarchivedproduct
     *
     *@private
     *@param{$.Element}$parenttheparentcontainertoapplyexclusions
     *@param{Array}combinationtheselectedcombinationofproductattributevalues
     */
    _checkExclusions:function($parent,combination){
        varself=this;
        varcombinationData=$parent
            .find('ul[data-attribute_exclusions]')
            .data('attribute_exclusions');

        $parent
            .find('option,input,label')
            .removeClass('css_not_available')
            .attr('title',function(){return$(this).data('value_name')||'';})
            .data('excluded-by','');

        //exclusionrules:arrayofptav
        //foreachofthem,containsarraywiththeotherptavtheyexclude
        if(combinationData.exclusions){
            //browseallthecurrentlyselectedattributes
            _.each(combination,function(current_ptav){
                if(combinationData.exclusions.hasOwnProperty(current_ptav)){
                    //foreachexclusionofthecurrentattribute:
                    _.each(combinationData.exclusions[current_ptav],function(excluded_ptav){
                        //disabletheexcludedinput(evenwhennotalreadyselected)
                        //togiveavisualfeedbackbeforeclick
                        self._disableInput(
                            $parent,
                            excluded_ptav,
                            current_ptav,
                            combinationData.mapped_attribute_names
                        );
                    });
                }
            });
        }

        //parentexclusions(tellwhichattributesareexcludedfromparent)
        _.each(combinationData.parent_exclusions,function(exclusions,excluded_by){
            //checkthattheselectedcombinationisintheparentexclusions
            _.each(exclusions,function(ptav){

                //disabletheexcludedinput(evenwhennotalreadyselected)
                //togiveavisualfeedbackbeforeclick
                self._disableInput(
                    $parent,
                    ptav,
                    excluded_by,
                    combinationData.mapped_attribute_names,
                    combinationData.parent_product_name
                );
            });
        });
    },
    /**
     *Extractedtoamethodtobeextendablebyothermodules
     *
     *@param{$.Element}$parent
     */
    _getProductId:function($parent){
        returnparseInt($parent.find('.product_id').val());
    },
    /**
     *Willdisabletheinput/optionthatreferstothepassedattributeValueId.
     *Thisisusedforshowingtheuserthatsomecombinationsarenotavailable.
     *
     *Itwillalsodisplayamessageexplainingwhytheinputisnotselectable.
     *Basedonthe"excludedBy"andthe"productName"params.
     *e.g:NotavailablewithColor:Black
     *
     *@private
     *@param{$.Element}$parent
     *@param{integer}attributeValueId
     *@param{integer}excludedByTheattributevaluethatexcludesthisinput
     *@param{Object}attributeNamesAdictcontainingallthenamesoftheattributevalues
     *  toshowahumanreadablemessageexplainingwhytheinputisdisabled.
     *@param{string}[productName]Theparentproduct.Ifprovided,itwillbeappendedbefore
     *  thenameoftheattributevaluethatexcludesthisinput
     *  e.g:NotavailablewithCustomizableDesk(Color:Black)
     */
    _disableInput:function($parent,attributeValueId,excludedBy,attributeNames,productName){
        var$input=$parent
            .find('option[value='+attributeValueId+'],input[value='+attributeValueId+']');
        $input.addClass('css_not_available');
        $input.closest('label').addClass('css_not_available');

        if(excludedBy&&attributeNames){
            var$target=$input.is('option')?$input:$input.closest('label').add($input);
            varexcludedByData=[];
            if($target.data('excluded-by')){
                excludedByData=JSON.parse($target.data('excluded-by'));
            }

            varexcludedByName=attributeNames[excludedBy];
            if(productName){
                excludedByName=productName+'('+excludedByName+')';
            }
            excludedByData.push(excludedByName);

            $target.attr('title',_.str.sprintf(_t('Notavailablewith%s'),excludedByData.join(',')));
            $target.data('excluded-by',JSON.stringify(excludedByData));
        }
    },
    /**
     *@seeonChangeVariant
     *
     *@private
     *@param{MouseEvent}ev
     *@param{$.Element}$parent
     *@param{Array}combination
     */
    _onChangeCombination:function(ev,$parent,combination){
        varself=this;
        var$price=$parent.find(".oe_price:first.oe_currency_value");
        var$default_price=$parent.find(".oe_default_price:first.oe_currency_value");
        var$optional_price=$parent.find(".oe_optional:first.oe_currency_value");
        $price.text(self._priceToStr(combination.price));
        $default_price.text(self._priceToStr(combination.list_price));

        varisCombinationPossible=true;
        if(!_.isUndefined(combination.is_combination_possible)){
            isCombinationPossible=combination.is_combination_possible;
        }
        this._toggleDisable($parent,isCombinationPossible);

        if(combination.has_discounted_price){
            $default_price
                .closest('.oe_website_sale')
                .addClass("discount");
            $optional_price
                .closest('.oe_optional')
                .removeClass('d-none')
                .css('text-decoration','line-through');
            $default_price.parent().removeClass('d-none');
        }else{
            $default_price
                .closest('.oe_website_sale')
                .removeClass("discount");
            $optional_price.closest('.oe_optional').addClass('d-none');
            $default_price.parent().addClass('d-none');
        }

        varrootComponentSelectors=[
            'tr.js_product',
            '.oe_website_sale',
            '.o_product_configurator'
        ];

        //updateimagesonlywhenchangingproduct
        //orwheneitheridsare'false',meaningdynamicproducts.
        //Dynamicproductsdon'thaveimagesBUTtheymayhaveinvalid
        //combinationsthatneedtodisabletheimage.
        if(!combination.product_id||
            !this.last_product_id||
            combination.product_id!==this.last_product_id){
            this.last_product_id=combination.product_id;
            self._updateProductImage(
                $parent.closest(rootComponentSelectors.join(',')),
                combination.display_image,
                combination.product_id,
                combination.product_template_id,
                combination.carousel,
                isCombinationPossible
            );
        }

        $parent
            .find('.product_id')
            .first()
            .val(combination.product_id||0)
            .trigger('change');

        $parent
            .find('.product_display_name')
            .first()
            .text(combination.display_name);

        $parent
            .find('.js_raw_price')
            .first()
            .text(combination.price)
            .trigger('change');

        this.handleCustomValues($(ev.target));
    },

    /**
     *returnstheformattedprice
     *
     *@private
     *@param{float}price
     */
    _priceToStr:function(price){
        varl10n=_t.database.parameters;
        varprecision=2;

        if($('.decimal_precision').length){
            precision=parseInt($('.decimal_precision').last().data('precision'));
        }
        varformatted=_.str.sprintf('%.'+precision+'f',price).split('.');
        formatted[0]=utils.insert_thousand_seps(formatted[0]);
        returnformatted.join(l10n.decimal_point);
    },
    /**
     *Returnsathrottled`_getCombinationInfo`withaleadingandatrailing
     *call,whichismemoizedper`uniqueId`,andforwhichpreviousresults
     *aredropped.
     *
     *TheuniqueIdisneededbecauseontheconfiguratormodaltheremightbe
     *multipleelementstriggeringtherpcatthesametime,andweneedeach
     *individualproductrpctobeexecuted,butonlyonceperindividual
     *product.
     *
     *Theleadingexecutionistokeepgoodreactivityonthefirstcall,for
     *abetteruserexperience.Thetrailingisbecauseultimatelyonlythe
     *informationaboutthelastselectedcombinationisuseful.All
     *intermediaryrpccanbeignoredandarethereforebestnotdoneatall.
     *
     *TheDropMisorderedistomakesureslowerrpcareignorediftheresult
     *ofanewerrpchasalreadybeenreceived.
     *
     *@private
     *@param{string}uniqueId
     *@returns{function}
     */
    _throttledGetCombinationInfo:_.memoize(function(uniqueId){
        vardropMisordered=newconcurrency.DropMisordered();
        var_getCombinationInfo=_.throttle(this._getCombinationInfo.bind(this),500);
        returnfunction(ev,params){
            returndropMisordered.add(_getCombinationInfo(ev,params));
        };
    }),
    /**
     *Togglesthedisabledclassdependingonthe$parentelement
     *andthepossibilityofthecurrentcombination.
     *
     *@private
     *@param{$.Element}$parent
     *@param{boolean}isCombinationPossible
     */
    _toggleDisable:function($parent,isCombinationPossible){
        $parent.toggleClass('css_not_available',!isCombinationPossible);
    },
    /**
     *Updatestheproductimage.
     *ThiswillusetheproductIdifavailableorwillfallbacktotheproductTemplateId.
     *
     *@private
     *@param{$.Element}$productContainer
     *@param{boolean}displayImagewillhidetheimageiftrue.Itwillusethe'invisible'class
     *  insteadofd-nonetopreventlayoutchange
     *@param{integer}product_id
     *@param{integer}productTemplateId
     */
    _updateProductImage:function($productContainer,displayImage,productId,productTemplateId){
        varmodel=productId?'product.product':'product.template';
        varmodelId=productId||productTemplateId;
        varimageUrl='/web/image/{0}/{1}/'+(this._productImageField?this._productImageField:'image_1024');
        varimageSrc=imageUrl
            .replace("{0}",model)
            .replace("{1}",modelId);

        varimagesSelectors=[
            'span[data-oe-model^="product."][data-oe-type="image"]img:first',
            'img.product_detail_img',
            'span.variant_imageimg',
            'img.variant_image',
        ];

        var$img=$productContainer.find(imagesSelectors.join(','));

        if(displayImage){
            $img.removeClass('invisible').attr('src',imageSrc);
        }else{
            $img.addClass('invisible');
        }
    },

    /**
     *Highlightselectedcolor
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onChangeColorAttribute:function(ev){
        var$parent=$(ev.target).closest('.js_product');
        $parent.find('.css_attribute_color')
            .removeClass("active")
            .filter(':has(input:checked)')
            .addClass("active");
    },

    /**
     *Extensionpointforwebsite_sale
     *
     *@private
     *@param{string}uriTheuritoadapt
     */
    _getUri:function(uri){
        returnuri;
    }
};

returnVariantMixin;

});
