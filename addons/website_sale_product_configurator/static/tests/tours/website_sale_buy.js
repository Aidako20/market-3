flectra.define("website_sale_product_configurator.website_sale_tour",function(require){
"usestrict";
/**
 *Addcustomstepstohandletheoptionalproductsmodalintroduced
 *bytheproductconfiguratormodule.
 */
vartour=require('web_tour.tour');
require('website_sale.tour');

varaddCartStepIndex=_.findIndex(tour.tours.shop_buy_product.steps,function(step){
    return(step.id==='add_cart_step');
});

tour.tours.shop_buy_product.steps.splice(addCartStepIndex+1,0,{
    content:"clickinmodalon'Proceedtocheckout'button",
    trigger:'button:contains("ProceedtoCheckout")',
});

});
