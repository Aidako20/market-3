flectra.define('stock.popover_widget_tests',function(require){
"usestrict";

vartestUtils=require('web.test_utils');
varFormView=require('web.FormView');
varcreateView=testUtils.createView;

QUnit.module('widgets',{},function(){
QUnit.module('ModelFieldSelector',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    json_data:{string:"",type:"char"},
                },
                records:[
                    {id:1,json_data:'{"color":"text-danger","msg":"varthat=self//whynot?","title":"JSMaster"}'}
                ]
            }
        };
    },
},function(){
    QUnit.test("Testcreation/usagepopoverwidgetform",asyncfunction(assert){
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="json_data"widget="popover_widget"/>'+
                '</form>',
            res_id:1
        });

        var$popover=$('div.popover');
        assert.strictEqual($popover.length,0,"Shouldn'thaveapopovercontainerinDOM");

        var$popoverButton=form.$('a.fa.fa-info-circle.text-danger');
        assert.strictEqual($popoverButton.length,1,"Shouldhaveapopovericon/buttoninred");
        assert.strictEqual($popoverButton.prop('special_click'),true,"Specialclickproperpyshouldbeactivated");
        awaittestUtils.dom.triggerEvents($popoverButton,['focus']);
        $popover=$('div.popover');
        assert.strictEqual($popover.length,1,"ShouldhaveapopovercontainerinDOM");
        assert.strictEqual($popover.html().includes("varthat=self//whynot?"),true,"ThemessageshouldbeinDOM");
        assert.strictEqual($popover.html().includes("JSMaster"),true,"ThetitleshouldbeinDOM");

        form.destroy();
    });
});
});

});
