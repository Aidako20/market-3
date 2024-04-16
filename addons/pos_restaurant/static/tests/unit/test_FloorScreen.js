flectra.define('pos_restaurant.tests.FloorScreen',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    const{useListener}=require('web.custom_hooks');
    consttestUtils=require('web.test_utils');
    constmakePosTestEnv=require('point_of_sale.test_env');
    const{xml}=owl.tags;
    const{useRef}=owl.hooks;

    QUnit.module('FloorScreencomponents',{});

    QUnit.test('TableWidget',asyncfunction(assert){
        assert.expect(9);

        classParentextendsPosComponent{
            constructor(){
                super();
                useListener('select-table',()=>assert.step('select-table'));
            }
            gettable(){
                //rendertableT1
                returnObject.values(this.env.pos.tables_by_id).find(
                    (table)=>table.name==='T1'
                );
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div><TableWidgettable="table"/></div>
        `;

        constparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        consttableEl=parent.el.querySelector('.table');
        assert.ok(tableEl.querySelector('span.label').textContent.includes('T1'));
        assert.ok(tableEl.querySelector('span.table-seats').textContent.includes('4'));
        assert.strictEqual(tableEl.style.width,'100px');
        assert.strictEqual(tableEl.style.height,'100px');
        assert.strictEqual(tableEl.style.background,'rgb(53,211,116)');
        assert.strictEqual(tableEl.style.top,'50px');
        assert.strictEqual(tableEl.style.left,'50px');

        awaittestUtils.dom.click(tableEl);
        assert.verifySteps(['select-table']);

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('EditableTable',asyncfunction(assert){
        assert.expect(11);

        classParentextendsPosComponent{
            constructor(){
                super();
                useListener('save-table',()=>assert.step('save-table'));
                this.tableRef=useRef('table-ref');
            }
            gettable(){
                //rendertableT1
                returnObject.values(this.env.pos.tables_by_id).find(
                    (table)=>table.name==='T1'
                );
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <divclass="floor-map">
                <EditableTabletable="table"t-ref="table-ref"/>
            </div>
        `;

        constparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        consttableEl=parent.el.querySelector('.table.selected');
        assert.ok(tableEl.querySelector('span.label').textContent.includes('T1'));
        assert.ok(tableEl.querySelector('span.table-seats').textContent.includes('4'));
        assert.strictEqual(tableEl.style.width,'100px');
        assert.strictEqual(tableEl.style.height,'100px');
        assert.strictEqual(tableEl.style.background,'rgb(53,211,116)');
        assert.strictEqual(tableEl.style.top,'50px');
        assert.strictEqual(tableEl.style.left,'50px');

        parent.tableRef.comp.trigger('resize-end',{
            size:{width:100,height:100},
            loc:{top:50,left:50},
        });
        assert.verifySteps(['save-table']);
        parent.tableRef.comp.trigger('drag-end',{loc:{top:50,left:50}});
        assert.verifySteps(['save-table']);

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('EditBar',asyncfunction(assert){
        assert.expect(26);

        classParentextendsPosComponent{
            constructor(){
                super();
                useListener('create-table',()=>assert.step('create-table'));
                useListener('duplicate-table',()=>assert.step('duplicate-table'));
                useListener('rename-table',()=>assert.step('rename-table'));
                useListener('change-seats-num',()=>assert.step('change-seats-num'));
                useListener('change-shape',()=>assert.step('change-shape'));
                useListener('set-table-color',this._onSetTableColor);
                useListener('set-floor-color',this._onSetFloorColor);
                useListener('delete-table',()=>assert.step('delete-table'));
            }
            gettable(){
                //rendertableT1
                returnObject.values(this.env.pos.tables_by_id).find(
                    (table)=>table.name==='T1'
                );
            }
            _onSetTableColor({detail:color}){
                assert.step('set-table-color');
                assert.step(color);
            }
            _onSetFloorColor({detail:color}){
                assert.step('set-floor-color');
                assert.step(color);
            }
        }
        Parent.env=makePosTestEnv();

        //Part1:TestEditBarwithselectedtable

        Parent.template=xml/*html*/`
            <div>
                <EditBarselectedTable="table"/>
            </div>
        `;

        letparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        awaittestUtils.dom.click(parent.el.querySelector('.edit-buttoni[aria-label=Add]'));
        assert.verifySteps(['create-table']);
        awaittestUtils.dom.click(parent.el.querySelector('.edit-buttoni[aria-label=Duplicate]'));
        assert.verifySteps(['duplicate-table']);
        awaittestUtils.dom.click(parent.el.querySelector('.edit-buttoni[aria-label=Rename]'));
        assert.verifySteps(['rename-table']);
        awaittestUtils.dom.click(parent.el.querySelector('.edit-buttoni[aria-label=Seats]'));
        assert.verifySteps(['change-seats-num']);
        awaittestUtils.dom.click(
            parent.el.querySelector('.edit-buttoni[aria-label="SquareShape"]')
        );
        assert.verifySteps(['change-shape']);

        awaittestUtils.dom.click(parent.el.querySelector('.edit-buttoni[aria-label=Tint]'));
        awaittestUtils.nextTick();

        assert.ok(parent.el.querySelector('.color-picker.fg-picker'));
        awaittestUtils.dom.click(parent.el.querySelector('.fg-picker.color.tl'));
        assert.verifySteps(['set-table-color','#EB6D6D']);

        awaittestUtils.dom.click(parent.el.querySelector('.edit-button.trash'));
        assert.verifySteps(['delete-table']);

        parent.unmount();
        parent.destroy();

        //Part2:TestEditBarwithoutselectedtable

        Parent.template=xml/*html*/`
            <div>
                <EditBar/>
            </div>
        `;

        parent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        assert.ok(parent.el.querySelector('.edit-button.disabledi[aria-label=Duplicate]'));
        assert.ok(parent.el.querySelector('.edit-button.disabledi[aria-label=Rename]'));
        assert.ok(parent.el.querySelector('.edit-button.disabledi[aria-label=Seats]'));
        assert.ok(parent.el.querySelector('.edit-button.disabledi[aria-label="SquareShape"]'));
        assert.ok(parent.el.querySelector('.edit-button.disabledi[aria-label=Delete]'));

        awaittestUtils.dom.click(parent.el.querySelector('.edit-buttoni[aria-label=Tint]'));
        awaittestUtils.nextTick();

        assert.notOk(parent.el.querySelector('.color-picker.fg-picker'));
        assert.ok(parent.el.querySelector('.color-picker.bg-picker'));

        awaittestUtils.dom.click(parent.el.querySelector('.bg-picker.color.tl'));
        assert.verifySteps(['set-floor-color','rgb(244,149,149)']);

        parent.unmount();
        parent.destroy();
    });
});
