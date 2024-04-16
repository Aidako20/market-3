flectra.define('point_of_sale.tests.ChromeWidgets',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constPopupControllerMixin=require('point_of_sale.PopupControllerMixin');
    consttestUtils=require('web.test_utils');
    constmakePosTestEnv=require('point_of_sale.test_env');
    const{xml}=owl.tags;

    QUnit.module('unittestsforChromeWidgets',{});

    QUnit.test('CashierName',asyncfunction(assert){
        assert.expect(1);

        classParentextendsPosComponent{}
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div><CashierName></CashierName></div>
        `;
        Parent.env.pos.employee.name='TestEmployee';

        constparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        assert.strictEqual(parent.el.querySelector('span.username').innerText,'TestEmployee');

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('HeaderButton',asyncfunction(assert){
        assert.expect(1);

        classParentextendsPosComponent{}
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div><HeaderButton></HeaderButton></div>
        `;

        constparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        constheaderButton=parent.el.querySelector('.header-button');
        awaittestUtils.dom.click(headerButton);
        awaittestUtils.nextTick();
        assert.ok(headerButton.classList.contains('confirm'));

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('SyncNotification',asyncfunction(assert){
        assert.expect(5);

        classParentextendsPosComponent{}
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div>
                <SyncNotification></SyncNotification>
            </div>
        `;

        constpos=Parent.env.pos;
        pos.set('synch',{status:'connected',pending:false});

        constparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());
        assert.ok(parent.el.querySelector('i.fa').parentElement.classList.contains('js_connected'));

        pos.set('synch',{status:'connecting',pending:false});
        awaittestUtils.nextTick();
        assert.ok(parent.el.querySelector('i.fa').parentElement.classList.contains('js_connecting'));

        pos.set('synch',{status:'disconnected',pending:false});
        awaittestUtils.nextTick();
        assert.ok(parent.el.querySelector('i.fa').parentElement.classList.contains('js_disconnected'));

        pos.set('synch',{status:'error',pending:false});
        awaittestUtils.nextTick();
        assert.ok(parent.el.querySelector('i.fa').parentElement.classList.contains('js_error'));

        pos.set('synch',{status:'error',pending:10});
        awaittestUtils.nextTick();
        assert.ok(parent.el.querySelector('.js_msg').innerText.includes('10'));

        parent.unmount();
        parent.destroy();
    });
});
