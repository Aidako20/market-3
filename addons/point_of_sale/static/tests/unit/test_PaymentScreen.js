flectra.define('point_of_sale.tests.PaymentScreen',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    const{useListener}=require('web.custom_hooks');
    consttestUtils=require('web.test_utils');
    constmakePosTestEnv=require('point_of_sale.test_env');
    const{xml}=owl.tags;
    const{useState}=owl;

    QUnit.module('unittestsforPaymentScreencomponents',{});

    QUnit.test('PaymentMethodButton',asyncfunction(assert){
        assert.expect(2);

        classParentextendsPosComponent{
            constructor(){
                super(...arguments);
                useListener('new-payment-line',this._newPaymentLine);
            }
            _newPaymentLine(){
                assert.step('new-payment-line');
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div>
                <PaymentMethodButtonpaymentMethod="{name:'Cash',id:1}"/>
            </div>
        `;

        constparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        constbutton=parent.el.querySelector('.paymentmethod');
        awaittestUtils.dom.click(button);
        assert.verifySteps(['new-payment-line']);

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('PSNumpadInputButton',asyncfunction(assert){
        assert.expect(15);

        classParentextendsPosComponent{
            constructor({value,text,changeClassTo}){
                super();
                this.state=useState({value,text,changeClassTo});
                useListener('input-from-numpad',this._inputFromNumpad);
            }
            _inputFromNumpad({detail:{key}}){
                assert.step(`${key}-input`);
            }
            setState(obj){
                Object.assign(this.state,obj);
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div>
                <PSNumpadInputButtonvalue="state.value"text="state.text"changeClassTo="state.changeClassTo"/>
            </div>
        `;

        letparent=newParent({value:'1'});
        awaitparent.mount(testUtils.prepareTarget());

        letbutton=parent.el.querySelector('button');
        assert.ok(button.textContent.includes('1'));
        assert.ok(button.classList.contains('number-char'));
        awaittestUtils.dom.click(button);
        awaittestUtils.nextTick();
        assert.verifySteps(['1-input']);

        parent.setState({value:'2',text:'Two'});
        awaittestUtils.nextTick();
        assert.ok(button.textContent.includes('Two'));
        awaittestUtils.dom.click(button);
        awaittestUtils.nextTick();
        assert.verifySteps(['2-input']);

        parent.setState({value:'+12',text:null,changeClassTo:'not-number-char'});
        awaittestUtils.nextTick();
        assert.ok(button.textContent.includes('+12'));
        assert.ok(button.classList.contains('not-number-char'));
        //classnumber-charshouldhavebeenreplaced
        assert.notOk(button.classList.contains('number-char'));
        awaittestUtils.dom.click(button);
        awaittestUtils.nextTick();
        assert.verifySteps(['+12-input']);

        parent.unmount();
        parent.destroy();

        //usingtheslotshouldignorevalueandtextpropsofthecomponent
        Parent.template=xml/*html*/`
            <div>
                <PSNumpadInputButtonvalue="state.value"text="state.text"changeClassTo="state.changeClassTo">
                    <span>UseSlot</span>
                </PSNumpadInputButton>
            </div>
        `;
        parent=newParent({value:'slotted',text:'Text'});
        awaitparent.mount(testUtils.prepareTarget());

        button=parent.el.querySelector('button');
        assert.ok(button.textContent.includes('UseSlot'));
        awaittestUtils.dom.click(button);
        awaittestUtils.nextTick();
        assert.verifySteps(['slotted-input']);

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('PaymentScreenPaymentLines',asyncfunction(assert){
        assert.expect(12);

        classParentextendsPosComponent{
            constructor(){
                super();
                useListener('delete-payment-line',this._onDeletePaymentLine);
                useListener('select-payment-line',this._onSelectPaymentLine);
            }
            getpaymentLines(){
                returnthis.order.get_paymentlines();
            }
            getorder(){
                returnthis.env.pos.get_order();
            }
            mounted(){
                this.order.paymentlines.on('change',this.render,this);
            }
            willUnmount(){
                this.order.paymentlines.off('change',null,this);
            }
            _onDeletePaymentLine(){
                assert.step('delete-click');
            }
            _onSelectPaymentLine(){
                assert.step('select-click');
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div>
                <PaymentScreenPaymentLinespaymentLines="paymentLines"/>
            </div>
        `;

        letparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        constorder=parent.env.pos.get_order();
        constcashPM={id:0,name:'Cash',is_cash_count:true,use_payment_terminal:false};
        constbankPM={id:0,name:'Bank',is_cash_count:false,use_payment_terminal:false};

        letpaymentline1=order.add_paymentline(cashPM);
        awaittestUtils.nextTick();

        letstatusContainer=parent.el.querySelector('.payment-status-container');
        letlinesEl=parent.el.querySelector('.paymentlines');
        assert.ok(linesEl,'paymentlinesareshown');
        letnewLine=linesEl.querySelector('.selected');
        assert.ok(newLine,'thenewlineisautomaticallyselected');

        letpaymentline2=order.add_paymentline(bankPM);
        awaittestUtils.nextTick();
        assert.notOk(
            linesEl.querySelector('.selected')===newLine,
            'thepreviouslyaddedpaymentlineshouldnotbeselectedanymore'
        );
        assert.ok(
            linesEl.querySelectorAll('.paymentline:not(.heading)').length===2,
            'thereshouldbetwopaymentlines'
        );

        letpaymentline3=order.add_paymentline(cashPM);
        awaittestUtils.nextTick();
        assert.ok(
            linesEl.querySelectorAll('.paymentline:not(.heading)').length===3,
            'thereshouldbethreepaymentlines'
        );
        assert.ok(
            linesEl.querySelectorAll('.paymentline.selected').length===1,
            'thereshouldonlybeoneselectedpaymentline'
        );

        awaittestUtils.dom.click(linesEl.querySelector('.paymentline.selected.delete-button'));
        awaittestUtils.nextTick();
        assert.verifySteps(['delete-click','select-click']);

        //clickthe2ndpaymentline
        awaittestUtils.dom.click(linesEl.querySelectorAll('.paymentline:not(.heading)')[1]);
        awaittestUtils.nextTick();
        assert.verifySteps(['select-click']);

        //removepaymentline3(theselected)
        order.remove_paymentline(paymentline3);
        awaittestUtils.nextTick();
        assert.notOk(
            linesEl.querySelector('.paymentline.selected'),
            'nomoreselectedpaymentline'
        );

        order.remove_paymentline(paymentline1);
        order.remove_paymentline(paymentline2);

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('PaymentScreenElectronicPayment',asyncfunction(assert){
        assert.expect(17);

        classSimulatedPaymentLineextendsBackbone.Model{
            constructor(){
                super();
                this.payment_status='pending';
                this.can_be_reversed=false;
            }
            canBeAdjusted(){
                returnfalse;
            }
            setPaymentStatus(status){
                this.payment_status=status;
                this.trigger('change');
            }
            toggleCanBeReversed(){
                this.can_be_reversed=!this.can_be_reversed;
                this.trigger('change');
            }
        }

        classParentextendsPosComponent{
            constructor(){
                super();
                this.line=newSimulatedPaymentLine();
                useListener('send-payment-request',()=>assert.step('send-payment-request'));
                useListener('send-force-done',()=>assert.step('send-force-done'));
                useListener('send-payment-cancel',()=>assert.step('send-payment-cancel'));
                useListener('send-payment-reverse',()=>assert.step('send-payment-reverse'));
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div>
                <PaymentScreenElectronicPaymentline="line"/>
            </div>
        `;

        letparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        assert.ok(parent.el.querySelector('.paymentline.send_payment_request'));
        awaittestUtils.dom.click(parent.el.querySelector('.paymentline.send_payment_request'));
        awaittestUtils.nextTick();
        assert.verifySteps(['send-payment-request']);

        parent.line.setPaymentStatus('retry');
        awaittestUtils.nextTick();
        awaittestUtils.dom.click(parent.el.querySelector('.paymentline.send_payment_request'));
        awaittestUtils.nextTick();
        assert.verifySteps(['send-payment-request']);

        parent.line.setPaymentStatus('force_done');
        awaittestUtils.nextTick();
        awaittestUtils.dom.click(parent.el.querySelector('.paymentline.send_force_done'));
        awaittestUtils.nextTick();
        assert.verifySteps(['send-force-done']);

        parent.line.setPaymentStatus('waitingCard');
        awaittestUtils.nextTick();
        awaittestUtils.dom.click(parent.el.querySelector('.paymentline.send_payment_cancel'));
        awaittestUtils.nextTick();
        assert.verifySteps(['send-payment-cancel']);

        parent.line.setPaymentStatus('waiting');
        awaittestUtils.nextTick();
        assert.ok(parent.el.querySelector('.paymentlinei.fa-spinner'));

        parent.line.setPaymentStatus('waitingCancel');
        awaittestUtils.nextTick();
        assert.ok(parent.el.querySelector('.paymentlinei.fa-spinner'));

        parent.line.setPaymentStatus('reversing');
        awaittestUtils.nextTick();
        assert.ok(parent.el.querySelector('.paymentlinei.fa-spinner'));

        parent.line.setPaymentStatus('done');
        awaittestUtils.nextTick();
        assert.notOk(parent.el.querySelector('.paymentline.send_payment_reversal'));

        parent.line.toggleCanBeReversed();
        awaittestUtils.nextTick();
        assert.ok(parent.el.querySelector('.paymentline.send_payment_reversal'));
        awaittestUtils.dom.click(parent.el.querySelector('.paymentline.send_payment_reversal'));
        awaittestUtils.nextTick();
        assert.verifySteps(['send-payment-reverse']);

        parent.line.setPaymentStatus('reversed');
        awaittestUtils.nextTick();
        assert.ok(parent.el.querySelector('.paymentline'));

        parent.unmount();
        parent.destroy();
    });
});
