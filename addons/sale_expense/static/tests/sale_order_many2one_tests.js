flectra.define('sale_expense.field_many_to_one_tests',function(require){
"usestrict";

varFormView=require('web.FormView');
vartestUtils=require('web.test_utils');

varcreateView=testUtils.createView;


QUnit.module('sale_expense',{
    beforeEach:function(){
        this.data={
            'hr.expense':{
                fields:{
                    name:{string:"Description",type:"char"},
                    sale_order_id:{string:"ReinvoiceCustomer",type:'many2one',relation:'sale.order'},
                },
                records:[]
            },
            'sale.order':{
                fields:{
                    name:{string:"Name",type:"char"},
                },
                records:[{
                    id:1,
                    name:"SO1",
                },{
                    id:2,
                    name:"SO2",
                },{
                    id:3,
                    name:"SO3"
                },{
                    id:4,
                    name:"SO4"
                },{
                    id:5,
                    name:"SO5"
                },{
                    id:6,
                    name:"SO6"
                },{
                    id:7,
                    name:"SO7"
                },{
                    id:8,
                    name:"SO8"
                },{
                    id:9,
                    name:"SO9"
                }]
            },
        };
    },
},function(){
    QUnit.test('saleordermany2onewithoutsearchmoreoption',asyncfunction(assert){
        assert.expect(3);
        varform=awaitcreateView({
            View:FormView,
            model:'hr.expense',
            data:this.data,
            arch:
                '<formstring="Expense">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="sale_order_id"widget="sale_order_many2one"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>'
        });
        var$dropdown=form.$('.o_field_many2oneinput').autocomplete('widget');
        awaittestUtils.fields.many2one.clickOpenDropdown('sale_order_id');
        assert.containsN($dropdown,'li:not(.o_m2o_dropdown_option)',9);
        assert.containsNone($dropdown,'li.o_m2o_dropdown_option');
        assert.containsNone($dropdown,'li.o_m2o_dropdown_option:contains("SearchMore...")',"Shouldnotdisplaythe'SearchMore...option'");
        form.destroy();
    });
});
});
