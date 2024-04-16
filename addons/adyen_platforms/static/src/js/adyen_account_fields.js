flectra.define('adyen_platforms.fields',function(require){
"usestrict";

varcore=require('web.core');
varFieldSelection=require('web.relational_fields').FieldSelection;
varfield_registry=require('web.field_registry');

varqweb=core.qweb;

varAdyenKYCStatusTag=FieldSelection.extend({
    _render:function(){
        this.$el.append(qweb.render('AdyenKYCStatusTag',{
            value:this.value,
        }));
    },
});

field_registry.add("adyen_kyc_status_tag",AdyenKYCStatusTag);

});
