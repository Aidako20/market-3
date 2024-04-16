flectra.define('l10n_ar_website_sale.website_sale_tour',function(require){
"usestrict";

    lettour=require('web_tour.tour');

    letwebsite_sale_tour=tour.tours.website_sale_tour;
    //Removethesteprelatedtootherlocalisations
    website_sale_tour.steps=_.filter(website_sale_tour.steps,step=>!step.l10n||step.l10n==="ar");

    letaddress_step=_.findIndex(website_sale_tour.steps,step=>step.content==='Fulfillbillingaddressform');
    letstep_run=website_sale_tour.steps[address_step].run;

    website_sale_tour.steps[address_step].run=function(){
        step_run();
        $("select[name='l10n_ar_afip_responsibility_type_id']option[value='5']").prop('selected',true);
        $("select[name='l10n_latam_identification_type_id']option[value='1']").prop('selected',true);
        $("input[name='vat']").val('123456789');
    };
});
