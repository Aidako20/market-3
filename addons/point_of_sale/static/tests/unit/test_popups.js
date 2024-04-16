flectra.define('point_of_sale.test_popups',function(require){
    'usestrict';

    constRegistries=require('point_of_sale.Registries');
    consttestUtils=require('web.test_utils');
    constPosComponent=require('point_of_sale.PosComponent');
    constPopupControllerMixin=require('point_of_sale.PopupControllerMixin');
    constmakePosTestEnv=require('point_of_sale.test_env');
    const{xml}=owl.tags;

    QUnit.module('unittestsforPopups',{
        before(){
            classRootextendsPopupControllerMixin(PosComponent){
                statictemplate=xml`
                    <div>
                        <tt-if="popup.isShown"t-component="popup.component"t-props="popupProps"t-key="popup.name"/>
                    </div>
                `;
            }
            Root.env=makePosTestEnv();
            this.Root=Root;
            Registries.Component.freeze();
        },
    });

    QUnit.test('ConfirmPopup',asyncfunction(assert){
        assert.expect(6);

        constroot=newthis.Root();
        awaitroot.mount(testUtils.prepareTarget());

        letpromResponse,userResponse;

        //Step:showpopupandconfirm
        promResponse=root.showPopup('ConfirmPopup',{});
        awaittestUtils.nextTick();
        testUtils.dom.click(root.el.querySelector('.confirm'));
        awaittestUtils.nextTick();
        userResponse=awaitpromResponse;
        assert.strictEqual(userResponse.confirmed,true);

        //Step:showpopupthencancel
        promResponse=root.showPopup('ConfirmPopup',{});
        awaittestUtils.nextTick();
        testUtils.dom.click(root.el.querySelector('.cancel'));
        awaittestUtils.nextTick();
        userResponse=awaitpromResponse;
        assert.strictEqual(userResponse.confirmed,false);

        //Step:checktexts
        promResponse=root.showPopup('ConfirmPopup',{
            title:'Areyousure?',
            body:'Areyouhavingfun?',
            confirmText:'HellYeah!',
            cancelText:'Areyoukiddingme?',
        });
        awaittestUtils.nextTick();
        assert.strictEqual(root.el.querySelector('.title').innerText.trim(),'Areyousure?');
        assert.strictEqual(root.el.querySelector('.body').innerText.trim(),'Areyouhavingfun?');
        assert.strictEqual(root.el.querySelector('.confirm').innerText.trim(),'HellYeah!');
        assert.strictEqual(
            root.el.querySelector('.cancel').innerText.trim(),
            'Areyoukiddingme?'
        );

        root.unmount();
        root.destroy();
    });

    QUnit.test('NumberPopup',asyncfunction(assert){
        assert.expect(8);

        constroot=newthis.Root();
        awaitroot.mount(testUtils.prepareTarget());

        letpromResponse,userResponse;

        //Step:showNumberPopupandconfirmwithemptybuffer
        promResponse=root.showPopup('NumberPopup',{});
        awaittestUtils.nextTick();
        testUtils.dom.triggerEvent(root.el.querySelector('.confirm'),'mousedown');
        awaittestUtils.nextTick();
        userResponse=awaitpromResponse;
        assert.strictEqual(userResponse.confirmed,true);
        assert.strictEqual(userResponse.payload,"");

        //Step:showNumberPopupandcancel
        promResponse=root.showPopup('NumberPopup',{});
        awaittestUtils.nextTick();
        testUtils.dom.triggerEvent(root.el.querySelector('.cancel'),'mousedown');
        awaittestUtils.nextTick();
        userResponse=awaitpromResponse;
        assert.strictEqual(userResponse.confirmed,false);

        //Step:showNumberPopupandconfirmwithfilledbuffer,newtitle,newtext
        promResponse=root.showPopup('NumberPopup',{
            title:'Areyousure?',
            confirmText:'HellYeah!',
            cancelText:'Areyoukiddingme?',
        });
        awaittestUtils.nextTick();
        letnodes=Array.from(root.el.querySelectorAll('button'));
        testUtils.dom.triggerEvent(nodes.find(elem=>elem.innerHTML==="7"),'mousedown');
        awaittestUtils.nextTick();
        testUtils.dom.triggerEvent(nodes.find(elem=>elem.innerHTML==="+10"),'mousedown');
        awaittestUtils.nextTick();
        assert.strictEqual(root.el.querySelector('.title').innerText.trim(),'Areyousure?');
        assert.strictEqual(root.el.querySelector('.confirm').innerText.trim(),'HellYeah!');
        assert.strictEqual(root.el.querySelector('.cancel').innerText.trim(),'Areyoukiddingme?');
        testUtils.dom.triggerEvent(root.el.querySelector('.confirm'),'mousedown');
        awaittestUtils.nextTick();
        userResponse=awaitpromResponse;
        assert.strictEqual(userResponse.confirmed,true);
        assert.strictEqual(userResponse.payload,"17");

        root.unmount();
        root.destroy();
    });

    QUnit.test('EditListPopup',asyncfunction(assert){
        assert.expect(7);

        constroot=newthis.Root();
        awaitroot.mount(testUtils.prepareTarget());

        letpromResponse,userResponse;

        //Step:showpopupandconfirm
        promResponse=root.showPopup('EditListPopup',{});
        awaittestUtils.nextTick();
        testUtils.dom.click(root.el.querySelector('.confirm'));
        awaittestUtils.nextTick();
        userResponse=awaitpromResponse;
        assert.strictEqual(userResponse.confirmed,true);
        assert.strictEqual(JSON.stringify(userResponse.payload.newArray),JSON.stringify([]));

        //Step:showpopupandcancel
        promResponse=root.showPopup('EditListPopup',{});
        awaittestUtils.nextTick();
        testUtils.dom.click(root.el.querySelector('.cancel'));
        awaittestUtils.nextTick();
        userResponse=awaitpromResponse;
        assert.strictEqual(userResponse.confirmed,false);

        //Step:showpopupandconfirmwithadefaultarray
        letdefaultArray=["Banana","Cherry"];
        promResponse=root.showPopup('EditListPopup',{
                title:"Fruits",
                isSingleItem:false,
                array:defaultArray,
            });
        awaittestUtils.nextTick();
        testUtils.dom.click(root.el.querySelector('.confirm'));
        awaittestUtils.nextTick();
        userResponse=awaitpromResponse;

        assert.strictEqual(userResponse.confirmed,true);
        leti=0;
        defaultArray=defaultArray.map((item)=>Object.assign({},{_id:i++},{'text':item}));
        assert.strictEqual(JSON.stringify(userResponse.payload.newArray),JSON.stringify(defaultArray));

        //Step:showpopupandconfirmwithanewarray
        promResponse=root.showPopup('EditListPopup',{
                title:"Fruits",
                isSingleItem:false,
                array:["Banana","Cherry"],
            });
        awaittestUtils.nextTick();
        testUtils.dom.click(root.el.querySelector('.fa-trash-o'));
        awaittestUtils.nextTick();
        testUtils.dom.click(root.el.querySelector('.confirm'));
        awaittestUtils.nextTick();
        userResponse=awaitpromResponse;
        assert.strictEqual(userResponse.confirmed,true);
        assert.strictEqual(JSON.stringify(userResponse.payload.newArray),JSON.stringify([{_id:1,text:"Cherry"}]));

        root.unmount();
        root.destroy();
    });
});
