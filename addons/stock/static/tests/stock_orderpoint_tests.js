flectra.define("stock.orderpoint_tests",function(require){
    "usestrict";

    const{createView,dom,nextTick}=require("web.test_utils");
    constStockOrderpointListView=require("stock.StockOrderpointListView");

    QUnit.module(
        "Views",
        {
            beforeEach:function(){
                this.data={
                    person:{
                        fields:{
                            name:{string:"Name",type:"char"},
                            age:{string:"Age",type:"integer"},
                            job:{string:"Profession",type:"char"},
                        },
                        records:[
                            {id:1,name:"DanielFortesque",age:32,job:"Soldier"},
                            {id:2,name:"SamuelOak",age:64,job:"Professor"},
                            {id:3,name:"LetoIIAtreides",age:128,job:"Emperor"},
                        ],
                    },
                };
            },
        },
        ()=>{
            QUnit.module("StockOrderpointListView");

            QUnit.test(
                "domainselection:ordershouldbecalledonallrecords",
                asyncfunction(assert){
                    assert.expect(1);

                    constview=awaitcreateView({
                        View:StockOrderpointListView,
                        model:"person",
                        data:this.data,
                        arch:`
                            <treejs_class="stock_orderpoint_list"limit="1">
                                <fieldname="name"/>
                            </tree>`,
                        mockRPC:function(route,{args,method,model}){
                            if(method==="action_replenish"){
                                assert.deepEqual(
                                    {args,model},
                                    {args:[[1,2,3]],model:"person"}
                                );
                                returnPromise.resolve({});
                            }
                            returnthis._super.apply(this,arguments);
                        },
                    });

                    awaitdom.click(view.$("thead.o_list_record_selectorinput"));
                    awaitdom.click(view.$(".o_list_selection_box.o_list_select_domain"));
                    awaitdom.click(view.$(".o_button_order"));
                    awaitnextTick();
                    view.destroy();
                }
            );

            QUnit.test(
                "domainselection:snoozeshouldbecalledonallrecords",
                asyncfunction(assert){
                    assert.expect(1);

                    constview=awaitcreateView({
                        View:StockOrderpointListView,
                        model:"person",
                        data:this.data,
                        arch:`
                            <treejs_class="stock_orderpoint_list"limit="1">
                                <fieldname="name"/>
                            </tree>`,
                        intercepts:{
                            do_action:function(event){
                                if(event.data.action==="stock.action_orderpoint_snooze"){
                                    assert.deepEqual(event.data.options.additional_context,{
                                        default_orderpoint_ids:[1,2,3],
                                    });
                                }
                            },
                        },
                    });

                    awaitdom.click(view.$("thead.o_list_record_selectorinput"));
                    awaitdom.click(view.$(".o_list_selection_box.o_list_select_domain"));
                    awaitdom.click(view.$(".o_button_snooze"));
                    awaitnextTick();
                    view.destroy();
                }
            );
        }
    );
});
