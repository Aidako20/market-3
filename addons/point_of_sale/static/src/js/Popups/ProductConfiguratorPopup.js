flectra.define('point_of_sale.ProductConfiguratorPopup',function(require){
    'usestrict';

    const{useState,useSubEnv}=owl.hooks;
    constPosComponent=require('point_of_sale.PosComponent');
    constAbstractAwaitablePopup=require('point_of_sale.AbstractAwaitablePopup');
    constRegistries=require('point_of_sale.Registries');

    classProductConfiguratorPopupextendsAbstractAwaitablePopup{
        constructor(){
            super(...arguments);
            useSubEnv({attribute_components:[]});
        }

        getPayload(){
            varselected_attributes=[];
            varprice_extra=0.0;

            this.env.attribute_components.forEach((attribute_component)=>{
                let{value,extra}=attribute_component.getValue();
                selected_attributes.push(value);
                price_extra+=extra;
            });

            return{
                selected_attributes,
                price_extra,
            };
        }
    }
    ProductConfiguratorPopup.template='ProductConfiguratorPopup';
    Registries.Component.add(ProductConfiguratorPopup);

    classBaseProductAttributeextendsPosComponent{
        constructor(){
            super(...arguments);

            this.env.attribute_components.push(this);

            this.attribute=this.props.attribute;
            this.values=this.attribute.values;
            this.state=useState({
                selected_value:parseFloat(this.values[0].id),
                custom_value:'',
            });
        }

        getValue(){
            letselected_value=this.values.find((val)=>val.id===parseFloat(this.state.selected_value));
            letvalue=selected_value.name;
            if(selected_value.is_custom&&this.state.custom_value){
                value+=`:${this.state.custom_value}`;
            }

            return{
                value,
                extra:selected_value.price_extra
            };
        }
    }

    classRadioProductAttributeextendsBaseProductAttribute{
        mounted(){
            //Withradiobuttons`t-model`selectsthedefaultinputbysearchingforinputswith
            //amatching`value`attribute.Inourcase,weuse`t-att-value`so`value`is
            //notfoundyetandnoradioisselectedbydefault.
            //Wethenmanuallyselectthefirstinputofeachradioattribute.
            $(this.el).find('input[type="radio"]:first').prop('checked',true);
        }
    }
    RadioProductAttribute.template='RadioProductAttribute';
    Registries.Component.add(RadioProductAttribute);

    classSelectProductAttributeextendsBaseProductAttribute{}
    SelectProductAttribute.template='SelectProductAttribute';
    Registries.Component.add(SelectProductAttribute);

    classColorProductAttributeextendsBaseProductAttribute{}
    ColorProductAttribute.template='ColorProductAttribute';
    Registries.Component.add(ColorProductAttribute);

    return{
        ProductConfiguratorPopup,
        BaseProductAttribute,
        RadioProductAttribute,
        SelectProductAttribute,
        ColorProductAttribute,
    };
});
