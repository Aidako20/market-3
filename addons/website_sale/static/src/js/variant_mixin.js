flectra.define('website_sale.VariantMixin',function(require){
'usestrict';

varVariantMixin=require('sale.VariantMixin');

/**
 *Websitebehaviorisslightlydifferentfrombackendsoweappend
 *"_website"toURLstoleadtoadifferentroute
 *
 *@private
 *@param{string}uriTheuritoadapt
 */
VariantMixin._getUri=function(uri){
    if(this.isWebsite){
        returnuri+'_website';
    }else{
        returnuri;
    }
};

returnVariantMixin;

});
