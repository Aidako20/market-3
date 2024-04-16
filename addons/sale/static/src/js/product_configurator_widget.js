flectra.define('sale.product_configurator',function(require){
varrelationalFields=require('web.relational_fields');
varFieldsRegistry=require('web.field_registry');
varcore=require('web.core');
var_t=core._t;

/**
 *Thesale.product_configuratorwidgetisasimplewidgetextendingFieldMany2One
 *Itallowsthedevelopmentofconfigurationstrategiesinothermodulesthrough
 *widgetextensions.
 *
 *
 *!!!WARNING!!!
 *
 *Thiswidgetisonlydesignedforsale_order_linecreation/updates.
 *!!!Itshouldonlybeusedonaproduct_productorproduct_templatefield!!!
 */
varProductConfiguratorWidget=relationalFields.FieldMany2One.extend({
    events:_.extend({},relationalFields.FieldMany2One.prototype.events,{
        'click.o_edit_product_configuration':'_onEditConfiguration'
    }),

     /**
      *@override
      */
    _render:function(){
        this._super.apply(this,arguments);
        if(this.mode==='edit'&&this.value&&
        (this._isConfigurableProduct()||this._isConfigurableLine())){
            this._addProductLinkButton();
            this._addConfigurationEditButton();
        }elseif(this.mode==='edit'&&this.value){
            this._addProductLinkButton();
            this.$('.o_edit_product_configuration').hide();
        }else{
            this.$('.o_external_button').hide();
            this.$('.o_edit_product_configuration').hide();
        }
    },

    /**
     *Addbuttonlinkingtoproduct_id/product_template_idform.
     */
    _addProductLinkButton:function(){
        if(this.$('.o_external_button').length===0){
            var$productLinkButton=$('<button>',{
                type:'button',
                class:'fafa-external-linkbtnbtn-secondaryo_external_button',
                tabindex:'-1',
                draggable:false,
                'aria-label':_t('ExternalLink'),
                title:_t('ExternalLink')
            });

            var$inputDropdown=this.$('.o_input_dropdown');
            $inputDropdown.after($productLinkButton);
        }
    },

    /**
     *Ifcurrentproductisconfigurable,
     *Showeditbutton(inEditMode)aftertheproduct/product_template
     */
    _addConfigurationEditButton:function(){
        var$inputDropdown=this.$('.o_input_dropdown');

        if($inputDropdown.length!==0&&
            this.$('.o_edit_product_configuration').length===0){
            var$editConfigurationButton=$('<button>',{
                type:'button',
                class:'fafa-pencilbtnbtn-secondaryo_edit_product_configuration',
                tabindex:'-1',
                draggable:false,
                'aria-label':_t('EditConfiguration'),
                title:_t('EditConfiguration')
            });

            $inputDropdown.after($editConfigurationButton);
        }
    },

    /**
     *Hooktooverridewith_onEditProductConfiguration
     *toknowifeditpencilbuttonhastobeputnexttothefield
     *
     *@private
     */
    _isConfigurableProduct:function(){
        returnfalse;
    },

    /**
     *Hooktooverridewith_onEditProductConfiguration
     *toknowifeditpencilbuttonhastobeputnexttothefield
     *
     *@private
     */
    _isConfigurableLine:function(){
        returnfalse;
    },

    /**
     *Overridecatchingchangesonproduct_idorproduct_template_id.
     *Calls_onTemplateChangeincaseofproduct_templatechange.
     *Calls_onProductChangeincaseofproductchange.
     *Shouldn'tbeoverriddenbyproductconfigurators
     *oronlytosetupsomedataforfurthercomputation
     *beforecallingsuper.
     *
     *@override
     *@param{FlectraEvent}ev
     *@param{boolean}ev.data.preventProductIdCheckpreventtheproductconfiguratorwidget
     *    fromloopingforeverwhenitneedstochangethe'product_template_id'
     *
     *@private
     */
    reset:asyncfunction(record,ev){
        awaitthis._super(...arguments);
        if(ev&&ev.target===this){
            if(ev.data.changes&&!ev.data.preventProductIdCheck&&ev.data.changes.product_template_id){
                this._onTemplateChange(record.data.product_template_id.data.id,ev.data.dataPointID);
            }elseif(ev.data.changes&&ev.data.changes.product_id){
                this._onProductChange(record.data.product_id.data&&record.data.product_id.data.id,ev.data.dataPointID).then(wizardOpened=>{
                    if(!wizardOpened){
                        this._onLineConfigured();
                    }
                });
            }
        }
    },

    /**
     *Hookforproduct_templatebasedconfigurators
     *(productconfigurator,matrix,...).
     *
     *@param{integer}productTemplateId
     *@param{String}dataPointID
     *
     *@private
     */
    _onTemplateChange:function(productTemplateId,dataPointId){
        returnPromise.resolve(false);
    },

    /**
     *Hookforproduct_productbasedconfigurators
     *(event,rental,...).
     *Shouldreturn
     *   trueifproducthasbeenconfiguredthroughwizardor
     *       theresultofthesupercallforotherwizardextensions
     *   falseiftheproductwasn'tconfigurablethroughthewizard
     *
     *@param{integer}productId
     *@param{String}dataPointID
     *@returns{Promise<Boolean>}stopPropagationtrueifasuitableconfiguratorhasbeenfound.
     *
     *@private
     */
    _onProductChange:function(productId,dataPointId){
        returnPromise.resolve(false);
    },

    /**
     *Hookforconfiguratorhappeningafterlinehasbeenset
     *(options,...).
     *Allowssale_product_configuratormoduletoapplyitsoptions
     *afterlineconfigurationhasbeendone.
     *
     *@private
     */
    _onLineConfigured:function(){

    },

    /**
     *Triggeredonclickoftheconfigurationbutton.
     *ItisonlyshowninEditmode,
     *when_isConfigurableProductor_isConfigurableLineisTrue.
     *
     *Afterreflexion,whenalinewasconfiguredthroughtwowizards,
     *onlythelineconfigurationwillopen.
     *
     *Twohooksareavailabledependingonconfiguratorcategory:
     *_onEditLineConfiguration:lineconfigurators
     *_onEditProductConfiguration:productconfigurators
     *
     *@private
     */
    _onEditConfiguration:function(){
        if(this._isConfigurableLine()){
            this._onEditLineConfiguration();
        }elseif(this._isConfigurableProduct()){
            this._onEditProductConfiguration();
        }
    },

    /**
     *Hookforlineconfigurators(rental,event)
     *onlineedition(penciliconinsideproductfield)
     */
    _onEditLineConfiguration:function(){

    },

    /**
     *Hookforproductconfigurators(matrix,product)
     *onlineedition(penciliconinsideproductfield)
     */
    _onEditProductConfiguration:function(){

    },

    /**
     *UtilitiesforrecordDataconversion
     */

    /**
     *WillconvertthevaluescontainedintherecordDataparameterto
     *alistof'4'operationsthatcanbepassedasa'default_'parameter.
     *
     *@param{Object}recordData
     *
     *@private
     */
    _convertFromMany2Many:function(recordData){
        if(recordData){
            varconvertedValues=[];
            _.each(recordData.res_ids,function(resId){
                convertedValues.push([4,parseInt(resId)]);
            });

            returnconvertedValues;
        }

        returnnull;
    },

    /**
     *WillconvertthevaluescontainedintherecordDataparameterto
     *alistof'0'or'4'operations(basedonwethertherecordisalreadypersistedornot)
     *thatcanbepassedasa'default_'parameter.
     *
     *@param{Object}recordData
     *
     *@private
     */
    _convertFromOne2Many:function(recordData){
        if(recordData){
            varconvertedValues=[];
            _.each(recordData.res_ids,function(resId){
                if(isNaN(resId)){
                    _.each(recordData.data,function(record){
                        if(record.ref===resId){
                            convertedValues.push([0,0,{
                                custom_product_template_attribute_value_id:record.data.custom_product_template_attribute_value_id.data.id,
                                custom_value:record.data.custom_value
                            }]);
                        }
                    });
                }else{
                    convertedValues.push([4,resId]);
                }
            });

            returnconvertedValues;
        }

        returnnull;
    }
});

FieldsRegistry.add('product_configurator',ProductConfiguratorWidget);

returnProductConfiguratorWidget;

});
