flectra.define('web/static/tests/report/client_action_tests',function(require){
    "usestrict";

    constControlPanel=require('web.ControlPanel');
    constReportClientAction=require('report.client_action');
    consttestUtils=require("web.test_utils");

    const{createActionManager,dom,mock}=testUtils;

    QUnit.module('ClientActionReport',{},()=>{
        QUnit.test("mountediscalledoncewhenreturningon'ClientActionReport'frombreadcrumb",asyncassert=>{
            //Thistestcanberemovedassoonaswedon'tmixlegacyandowllayersanymore.
            assert.expect(7);

            letmountCount=0;

            //patchthereportclientactiontooverrideitsiframe'surlsothat
            //itdoesn'ttriggeranRPCwhenitisappendedtotheDOM(forthis
            //usecase,usingremoveSRCAttributedoesn'tworkastheRPCis
            //triggeredassoonastheiframeisintheDOM,evenifitssrc
            //attributeisremovedrightafter)
            mock.patch(ReportClientAction,{
                start:function(){
                    varself=this;
                    returnthis._super.apply(this,arguments).then(function(){
                        self._rpc({route:self.iframe.getAttribute('src')});
                        self.iframe.setAttribute('src','about:blank');
                    });
                }
            });

            ControlPanel.patch('test.ControlPanel',T=>{
                classControlPanelPatchTestextendsT{
                    mounted(){
                        mountCount=mountCount+1;
                        this.__uniqueId=mountCount;
                        assert.step(`mounted${this.__uniqueId}`);
                        super.mounted(...arguments);
                    }
                    willUnmount(){
                        assert.step(`willUnmount${this.__uniqueId}`);
                        super.mounted(...arguments);
                    }
                }
                returnControlPanelPatchTest;
            });
            constactionManager=awaitcreateActionManager({
                actions:[
                    {
                        id:42,
                        name:"ClientActionReport",
                        tag:'report.client_action',
                        type:'ir.actions.report',
                        report_type:'qweb-html',
                    },
                    {
                        id:43,
                        type:"ir.actions.act_window",
                        res_id:1,
                        res_model:"partner",
                        views:[
                            [false,"form"],
                        ],
                    }
                ],
                archs:{
                    'partner,false,form':'<form><fieldname="display_name"/></form>',
                    'partner,false,search':'<search></search>',
                },
                data:{
                    partner:{
                        fields:{
                            display_name:{string:"Displayedname",type:"char"},
                        },
                        records:[
                            {id:1,display_name:"GendaSwami"},
                        ],
                    },
                },
                mockRPC:function(route){
                    if(route==='/report/html/undefined?context=%7B%7D'){
                        returnPromise.resolve('<aaction="go_to_details">Gotodetailview</a>');
                    }
                    returnthis._super.apply(this,arguments);
                },
                intercepts:{
                    do_action:ev=>actionManager.doAction(ev.data.action,ev.data.options),
                },
            });

            awaitactionManager.doAction(42);
            //simulateanactionaswearenotabletoreproducearealdoActionusing'ClientActionReport'
            awaitactionManager.doAction(43);
            awaitdom.click(actionManager.$('.breadcrumb-item:first'));
            actionManager.destroy();

            assert.verifySteps([
                'mounted1',
                'willUnmount1',
                'mounted2',
                'willUnmount2',
                'mounted3',
                'willUnmount3',
            ]);

            ControlPanel.unpatch('test.ControlPanel');
            mock.unpatch(ReportClientAction);
        });
    });

});
