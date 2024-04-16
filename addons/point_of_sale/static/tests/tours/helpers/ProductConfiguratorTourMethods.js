flectra.define('point_of_sale.tour.ProductConfiguratorTourMethods',function(require){
    'usestrict';

    const{createTourMethods}=require('point_of_sale.tour.utils');

    classDo{
        pickRadio(name){
            return[
                {
                    content:`pickingradioattributewithname${name}`,
                    trigger:`.product-configurator-popup.radio_attribute_label:contains('${name}')`,
                },
            ];
        }

        pickSelect(name){
            return[
                {
                    content:`pickingselectattributewithname${name}`,
                    trigger:`.product-configurator-popup.configurator_select:has(option:contains('${name}'))`,
                    run:`text${name}`,
                },
            ];
        }

        pickColor(name){
            return[
                {
                    content:`pickingcolorattributewithname${name}`,
                    trigger:`.product-configurator-popup.configurator_color[data-color='${name}']`,
                },
            ];
        }

        fillCustomAttribute(value){
            return[
                {
                    content:`fillingcustomattributewithvalue${value}`,
                    trigger:`.product-configurator-popup.custom_value`,
                    run:`text${value}`,
                },
            ];
        }

        confirmAttributes(){
            return[
                {
                    content:`confirmingproductconfiguration`,
                    trigger:`.product-configurator-popup.button.confirm`,
                },
            ];
        }

        cancelAttributes(){
            return[
                {
                    content:`cancelingproductconfiguration`,
                    trigger:`.product-configurator-popup.button.cancel`,
                },
            ];
        }
    }

    classCheck{
        isShown(){
            return[
                {
                    content:'productconfiguratorisshown',
                    trigger:'.product-configurator-popup:not(:has(.oe_hidden))',
                    run:()=>{},
                },
            ];
        }
    }

    returncreateTourMethods('ProductConfigurator',Do,Check);
});
