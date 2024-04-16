flectra.define('web.widget_tests',function(require){
"usestrict";

varAjaxService=require('web.AjaxService');
varcore=require('web.core');
varDialog=require('web.Dialog');
varQWeb=require('web.QWeb');
varWidget=require('web.Widget');
vartestUtils=require('web.test_utils');

QUnit.module('core',{},function(){

    QUnit.module('Widget');

    QUnit.test('proxy(String)',function(assert){
        assert.expect(1);

        varW=Widget.extend({
            exec:function(){
                this.executed=true;
            }
        });
        varw=newW();
        varfn=w.proxy('exec');
        fn();
        assert.ok(w.executed,'shouldexecutethenamedmethodintherightcontext');
        w.destroy();
    });

    QUnit.test('proxy(String)(*args)',function(assert){
        assert.expect(2);

        varW=Widget.extend({
            exec:function(arg){
                this.executed=arg;
            }
        });
        varw=newW();
        varfn=w.proxy('exec');
        fn(42);
        assert.ok(w.executed,"shouldexecutethenamedmethodintherightcontext");
        assert.strictEqual(w.executed,42,"shouldbepassedtheproxy'sarguments");
        w.destroy();
    });

    QUnit.test('proxy(String),include',function(assert){
        assert.expect(1);

        //theproxyfunctionshouldhandlemethodsbeingchangedontheclass
        //andshouldalwaysproxy"byname",tothemostrecentone
        varW=Widget.extend({
            exec:function(){
                this.executed=1;
            }
        });
        varw=newW();
        varfn=w.proxy('exec');
        W.include({
            exec:function(){this.executed=2;}
        });

        fn();
        assert.strictEqual(w.executed,2,"shouldbelazilyresolved");
        w.destroy();
    });

    QUnit.test('proxy(Function)',function(assert){
        assert.expect(1);

        varw=new(Widget.extend({}))();

        varfn=w.proxy(function(){this.executed=true;});
        fn();
        assert.ok(w.executed,"shouldsetthefunction'scontext(likeFunction#bind)");
        w.destroy();
    });

    QUnit.test('proxy(Function)(*args)',function(assert){
        assert.expect(1);

        varw=new(Widget.extend({}))();

        varfn=w.proxy(function(arg){this.executed=arg;});
        fn(42);
        assert.strictEqual(w.executed,42,"shouldbepassedtheproxy'sarguments");
        w.destroy();
    });

    QUnit.test('renderElement,notemplate,default',function(assert){
        assert.expect(7);

        varwidget=new(Widget.extend({}))();

        assert.strictEqual(widget.$el,undefined,"shouldnothavearootelement");

        widget.renderElement();

        assert.ok(widget.$el,"shouldhavegeneratedarootelement");
        assert.strictEqual(widget.$el,widget.$el,"shouldprovide$elalias");
        assert.ok(widget.$el.is(widget.el),"shouldproviderawDOMalias");

        assert.strictEqual(widget.el.nodeName,'DIV',"shouldhavegeneratedthedefaultelement");
        assert.strictEqual(widget.el.attributes.length,0,"shouldnothavegeneratedanyattribute");
        assert.ok(_.isEmpty(widget.$el.html(),"shouldnothavegeneratedanycontent"));
        widget.destroy();
    });

    QUnit.test('notemplate,customtag',function(assert){
        assert.expect(1);


        varwidget=new(Widget.extend({
            tagName:'ul'
        }))();
        widget.renderElement();

        assert.strictEqual(widget.el.nodeName,'UL',"shouldhavegeneratedthecustomelementtag");
        widget.destroy();
    });

    QUnit.test('notemplate,@id',function(assert){
        assert.expect(3);

        varwidget=new(Widget.extend({
            id:'foo'
        }))();
        widget.renderElement();

        assert.strictEqual(widget.el.attributes.length,1,"shouldhaveoneattribute");
        assert.hasAttrValue(widget.$el,'id','foo',"shouldhavegeneratedtheidattribute");
        assert.strictEqual(widget.el.id,'foo',"shouldalsobeavailableviaproperty");
        widget.destroy();
    });

    QUnit.test('notemplate,@className',function(assert){
        assert.expect(2);

        varwidget=new(Widget.extend({
            className:'oe_some_class'
        }))();
        widget.renderElement();

        assert.strictEqual(widget.el.className,'oe_some_class',"shouldhavetherightproperty");
        assert.hasAttrValue(widget.$el,'class','oe_some_class',"shouldhavetherightattribute");
        widget.destroy();
    });

    QUnit.test('notemplate,bunchofattributes',function(assert){
        assert.expect(9);

        varwidget=new(Widget.extend({
            attributes:{
                'id':'some_id',
                'class':'some_class',
                'data-foo':'dataattribute',
                'clark':'gable',
                'spoiler'://don'treadthenextlineifyoucareaboutHarryPotter...
                        'snapekillsdumbledore'
            }
        }))();
        widget.renderElement();

        assert.strictEqual(widget.el.attributes.length,5,"shouldhaveallthespecifiedattributes");

        assert.strictEqual(widget.el.id,'some_id');
        assert.hasAttrValue(widget.$el,'id','some_id');

        assert.strictEqual(widget.el.className,'some_class');
        assert.hasAttrValue(widget.$el,'class','some_class');

        assert.hasAttrValue(widget.$el,'data-foo','dataattribute');
        assert.strictEqual(widget.$el.data('foo'),'dataattribute');

        assert.hasAttrValue(widget.$el,'clark','gable');
        assert.hasAttrValue(widget.$el,'spoiler','snapekillsdumbledore');
        widget.destroy();
    });

    QUnit.test('template',function(assert){
        assert.expect(3);

        core.qweb.add_template(
            '<no>'+
                '<tt-name="test.widget.template">'+
                    '<ol>'+
                        '<lit-foreach="5"t-as="counter"'+
                            't-attf-class="class-#{counter}">'+
                            '<input/>'+
                            '<tt-esc="counter"/>'+
                        '</li>'+
                    '</ol>'+
                '</t>'+
            '</no>'
        );

        varwidget=new(Widget.extend({
            template:'test.widget.template'
        }))();
        widget.renderElement();

        assert.strictEqual(widget.el.nodeName,'OL');
        assert.strictEqual(widget.$el.children().length,5);
        assert.strictEqual(widget.el.textContent,'01234');
        widget.destroy();
    });

    QUnit.test('repeated',asyncfunction(assert){
        assert.expect(4);
        var$fix=$("#qunit-fixture");

        core.qweb.add_template(
            '<no>'+
                '<tt-name="test.widget.template">'+
                    '<p><tt-esc="widget.value"/></p>'+
                '</t>'+
            '</no>'
        );
        varwidget=new(Widget.extend({
            template:'test.widget.template'
        }))();
        widget.value=42;

        awaitwidget.appendTo($fix)
            .then(function(){
                assert.strictEqual($fix.find('p').text(),'42',"DOMfixtureshouldcontaininitialvalue");
                assert.strictEqual(widget.$el.text(),'42',"shouldsetinitialvalue");
                widget.value=36;
                widget.renderElement();
                assert.strictEqual($fix.find('p').text(),'36',"DOMfixtureshouldusenewvalue");
                assert.strictEqual(widget.$el.text(),'36',"shouldsetnewvalue");
            });
        widget.destroy();
    });


    QUnit.module('Widgets,withQWeb',{
        beforeEach:function(){
            this.oldQWeb=core.qweb;
            core.qweb=newQWeb();
            core.qweb.add_template(
                '<no>'+
                    '<tt-name="test.widget.template">'+
                        '<ol>'+
                            '<lit-foreach="5"t-as="counter"'+
                                't-attf-class="class-#{counter}">'+
                                '<input/>'+
                                '<tt-esc="counter"/>'+
                            '</li>'+
                        '</ol>'+
                    '</t>'+
                '</no>'
            );
        },
        afterEach:function(){
            core.qweb=this.oldQWeb;
        },
    });

    QUnit.test('basic-alias',function(assert){
        assert.expect(1);


        varwidget=new(Widget.extend({
            template:'test.widget.template'
        }))();
        widget.renderElement();

        assert.ok(widget.$('li:eq(3)').is(widget.$el.find('li:eq(3)')),
            "shoulddothesamethingascallingfindonthewidgetroot");
        widget.destroy();
    });


    QUnit.test('delegate',asyncfunction(assert){
        assert.expect(5);

        vara=[];
        varwidget=new(Widget.extend({
            template:'test.widget.template',
            events:{
                'click':function(){
                    a[0]=true;
                    assert.strictEqual(this,widget,"shouldtriggereventsinwidget");
                },
                'clickli.class-3':'class3',
                'changeinput':function(){a[2]=true;}
            },
            class3:function(){a[1]=true;}
        }))();
        widget.renderElement();

        awaittestUtils.dom.click(widget.$el,{allowInvisible:true});
        awaittestUtils.dom.click(widget.$('li:eq(3)'),{allowInvisible:true});
        awaittestUtils.fields.editAndTrigger(widget.$('input:last'),'foo','change');

        for(vari=0;i<3;++i){
            assert.ok(a[i],"shouldpasstest"+i);
        }
        widget.destroy();
    });

    QUnit.test('undelegate',asyncfunction(assert){
        assert.expect(4);

        varclicked=false;
        varnewclicked=false;

        varwidget=new(Widget.extend({
            template:'test.widget.template',
            events:{'clickli':function(){clicked=true;}}
        }))();

        widget.renderElement();
        widget.$el.on('click','li',function(){newclicked=true;});

        awaittestUtils.dom.clickFirst(widget.$('li'),{allowInvisible:true});
        assert.ok(clicked,"shouldtriggerboundevents");
        assert.ok(newclicked,"shouldtriggerboundevents");

        clicked=newclicked=false;
        widget._undelegateEvents();
        awaittestUtils.dom.clickFirst(widget.$('li'),{allowInvisible:true});
        assert.ok(!clicked,"undelegateshouldunbindeventsdelegated");
        assert.ok(newclicked,"undelegateshouldonlyunbindeventsitcreated");
        widget.destroy();
    });

    QUnit.module('Widget,andasyncstuff');

    QUnit.test("alive(alive)",asyncfunction(assert){
        assert.expect(1);

        varwidget=new(Widget.extend({}));

        awaitwidget.start()
            .then(function(){returnwidget.alive(Promise.resolve());})
            .then(function(){assert.ok(true);});

        widget.destroy();
    });

    QUnit.test("alive(dead)",function(assert){
        assert.expect(1);
        varwidget=new(Widget.extend({}));

        returnnewPromise(function(resolve,reject){
            widget.start()
            .then(function(){
                //destroywidget
                widget.destroy();
                varpromise=Promise.resolve();
                //leavetimeforalive()todoitsstuff
                promise.then(function(){
                    returnPromise.resolve();
                }).then(function(){
                    assert.ok(true);
                    resolve();
                });
                //ensurethatwidget.alive()refusestoresolveorreject
                returnwidget.alive(promise);
            }).then(function(){
                reject();
                assert.ok(false,"alive()shouldnotterminatebydefault");
            }).catch(function(){
                reject();
                assert.ok(false,"alive()shouldnotterminatebydefault");
            });
        });
    });

    QUnit.test("alive(alive,true)",asyncfunction(assert){
        assert.expect(1);
        varwidget=new(Widget.extend({}));
        awaitwidget.start()
            .then(function(){returnwidget.alive(Promise.resolve(),true);})
            .then(function(){assert.ok(true);});
        widget.destroy();
    });

    QUnit.test("alive(dead,true)",function(assert){
        assert.expect(1);
        vardone=assert.async();

        varwidget=new(Widget.extend({}));

        widget.start()
        .then(function(){
            //destroywidget
            widget.destroy();
            returnwidget.alive(Promise.resolve(),true);
        }).then(function(){
            assert.ok(false,"alive(p,true)shouldfailitspromise");
            done();
        },function(){
            assert.ok(true,"alive(p,true)shouldfailitspromise");
            done();
        });
    });

    QUnit.test("calling_rpcondestroyedwidgets",asyncfunction(assert){
        assert.expect(3);

        vardef;
        varparent=newWidget();
        awaittestUtils.mock.addMockEnvironment(parent,{
            session:{
                rpc:function(){
                    def=testUtils.makeTestPromise();
                    def.abort=def.reject;
                    returndef;
                },
            },
            services:{
                ajax:AjaxService
            },
        });
        varwidget=newWidget(parent);

        widget._rpc({route:'/a/route'}).then(function(){
            assert.ok(true,"Theajaxcallshouldberesolve");
        });
        def.resolve();
        awaittestUtils.nextMicrotaskTick();
        def=null;

        widget._rpc({route:'/a/route'}).then(function(){
            throwError("Calling_rpconadestroyedwidgetshouldreturna"+
            "promisethatremainspendingforever");
        }).catch(function(){
            throwError("Calling_rpconadestroyedwidgetshouldreturna"+
            "promisethatremainspendingforever");
        });
        widget.destroy();
        def.resolve();
        awaittestUtils.nextMicrotaskTick();
        def=null;

        widget._rpc({route:'/a/route'}).then(function(){
            throwError("Calling_rpconadestroyedwidgetshouldreturna"+
                "promisethatremainspendingforever");
        }).catch(function(){
            throwError("Calling_rpconadestroyedwidgetshouldreturna"+
            "promisethatremainspendingforever");
        });
        assert.ok(!def,"trigger_upisnotperformedandthecallreturnsa"+
            "promisethatremainspendingforever");

        assert.ok(true,
            "thereshouldbenocrashwhencalling_rpconadestroyedwidget");
        parent.destroy();
    });

    QUnit.test("callingdo_hideonawidgetdestroyedbeforebeingrendered",asyncfunction(assert){
        assert.expect(1);

        constMyWidget=Widget.extend({
            willStart(){
                returnnewPromise(()=>{});
            }
        });

        constwidget=newMyWidget();
        widget.appendTo(document.createDocumentFragment());
        widget.destroy();

        //thosecallsshouldnotcrash
        widget.do_hide();
        widget.do_show();
        widget.do_toggle(true);

        assert.ok(true);
    });

    QUnit.test('startisnotcalledwhenwidgetisdestroyed',function(assert){
        assert.expect(0);
        const$fix=$("#qunit-fixture");

        //Note:willStartisalwaysasync
        constMyWidget=Widget.extend({
            start:function(){
                assert.ok(false,'Shouldnotcallstartmethod');
            },
        });

        constwidget=newMyWidget();
        widget.appendTo($fix);
        widget.destroy();

        constdivEl=document.createElement('div');
        $fix[0].appendChild(divEl);
        constwidget2=newMyWidget();
        widget2.attachTo(divEl);
        widget2.destroy();
    });

    QUnit.test("don'tdestroytwicewidget'schildren",function(assert){
        assert.expect(2);

        varparent=newWidget();
        varchild=new(Widget.extend({
            destroy:function(){
                assert.step('destroy');
            }
        }))(parent);

        parent.destroy();
        assert.verifySteps(['destroy'],"childshouldhavebeendetroyedonlyonce");
    });


    QUnit.module('Widgets,Dialog');

    QUnit.test("don'tclosedialogonbackdropclick",asyncfunction(assert){
        assert.expect(3);

        vardialog=newDialog(null);
        dialog.open();
        awaitdialog.opened();

        assert.strictEqual($('.modal.show').length,1,"adialogshouldhaveopened");
        var$backdrop=$('.modal-backdrop');
        assert.strictEqual($backdrop.length,1,"thedialogshouldhaveamodalbackdrop");
        testUtils.dom.click('.modal.show');//Clickonbackdropisinfactadirectclickonthe.modalelement
        assert.strictEqual($('.modal.show').length,1,"thedialogshouldstillbeopened");

        dialog.close();
    });
});

});
