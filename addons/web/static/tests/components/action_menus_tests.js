flectra.define('web.action_menus_tests',function(require){
    "usestrict";

    constActionMenus=require('web.ActionMenus');
    constRegistry=require('web.Registry');
    consttestUtils=require('web.test_utils');

    const{Component}=owl;
    constcpHelpers=testUtils.controlPanel;
    const{createComponent}=testUtils;

    QUnit.module('Components',{
        beforeEach(){
            this.action={
                res_model:'hobbit',
            };
            this.view={
                //neededbygoogle_drivemodule,makessensetogiveaviewanyway.
                type:'form',
            };
            this.props={
                activeIds:[23],
                context:{},
                items:{
                    action:[
                        {action:{id:1},name:"What'staters,precious?",id:1},
                    ],
                    print:[
                        {action:{id:2},name:"Po-ta-toes",id:2},
                    ],
                    other:[
                        {description:"Boil'em",callback(){}},
                        {description:"Mash'em",callback(){}},
                        {description:"Stick'eminastew",url:'#stew'},
                    ],
                },
            };
            //Patchtheregistryoftheactionmenus
            this.actionMenusRegistry=ActionMenus.registry;
            ActionMenus.registry=newRegistry();
        },
        afterEach(){
            ActionMenus.registry=this.actionMenusRegistry;
        },
    },function(){

        QUnit.module('ActionMenus');

        QUnit.test('basicinteractions',asyncfunction(assert){
            assert.expect(10);

            constactionMenus=awaitcreateComponent(ActionMenus,{
                env:{
                    action:this.action,
                    view:this.view,
                },
                props:this.props,
            });

            constdropdowns=actionMenus.el.getElementsByClassName('o_dropdown');
            assert.strictEqual(dropdowns.length,2,"ActionMenusshouldcontain2menus");
            assert.strictEqual(dropdowns[0].querySelector('.o_dropdown_title').innerText.trim(),"Print");
            assert.strictEqual(dropdowns[1].querySelector('.o_dropdown_title').innerText.trim(),"Action");
            assert.containsNone(actionMenus,'.o_dropdown_menu');

            awaitcpHelpers.toggleActionMenu(actionMenus,"Action");

            assert.containsOnce(actionMenus,'.o_dropdown_menu');
            assert.containsN(actionMenus,'.o_dropdown_menu.o_menu_item',4);
            constactionsTexts=[...dropdowns[1].querySelectorAll('.o_menu_item')].map(el=>el.innerText.trim());
            assert.deepEqual(actionsTexts,[
                "Boil'em",
                "Mash'em",
                "Stick'eminastew",
                "What'staters,precious?",
            ],"callbacksshouldappearbeforeactions");

            awaitcpHelpers.toggleActionMenu(actionMenus,"Print");

            assert.containsOnce(actionMenus,'.o_dropdown_menu');
            assert.containsN(actionMenus,'.o_dropdown_menu.o_menu_item',1);

            awaitcpHelpers.toggleActionMenu(actionMenus,"Print");

            assert.containsNone(actionMenus,'.o_dropdown_menu');

            actionMenus.destroy();
        });

        QUnit.test("emptyactionmenus",asyncfunction(assert){
            assert.expect(1);

            ActionMenus.registry.add("test",{Component,getProps:()=>false});
            this.props.items={};

            constactionMenus=awaitcreateComponent(ActionMenus,{
                env:{
                    action:this.action,
                    view:this.view,
                },
                props:this.props,
            });

            assert.containsNone(actionMenus,".o_cp_action_menus>*");

            actionMenus.destroy();
        });

        QUnit.test('executeaction',asyncfunction(assert){
            assert.expect(4);

            constactionMenus=awaitcreateComponent(ActionMenus,{
                env:{
                    action:this.action,
                    view:this.view,
                },
                props:this.props,
                intercepts:{
                    'do-action':ev=>assert.step('do-action'),
                },
                asyncmockRPC(route,args){
                    switch(route){
                        case'/web/action/load':
                            constexpectedContext={
                                active_id:23,
                                active_ids:[23],
                                active_model:'hobbit',
                            };
                            assert.deepEqual(args.context,expectedContext);
                            assert.step('load-action');
                            return{context:{},flags:{}};
                        default:
                            returnthis._super(...arguments);

                    }
                },
            });

            awaitcpHelpers.toggleActionMenu(actionMenus,"Action");
            awaitcpHelpers.toggleMenuItem(actionMenus,"What'staters,precious?");

            assert.verifySteps(['load-action','do-action']);

            actionMenus.destroy();
        });

        QUnit.test('executecallbackaction',asyncfunction(assert){
            assert.expect(2);

            constcallbackPromise=testUtils.makeTestPromise();
            this.props.items.other[0].callback=function(items){
                assert.strictEqual(items.length,1);
                assert.strictEqual(items[0].description,"Boil'em");
                callbackPromise.resolve();
            };

            constactionMenus=awaitcreateComponent(ActionMenus,{
                env:{
                    action:this.action,
                    view:this.view,
                },
                props:this.props,
                asyncmockRPC(route,args){
                    switch(route){
                        case'/web/action/load':
                            thrownewError("Noactionshouldbeloaded.");
                        default:
                            returnthis._super(...arguments);
                    }
                },
            });

            awaitcpHelpers.toggleActionMenu(actionMenus,"Action");
            awaitcpHelpers.toggleMenuItem(actionMenus,"Boil'em");

            awaitcallbackPromise;

            actionMenus.destroy();
        });

        QUnit.test('executeprintaction',asyncfunction(assert){
            assert.expect(4);

            constactionMenus=awaitcreateComponent(ActionMenus,{
                env:{
                    action:this.action,
                    view:this.view,
                },
                intercepts:{
                    'do-action':ev=>assert.step('do-action'),
                },
                props:this.props,
                asyncmockRPC(route,args){
                    switch(route){
                        case'/web/action/load':
                            constexpectedContext={
                                active_id:23,
                                active_ids:[23],
                                active_model:'hobbit',
                            };
                            assert.deepEqual(args.context,expectedContext);
                            assert.step('load-action');
                            return{context:{},flags:{}};
                        default:
                            returnthis._super(...arguments);

                    }
                },
            });

            awaitcpHelpers.toggleActionMenu(actionMenus,"Print");
            awaitcpHelpers.toggleMenuItem(actionMenus,"Po-ta-toes");

            assert.verifySteps(['load-action','do-action']);

            actionMenus.destroy();
        });

        QUnit.test('executeurlaction',asyncfunction(assert){
            assert.expect(2);

            constactionMenus=awaitcreateComponent(ActionMenus,{
                env:{
                    action:this.action,
                    services:{
                        navigate(url){
                            assert.step(url);
                        },
                    },
                    view:this.view,
                },
                props:this.props,
                asyncmockRPC(route,args){
                    switch(route){
                        case'/web/action/load':
                            thrownewError("Noactionshouldbeloaded.");
                        default:
                            returnthis._super(...arguments);
                    }
                },
            });

            awaitcpHelpers.toggleActionMenu(actionMenus,"Action");
            awaitcpHelpers.toggleMenuItem(actionMenus,"Stick'eminastew");

            assert.verifySteps(['#stew']);

            actionMenus.destroy();
        });
    });
});
