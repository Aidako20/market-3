flectra.define('point_of_sale.tests.ProductScreen',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');
    const{useListener}=require('web.custom_hooks');
    consttestUtils=require('web.test_utils');
    constmakePosTestEnv=require('point_of_sale.test_env');
    const{xml}=owl.tags;
    const{useState}=owl;

    QUnit.module('unittestsforProductScreencomponents',{});

    QUnit.test('ActionpadWidget',asyncfunction(assert){
        assert.expect(7);

        classParentextendsPosComponent{
            constructor(){
                super();
                useListener('click-customer',()=>assert.step('click-customer'));
                useListener('click-pay',()=>assert.step('click-pay'));
                this.state=useState({client:null});
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div>
                <ActionpadWidgetclient="state.client"/>
            </div>
        `;

        constparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        constsetCustomerButton=parent.el.querySelector('button.set-customer');
        constpayButton=parent.el.querySelector('button.pay');

        awaittestUtils.nextTick();
        assert.ok(setCustomerButton.innerText.includes('Customer'));

        //changetocustomerwithshortname
        parent.state.client={name:'Test'};
        awaittestUtils.nextTick();
        assert.ok(setCustomerButton.innerText.includes('Test'));

        //changetocustomerwithlongname
        parent.state.client={name:'ChangeCustomer'};
        awaittestUtils.nextTick();
        assert.ok(setCustomerButton.classList.contains('decentered'));

        parent.state.client=null;

        //clickset-customerbutton
        awaittestUtils.dom.click(setCustomerButton);
        awaittestUtils.nextTick();
        assert.verifySteps(['click-customer']);

        //clickpaybutton
        awaittestUtils.dom.click(payButton);
        awaittestUtils.nextTick();
        assert.verifySteps(['click-pay']);

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('NumpadWidget',asyncfunction(assert){
        assert.expect(25);

        classParentextendsPosComponent{
            constructor(){
                super(...arguments);
                useListener('set-numpad-mode',this.setNumpadMode);
                useListener('numpad-click-input',this.numpadClickInput);
                this.state=useState({mode:'quantity'});
            }
            setNumpadMode({detail:{mode}}){
                this.state.mode=mode;
                assert.step(mode);
            }
            numpadClickInput({detail:{key}}){
                assert.step(key);
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div><NumpadWidgetactiveMode="state.mode"></NumpadWidget></div>
        `;

        constpos=Parent.env.pos;
        //setthisoldvaluesbackaftertesting
        constold_config=pos.config;
        constold_cashier=pos.get('cashier');

        //setdummyvaluesinpos.configandpos.get('cashier')
        pos.config={
            restrict_price_control:false,
            manual_discount:true
        };
        pos.set('cashier',{role:'manager'});

        constparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        constmodeButtons=parent.el.querySelectorAll('.mode-button');
        letqtyButton,discButton,priceButton;
        for(letbuttonofmodeButtons){
            if(button.textContent.includes('Qty')){
                qtyButton=button;
            }
            if(button.textContent.includes('Disc')){
                discButton=button;
            }
            if(button.textContent.includes('Price')){
                priceButton=button;
            }
        }

        //initially,qtybuttonisactive
        assert.ok(qtyButton.classList.contains('selected-mode'));
        assert.ok(!discButton.classList.contains('selected-mode'));
        assert.ok(!priceButton.classList.contains('selected-mode'));

        awaittestUtils.dom.click(discButton);
        awaittestUtils.nextTick();
        assert.ok(!qtyButton.classList.contains('selected-mode'));
        assert.ok(discButton.classList.contains('selected-mode'));
        assert.ok(!priceButton.classList.contains('selected-mode'));
        assert.verifySteps(['discount']);

        awaittestUtils.dom.click(priceButton);
        awaittestUtils.nextTick();
        assert.ok(!qtyButton.classList.contains('selected-mode'));
        assert.ok(!discButton.classList.contains('selected-mode'));
        assert.ok(priceButton.classList.contains('selected-mode'));
        assert.verifySteps(['price']);

        constnumpadOne=[...parent.el.querySelectorAll('.number-char').values()].find((el)=>
            el.textContent.includes('1')
        );
        constnumpadMinus=parent.el.querySelector('.numpad-minus');
        constnumpadBackspace=parent.el.querySelector('.numpad-backspace');

        awaittestUtils.dom.click(numpadOne);
        awaittestUtils.nextTick();
        assert.verifySteps(['1']);

        awaittestUtils.dom.click(numpadMinus);
        awaittestUtils.nextTick();
        assert.verifySteps(['-']);

        awaittestUtils.dom.click(numpadBackspace);
        awaittestUtils.nextTick();
        assert.verifySteps(['Backspace']);

        awaittestUtils.dom.click(priceButton);
        awaittestUtils.nextTick();
        assert.verifySteps(['price']);

        //changetopricecontrolrestrictionandthecashierisnotmanager
        pos.config.restrict_price_control=true;
        pos.set('cashier',{role:'notmanager'});
        awaittestUtils.nextTick();

        assert.ok(priceButton.classList.contains('disabled-mode'));
        assert.ok(qtyButton.classList.contains('selected-mode'));
        //afterthecashierischanged,sinceitisnotamanager,
        //the'set-numpad-mode'istriggered,settingthemodeto
        //'quantity'.
        assert.verifySteps(['quantity']);

        //resetoldconfigandcashiervaluestopos
        pos.config=old_config;
        pos.set('cashier',old_cashier);

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('ProductsWidgetControlPanel',asyncfunction(assert){
        assert.expect(32);

        //Thistestincorporatesthefollowingcomponents:
        //CategoryBreadcrumb
        //CategoryButton
        //CategorySimpleButton
        //HomeCategoryBreadcrumb

        //Createdummycategorydata
        //
        //Root
        //  |Test1
        //  |  |Test2
        //  |  `Test3
        //  |      |Test5
        //  |      `Test6
        //  `Test4

        constrootCategory={id:0,name:'Root',parent:null};
        consttestCategory1={id:1,name:'Test1',parent:0};
        consttestCategory2={id:2,name:'Test2',parent:1};
        consttestCategory3={id:3,name:'Test3',parent:1};
        consttestCategory4={id:4,name:'Test4',parent:0};
        consttestCategory5={id:5,name:'Test5',parent:3};
        consttestCategory6={id:6,name:'Test6',parent:3};
        constcategories={
            0:rootCategory,
            1:testCategory1,
            2:testCategory2,
            3:testCategory3,
            4:testCategory4,
            5:testCategory5,
            6:testCategory6,
        };

        classParentextendsPosComponent{
            constructor(){
                super(...arguments);
                this.state=useState({selectedCategoryId:0});
                useListener('switch-category',this.switchCategory);
                useListener('update-search',this.updateSearch);
                useListener('clear-search',this.clearSearch);
            }
            getbreadcrumbs(){
                if(this.state.selectedCategoryId===0)return[];
                letcurrent=categories[this.state.selectedCategoryId];
                constres=[current];
                while(current.parent!=0){
                    consttoAdd=categories[current.parent];
                    res.push(toAdd);
                    current=toAdd;
                }
                returnres.reverse();
            }
            getsubcategories(){
                returnObject.values(categories).filter(
                    ({parent})=>parent==this.state.selectedCategoryId
                );
            }
            switchCategory({detail:id}){
                this.state.selectedCategoryId=id;
                assert.step(`${id}`);
            }
            updateSearch(event){
                assert.step(event.detail);
            }
            clearSearch(){
                assert.step('cleared');
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <divclass="pos">
                <divclass="search-bar-portal">
                    <ProductsWidgetControlPanelbreadcrumbs="breadcrumbs"subcategories="subcategories"/>
                </div>
            </div>
        `;

        constpos=Parent.env.pos;
        constold_config=pos.config;
        //setdummyconfig
        pos.config={iface_display_categ_images:false};

        constparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        //Thefollowingteststhebreadcrumbsandsubcategorybuttons

        //checkifHomeCategoryBreadcrumbisrendered
        assert.ok(
            parent.el.querySelector('.breadcrumb-home'),
            'Homecategoryshouldalwaysbethere'
        );
        letsubcategorySpans=[...parent.el.querySelectorAll('.category-simple-button')];
        assert.ok(subcategorySpans.length===2,'Thereshouldbe2subcategoriesforRoot.');
        assert.ok(subcategorySpans.find((span)=>span.textContent.includes('Test1')));
        assert.ok(subcategorySpans.find((span)=>span.textContent.includes('Test4')));

        //clickTest1
        lettest1Span=subcategorySpans.find((span)=>span.textContent.includes('Test1'));
        awaittestUtils.dom.click(test1Span);
        awaittestUtils.nextTick();
        assert.verifySteps(['1']);
        assert.ok(
            [...parent.el.querySelectorAll('.breadcrumb-button')][1].textContent.includes('Test1')
        );
        subcategorySpans=[...parent.el.querySelectorAll('.category-simple-button')];
        assert.ok(subcategorySpans.length===2,'Thereshouldbe2subcategoriesforRoot.');
        assert.ok(subcategorySpans.find((span)=>span.textContent.includes('Test2')));
        assert.ok(subcategorySpans.find((span)=>span.textContent.includes('Test3')));

        //clickTest2
        lettest2Span=subcategorySpans.find((span)=>span.textContent.includes('Test2'));
        awaittestUtils.dom.click(test2Span);
        awaittestUtils.nextTick();
        assert.verifySteps(['2']);
        subcategorySpans=[...parent.el.querySelectorAll('.category-simple-button')];
        assert.ok(subcategorySpans.length===0,'Test2shouldnothavesubcategories');

        //gobacktoTest1
        letbreadcrumb1=[...parent.el.querySelectorAll('.breadcrumb-button')].find((el)=>
            el.textContent.includes('Test1')
        );
        awaittestUtils.dom.click(breadcrumb1);
        awaittestUtils.nextTick();
        assert.verifySteps(['1']);

        //clickTest3
        subcategorySpans=[...parent.el.querySelectorAll('.category-simple-button')];
        lettest3Span=subcategorySpans.find((span)=>span.textContent.includes('Test3'));
        awaittestUtils.dom.click(test3Span);
        awaittestUtils.nextTick();
        assert.verifySteps(['3']);
        subcategorySpans=[...parent.el.querySelectorAll('.category-simple-button')];
        assert.ok(subcategorySpans.length===2);

        //clickTest6
        lettest6Span=subcategorySpans.find((span)=>span.textContent.includes('Test6'));
        awaittestUtils.dom.click(test6Span);
        awaittestUtils.nextTick();
        assert.verifySteps(['6']);
        letbreadcrumbButtons=[...parent.el.querySelectorAll('.breadcrumb-button')];
        assert.ok(breadcrumbButtons.length===4);

        //Nowchecksubcategorybuttonswithimages
        pos.config.iface_display_categ_images=true;

        letbreadcrumbHome=parent.el.querySelector('.breadcrumb-home');
        awaittestUtils.dom.click(breadcrumbHome);
        awaittestUtils.nextTick();
        assert.verifySteps(['0']);
        assert.ok(
            !parent.el.querySelector('.category-list').classList.contains('simple'),
            'Categorylistshouldnothavesimpleclass'
        );
        letcategoryButtons=[...parent.el.querySelectorAll('.category-button')];
        assert.ok(categoryButtons.length===2,'Thereshouldbe2subcategoriesforRoot');

        //Thefollowingteststhesearchbar

        constwait=(ms)=>{
            returnnewPromise((resolve)=>{
                setTimeout(resolve,ms);
            });
        };

        constinputEl=parent.el.querySelector('.search-boxinput');
        awaittestUtils.dom.triggerEvent(inputEl,'keyup',{key:'A'});
        //Triggeringkeyupeventdoesn'ttypethekeytotheinput
        //sowemanuallyassignthevalueoftheinput.
        inputEl.value='A';
        awaitwait(30);
        awaittestUtils.dom.triggerEvent(inputEl,'keyup',{key:'B'});
        inputEl.value='AB';
        awaitwait(30);
        awaittestUtils.dom.triggerEvent(inputEl,'keyup',{key:'C'});
        inputEl.value='ABC';
        awaitwait(110);
        //Onlyafterwaitingformorethan100msthatupdate-searchistriggered
        //becausethemethodisdebounced.
        assert.verifySteps(['ABC']);
        awaittestUtils.dom.triggerEvent(inputEl,'keyup',{key:'D'});
        inputEl.value='ABCD';
        awaitwait(110);
        assert.verifySteps(['ABCD']);

        //clearthesearchbar
        awaittestUtils.dom.click(parent.el.querySelector('.search-box.clear-icon'));
        awaittestUtils.nextTick();
        assert.verifySteps(['cleared']);
        assert.ok(inputEl.value==='','valueoftheinputelementshouldbeempty');

        pos.config=old_config;

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('ProductList,ProductItem',asyncfunction(assert){
        assert.expect(10);

        //patchimageUrlandpriceofProductItemcomponent
        constMockProductItemExt=(X)=>
            classextendsX{
                getimageUrl(){
                    return'data:,';
                }
                getprice(){
                    returnthis.props.product.price;
                }
            };

        constextension=Registries.Component.extend('ProductItem',MockProductItemExt);
        extension.compile();

        constdummyProducts=[
            {id:0,display_name:'Burger',price:'$10'},
            {id:1,display_name:'Water',price:'$2'},
            {id:2,display_name:'Chair',price:'$25'},
        ];

        classParentextendsPosComponent{
            constructor(){
                super(...arguments);
                this.state=useState({searchWord:'',products:dummyProducts});
                useListener('click-product',this._clickProduct);
            }
            _clickProduct({detail:product}){
                assert.step(product.display_name);
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div>
                <ProductListproducts="state.products"searchWord="state.searchWord"/>
            </div>
        `;

        constparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        //Checkifthereare3productslisted
        assert.strictEqual(
            parent.el.querySelectorAll('article.product').length,
            3,
            'Thereshouldbe3productslisted'
        );

        //Checkcontentsofproductitemandclick
        constproduct1el=parent.el.querySelector(
            'article.product[aria-labelledby="article_product_1"]'
        );
        assert.ok(product1el.querySelector('.product-imgimg[data-alt="Water"]'));
        assert.ok(product1el.querySelector('.product-img.price-tag').textContent.includes('$2'));
        awaittestUtils.dom.click(product1el);
        awaittestUtils.nextTick();
        assert.verifySteps(['Water']);

        //Removeoneproduct,checkifonlytwoislisted
        parent.state.products.splice(0,1);
        awaittestUtils.nextTick();
        assert.strictEqual(
            parent.el.querySelectorAll('article.product').length,
            2,
            'Thereshouldbe2productslistedafterremovingthefirstitem'
        );

        //Removeallproducts,checkifemptymessageisTherearenoproductsinthiscategory
        parent.state.products.splice(0,parent.state.products.length);
        awaittestUtils.nextTick();
        assert.strictEqual(
            parent.el.querySelectorAll('article.product').length,
            0,
            'Thereshouldbe0productslistedafterremovingeverything'
        );
        assert.ok(
            parent.el
                .querySelector('.product-list-emptyp')
                .textContent.includes('Therearenoproductsinthiscategory.')
        );

        //changethesearchWordto'something',checkifemptymessageisNoresultsfound
        parent.state.searchWord='something';
        awaittestUtils.nextTick();
        assert.ok(
            parent.el
                .querySelector('.product-list-emptyp')
                .textContent.includes('Noresultsfoundfor')
        );
        assert.ok(
            parent.el.querySelector('.product-list-emptypb').textContent.includes('something')
        );

        extension.remove();

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('Orderline',asyncfunction(assert){
        assert.expect(10);

        classParentextendsPosComponent{
            constructor(product){
                super();
                useListener('select-line',this._selectLine);
                useListener('edit-pack-lot-lines',this._editPackLotLines);
                this.order.add_product(product);
            }
            getorder(){
                returnthis.env.pos.get_order();
            }
            getline(){
                returnthis.env.pos.get_order().get_orderlines()[0];
            }
            _selectLine(){
                assert.step('select-line');
            }
            _editPackLotLines(){
                assert.step('edit-pack-lot-lines');
            }
            willUnmount(){
                this.order.remove_orderline(this.line);
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div>
                <Orderlineline="line"/>
            </div>
        `;

        const[chair1,chair2]=Parent.env.pos.db.search_product_in_category(0,'OfficeChair');
        //patchchair2tohavetracking
        chair2.tracking='serial';

        //1.Testorderlinewithoutloticon

        letparent=newParent(chair1);
        awaitparent.mount(testUtils.prepareTarget());

        letline=parent.el.querySelector('li.orderline');
        assert.ok(line);
        assert.notOk(line.querySelector('.line-lot-icon'),'thereshouldbenoloticon');
        awaittestUtils.dom.click(line);
        assert.verifySteps(['select-line']);

        parent.unmount();
        parent.destroy();

        //2.Testorderlinewithloticon

        parent=newParent(chair2);
        awaitparent.mount(testUtils.prepareTarget());

        line=parent.el.querySelector('li.orderline');
        constlotIcon=line.querySelector('.line-lot-icon');
        assert.ok(line);
        assert.ok(lotIcon,'thereshouldbeloticon');
        awaittestUtils.dom.click(line);
        assert.verifySteps(['select-line']);
        awaittestUtils.dom.click(lotIcon);
        assert.verifySteps(['edit-pack-lot-lines']);

        parent.unmount();
        parent.destroy();
    });

    QUnit.test('OrderWidget',asyncfunction(assert){
        assert.expect(8);

        //OrderWidgetisdependentonitsparent'srerendering
        classParentextendsPosComponent{
            mounted(){
                this.env.pos.on('change:selectedOrder',this.render,this);
            }
            willUnmount(){
                this.env.pos.off('change:selectedOrder',null,this);
            }
        }
        Parent.env=makePosTestEnv();
        Parent.template=xml/*html*/`
            <div>
                <OrderWidget/>
            </div>
        `;

        const[chair1,chair2]=Parent.env.pos.db.search_product_in_category(0,'OfficeChair');

        letparent=newParent();
        awaitparent.mount(testUtils.prepareTarget());

        //currentorderisempty
        assert.notOk(parent.el.querySelector('.summary'));
        assert.ok(parent.el.querySelector('.order-empty'));

        //addlinetothecurrentorder
        constorder1=parent.env.pos.get_order();
        order1.add_product(chair1);
        awaittestUtils.nextTick();
        assert.ok(parent.el.querySelector('.summary'));
        assert.notOk(parent.el.querySelector('.order-empty'));

        //selectedneworder,neworderisempty
        constorder2=parent.env.pos.add_new_order();
        awaittestUtils.nextTick();
        assert.notOk(parent.el.querySelector('.summary'));
        assert.ok(parent.el.querySelector('.order-empty'));

        //addlinetothecurrentorder
        order2.add_product(chair2);
        awaittestUtils.nextTick();
        assert.ok(parent.el.querySelector('.summary'));
        assert.notOk(parent.el.querySelector('.order-empty'));

        parent.env.pos.delete_current_order();
        parent.env.pos.delete_current_order();

        parent.unmount();
        parent.destroy();
    });
});
