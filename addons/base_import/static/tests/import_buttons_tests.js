flectra.define('web.base_import_tests',function(require){
"usestrict";

constKanbanView=require('web.KanbanView');
constListView=require('web.ListView');
constPivotView=require('web.PivotView');
consttestUtils=require('web.test_utils');

constcreateView=testUtils.createView;

QUnit.module('BaseImportTests',{
    beforeEach:function(){
        this.data={
            foo:{
                fields:{
                    foo:{string:"Foo",type:"char"},
                },
                records:[
                    {id:1,foo:"yop"},
                ]
            },
        };
    }
});

QUnit.test('importinfavoritedropdowninlist',asyncfunction(assert){
    assert.expect(2);

    constlist=awaitcreateView({
        View:ListView,
        model:'foo',
        data:this.data,
        arch:'<tree><fieldname="foo"/></tree>',
    });

    testUtils.mock.intercept(list,'do_action',function(){
        assert.ok(true,"shouldhavetriggeredado_action");
    });

    awaittestUtils.dom.click(list.$('.o_favorite_menubutton'));
    assert.containsOnce(list,'.o_import_menu');

    awaittestUtils.dom.click(list.$('.o_import_menubutton'));

    list.destroy();
});

QUnit.test('importfavoritedropdownitemshouldnotinlistwithcreate="0"',asyncfunction(assert){
    assert.expect(1);

    constlist=awaitcreateView({
        View:ListView,
        model:'foo',
        data:this.data,
        arch:'<treecreate="0"><fieldname="foo"/></tree>',
    });

    awaittestUtils.dom.click(list.$('.o_favorite_menubutton'));
    assert.containsNone(list,'.o_import_menu');

    list.destroy();
});

QUnit.test('importfavoritedropdownitemshouldnotinlistwithimport="0"',asyncfunction(assert){
    assert.expect(1);

    constlist=awaitcreateView({
        View:ListView,
        model:'foo',
        data:this.data,
        arch:'<treeimport="0"><fieldname="foo"/></tree>',
    });

    awaittestUtils.dom.click(list.$('.o_favorite_menubutton'));
    assert.containsNone(list,'.o_import_menu');

    list.destroy();
});

QUnit.test('importinfavoritedropdowninkanban',asyncfunction(assert){
    assert.expect(2);

    constkanban=awaitcreateView({
        View:KanbanView,
        model:'foo',
        data:this.data,
        arch:`<kanban>
                <templates>
                    <tt-name="kanban-box">
                        <div><fieldname="foo"/></div>
                    </t>
                </templates>
            </kanban>`,
    });

    testUtils.mock.intercept(kanban,'do_action',function(){
        assert.ok(true,"shouldhavetriggeredado_action");
    });

    awaittestUtils.dom.click(kanban.$('.o_favorite_menubutton'));
    assert.containsOnce(kanban,'.o_import_menu');

    awaittestUtils.dom.click(kanban.$('.o_import_menubutton'));

    kanban.destroy();
});

QUnit.test('importfavoritedropdownitemshouldnotinlistwithcreate="0"',asyncfunction(assert){
    assert.expect(1);

    constkanban=awaitcreateView({
        View:KanbanView,
        model:'foo',
        data:this.data,
        arch:`<kanbancreate="0">
                <templates>
                    <tt-name="kanban-box">
                        <div><fieldname="foo"/></div>
                    </t>
                </templates>
            </kanban>`,
    });

    awaittestUtils.dom.click(kanban.$('.o_favorite_menubutton'));
    assert.containsNone(kanban,'.o_import_menu');

    kanban.destroy();
});

QUnit.test('importdropdownfavoriteshouldnotinkanbanwithimport="0"',asyncfunction(assert){
    assert.expect(1);

    constkanban=awaitcreateView({
        View:KanbanView,
        model:'foo',
        data:this.data,
        arch:`<kanbanimport="0">
                <templates>
                    <tt-name="kanban-box">
                        <div><fieldname="foo"/></div>
                    </t>
                </templates>
            </kanban>`,
    });

    awaittestUtils.dom.click(kanban.$('.o_favorite_menubutton'));
    assert.containsNone(kanban,'.o_import_menu');

    kanban.destroy();
});

QUnit.test('importshouldnotavailableinfavoritedropdowninpivot(otherthankanbanorlist)',asyncfunction(assert){
    assert.expect(1);

    this.data.foo.fields.foobar={string:"Fubar",type:"integer",group_operator:'sum'};

    constpivot=awaitcreateView({
        View:PivotView,
        model:'foo',
        data:this.data,
        arch:'<pivot><fieldname="foobar"type="measure"/></pivot>',
    });

    awaittestUtils.dom.click(pivot.$('.o_favorite_menubutton'));
    assert.containsNone(pivot,'.o_import_menu');

    pivot.destroy();
});

});
