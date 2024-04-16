flectra.define('stock.stock_traceability_report_backend_tests',function(require){
    "usestrict";

    constControlPanel=require('web.ControlPanel');
    constdom=require('web.dom');
    constStockReportGeneric=require('stock.stock_report_generic');
    consttestUtils=require('web.test_utils');

    const{createActionManager,dom:domUtils}=testUtils;

    /**
     *Helperfunctiontoinstantiateastockreportaction.
     *@param{Object}params
     *@param{Object}params.action
     *@param{boolean}[params.debug]
     *@returns{Promise<StockReportGeneric>}
     */
    asyncfunctioncreateStockReportAction(params){
        constparent=awaittestUtils.createParent(params);
        constreport=newStockReportGeneric(parent,params.action);
        consttarget=testUtils.prepareTarget(params.debug);

        const_destroy=report.destroy;
        report.destroy=function(){
            report.destroy=_destroy;
            parent.destroy();
        };
        constfragment=document.createDocumentFragment();
        awaitreport.appendTo(fragment);
        dom.prepend(target,fragment,{
            callbacks:[{widget:report}],
            in_DOM:true,
        });
        //WaitfortheReportWidgettobeappended
        awaittestUtils.nextTick();

        returnreport;
    }

    QUnit.module('Stock',{},function(){
        QUnit.module('Traceabilityreport');

        QUnit.test("Renderingwithnolines",asyncfunction(assert){
            assert.expect(1);

            consttemplate=`
                <divclass="container-fluido_stock_reports_pageo_stock_reports_no_print">
                    <divclass="o_stock_reports_tabletable-responsive">
                        <spanclass="text-center">
                            <h1>Nooperationmadeonthislot.</h1>
                        </span>
                    </div>
                </div>`;
            constreport=awaitcreateStockReportAction({
                action:{
                    context:{},
                    params:{},
                },
                data:{
                    'stock.traceability.report':{
                        fields:{},
                        get_html:()=>({html:template}),
                    },
                },
            });

            //HTMLcontentisnestedinadivinsideofthecontent
            assert.strictEqual(report.el.querySelector('.o_content>div').innerHTML,template,
                "Displayedtemplateshouldmatch");

            report.destroy();
        });

        QUnit.test("mountediscalledoncewhenreturningon'Stockreport'frombreadcrumb",asyncassert=>{
            //Thistestcanberemovedassoonaswedon'tmixlegacyandowllayersanymore.
            assert.expect(7);

            letmountCount=0;

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
                        name:"Stockreport",
                        tag:'stock_report_generic',
                        type:'ir.actions.client',
                        context:{},
                        params:{},
                    },
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
                    if(route==='/web/dataset/call_kw/stock.traceability.report/get_html'){
                        returnPromise.resolve({
                            html:'<aclass="o_stock_reports_web_action"href="#"data-active-id="1"data-res-model="partner">Gotoformview</a>',
                        });
                    }
                    returnthis._super.apply(this,arguments);
                },
                intercepts:{
                    do_action:ev=>actionManager.doAction(ev.data.action,ev.data.options),
                },
            });

            awaitactionManager.doAction(42);
            awaitdomUtils.click(actionManager.$('.o_stock_reports_web_action'));
            awaitdomUtils.click(actionManager.$('.breadcrumb-item:first'));
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
        });
    });
});
