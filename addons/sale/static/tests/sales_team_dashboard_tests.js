flectra.define('sale.dashboard_tests',function(require){
"usestrict";

varKanbanView=require('web.KanbanView');
vartestUtils=require('web.test_utils');

varcreateView=testUtils.createView;

QUnit.module('SalesTeamDashboard',{
    beforeEach:function(){
        this.data={
            'crm.team':{
                fields:{
                    foo:{string:"Foo",type:'char'},
                    invoiced_target:{string:"Invoiced_target",type:'integer'},
                },
                records:[
                    {id:1,foo:"yop"},
                ],
            },
        };
    }
});

QUnit.test('edittargetwithseveralo_kanban_primary_bottomdivs[REQUIREFOCUS]',asyncfunction(assert){
    assert.expect(6);

    varkanban=awaitcreateView({
        View:KanbanView,
        model:'crm.team',
        data:this.data,
        arch:'<kanban>'+
                '<templates>'+
                    '<tt-name="kanban-box">'+
                        '<divclass="containero_kanban_card_content">'+
                            '<fieldname="invoiced_target"/>'+
                            '<ahref="#"class="sales_team_target_definitiono_inline_link">'+
                                'Clicktodefineatarget</a>'+
                            '<divclass="col-12o_kanban_primary_bottom"/>'+
                            '<divclass="col-12o_kanban_primary_bottombottom_block"/>'+
                        '</div>'+
                    '</t>'+
                '</templates>'+
              '</kanban>',
        mockRPC:function(route,args){
            if(args.method==='write'){
                assert.strictEqual(args.args[1].invoiced_target,123,
                    "newvalueiscorrectlysaved");
            }
            if(args.method==='read'){//Readhappensafterthewrite
                assert.deepEqual(args.args[1],['invoiced_target','display_name'],
                    'theread(afterwrite)shouldaskforinvoiced_target');
            }
            returnthis._super.apply(this,arguments);
        },
    });

    assert.containsOnce(kanban,'.o_kanban_view.sales_team_target_definition',
        "shouldhaveclassname'sales_team_target_definition'");
    assert.containsN(kanban,'.o_kanban_primary_bottom',2,
        "shouldhavetwodivswithclassname'o_kanban_primary_bottom'");

    awaittestUtils.dom.click(kanban.$('a.sales_team_target_definition'));
    assert.containsOnce(kanban,'.o_kanban_primary_bottom:lastinput',
        "shouldhaverenderedaninputinthelasto_kanban_primary_bottomdiv");

    kanban.$('.o_kanban_primary_bottom:lastinput').focus();
    kanban.$('.o_kanban_primary_bottom:lastinput').val('123');
    kanban.$('.o_kanban_primary_bottom:lastinput').trigger('blur');
    awaittestUtils.nextTick();
    assert.strictEqual(kanban.$('.o_kanban_record').text(),"123Clicktodefineatarget",
        'Thekanbanrecordshoulddisplaytheupdatedtargetvalue');

    kanban.destroy();
});

QUnit.test('edittargetsupportspushEnter',asyncfunction(assert){
    assert.expect(3);

    varkanban=awaitcreateView({
        View:KanbanView,
        model:'crm.team',
        data:this.data,
        arch:'<kanban>'+
                '<templates>'+
                    '<tt-name="kanban-box">'+
                        '<divclass="containero_kanban_card_content">'+
                            '<fieldname="invoiced_target"/>'+
                            '<ahref="#"class="sales_team_target_definitiono_inline_link">'+
                                'Clicktodefineatarget</a>'+
                            '<divclass="col-12o_kanban_primary_bottom"/>'+
                            '<divclass="col-12o_kanban_primary_bottombottom_block"/>'+
                        '</div>'+
                    '</t>'+
                '</templates>'+
              '</kanban>',
        mockRPC:function(route,args){
            if(args.method==='write'){
                assert.strictEqual(args.args[1].invoiced_target,123,
                    "newvalueiscorrectlysaved");
            }
            if(args.method==='read'){//Readhappensafterthewrite
                assert.deepEqual(args.args[1],['invoiced_target','display_name'],
                    'theread(afterwrite)shouldaskforinvoiced_target');
            }
            returnthis._super.apply(this,arguments);
        },
    });

    awaittestUtils.dom.click(kanban.$('a.sales_team_target_definition'));

    kanban.$('.o_kanban_primary_bottom:lastinput').focus();
    kanban.$('.o_kanban_primary_bottom:lastinput').val('123');
    kanban.$('.o_kanban_primary_bottom:lastinput').trigger($.Event('keydown',{which:$.ui.keyCode.ENTER,keyCode:$.ui.keyCode.ENTER}));
    awaittestUtils.nextTick();
    assert.strictEqual(kanban.$('.o_kanban_record').text(),"123Clicktodefineatarget",
        'Thekanbanrecordshoulddisplaytheupdatedtargetvalue');

    kanban.destroy();
});

});
