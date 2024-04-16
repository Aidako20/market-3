flectra.define('account.reconciliation_field_tests',function(require){
"usestrict";

varFormView=require('web.FormView');
vartestUtils=require('web.test_utils');

varcreateView=testUtils.createView;

QUnit.module('account',{
    beforeEach:function(){
        this.data={
            'account.move':{
                fields:{
                    payments_widget:{string:"payments_widgetdata",type:"char"},
                    outstanding_credits_debits_widget:{string:"outstanding_credits_debits_widgetdata",type:"char"},
                },
                records:[{
                    id:1,
                    payments_widget:'{"content":[{"digits":[69,2],"currency":"$","amount":555.0,"name":"CustomerPayment:INV/2017/0004","date":"2017-04-25","position":"before","ref":"BNK1/2017/0003(INV/2017/0004)","payment_id":22,"move_id":10,"partial_id":38,"journal_name":"Bank"}],"outstanding":false,"title":"LessPayment"}',
                    outstanding_credits_debits_widget:'{"content":[{"digits":[69,2],"currency":"$","amount":100.0,"journal_name":"INV/2017/0004","position":"before","id":20}],"move_id":4,"outstanding":true,"title":"Outstandingcredits"}',
                }]
            },
        };
    }
},function(){
    QUnit.module('Reconciliation');

    QUnit.test('Reconciliationformfield',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'account.move',
            data:this.data,
            arch:'<form>'+
                '<fieldname="outstanding_credits_debits_widget"widget="payment"/>'+
                '<fieldname="payments_widget"widget="payment"/>'+
            '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='js_remove_outstanding_partial'){
                    assert.deepEqual(args.args,[10,38],"shouldcalljs_remove_outstanding_partial{warning:requiredfocus}");
                    returnPromise.resolve();
                }
                if(args.method==='js_assign_outstanding_line'){
                    assert.deepEqual(args.args,[4,20],"shouldcalljs_assign_outstanding_line{warning:requiredfocus}");
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
            intercepts:{
                do_action:function(event){
                    assert.deepEqual(event.data.action,{
                            'type':'ir.actions.act_window',
                            'res_model':'account.move',
                            'res_id':10,
                            'views':[[false,'form']],
                            'target':'current'
                        },
                        "shouldopentheformview");
                },
            },
        });

        assert.strictEqual(form.$('.o_field_widget[name="payments_widget"]').text().replace(/[\s\n\r]+/g,''),
            "Paidon04/25/2017$555.00",
            "shoulddisplaypaymentinformation");

        form.$('.o_field_widget[name="outstanding_credits_debits_widget"].outstanding_credit_assign').trigger('click');

        assert.strictEqual(form.$('.o_field_widget[name="outstanding_credits_debits_widget"]').text().replace(/[\s\n\r]+/g,''),
            "OutstandingcreditsAddINV/2017/0004$100.00",
            "shoulddisplayoutstandinginformation");

        form.$('.o_field_widget[name="payments_widget"].js_payment_info').trigger('focus');
        form.$('.popover.js_open_payment').trigger('click');

        form.$('.o_field_widget[name="payments_widget"].js_payment_info').trigger('focus');
        form.$('.popover.js_unreconcile_payment').trigger('click');

        form.destroy();
    });
});
});
