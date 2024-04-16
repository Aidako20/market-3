flectra.define('sale_product_configurator.product_configurator',function(require){
varProductConfiguratorWidget=require('sale.product_configurator');

/**
 *ExtensionoftheProductConfiguratorWidgettosupportproductconfiguration.
 *Itopenswhenaconfigurableproduct_templateisset.
 *(multiplevariants,orcustomattributes)
 *
 *Theproductcustomizationinformationincludes:
 *-is_configurable_product
 *-product_template_attribute_value_ids
 *
 */
ProductConfiguratorWidget.include({
    /**
     *Overrideofsale.product_configuratorHook
     *
     *@override
    */
    _isConfigurableProduct:function(){
        returnthis.recordData.is_configurable_product||this._super.apply(this,arguments);
    },

    /**
     *SetrestoreProductTemplateIdforfurtherbacktrack.
     *Savestheoptionalproductsinthewidgetforfutureapplication
     *post-lineconfiguration.
     *
     *{FlectraEventev}
     *   {Array}ev.data.optionalProductsthevariousselectedoptionalproducts
     *    withtheirconfiguration
     *
     *@override
     *@private
     */
    reset:function(record,ev){
        if(ev&&ev.target===this){
            this.restoreProductTemplateId=this.recordData.product_template_id;
            this.optionalProducts=(ev.data&&ev.data.optionalProducts)||this.optionalProducts;
        }

        this._super.apply(this,arguments);
    },

    /**
    *Thismethodisoverriddentocheckiftheproduct_template_id
    *needsconfigurationornot:
    *
    *-Theproduct_templatehasonlyone"product.product"andisnotdynamic
    *  ->Settheproduct_idontheSOline
    *  ->Iftheproducthasoptionalproducts,opentheconfiguratorin'options'mode
    *
    *-Theproduct_templateisconfigurable
    *  ->Opentheproductconfiguratorwizardandinitializeitwith
    *     theprovidedproduct_template_idanditscurrentattributevalues
    *
    *@override
    *@private
    */
    _onTemplateChange:function(productTemplateId,dataPointId){
        varself=this;
        varctx={};
        if(this.record&&this.recordParams){
            ctx=this.record.getContext(this.recordParams);
        }

        returnthis._rpc({
            model:'product.template',
            method:'get_single_product_variant',
            args:[productTemplateId],
            context:ctx,
        }).then(function(result){
            if(result.product_id&&!result.has_optional_products){
                self.trigger_up('field_changed',{
                    dataPointID:dataPointId,
                    changes:{
                        product_id:{id:result.product_id},
                        product_custom_attribute_value_ids:{
                            operation:'DELETE_ALL'
                        }
                    },
                });
            }else{
                returnself._openConfigurator(result,productTemplateId,dataPointId);
            }
            //alwaysreturnstrueforthemomentbecausenootherconfiguratorexists.
        });
    },

    /**
     * Whenlineisconfigured,applytheoptionsdefinedearlier.
     * @override
     * @private
     */
    _onLineConfigured:function(){
        varself=this;
        this._super.apply(this,arguments);
        varparentList=self.getParent();
        varunselectRow=(parentList.unselectRow||function(){}).bind(parentList);//formviewonmobile
        if(self.optionalProducts&&self.optionalProducts.length!==0){
            self.trigger_up('add_record',{
                context:self._productsToRecords(self.optionalProducts),
                forceEditable:'bottom',
                allowWarning:true,
                onSuccess:function(){
                    //Leaveeditmodeofone2manylist.
                    unselectRow();
                }
            });
        }elseif(!self._isConfigurableLine()&&self._isConfigurableProduct()){
            //Leaveeditmodeofcurrentlineiflinewasconfigured
            //onlythroughtheproductconfigurator.
            unselectRow();
        }
    },

    _openConfigurator:function(result,productTemplateId,dataPointId){
        if(!result.mode||result.mode==='configurator'){
            this._openProductConfigurator({
                    configuratorMode:result&&result.has_optional_products?'options':'add',
                    default_pricelist_id:this._getPricelistId(),
                    default_product_template_id:productTemplateId
                },
                dataPointId
            );
            returnPromise.resolve(true);
        }
        returnPromise.resolve(false);
    },

    /**
     *Openstheproductconfiguratortoallowconfiguringtheproducttemplate
     *anditsvariousoptions.
     *
     *TheconfiguratorModeparamcontrolshowtoopentheconfigurator.
     *-The"add"modewillallowconfiguringtheproducttemplate&options.
     *-The"edit"modewillonlyalloweditingtheproducttemplate'sconfiguration.
     *-The"options"modeisaspecialcasewheretheproductconfiguratorisusedasabridge
     *  betweentheSOlineandtheoptionalproductsmodal.Itwillhideitswindowandhandle
     *  thecommunicationbetweenthosetwo.
     *
     *Whentheconfigurationiscanceled(i.ewhentheproductconfiguratorisclosedusingthe
     *"CANCEL"buttonorthecrossonthetoprightcornerofthewindow),
     *theproduct_templateisresettoitspreviousvalueifany.
     *
     *@param{Object}datavarious"default_"values
     * {string}data.configuratorMode'add'or'edit'or'options'.
     *@param{string}dataPointId
     *
     *@private
     */
    _openProductConfigurator:function(data,dataPointId){
        this.optionalProducts=undefined;
        varself=this;
        this.do_action('sale_product_configurator.sale_product_configurator_action',{
            additional_context:data,
            on_close:function(result){
                if(result&&!result.special){
                    self._addProducts(result,dataPointId);
                }else{
                    if(self.restoreProductTemplateId){
                        //ifconfiguratoropenedineditmode.
                        self.trigger_up('field_changed',{
                            dataPointID:dataPointId,
                            preventProductIdCheck:true,
                            changes:{
                                product_template_id:self.restoreProductTemplateId.data
                            }
                        });
                    }else{
                        //ifconfiguratoropenedtocreateline:
                        //destroylineifconfiguratorclosedduringconfigurationprocess.
                        self.trigger_up('field_changed',{
                            dataPointID:dataPointId,
                            changes:{
                                product_template_id:false,
                                product_id:false,
                            },
                        });
                    }
                }
            }
        });
    },

    /**
     *Openstheproductconfiguratorin"edit"mode.
     *(see'_openProductConfigurator'formoreinfoonthe"edit"mode).
     *TherequirestoretrievealltheneededdatafromtheSOline
     *thatarekeptinthe"recordData"object.
     *
     *@private
     */
    _onEditProductConfiguration:function(){
        if(!this.recordData.is_configurable_product){
            //iflineshouldbeeditedbyanotherconfigurator
            //orsimplyinline.
            this._super.apply(this,arguments);
            return;
        }
        this.restoreProductTemplateId=this.recordData.product_template_id;
        //Iflinehasbeensetupthroughtheproduct_configurator:
        this._openProductConfigurator({
                configuratorMode:'edit',
                default_product_template_id:this.recordData.product_template_id.data.id,
                default_pricelist_id:this._getPricelistId(),
                default_product_template_attribute_value_ids:this._convertFromMany2Many(
                    this.recordData.product_template_attribute_value_ids
                ),
                default_product_no_variant_attribute_value_ids:this._convertFromMany2Many(
                    this.recordData.product_no_variant_attribute_value_ids
                ),
                default_product_custom_attribute_value_ids:this._convertFromOne2Many(
                    this.recordData.product_custom_attribute_value_ids
                ),
                default_quantity:this.recordData.product_uom_qty
            },
            this.dataPointID
        );
    },

    /**
     *ThiswillfirstmodifytheSOlinetoupdatealltheinformationcomingfrom
     *theproductconfiguratorusingthe'field_changed'event.
     *
     *onSuccessfromthatfirstmethod,itwilladdtheoptionalproductstotheSO
     *usingthe'add_record'event.
     *
     *Doingbothatthesametimecouldleadtounorderedproduct_template/options.
     *
     *@param{Object}productstheproductstoaddtotheSOline.
     *  {Object}products.mainProducttheproduct_templateconfigured
     *    withvariousattribute/customvalues
     *  {Array}products.optionsthevariousselectedoptionalproducts
     *    withtheirconfiguration
     *@param{string}dataPointId
     *
     *@private
     */
    _addProducts:function(result,dataPointId){
        this.trigger_up('field_changed',{
            dataPointID:dataPointId,
            preventProductIdCheck:true,
            optionalProducts:result.options,
            changes:this._getMainProductChanges(result.mainProduct)
        });
    },

    /**
     *Thiswillconverttheresultoftheproductconfiguratorinto
     *"changes"thatareunderstoodbythebasic_model.js
     *
     *Fortheproduct_custom_attribute_value_ids,weneedtodoaDELETE_ALL
     *commandtocleanthecurrentlyselectedvaluesandthenaCREATEforevery
     *customvaluespecifiedintheconfigurator.
     *
     *Fortheproduct_no_variant_attribute_value_ids,wealsoneedtodoaDELETE_ALL
     *commandtocleanthecurrentlyselectedvaluesandissueasingleADD_M2Mcontaining
     *alltheidsoftheproduct_attribute_values.
     *
     *@param{Object}mainProduct
     *
     *@private
     */
    _getMainProductChanges:function(mainProduct){
        varresult={
            product_id:{id:mainProduct.product_id},
            product_template_id:{id:mainProduct.product_template_id},
            product_uom_qty:mainProduct.quantity
        };

        varcustomAttributeValues=mainProduct.product_custom_attribute_values;
        varcustomValuesCommands=[{operation:'DELETE_ALL'}];
        if(customAttributeValues&&customAttributeValues.length!==0){
            _.each(customAttributeValues,function(customValue){
                //FIXMEawa:Thiscouldbeoptimizedbyaddinga"disableDefaultGet"toavoid
                //havingmultipledefault_getcallsthatareuselesssincewealready
                //haveallthedefaultvalueslocally.
                //However,thiswouldmeanalotofchangesinbasic_model.jstohandle
                //those"default_"valuesandsetthemonthevariousfields(text,o2m,m2m,...).
                //->Thisisnotconsideredasworthitrightnow.
                customValuesCommands.push({
                    operation:'CREATE',
                    context:[{
                        default_custom_product_template_attribute_value_id:customValue.custom_product_template_attribute_value_id,
                        default_custom_value:customValue.custom_value
                    }]
                });
            });
        }

        result['product_custom_attribute_value_ids']={
            operation:'MULTI',
            commands:customValuesCommands
        };

        varnoVariantAttributeValues=mainProduct.no_variant_attribute_values;
        varnoVariantCommands=[{operation:'DELETE_ALL'}];
        if(noVariantAttributeValues&&noVariantAttributeValues.length!==0){
            varresIds=_.map(noVariantAttributeValues,function(noVariantValue){
                return{id:parseInt(noVariantValue.value)};
            });

            noVariantCommands.push({
                operation:'ADD_M2M',
                ids:resIds
            });
        }

        result['product_no_variant_attribute_value_ids']={
            operation:'MULTI',
            commands:noVariantCommands
        };

        returnresult;
    },

    /**
     *Returnsthepricelist_idsetonthesale_orderform
     *
     *@private
     *@returns{integer}pricelist_id'sid
     */
    _getPricelistId:function(){
        returnthis.record.evalContext.parent.pricelist_id;
    },

    /**
     *Willmaptheproductstoappropriaterecordobjectsthatare
     *readyforthedefault_get.
     *
     *@param{Array}productsTheproductstotransformintorecords
     *
     *@private
     */
    _productsToRecords:function(products){
        varrecords=[];
        _.each(products,function(product){
            varrecord={
                default_product_id:product.product_id,
                default_product_template_id:product.product_template_id,
                default_product_uom_qty:product.quantity
            };

            if(product.no_variant_attribute_values){
                vardefaultProductNoVariantAttributeValues=[];
                _.each(product.no_variant_attribute_values,function(attributeValue){
                        defaultProductNoVariantAttributeValues.push(
                            [4,parseInt(attributeValue.value)]
                        );
                });
                record['default_product_no_variant_attribute_value_ids']
                    =defaultProductNoVariantAttributeValues;
            }

            if(product.product_custom_attribute_values){
                vardefaultCustomAttributeValues=[];
                _.each(product.product_custom_attribute_values,function(attributeValue){
                    defaultCustomAttributeValues.push(
                            [0,0,{
                                custom_product_template_attribute_value_id:attributeValue.custom_product_template_attribute_value_id,
                                custom_value:attributeValue.custom_value
                            }]
                        );
                });
                record['default_product_custom_attribute_value_ids']
                    =defaultCustomAttributeValues;
            }

            records.push(record);
        });

        returnrecords;
    }
});

returnProductConfiguratorWidget;

});
