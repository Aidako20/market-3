flectra.define('web.component_extension_tests',function(require){
    "usestrict";

    constmakeTestEnvironment=require("web.test_env");
    consttestUtils=require("web.test_utils");

    const{Component,tags}=owl;
    const{xml}=tags;
    const{useListener}=require('web.custom_hooks');

    QUnit.module("web",function(){
        QUnit.module("ComponentExtension");

        QUnit.test("ComponentdestroyedwhileperformingsuccessfulRPC",asyncfunction(assert){
            assert.expect(1);

            classParentextendsComponent{}
            Parent.env=makeTestEnvironment({},()=>Promise.resolve());
            Parent.template=xml`<div/>`;

            constparent=newParent();

            parent.rpc({}).then(()=>{thrownewError();});
            parent.destroy();

            awaittestUtils.nextTick();

            assert.ok(true,"Promiseshouldstillbepending");
        });

        QUnit.test("ComponentdestroyedwhileperformingfailedRPC",asyncfunction(assert){
            assert.expect(1);

            classParentextendsComponent{}
            Parent.env=makeTestEnvironment({},()=>Promise.reject());
            Parent.template=xml`<div/>`;

            constparent=newParent();

            parent.rpc({}).catch(()=>{thrownewError();});
            parent.destroy();

            awaittestUtils.nextTick();

            assert.ok(true,"Promiseshouldstillbepending");
        });

        QUnit.module("CustomHooks");

        QUnit.test("useListenerhandlertype",asyncfunction(assert){
            assert.expect(1);

            classParentextendsComponent{
                constructor(){
                    super();
                    useListener('custom1','_onCustom1');
                }
            }
            Parent.env=makeTestEnvironment({},()=>Promise.reject());
            Parent.template=xml`<div/>`;

            assert.throws(()=>newParent(null),'Thehandlermustbeafunction');
        });

        QUnit.test("useListenerininheritancesetting",asyncfunction(assert){
            assert.expect(12);
            constfixture=document.body.querySelector('#qunit-fixture');

            classParentextendsComponent{
                constructor(){
                    super();
                    useListener('custom1',this._onCustom1);
                    useListener('custom2',this._onCustom2);
                }
                _onCustom1(){
                    assert.step(`${this.constructor.name}custom1`);
                }
                _onCustom2(){
                    assert.step('parentcustom2');
                }
            }
            Parent.env=makeTestEnvironment({},()=>Promise.reject());
            Parent.template=xml`<div/>`;

            classChildextendsParent{
                constructor(){
                    super();
                    useListener('custom2',this._onCustom2);
                    useListener('custom3',this._onCustom3);
                }
                _onCustom2(){
                    assert.step('overridencustom2');
                }
                _onCustom3(){
                    assert.step('childcustom3');
                }
            }

            constparent=newParent(null);
            constchild=newChild(null);
            awaitparent.mount(fixture);
            awaitchild.mount(fixture);

            parent.trigger('custom1');
            assert.verifySteps(['Parentcustom1']);
            parent.trigger('custom2');
            assert.verifySteps(['parentcustom2']);
            parent.trigger('custom3');
            assert.verifySteps([]);

            child.trigger('custom1');
            assert.verifySteps(['Childcustom1']);
            //Therearetwohandlersforthatone(ParentandChild)
            //AlthoughthehandlerisoverrideninChild
            child.trigger('custom2');
            assert.verifySteps(['overridencustom2','overridencustom2']);
            child.trigger('custom3');
            assert.verifySteps(['childcustom3']);
            parent.destroy();
            child.destroy();
        });

        QUnit.test("useListenerwithnativeJSselector",asyncfunction(assert){
            assert.expect(3);
            constfixture=document.body.querySelector('#qunit-fixture');

            classParentextendsComponent{
                constructor(){
                    super();
                    useListener('custom1','div.custom-class',this._onCustom1);
                }
                _onCustom1(){
                    assert.step(`custom1`);
                }
            }
            Parent.env=makeTestEnvironment({},()=>Promise.reject());
            Parent.template=xml`
                <div>
                    <p>notrigger</p>
                    <h1class="custom-class">triggers</h1>
                </div>`;

            constparent=newParent(null);
            awaitparent.mount(fixture);

            parent.el.querySelector('p').dispatchEvent(newEvent('custom1',{bubbles:true}));
            assert.verifySteps([]);
            parent.el.querySelector('h1').dispatchEvent(newEvent('custom1',{bubbles:true}));
            assert.verifySteps(['custom1']);
            parent.destroy();
        });

        QUnit.test("useListenerwithnativeJSselectordelegation",asyncfunction(assert){
            assert.expect(3);
            constfixture=document.body.querySelector('#qunit-fixture');

            classParentextendsComponent{
                constructor(){
                    super();
                    useListener('custom1','.custom-class',this._onCustom1);
                }
                _onCustom1(){
                    assert.step(`custom1`);
                }
            }
            Parent.env=makeTestEnvironment({},()=>Promise.reject());
            Parent.template=xml`
                <div>
                    <p>notrigger</p>
                    <h1class="custom-class"><h2>triggers</h2></h1>
                </div>`;

            fixture.classList.add('custom-class');
            constparent=newParent(null);
            awaitparent.mount(fixture);

            parent.el.querySelector('p').dispatchEvent(newEvent('custom1',{bubbles:true}));
            assert.verifySteps([]);
            parent.el.querySelector('h2').dispatchEvent(newEvent('custom1',{bubbles:true}));
            assert.verifySteps(['custom1']);
            parent.destroy();
            fixture.classList.remove('custom-class');
        });

        QUnit.test("useListenerwithcaptureoption",asyncfunction(assert){
            assert.expect(7);
            constfixture=document.body.querySelector('#qunit-fixture');

            classLeafextendsComponent{
                constructor(){
                    super();
                    useListener('custom1',this._onCustom1);
                }
                _onCustom1(){
                    assert.step(`${this.constructor.name}custom1`);
                }
            }
            Leaf.template=xml`<divclass="leaf"/>`;

            classRootextendsComponent{
                constructor(){
                    super();
                    useListener('custom1',this._onCustom1,{capture:true});
                }
                _onCustom1(event){
                    assert.step(`${this.constructor.name}custom1`);
                    constdetail=event.detail;
                    if(detail&&detail.stopMe){
                        event.stopPropagation();
                    }
                }
            }
            Root.template=xml`<divclass="root"><Leaf/></div>`;
            Root.components={Leaf};

            constroot=newRoot(null);
            awaitroot.mount(fixture);

            constrootNode=document.body.querySelector('.root');
            constleafNode=document.body.querySelector('.leaf');
            rootNode.dispatchEvent(newCustomEvent('custom1',{
                bubbles:true,
                cancelable:true
            }));
            assert.verifySteps(['Rootcustom1']);

            //Dispatchcustom1ontheleafelement.
            //Sincewelisteninthecapturephase,Rootisfirsttriggered.
            //Theeventisstoppedthere.
            leafNode.dispatchEvent(newCustomEvent('custom1',{
                bubbles:true,
                cancelable:true,
                detail:{
                    stopMe:true
                },
            }));
            assert.verifySteps(['Rootcustom1']);

            //Sameasbefore,exceptthistimewedon'tstoptheevent
            leafNode.dispatchEvent(newCustomEvent('custom1',{
                bubbles:true,
                cancelable:true,
                detail:{
                    stopMe:false
                }
            }));
            assert.verifySteps(['Rootcustom1','Leafcustom1']);

            root.destroy();
        });
    });
});
