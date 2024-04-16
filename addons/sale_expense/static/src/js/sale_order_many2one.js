flectra.define('sale_expense.sale_order_many2one',function(require){
"usestrict";

varFieldMany2One=require('web.relational_fields').FieldMany2One;
varFieldRegistry=require('web.field_registry');


varOrderField=FieldMany2One.extend({
    /**
     *hidethesearchmoreoptionfromthedropdownmenu
     *@override
     *@private
     *@returns{Object}
     */
    _manageSearchMore:function(values){
        returnvalues;
    }
});
FieldRegistry.add('sale_order_many2one',OrderField);
returnOrderField;
});
