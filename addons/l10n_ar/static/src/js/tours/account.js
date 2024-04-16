flectra.define('l10n_ar.account_tour',function(require){
"usestrict";

    lettour=require('web_tour.tour');
    letaccount_tour=tour.tours.account_tour;
    //Removethestepsuggestingtochangethenameasitisdoneanotherway(documentnumber)
    account_tour.steps=_.filter(account_tour.steps,step=>step.trigger!="input[name=name]");

    //ConfiguretheAFIPResponsibility
    letpartner_step_idx=_.findIndex(account_tour.steps,step=>step.trigger=='div[name=partner_id]input');
    account_tour.steps.splice(partner_step_idx+2,0,{
        trigger:"div[name=l10n_ar_afip_responsibility_type_id]input",
        extra_trigger:"[name=move_type][raw-value=out_invoice]",
        position:"bottom",
        content:"SettheAFIPResponsability",
        run:"textIVA",
    })
    account_tour.steps.splice(partner_step_idx+3,0,{
        trigger:".ui-menu-item>a:contains('IVA').ui-state-active",
        auto:true,
        in_modal:false,
    })

})
