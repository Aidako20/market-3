flectra.define('web.OwlCompatibilityTests',function(require){
    "usestrict";

    const{ComponentAdapter,ComponentWrapper,WidgetAdapterMixin}=require('web.OwlCompatibility');
    consttestUtils=require('web.test_utils');
    constWidget=require('web.Widget');

    constmakeTestPromise=testUtils.makeTestPromise;
    constnextTick=testUtils.nextTick;
    constaddMockEnvironmentOwl=testUtils.mock.addMockEnvironmentOwl;

    const{Component,tags,useState}=owl;
    const{xml}=tags;

    //fromOwlinternalstatusenum
    constISMOUNTED=3;
    constISDESTROYED=5;

    constWidgetAdapter=Widget.extend(WidgetAdapterMixin,{
        destroy(){
            this._super(...arguments);
            WidgetAdapterMixin.destroy.call(this,...arguments);
        },
    });

    QUnit.module("OwlCompatibility",function(){
        QUnit.module("ComponentAdapter");

        QUnit.test("subwidgetwithnoargument",asyncfunction(assert){
            assert.expect(1);

            constMyWidget=Widget.extend({
                start:function(){
                    this.$el.text('HelloWorld!');
                }
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
            }
            Parent.template=xml`
                <div>
                    <ComponentAdapterComponent="MyWidget"/>
                </div>`;
            Parent.components={ComponentAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div>HelloWorld!</div>');

            parent.destroy();
        });

        QUnit.test("subwidgetwithoneargument",asyncfunction(assert){
            assert.expect(1);

            constMyWidget=Widget.extend({
                init:function(parent,name){
                    this._super.apply(this,arguments);
                    this.name=name;
                },
                start:function(){
                    this.$el.text(`Hello${this.name}!`);
                }
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
            }
            Parent.template=xml`
                <div>
                    <ComponentAdapterComponent="MyWidget"name="'World'"/>
                </div>`;
            Parent.components={ComponentAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div>HelloWorld!</div>');

            parent.destroy();
        });

        QUnit.test("subwidgetwithseveralarguments(commonAdapter)",asyncfunction(assert){
            assert.expect(1);

            constMyWidget=Widget.extend({
                init:function(parent,a1,a2){
                    this._super.apply(this,arguments);
                    this.a1=a1;
                    this.a2=a2;
                },
                start:function(){
                    this.$el.text(`${this.a1}${this.a2}!`);
                }
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
            }
            Parent.template=xml`
                <div>
                    <ComponentAdapterComponent="MyWidget"a1="'Hello'"a2="'World'"/>
                </div>`;
            Parent.components={ComponentAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            try{
                awaitparent.mount(target);
            }catch(e){
                assert.strictEqual(e.toString(),
                    `Error:ComponentAdapterhasmorethan1argument,'widgetArgs'mustbeoverriden.`);
            }

            parent.destroy();
        });

        QUnit.test("subwidgetwithseveralarguments(specificAdapter)",asyncfunction(assert){
            assert.expect(1);

            constMyWidget=Widget.extend({
                init:function(parent,a1,a2){
                    this._super.apply(this,arguments);
                    this.a1=a1;
                    this.a2=a2;
                },
                start:function(){
                    this.$el.text(`${this.a1}${this.a2}!`);
                }
            });
            classMyWidgetAdapterextendsComponentAdapter{
                getwidgetArgs(){
                    return[this.props.a1,this.props.a2];
                }
            }
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
            }
            Parent.template=xml`
                <div>
                    <MyWidgetAdapterComponent="MyWidget"a1="'Hello'"a2="'World'"/>
                </div>`;
            Parent.components={MyWidgetAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div>HelloWorld!</div>');

            parent.destroy();
        });

        QUnit.test("subwidgetandwidgetArgsprops",asyncfunction(assert){
            assert.expect(1);

            constMyWidget=Widget.extend({
                init:function(parent,a1,a2){
                    this._super.apply(this,arguments);
                    this.a1=a1;
                    this.a2=a2;
                },
                start:function(){
                    this.$el.text(`${this.a1}${this.a2}!`);
                }
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
            }
            Parent.template=xml`
                <div>
                    <ComponentAdapterComponent="MyWidget"a1="'Hello'"a2="'World'"widgetArgs="['Hello','World']"/>
                </div>`;
            Parent.components={ComponentAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div>HelloWorld!</div>');

            parent.destroy();
        });

        QUnit.test("subwidgetisupdatedwhenpropschange",asyncfunction(assert){
            assert.expect(2);

            constMyWidget=Widget.extend({
                init:function(parent,name){
                    this._super.apply(this,arguments);
                    this.name=name;
                },
                start:function(){
                    this.render();
                },
                render:function(){
                    this.$el.text(`Hello${this.name}!`);
                },
                update:function(name){
                    this.name=name;
                },
            });
            classMyWidgetAdapterextendsComponentAdapter{
                updateWidget(nextProps){
                    returnthis.widget.update(nextProps.name);
                }
                renderWidget(){
                    this.widget.render();
                }
            }
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                    this.state=useState({
                        name:"World",
                    });
                }
            }
            Parent.template=xml`
                <div>
                    <MyWidgetAdapterComponent="MyWidget"name="state.name"/>
                </div>`;
            Parent.components={MyWidgetAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div>HelloWorld!</div>');

            parent.state.name="GED";
            awaitnextTick();

            assert.strictEqual(parent.el.innerHTML,'<div>HelloGED!</div>');

            parent.destroy();
        });

        QUnit.test("subwidgetisupdatedwhenpropschange(async)",asyncfunction(assert){
            assert.expect(7);

            constprom=makeTestPromise();
            constMyWidget=Widget.extend({
                init:function(parent,name){
                    this._super.apply(this,arguments);
                    this.name=name;
                },
                start:function(){
                    this.render();
                },
                render:function(){
                    this.$el.text(`Hello${this.name}!`);
                    assert.step('render');
                },
                update:function(name){
                    assert.step('update');
                    this.name=name;
                },
            });
            classMyWidgetAdapterextendsComponentAdapter{
                updateWidget(nextProps){
                    returnthis.widget.update(nextProps.name);
                }
                renderWidget(){
                    this.widget.render();
                }
            }
            classAsyncComponentextendsComponent{
                willUpdateProps(){
                    returnprom;
                }
            }
            AsyncComponent.template=xml`<div>Hi<tt-esc="props.name"/>!</div>`;
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                    this.state=useState({
                        name:"World",
                    });
                }
            }
            Parent.template=xml`
                <div>
                    <AsyncComponentname="state.name"/>
                    <MyWidgetAdapterComponent="MyWidget"name="state.name"/>
                </div>`;
            Parent.components={AsyncComponent,MyWidgetAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div>HiWorld!</div><div>HelloWorld!</div>');

            parent.state.name="GED";
            awaitnextTick();

            assert.strictEqual(parent.el.innerHTML,'<div>HiWorld!</div><div>HelloWorld!</div>');

            prom.resolve();
            awaitnextTick();

            assert.strictEqual(parent.el.innerHTML,'<div>HiGED!</div><div>HelloGED!</div>');

            assert.verifySteps(['render','update','render']);

            parent.destroy();
        });

        QUnit.test("subwidgetmethodsarecorrectlycalled",asyncfunction(assert){
            assert.expect(8);

            constMyWidget=Widget.extend({
                on_attach_callback:function(){
                    assert.step('on_attach_callback');
                },
                on_detach_callback:function(){
                    assert.step('on_detach_callback');
                },
                destroy:function(){
                    assert.step('destroy');
                    this._super.apply(this,arguments);
                },
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
            }
            Parent.template=xml`
                <div>
                    <ComponentAdapterComponent="MyWidget"/>
                </div>`;
            Parent.components={ComponentAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.verifySteps(['on_attach_callback']);

            parent.unmount();
            awaitparent.mount(target);

            assert.verifySteps(['on_detach_callback','on_attach_callback']);

            parent.destroy();

            assert.verifySteps(['on_detach_callback','destroy']);
        });

        QUnit.test("dynamicsubwidget/component",asyncfunction(assert){
            assert.expect(1);

            constMyWidget=Widget.extend({
                start:function(){
                    this.$el.text('widget');
                },
            });
            classMyComponentextendsComponent{}
            MyComponent.template=xml`<div>component</div>`;
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.Children=[MyWidget,MyComponent];
                }
            }
            Parent.template=xml`
                <div>
                    <ComponentAdaptert-foreach="Children"t-as="Child"Component="Child"/>
                </div>`;
            Parent.components={ComponentAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div>widget</div><div>component</div>');

            parent.destroy();
        });

        QUnit.test("subwidgetthattriggersevents",asyncfunction(assert){
            assert.expect(5);

            letwidget;
            constMyWidget=Widget.extend({
                init:function(){
                    this._super.apply(this,arguments);
                    widget=this;
                },
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
                onSomeEvent(ev){
                    assert.step(ev.detail.value);
                    assert.ok(ev.detail.__targetWidgetinstanceofMyWidget);
                }
            }
            Parent.template=xml`
                <divt-on-some-event="onSomeEvent">
                    <ComponentAdapterComponent="MyWidget"/>
                </div>`;
            Parent.components={ComponentAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            widget.trigger_up('some-event',{value:'a'});
            widget.trigger_up('some_event',{value:'b'});//_areconvertedto-

            assert.verifySteps(['a','b']);

            parent.destroy();
        });

        QUnit.test("subwidgetthatcalls_rpc",asyncfunction(assert){
            assert.expect(3);

            constMyWidget=Widget.extend({
                willStart:function(){
                    returnthis._rpc({route:'some/route',params:{val:2}});
                },
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
            }
            Parent.template=xml`
                <div>
                    <ComponentAdapterComponent="MyWidget"/>
                </div>`;
            Parent.components={ComponentAdapter};
            constcleanUp=awaitaddMockEnvironmentOwl(Parent,{
                mockRPC:function(route,args){
                    assert.step(`${route}${args.val}`);
                    returnPromise.resolve();
                },
            });

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div></div>');
            assert.verifySteps(['some/route2']);

            parent.destroy();
            cleanUp();
        });

        QUnit.test("subwidgetthatcallsaservice",asyncfunction(assert){
            assert.expect(1);

            constMyWidget=Widget.extend({
                start:function(){
                    letresult;
                    this.trigger_up('call_service',{
                        service:'math',
                        method:'sqrt',
                        args:[9],
                        callback:r=>{
                            result=r;
                        },
                    });
                    assert.strictEqual(result,3);
                },
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
            }
            Parent.template=xml`
                <div>
                    <ComponentAdapterComponent="MyWidget"/>
                </div>`;
            Parent.components={ComponentAdapter};
            Parent.env.services.math={
                sqrt:v=>Math.sqrt(v),
            };

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            parent.destroy();
        });

        QUnit.test("subwidgetthatrequeststhesession",asyncfunction(assert){
            assert.expect(1);

            constMyWidget=Widget.extend({
                start:function(){
                    assert.strictEqual(this.getSession().key,'value');
                },
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
            }
            Parent.template=xml`
                <div>
                    <ComponentAdapterComponent="MyWidget"/>
                </div>`;
            Parent.components={ComponentAdapter};
            constcleanUp=awaitaddMockEnvironmentOwl(Parent,{
                session:{key:'value'},
            });

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            parent.destroy();
            cleanUp();
        });

        QUnit.test("subwidgetthatcallsload_views",asyncfunction(assert){
            assert.expect(4);

            constMyWidget=Widget.extend({
                willStart:function(){
                    returnthis.loadViews('some_model',{x:2},[[false,'list']]);
                },
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
            }
            Parent.template=xml`
                <div>
                    <ComponentAdapterComponent="MyWidget"/>
                </div>`;
            Parent.components={ComponentAdapter};
            constcleanUp=awaitaddMockEnvironmentOwl(Parent,{
                mockRPC:function(route,args){
                    assert.strictEqual(route,'/web/dataset/call_kw/some_model');
                    assert.deepEqual(args.kwargs.context,{x:2});
                    assert.deepEqual(args.kwargs.views,[[false,'list']]);
                    returnPromise.resolve();
                },
            });

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div></div>');

            parent.destroy();
            cleanUp();
        });

        QUnit.test("subwidgetsinat-if/t-else",asyncfunction(assert){
            assert.expect(3);

            constMyWidget1=Widget.extend({
                start:function(){
                    this.$el.text('Hi');
                },
            });
            constMyWidget2=Widget.extend({
                start:function(){
                    this.$el.text('Hello');
                },
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget1=MyWidget1;
                    this.MyWidget2=MyWidget2;
                    this.state=useState({
                        flag:true,
                    });
                }
            }
            Parent.template=xml`
                <div>
                    <ComponentAdaptert-if="state.flag"Component="MyWidget1"/>
                    <ComponentAdaptert-else=""Component="MyWidget2"/>
                </div>`;
            Parent.components={ComponentAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div>Hi</div>');

            parent.state.flag=false;
            awaitnextTick();

            assert.strictEqual(parent.el.innerHTML,'<div>Hello</div>');

            parent.state.flag=true;
            awaitnextTick();

            assert.strictEqual(parent.el.innerHTML,'<div>Hi</div>');

            parent.destroy();
        });

        QUnit.test("subwidgetinat-if,andevents",asyncfunction(assert){
            assert.expect(6);

            letmyWidget;
            constMyWidget=Widget.extend({
                start:function(){
                    myWidget=this;
                    this.$el.text('Hi');
                },
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                    this.state=useState({
                        flag:true,
                    });
                }
                onSomeEvent(ev){
                    assert.step(ev.detail.value);
                }
            }
            Parent.template=xml`
                <divt-on-some-event="onSomeEvent">
                    <ComponentAdaptert-if="state.flag"Component="MyWidget"/>
                </div>`;
            Parent.components={ComponentAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div>Hi</div>');
            myWidget.trigger_up('some-event',{value:'a'});

            parent.state.flag=false;
            awaitnextTick();

            assert.strictEqual(parent.el.innerHTML,'');
            myWidget.trigger_up('some-event',{value:'b'});

            parent.state.flag=true;
            awaitnextTick();

            assert.strictEqual(parent.el.innerHTML,'<div>Hi</div>');
            myWidget.trigger_up('some-event',{value:'c'});

            assert.verifySteps(['a','c']);

            parent.destroy();
        });

        QUnit.test("adapterkeepssameelassubwidget(modify)",asyncfunction(assert){
            assert.expect(7);

            letmyWidget;
            constMyWidget=Widget.extend({
                events:{
                    click:"_onClick",
                },
                init:function(parent,name){
                    myWidget=this;
                    this._super.apply(this,arguments);
                    this.name=name;
                },
                start:function(){
                    this.render();
                },
                render:function(){
                    this.$el.text("Clickme!");
                },
                update:function(name){
                    this.name=name;
                },
                _onClick:function(){
                    assert.step(this.name);
                },
            });
            classMyWidgetAdapterextendsComponentAdapter{
                updateWidget(nextProps){
                    returnthis.widget.update(nextProps.name);
                }
                renderWidget(){
                    this.widget.render();
                }
            }
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                    this.state=useState({
                        name:"GED",
                    });
                }
            }
            Parent.template=xml`
                <MyWidgetAdapterComponent="MyWidget"name="state.name"/>
            `;
            Parent.components={MyWidgetAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el,myWidget.el);
            awaittestUtils.dom.click(parent.el);

            parent.state.name="AAB";
            awaitnextTick();

            assert.strictEqual(parent.el,myWidget.el);
            awaittestUtils.dom.click(parent.el);

            parent.state.name="MCM";
            awaitnextTick();

            assert.strictEqual(parent.el,myWidget.el);
            awaittestUtils.dom.click(parent.el);

            assert.verifySteps(["GED","AAB","MCM"]);

            parent.destroy();
        });

        QUnit.test("adapterkeepssameelassubwidget(replace)",asyncfunction(assert){
            assert.expect(7);

            letmyWidget;
            constMyWidget=Widget.extend({
                events:{
                    click:"_onClick",
                },
                init:function(parent,name){
                    myWidget=this;
                    this._super.apply(this,arguments);
                    this.name=name;
                },
                start:function(){
                    this.render();
                },
                render:function(){
                    this._replaceElement("<div>Clickme!</div>");
                },
                update:function(name){
                    this.name=name;
                },
                _onClick:function(){
                    assert.step(this.name);
                },
            });
            classMyWidgetAdapterextendsComponentAdapter{
                updateWidget(nextProps){
                    returnthis.widget.update(nextProps.name);
                }
                renderWidget(){
                    this.widget.render();
                }
            }
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                    this.state=useState({
                        name:"GED",
                    });
                }
            }
            Parent.template=xml`
                <MyWidgetAdapterComponent="MyWidget"name="state.name"/>
            `;
            Parent.components={MyWidgetAdapter};

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el,myWidget.el);
            awaittestUtils.dom.click(parent.el);

            parent.state.name="AAB";
            awaitnextTick();

            assert.strictEqual(parent.el,myWidget.el);
            awaittestUtils.dom.click(parent.el);

            parent.state.name="MCM";
            awaitnextTick();

            assert.strictEqual(parent.el,myWidget.el);
            awaittestUtils.dom.click(parent.el);

            assert.verifySteps(["GED","AAB","MCM"]);

            parent.destroy();
        });

        QUnit.module('WidgetAdapterMixinandComponentWrapper');

        QUnit.test("widgetwithsubcomponent",asyncfunction(assert){
            assert.expect(1);

            classMyComponentextendsComponent{}
            MyComponent.template=xml`<div>Component</div>`;
            constMyWidget=WidgetAdapter.extend({
                start(){
                    constcomponent=newComponentWrapper(this,MyComponent,{});
                    returncomponent.mount(this.el);
                }
            });

            consttarget=testUtils.prepareTarget();
            constwidget=newMyWidget();
            awaitwidget.appendTo(target);

            assert.strictEqual(widget.el.innerHTML,'<div>Component</div>');

            widget.destroy();
        });

        QUnit.test("subcomponenthooksarecorrectlycalled",asyncfunction(assert){
            assert.expect(14);

            letcomponent;
            classMyComponentextendsComponent{
                constructor(parent){
                    super(parent);
                    assert.step("init");
                }
                asyncwillStart(){
                    assert.step("willStart");
                }
                mounted(){
                    assert.step("mounted");
                }
                willUnmount(){
                    assert.step("willUnmount");
                }
                __destroy(){
                    super.__destroy();
                    assert.step("__destroy");
                }
            }
            MyComponent.template=xml`<div>Component</div>`;
            constMyWidget=WidgetAdapter.extend({
                start(){
                    component=newComponentWrapper(this,MyComponent,{});
                    returncomponent.mount(this.el);
                }
            });

            consttarget=testUtils.prepareTarget();
            constwidget=newMyWidget();
            awaitwidget.appendTo(target);

            assert.verifySteps(['init','willStart','mounted']);
            assert.ok(component.__owl__.status===ISMOUNTED);

            widget.$el.detach();
            widget.on_detach_callback();

            assert.verifySteps(['willUnmount']);
            assert.ok(component.__owl__.status!==ISMOUNTED);

            widget.$el.appendTo(target);
            widget.on_attach_callback();

            assert.verifySteps(['mounted']);
            assert.ok(component.__owl__.status===ISMOUNTED);

            widget.destroy();

            assert.verifySteps(['willUnmount','__destroy']);
        });

        QUnit.test("isMountedwithseveralsubcomponents",asyncfunction(assert){
            assert.expect(9);

            letc1;
            letc2;
            classMyComponentextendsComponent{}
            MyComponent.template=xml`<div>Component<tt-esc="props.id"/></div>`;
            constMyWidget=WidgetAdapter.extend({
                start(){
                    c1=newComponentWrapper(this,MyComponent,{id:1});
                    c2=newComponentWrapper(this,MyComponent,{id:2});
                    returnPromise.all([c1.mount(this.el),c2.mount(this.el)]);
                }
            });

            consttarget=testUtils.prepareTarget();
            constwidget=newMyWidget();
            awaitwidget.appendTo(target);

            assert.strictEqual(widget.el.innerHTML,'<div>Component1</div><div>Component2</div>');
            assert.ok(c1.__owl__.status===ISMOUNTED);
            assert.ok(c2.__owl__.status===ISMOUNTED);

            widget.$el.detach();
            widget.on_detach_callback();

            assert.ok(c1.__owl__.status!==ISMOUNTED);
            assert.ok(c2.__owl__.status!==ISMOUNTED);

            widget.$el.appendTo(target);
            widget.on_attach_callback();

            assert.ok(c1.__owl__.status===ISMOUNTED);
            assert.ok(c2.__owl__.status===ISMOUNTED);

            widget.destroy();

            assert.ok(c1.__owl__.status===ISDESTROYED);
            assert.ok(c2.__owl__.status===ISDESTROYED);
        });

        QUnit.test("isMountedwithseverallevelsofsubcomponents",asyncfunction(assert){
            assert.expect(5);

            letchild;
            classMyChildComponentextendsComponent{
                constructor(){
                    super(...arguments);
                    child=this;
                }
            }
            MyChildComponent.template=xml`<div>child</div>`;
            classMyComponentextendsComponent{}
            MyComponent.template=xml`<div><MyChildComponent/></div>`;
            MyComponent.components={MyChildComponent};
            constMyWidget=WidgetAdapter.extend({
                start(){
                    letcomponent=newComponentWrapper(this,MyComponent,{});
                    returncomponent.mount(this.el);
                }
            });

            consttarget=testUtils.prepareTarget();
            constwidget=newMyWidget();
            awaitwidget.appendTo(target);

            assert.strictEqual(widget.el.innerHTML,'<div><div>child</div></div>');
            assert.ok(child.__owl__.status===ISMOUNTED);

            widget.$el.detach();
            widget.on_detach_callback();

            assert.ok(child.__owl__.status!==ISMOUNTED);

            widget.$el.appendTo(target);
            widget.on_attach_callback();

            assert.ok(child.__owl__.status===ISMOUNTED);

            widget.destroy();

            assert.ok(child.__owl__.status===ISDESTROYED);
        });

        QUnit.test("subcomponentcanbeupdated(inDOM)",asyncfunction(assert){
            assert.expect(2);

            classMyComponentextendsComponent{}
            MyComponent.template=xml`<div>Component<tt-esc="props.val"/></div>`;
            constMyWidget=WidgetAdapter.extend({
                start(){
                    this.component=newComponentWrapper(this,MyComponent,{val:1});
                    returnthis.component.mount(this.el);
                },
                update(){
                    returnthis.component.update({val:2});
                },
            });

            consttarget=testUtils.prepareTarget();
            constwidget=newMyWidget();
            awaitwidget.appendTo(target);

            assert.strictEqual(widget.el.innerHTML,'<div>Component1</div>');

            awaitwidget.update();

            assert.strictEqual(widget.el.innerHTML,'<div>Component2</div>');

            widget.destroy();
        });

        QUnit.test("subcomponentcanbeupdated(notinDOM)",asyncfunction(assert){
            assert.expect(4);

            classMyComponentextendsComponent{}
            MyComponent.template=xml`<div>Component<tt-esc="props.val"/></div>`;
            constMyWidget=WidgetAdapter.extend({
                start(){
                    this.component=newComponentWrapper(this,MyComponent,{val:1});
                    returnthis.component.mount(this.el);
                },
                update(){
                    returnthis.component.update({val:2});
                },
            });

            consttarget=testUtils.prepareTarget();
            constwidget=newMyWidget();
            awaitwidget.appendTo(target);

            assert.strictEqual(widget.el.innerHTML,'<div>Component1</div>');

            widget.$el.detach();
            widget.on_detach_callback();

            assert.ok(widget.component.__owl__.status!==ISMOUNTED);

            awaitwidget.update();

            widget.$el.appendTo(target);
            widget.on_attach_callback();

            assert.ok(widget.component.__owl__.status===ISMOUNTED);
            assert.strictEqual(widget.el.innerHTML,'<div>Component2</div>');

            widget.destroy();
        });

        QUnit.test("updateadestroyedsubcomponent",asyncfunction(assert){
            assert.expect(1);

            classMyComponentextendsComponent{}
            MyComponent.template=xml`<div>Component<tt-esc="props.val"/></div>`;
            constMyWidget=WidgetAdapter.extend({
                start(){
                    this.component=newComponentWrapper(this,MyComponent,{val:1});
                    returnthis.component.mount(this.el);
                },
                update(){
                    this.component.update({val:2});
                },
            });

            consttarget=testUtils.prepareTarget();
            constwidget=newMyWidget();
            awaitwidget.appendTo(target);

            assert.strictEqual(widget.el.innerHTML,'<div>Component1</div>');

            widget.destroy();

            widget.update();//shouldnotcrash
        });

        QUnit.test("subcomponentthattriggersevents",asyncfunction(assert){
            assert.expect(3);

            classWidgetComponentextendsComponent{}
            WidgetComponent.template=xml`<div>Component</div>`;

            constMyWidget=WidgetAdapter.extend({
                custom_events:_.extend({},Widget.custom_events,{
                    some_event:function(ev){
                        assert.step(ev.data.value);
                    }
                }),
                start(){
                    this.component=newComponentWrapper(this,WidgetComponent,{});
                    returnthis.component.mount(this.el);
                },
            });

            consttarget=testUtils.prepareTarget();
            constwidget=newMyWidget();
            awaitwidget.appendTo(target);

            widget.component.trigger('some_event',{value:'a'});
            widget.component.trigger('some-event',{value:'b'});//-areconvertedto_

            assert.verifySteps(['a','b']);

            widget.destroy();
        });

        QUnit.test("changeparentofComponentWrapper",asyncfunction(assert){
            assert.expect(7);

            letmyComponent;
            letwidget1;
            letwidget2;
            classWidgetComponentextendsComponent{}
            WidgetComponent.template=xml`<div>Component</div>`;
            constMyWidget=WidgetAdapter.extend({
                custom_events:_.extend({},Widget.custom_events,{
                    some_event:function(ev){
                        assert.strictEqual(this,ev.data.widget);
                        assert.step(ev.data.value);
                    }
                }),
            });
            constParent=Widget.extend({
                start(){
                    constproms=[];
                    myComponent=newComponentWrapper(null,WidgetComponent,{});
                    widget1=newMyWidget();
                    widget2=newMyWidget();
                    proms.push(myComponent.mount(this.el));
                    proms.push(widget1.appendTo(this.$el));
                    proms.push(widget2.appendTo(this.$el));
                    returnPromise.all(proms);
                }
            });

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.appendTo(target);

            //1.Noparent
            myComponent.trigger('some-event',{value:'a',widget:null});

            assert.verifySteps([]);

            //2.Noparent-->parent(widget1)
            myComponent.unmount();
            awaitmyComponent.mount(widget1.el);
            myComponent.setParent(widget1);

            myComponent.trigger('some-event',{value:'b',widget:widget1});

            assert.verifySteps(['b']);

            //3.Parent(widget1)-->newparent(widget2)
            myComponent.unmount();
            awaitmyComponent.mount(widget2.el);
            myComponent.setParent(widget2);

            myComponent.trigger('some-event',{value:'c',widget:widget2});

            assert.verifySteps(['c']);

            parent.destroy();
        });

        QUnit.module('SeverallayersoflegacywidgetsandOwlcomponents');

        QUnit.test("OwloverlegacyoverOwl",asyncfunction(assert){
            assert.expect(7);

            letleafComponent;
            classMyComponentextendsComponent{}
            MyComponent.template=xml`<span>Component</span>`;
            constMyWidget=WidgetAdapter.extend({
                custom_events:{
                    widget_event:function(ev){
                        assert.step(`[widget]widget-event${ev.data.value}`);
                    },
                    both_event:function(ev){
                        assert.step(`[widget]both-event${ev.data.value}`);
                        if(ev.data.value===4){
                            ev.stopPropagation();
                        }
                    }
                },
                start(){
                    leafComponent=newComponentWrapper(this,MyComponent,{});
                    returnleafComponent.mount(this.el);
                },
            });
            classParentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
                onRootEvent(ev){
                    assert.step(`[root]root-event${ev.detail.value}`);
                }
                onBothEvent(ev){
                    assert.step(`[root]both-event${ev.detail.value}`);
                }
            }
            Parent.template=xml`
                <divt-on-root-event="onRootEvent"t-on-both-event="onBothEvent">
                    <ComponentAdapterComponent="MyWidget"/>
                </div>`;
            Parent.components={ComponentAdapter};


            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.mount(target);

            assert.strictEqual(parent.el.innerHTML,'<div><span>Component</span></div>');

            leafComponent.trigger('root-event',{value:1});
            leafComponent.trigger('widget-event',{value:2});
            leafComponent.trigger('both-event',{value:3});
            leafComponent.trigger('both-event',{value:4});//willbestoppedbywidget

            assert.verifySteps([
                '[root]root-event1',
                '[widget]widget-event2',
                '[widget]both-event3',
                '[root]both-event3',
                '[widget]both-event4',
            ]);

            parent.destroy();
        });

        QUnit.test("LegacyoverOwloverlegacy",asyncfunction(assert){
            assert.expect(7);

            letleafWidget;
            constMyWidget=Widget.extend({
                start:function(){
                    leafWidget=this;
                    this.$el.text('Widget');
                }
            });
            classMyComponentextendsComponent{
                constructor(){
                    super(...arguments);
                    this.MyWidget=MyWidget;
                }
                onComponentEvent(ev){
                    assert.step(`[component]component-event${ev.detail.value}`);
                }
                onBothEvent(ev){
                    assert.step(`[component]both-event${ev.detail.value}`);
                    if(ev.detail.value===4){
                        ev.stopPropagation();
                    }
                }
            }
            MyComponent.template=xml`
                <spant-on-component-event="onComponentEvent"t-on-both-event="onBothEvent">
                    <ComponentAdapterComponent="MyWidget"/>
                </span>`;
            MyComponent.components={ComponentAdapter};
            constParent=WidgetAdapter.extend({
                custom_events:{
                    root_event:function(ev){
                        assert.step(`[root]root-event${ev.data.value}`);
                    },
                    both_event:function(ev){
                        assert.step(`[root]both-event${ev.data.value}`);
                    },
                },
                start(){
                    constcomponent=newComponentWrapper(this,MyComponent,{});
                    returncomponent.mount(this.el);
                }
            });

            consttarget=testUtils.prepareTarget();
            constparent=newParent();
            awaitparent.appendTo(target);

            assert.strictEqual(parent.el.innerHTML,'<span><div>Widget</div></span>');

            leafWidget.trigger_up('root-event',{value:1});
            leafWidget.trigger_up('component-event',{value:2});
            leafWidget.trigger_up('both-event',{value:3});
            leafWidget.trigger_up('both-event',{value:4});//willbestoppedbycomponent

            assert.verifySteps([
                '[root]root-event1',
                '[component]component-event2',
                '[component]both-event3',
                '[root]both-event3',
                '[component]both-event4',
            ]);

            parent.destroy();
        });
    });
});
