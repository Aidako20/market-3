flectra.define('website/static/tests/dashboard_tests',function(require){
"usestrict";

constControlPanel=require('web.ControlPanel');
constDashboard=require('website.backend.dashboard');
consttestUtils=require("web.test_utils");

const{createParent,nextTick,prepareTarget}=testUtils;

QUnit.module('WebsiteBackendDashboard',{
},function(){
    QUnit.test("mountediscalledonceforthedashboarrd'sControlPanel",asyncfunction(assert){
        //Thistestcanberemovedassoonaswedon'tmixlegacyandowllayersanymore.
        assert.expect(5);

        ControlPanel.patch('test.ControlPanel',T=>{
            classControlPanelPatchTestextendsT{
                mounted(){
                    assert.step('mounted');
                    super.mounted(...arguments);
                }
                willUnmount(){
                    assert.step('willUnmount');
                    super.mounted(...arguments);
                }
            }
            returnControlPanelPatchTest;
        });

        constparams={
            mockRPC:(route)=>{
                if(route==='/website/fetch_dashboard_data'){
                    returnPromise.resolve({
                        dashboards:{
                            visits:{},
                            sales:{summary:{}},
                        },
                        groups:{system:true,website_designer:true},
                        websites:[
                            {id:1,name:"MyWebsite",domain:"",selected:true},
                        ],
                    });
                }
                returnthis._super(...arguments);
            },
        };
        constparent=awaitcreateParent(params);
        constdashboard=newDashboard(parent,{});
        awaitdashboard.appendTo(document.createDocumentFragment());

        assert.verifySteps([]);

        dashboard.$el.appendTo(prepareTarget());
        dashboard.on_attach_callback();

        awaitnextTick();

        assert.verifySteps(['mounted']);

        dashboard.destroy();
        assert.verifySteps(['willUnmount']);

        ControlPanel.unpatch('test.ControlPanel');
    });
});

});
