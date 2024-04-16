flectra.define('web_kanban_gauge.gauge_tests',function(require){
"usestrict";

varKanbanView=require('web.KanbanView');
vartestUtils=require('web.test_utils');

varcreateView=testUtils.createView;

QUnit.module('fields',{},function(){

QUnit.module('basic_fields',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    int_field:{string:"int_field",type:"integer",sortable:true},
                },
                records:[
                    {id:1,int_field:10},
                    {id:2,int_field:4},
                ]
            },
        };
    }
},function(){

    QUnit.module('gaugewidget');

    QUnit.test('basicrendering',asyncfunction(assert){
        assert.expect(1);

        varkanban=awaitcreateView({
            View:KanbanView,
            model:'partner',
            data:this.data,
            arch:'<kanban><templates><tt-name="kanban-box">'+
                    '<div><fieldname="int_field"widget="gauge"/></div>'+
                '</t></templates></kanban>',
        });

        assert.containsOnce(kanban,'.o_kanban_record:first.oe_gaugecanvas',
            "shouldrenderthegaugewidget");

        kanban.destroy();
    });

});
});
});
