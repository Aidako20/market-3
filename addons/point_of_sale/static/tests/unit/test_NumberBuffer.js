flectra.define('point_of_sale.tests.NumberBuffer',function(require){
    'usestrict';

    const{Component,useState}=owl;
    const{xml}=owl.tags;
    constNumberBuffer=require('point_of_sale.NumberBuffer');
    constmakeTestEnvironment=require('web.test_env');
    consttestUtils=require('web.test_utils');

    QUnit.module('unittestsforNumberBuffer',{
        before(){},
    });

    QUnit.test('simplefastinputswithcaptureinbetween',asyncfunction(assert){
        assert.expect(3);

        classRootextendsComponent{
            constructor(){
                super();
                this.state=useState({buffer:''});
                NumberBuffer.activate();
                NumberBuffer.use({
                    nonKeyboardInputEvent:'numpad-click-input',
                    state:this.state,
                });
            }
            resetBuffer(){
                NumberBuffer.capture();
                NumberBuffer.reset();
            }
        }
        Root.env=makeTestEnvironment();
        Root.template=xml/*html*/`
            <div>
                <p><tt-esc="state.buffer"/></p>
                <buttonclass="one"t-on-click="trigger('numpad-click-input',{key:'1'})">1</button>
                <buttonclass="two"t-on-click="trigger('numpad-click-input',{key:'2'})">2</button>
                <buttonclass="reset"t-on-click="resetBuffer">reset</button>
            </div>
        `;

        constroot=newRoot();
        awaitroot.mount(testUtils.prepareTarget());

        constoneButton=root.el.querySelector('button.one');
        consttwoButton=root.el.querySelector('button.two');
        constresetButton=root.el.querySelector('button.reset');
        constbufferEl=root.el.querySelector('p');

        testUtils.dom.click(oneButton);
        testUtils.dom.click(twoButton);
        awaittestUtils.nextTick();
        assert.strictEqual(bufferEl.textContent,'12');
        testUtils.dom.click(resetButton);
        awaittestUtils.nextTick();
        assert.strictEqual(bufferEl.textContent,'');
        testUtils.dom.click(twoButton);
        testUtils.dom.click(oneButton);
        awaittestUtils.nextTick();
        assert.strictEqual(bufferEl.textContent,'21');

        root.unmount();
        root.destroy();
    });
});
