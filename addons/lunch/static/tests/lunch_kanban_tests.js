flectra.define('lunch.lunchKanbanTests',function(require){
"usestrict";

constLunchKanbanView=require('lunch.LunchKanbanView');

consttestUtils=require('web.test_utils');
const{createLunchView,mockLunchRPC}=require('lunch.test_utils');

QUnit.module('Views');

QUnit.module('LunchKanbanView',{
    beforeEach(){
        constPORTAL_GROUP_ID=1234;

        this.data={
            'product':{
                fields:{
                    is_available_at:{string:'ProductAvailability',type:'many2one',relation:'lunch.location'},
                    category_id:{string:'ProductCategory',type:'many2one',relation:'lunch.product.category'},
                    supplier_id:{string:'Vendor',type:'many2one',relation:'lunch.supplier'},
                },
                records:[
                    {id:1,name:'Tunasandwich',is_available_at:1},
                ],
            },
            'lunch.order':{
                fields:{},
                update_quantity(){
                    returnPromise.resolve();
                },
            },
            'lunch.product.category':{
                fields:{},
                records:[],
            },
            'lunch.supplier':{
                fields:{},
                records:[],
            },
            'ir.model.data':{
                fields:{},
                xmlid_to_res_id(){
                    returnPromise.resolve(PORTAL_GROUP_ID);
                },
            },
            'lunch.location':{
                fields:{
                    name:{string:'Name',type:'char'},
                },
                records:[
                    {id:1,name:"Office1"},
                    {id:2,name:"Office2"},
                ],
            },
            'res.users':{
                fields:{
                    name:{string:'Name',type:'char'},
                    groups_id:{string:'Groups',type:'many2many'},
                },
                records:[
                    {id:1,name:"MitchellAdmin",groups_id:[]},
                    {id:2,name:"MarcDemo",groups_id:[]},
                    {id:3,name:"Jean-LucPortal",groups_id:[PORTAL_GROUP_ID]},
                ],
            },
        };
        this.regularInfos={
            username:"MarcDemo",
            wallet:36.5,
            is_manager:false,
            currency:{
                symbol:"\u20ac",
                position:"after"
            },
            user_location:[2,"Office2"],
        };
        this.managerInfos={
            username:"MitchellAdmin",
            wallet:47.6,
            is_manager:true,
            currency:{
                symbol:"\u20ac",
                position:"after"
            },
            user_location:[2,"Office2"],
        };
    },
},function(){
    QUnit.test('basicrendering',asyncfunction(assert){
        assert.expect(7);

        constkanban=awaitcreateLunchView({
            View:LunchKanbanView,
            model:'product',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div><fieldname="name"/></div>
                        </t>
                    </templates>
                </kanban>
            `,
            mockRPC:mockLunchRPC({
                infos:this.regularInfos,
                userLocation:this.data['lunch.location'].records[0].id,
            }),
        });

        assert.containsOnce(kanban,'.o_kanban_view.o_kanban_record:not(.o_kanban_ghost)',
            "shouldhave1recordsintherenderer");

        //checkviewlayout
        assert.containsN(kanban,'.o_content>div',2,
            "shouldhave2columns");
        assert.containsOnce(kanban,'.o_content>div.o_search_panel',
            "shouldhavea'lunchfilters'column");
        assert.containsOnce(kanban,'.o_content>.o_lunch_content',
            "shouldhavea'lunchwrapper'column");
        assert.containsOnce(kanban,'.o_lunch_content>.o_kanban_view',
            "shouldhavea'classicalkanbanview'column");
        assert.hasClass(kanban.$('.o_kanban_view'),'o_lunch_kanban_view',
            "shouldhaveclassname'o_lunch_kanban_view'");
        assert.containsOnce(kanban,'.o_lunch_content>span>.o_lunch_banner',
            "shouldhavea'lunch'banner");

        kanban.destroy();
    });

    QUnit.test('noflickeringatreload',asyncfunction(assert){
        assert.expect(2);

        constself=this;
        letinfosProm=Promise.resolve();
        constkanban=awaitcreateLunchView({
            View:LunchKanbanView,
            model:'product',
            data:this.data,
            arch:`
                <kanban>
                    <templates>
                        <tt-name="kanban-box">
                            <div><fieldname="name"/></div>
                        </t>
                    </templates>
                </kanban>
            `,
            mockRPC:function(route,args){
                if(route==='/lunch/user_location_get'){
                    returnPromise.resolve(self.data['lunch.location'].records[0].id);
                }
                if(route==='/lunch/infos'){
                    returnPromise.resolve(self.regularInfos);
                }
                varresult=this._super.apply(this,arguments);
                if(args.method==='xmlid_to_res_id'){
                    //delaytherenderingofthelunchwidget
                    returninfosProm.then(_.constant(result));
                }
                returnresult;
            },
        });

        infosProm=testUtils.makeTestPromise();
        kanban.reload();

        assert.strictEqual(kanban.$('.o_lunch_widget').length,1,
            "oldwidgetshouldstillbepresent");

        awaitinfosProm.resolve();

        assert.strictEqual(kanban.$('.o_lunch_widget').length,1);

        kanban.destroy();
    });

    QUnit.module('LunchWidget',function(){

        QUnit.test('emptycart',asyncfunction(assert){
            assert.expect(3);

            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:mockLunchRPC({
                    infos:this.regularInfos,
                    userLocation:this.data['lunch.location'].records[0].id,
                }),
            });

            const$kanbanWidget=kanban.$('.o_lunch_widget');

            assert.containsN($kanbanWidget,'>.o_lunch_widget_info',3,
                "shouldhave3columns");
            assert.isVisible($kanbanWidget.find('>.o_lunch_widget_info:first'),
                "shouldhavethefirstcolumnvisible");
            assert.strictEqual($kanbanWidget.find('>.o_lunch_widget_info:not(:first)').html().trim(),"",
                "allcolumnsbutthefirstshouldbeempty");

            kanban.destroy();
        });

        QUnit.test('searchpaneldomainlocation',asyncfunction(assert){
            assert.expect(20);
            letexpectedLocation=1;
            letlocationId=this.data['lunch.location'].records[0].id;
            constregularInfos=_.extend({},this.regularInfos);

            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:function(route,args){
                    assert.step(route);

                    if(route.startsWith('/lunch')){
                        if(route==='/lunch/user_location_set'){
                            locationId=args.location_id;
                            returnPromise.resolve(true);
                        }
                        returnmockLunchRPC({
                            infos:regularInfos,
                            userLocation:locationId,
                        }).apply(this,arguments);
                    }
                    if(args.method==='search_panel_select_multi_range'){
                        assert.deepEqual(args.kwargs.search_domain,[["is_available_at","in",[expectedLocation]]],
                            'Theinitialdomainofthesearchpanelmustcontaintheuserlocation');
                    }
                    if(route==='/web/dataset/search_read'){
                        assert.deepEqual(args.domain,[["is_available_at","in",[expectedLocation]]],
                            'Thedomainforfetchingactualdatashouldbecorrect');
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            expectedLocation=2;
            awaittestUtils.fields.many2one.clickOpenDropdown('locations');
            awaittestUtils.fields.many2one.clickItem('locations',"Office2");

            assert.verifySteps([
                //Initialstate
                '/lunch/user_location_get',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/search_read',
                '/lunch/infos',
                '/web/dataset/call_kw/ir.model.data/xmlid_to_res_id',
                //Clickm2o
                '/web/dataset/call_kw/lunch.location/name_search',
                //Clicknewlocation
                '/lunch/user_location_set',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/search_read',
                '/lunch/infos',
                '/web/dataset/call_kw/ir.model.data/xmlid_to_res_id',
            ]);

            kanban.destroy();
        });

        QUnit.test('searchpaneldomainlocationfalse:fetchproductsinalllocations',asyncfunction(assert){
            assert.expect(10);
            constregularInfos=_.extend({},this.regularInfos);

            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:function(route,args){
                    assert.step(route);

                    if(route.startsWith('/lunch')){
                        returnmockLunchRPC({
                            infos:regularInfos,
                            userLocation:false,
                        }).apply(this,arguments);
                    }
                    if(args.method==='search_panel_select_multi_range'){
                        assert.deepEqual(args.kwargs.search_domain,[],
                            'Thedomainshouldnotexistsincethelocationisfalse.');
                    }
                    if(route==='/web/dataset/search_read'){
                        assert.deepEqual(args.domain,[],
                            'Thedomainforfetchingactualdatashouldbecorrect');
                    }
                    returnthis._super.apply(this,arguments);
                }
            });
            assert.verifySteps([
                '/lunch/user_location_get',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/call_kw/product/search_panel_select_multi_range',
                '/web/dataset/search_read',
                '/lunch/infos',
                '/web/dataset/call_kw/ir.model.data/xmlid_to_res_id',
            ])

            kanban.destroy();
        });

        QUnit.test('non-emptycart',asyncfunction(assert){
            assert.expect(17);

            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:mockLunchRPC({
                    infos:Object.assign({},this.regularInfos,{
                        total:"3.00",
                        lines:[
                            {
                                product:[1,"Tunasandwich","3.00"],
                                toppings:[],
                                quantity:1.0,
                            },
                        ],
                    }),
                    userLocation:this.data['lunch.location'].records[0].id,
                }),
            });

            const$kanbanWidget=kanban.$('.o_lunch_widget');

            assert.containsN($kanbanWidget,'>.o_lunch_widget_info',3,
                "shouldhave3columns");

            assert.containsOnce($kanbanWidget,'.o_lunch_widget_info:eq(1)',
                "shouldhaveasecondcolumn");

            const$widgetSecondColumn=$kanbanWidget.find('.o_lunch_widget_info:eq(1)');

            assert.containsOnce($widgetSecondColumn,'.o_lunch_widget_unlink',
                "shouldhaveabuttontocleartheorder");

            assert.containsOnce($widgetSecondColumn,'.o_lunch_widget_lines>li',
                "shouldhave1orderline");

            const$firstLine=$widgetSecondColumn.find('.o_lunch_widget_lines>li:first');
            assert.containsOnce($firstLine,'button.o_remove_product',
                "shouldhaveabuttontoremoveaproductquantityoneachline");
            assert.containsOnce($firstLine,'button.o_add_product',
                "shouldhaveabuttontoaddaproductquantityoneachline");
            assert.containsOnce($firstLine,'.o_lunch_product_quantity>:eq(1)',
                "shouldhavetheline'squantity");
            assert.strictEqual($firstLine.find('.o_lunch_product_quantity>:eq(1)').text().trim(),"1",
                "shouldhave1astheline'squantity");
            assert.containsOnce($firstLine,'.o_lunch_open_wizard',
                "shouldhavetheline'sproductnametoopenthewizard");
            assert.strictEqual($firstLine.find('.o_lunch_open_wizard').text().trim(),"Tunasandwich",
                "shouldhave'Tunasandwich'astheline'sproductname");
            assert.containsOnce($firstLine,'.o_field_monetary',
                "shouldhavetheline'samount");
            assert.strictEqual($firstLine.find('.o_field_monetary').text().trim(),"3.00€",
                "shouldhave'3.00€'astheline'samount");

            assert.containsOnce($kanbanWidget,'.o_lunch_widget_info:eq(2)',
                "shouldhaveathirdcolumn");

            const$widgetThirdColumn=kanban.$('.o_lunch_widget.o_lunch_widget_info:eq(2)');

            assert.containsOnce($widgetThirdColumn,'.o_field_monetary',
                "shouldhaveanaccountbalance");
            assert.strictEqual($widgetThirdColumn.find('.o_field_monetary').text().trim(),"3.00€",
                "shouldhave'3.00€'intheaccountbalance");
            assert.containsOnce($widgetThirdColumn,'.o_lunch_widget_order_button',
                "shouldhaveabuttontovalidatetheorder");
            assert.strictEqual($widgetThirdColumn.find('.o_lunch_widget_order_button').text().trim(),"Ordernow",
                "shouldhave'Ordernow'asthevalidateorderbuttontext");

            kanban.destroy();
        });

        QUnit.test('orderedcart',asyncfunction(assert){
            assert.expect(15);

            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:mockLunchRPC({
                    infos:Object.assign({},this.regularInfos,{
                        raw_state:"ordered",
                        state:"Ordered",
                        lines:[
                            {
                                product:[1,"Tunasandwich","3.00"],
                                toppings:[],
                                quantity:1.0,
                            },
                        ],
                    }),
                    userLocation:this.data['lunch.location'].records[0].id,
                }),
            });

            const$kanbanWidget=kanban.$('.o_lunch_widget');

            assert.containsN($kanbanWidget,'>.o_lunch_widget_info',3,
                "shouldhave3columns");

            assert.containsOnce($kanbanWidget,'.o_lunch_widget_info:eq(1)',
                "shouldhaveasecondcolumn");

            const$widgetSecondColumn=$kanbanWidget.find('.o_lunch_widget_info:eq(1)');

            assert.containsOnce($widgetSecondColumn,'.o_lunch_widget_unlink',
                "shouldhaveabuttontocleartheorder");
            assert.containsOnce($widgetSecondColumn,'.badge.badge-warning.o_lunch_ordered',
                "shouldhaveanorderedstatebadge");
            assert.strictEqual($widgetSecondColumn.find('.o_lunch_ordered').text().trim(),"Ordered",
                "shouldhave'Ordered'inthestatebadge");

            assert.containsOnce($widgetSecondColumn,'.o_lunch_widget_lines>li',
                "shouldhave1orderline");

            const$firstLine=$widgetSecondColumn.find('.o_lunch_widget_lines>li:first');
            assert.containsOnce($firstLine,'button.o_remove_product',
                "shouldhaveabuttontoremoveaproductquantityoneachline");
            assert.containsOnce($firstLine,'button.o_add_product',
                "shouldhaveabuttontoaddaproductquantityoneachline");
            assert.containsOnce($firstLine,'.o_lunch_product_quantity>:eq(1)',
                "shouldhavetheline'squantity");
            assert.strictEqual($firstLine.find('.o_lunch_product_quantity>:eq(1)').text().trim(),"1",
                "shouldhave1astheline'squantity");
            assert.containsOnce($firstLine,'.o_lunch_open_wizard',
                "shouldhavetheline'sproductnametoopenthewizard");
            assert.strictEqual($firstLine.find('.o_lunch_open_wizard').text().trim(),"Tunasandwich",
                "shouldhave'Tunasandwich'astheline'sproductname");
            assert.containsOnce($firstLine,'.o_field_monetary',
                "shouldhavetheline'samount");
            assert.strictEqual($firstLine.find('.o_field_monetary').text().trim(),"3.00€",
                "shouldhave'3.00€'astheline'samount");

            assert.strictEqual($kanbanWidget.find('>.o_lunch_widget_info:eq(2)').html().trim(),"",
                "thirdcolumnshouldbeempty");

            kanban.destroy();
        });

        QUnit.test('confirmedcart',asyncfunction(assert){
            assert.expect(15);

            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:mockLunchRPC({
                    infos:Object.assign({},this.regularInfos,{
                        raw_state:"confirmed",
                        state:"Received",
                        lines:[
                            {
                                product:[1,"Tunasandwich","3.00"],
                                toppings:[],
                                quantity:1.0,
                            },
                        ],
                    }),
                    userLocation:this.data['lunch.location'].records[0].id,
                }),
            });

            const$kanbanWidget=kanban.$('.o_lunch_widget');

            assert.containsN($kanbanWidget,'>.o_lunch_widget_info',3,
                "shouldhave3columns");

            assert.containsOnce($kanbanWidget,'.o_lunch_widget_info:eq(1)',
                "shouldhaveasecondcolumn");

            const$widgetSecondColumn=$kanbanWidget.find('.o_lunch_widget_info:eq(1)');

            assert.containsNone($widgetSecondColumn,'.o_lunch_widget_unlink',
                "shouldn'thaveabuttontocleartheorder");
            assert.containsOnce($widgetSecondColumn,'.badge.badge-success.o_lunch_confirmed',
                "shouldhaveaconfirmedstatebadge");
            assert.strictEqual($widgetSecondColumn.find('.o_lunch_confirmed').text().trim(),"Received",
                "shouldhave'Received'inthestatebadge");

            assert.containsOnce($widgetSecondColumn,'.o_lunch_widget_lines>li',
                "shouldhave1orderline");

            const$firstLine=$widgetSecondColumn.find('.o_lunch_widget_lines>li:first');
            assert.containsNone($firstLine,'button.o_remove_product',
                "shouldn'thaveabuttontoremoveaproductquantityoneachline");
            assert.containsNone($firstLine,'button.o_add_product',
                "shouldn'thaveabuttontoaddaproductquantityoneachline");
            assert.containsOnce($firstLine,'.o_lunch_product_quantity',
                "shouldhavetheline'squantity");
            assert.strictEqual($firstLine.find('.o_lunch_product_quantity').text().trim(),"1",
                "shouldhave1astheline'squantity");
            assert.containsOnce($firstLine,'.o_lunch_open_wizard',
                "shouldhavetheline'sproductnametoopenthewizard");
            assert.strictEqual($firstLine.find('.o_lunch_open_wizard').text().trim(),"Tunasandwich",
                "shouldhave'Tunasandwich'astheline'sproductname");
            assert.containsOnce($firstLine,'.o_field_monetary',
                "shouldhavetheline'samount");
            assert.strictEqual($firstLine.find('.o_field_monetary').text().trim(),"3.00€",
                "shouldhave'3.00€'astheline'samount");

            assert.strictEqual($kanbanWidget.find('>.o_lunch_widget_info:eq(2)').html().trim(),"",
                "thirdcolumnshouldbeempty");

            kanban.destroy();
        });

        QUnit.test('regularuser',asyncfunction(assert){
            assert.expect(11);

            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:mockLunchRPC({
                    infos:this.regularInfos,
                    userLocation:this.data['lunch.location'].records[0].id,
                }),
            });

            const$kanbanWidget=kanban.$('.o_lunch_widget');

            assert.containsOnce($kanbanWidget,'.o_lunch_widget_info:first',
                "shouldhaveafirstcolumn");

            const$widgetFirstColumn=$kanbanWidget.find('.o_lunch_widget_info:first');

            assert.containsOnce($widgetFirstColumn,'img.rounded-circle',
                "shouldhavearoundedavatarimage");

            assert.containsOnce($widgetFirstColumn,'.o_lunch_user_field',
                "shouldhaveauserfield");
            assert.containsNone($widgetFirstColumn,'.o_lunch_user_field>.o_field_widget',
                "shouldn'thaveafieldwidgetintheuserfield");
            assert.strictEqual($widgetFirstColumn.find('.o_lunch_user_field').text().trim(),"MarcDemo",
                "shouldhave'MarcDemo'intheuserfield");

            assert.containsOnce($widgetFirstColumn,'.o_lunch_location_field',
                "shouldhavealocationfield");
            assert.containsOnce($widgetFirstColumn,'.o_lunch_location_field>.o_field_many2one[name="locations"]',
                "shouldhaveamany2oneinthelocationfield");

            awaittestUtils.fields.many2one.clickOpenDropdown('locations');
            const$input=$widgetFirstColumn.find('.o_field_many2one[name="locations"]input');
            assert.containsN($input.autocomplete('widget'),'li',2,
                "autocompletedropdownshouldhave2entries");
            assert.strictEqual($input.val(),"Office2",
                "locationsinputshouldhave'Office2'asvalue");

            assert.containsOnce($widgetFirstColumn,'.o_lunch_location_field+div',
                "shouldhaveanaccountbalance");
            assert.strictEqual($widgetFirstColumn.find('.o_lunch_location_field+div.o_field_monetary').text().trim(),"36.50€",
                "shouldhave'36.50€'intheaccountbalance");

            kanban.destroy();
        });

        QUnit.test('manageruser',asyncfunction(assert){
            assert.expect(12);

            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:mockLunchRPC({
                    infos:this.managerInfos,
                    userLocation:this.data['lunch.location'].records[0].id,
                }),
            });

            const$kanbanWidget=kanban.$('.o_lunch_widget');

            assert.containsOnce($kanbanWidget,'.o_lunch_widget_info:first',
                "shouldhaveafirstcolumn");

            const$widgetFirstColumn=$kanbanWidget.find('.o_lunch_widget_info:first');

            assert.containsOnce($widgetFirstColumn,'img.rounded-circle',
                "shouldhavearoundedavatarimage");

            assert.containsOnce($widgetFirstColumn,'.o_lunch_user_field',
                "shouldhaveauserfield");
            assert.containsOnce($widgetFirstColumn,'.o_lunch_user_field>.o_field_many2one[name="users"]',
                "shouldn'thaveafieldwidgetintheuserfield");

            awaittestUtils.fields.many2one.clickOpenDropdown('users');
            const$userInput=$widgetFirstColumn.find('.o_field_many2one[name="users"]input');
            assert.containsN($userInput.autocomplete('widget'),'li',2,
                "usersautocompletedropdownshouldhave2entries");
            assert.strictEqual($userInput.val(),"MitchellAdmin",
                "shouldhave'MitchellAdmin'asvalueinuserfield");

            assert.containsOnce($widgetFirstColumn,'.o_lunch_location_field',
                "shouldhavealocationfield");
            assert.containsOnce($widgetFirstColumn,'.o_lunch_location_field>.o_field_many2one[name="locations"]',
                "shouldhaveamany2oneinthelocationfield");

            awaittestUtils.fields.many2one.clickOpenDropdown('locations');
            const$locationInput=$widgetFirstColumn.find('.o_field_many2one[name="locations"]input');
            assert.containsN($locationInput.autocomplete('widget'),'li',2,
                "locationsautocompletedropdownshouldhave2entries");
            assert.strictEqual($locationInput.val(),"Office2",
                "shouldhave'Office2'asvalue");

            assert.containsOnce($widgetFirstColumn,'.o_lunch_location_field+div',
                "shouldhaveanaccountbalance");
                assert.strictEqual($widgetFirstColumn.find('.o_lunch_location_field+div.o_field_monetary').text().trim(),"47.60€",
                    "shouldhave'47.60€'intheaccountbalance");

            kanban.destroy();
        });

        QUnit.test('addaproduct',asyncfunction(assert){
            assert.expect(1);

            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:mockLunchRPC({
                    infos:this.regularInfos,
                    userLocation:this.data['lunch.location'].records[0].id,
                }),
                intercepts:{
                    do_action:function(ev){
                        assert.deepEqual(ev.data.action,{
                            name:"ConfigureYourOrder",
                            res_model:'lunch.order',
                            type:'ir.actions.act_window',
                            views:[[false,'form']],
                            target:'new',
                            context:{
                                default_product_id:1,
                            },
                        },
                        "shouldopenthewizard");
                    },
                },
            });

            awaittestUtils.dom.click(kanban.$('.o_kanban_record:first'));

            kanban.destroy();
        });

        QUnit.test('addproductquantity',asyncfunction(assert){
            assert.expect(3);

            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:Object.assign({},this.data,{
                    'lunch.order':{
                        fields:{},
                        update_quantity([lineIds,increment]){
                            assert.deepEqual(lineIds,[6],"shouldhave[6]aslineIdtoupdatequantity");
                            assert.strictEqual(increment,1,"shouldhave+1asincrementtoupdatequantity");
                            returnPromise.resolve();
                        },
                    },
                }),
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:mockLunchRPC({
                    infos:Object.assign({},this.regularInfos,{
                        lines:[
                            {
                                id:6,
                                product:[1,"Tunasandwich","3.00"],
                                toppings:[],
                                quantity:1.0,
                            },
                        ],
                    }),
                    userLocation:this.data['lunch.location'].records[0].id,
                }),
            });

            const$widgetSecondColumn=kanban.$('.o_lunch_widget.o_lunch_widget_info:eq(1)');

            assert.containsOnce($widgetSecondColumn,'.o_lunch_widget_lines>li',
                "shouldhave1orderline");

            const$firstLine=$widgetSecondColumn.find('.o_lunch_widget_lines>li:first');

            awaittestUtils.dom.click($firstLine.find('button.o_add_product'));

            kanban.destroy();
        });

        QUnit.test('removeproductquantity',asyncfunction(assert){
            assert.expect(3);

            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:Object.assign({},this.data,{
                    'lunch.order':{
                        fields:{},
                        update_quantity([lineIds,increment]){
                            assert.deepEqual(lineIds,[6],"shouldhave[6]aslineIdtoupdatequantity");
                            assert.strictEqual(increment,-1,"shouldhave-1asincrementtoupdatequantity");
                            returnPromise.resolve();
                        },
                    },
                }),
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:mockLunchRPC({
                    infos:Object.assign({},this.regularInfos,{
                        lines:[
                            {
                                id:6,
                                product:[1,"Tunasandwich","3.00"],
                                toppings:[],
                                quantity:1.0,
                            },
                        ],
                    }),
                    userLocation:this.data['lunch.location'].records[0].id,
                }),
            });

            const$widgetSecondColumn=kanban.$('.o_lunch_widget.o_lunch_widget_info:eq(1)');

            assert.containsOnce($widgetSecondColumn,'.o_lunch_widget_lines>li',
                "shouldhave1orderline");

            const$firstLine=$widgetSecondColumn.find('.o_lunch_widget_lines>li:first');

            awaittestUtils.dom.click($firstLine.find('button.o_remove_product'));

            kanban.destroy();
        });

        QUnit.test('clearorder',asyncfunction(assert){
            assert.expect(1);

            constself=this;
            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:function(route){
                    if(route.startsWith('/lunch')){
                        if(route==='/lunch/trash'){
                            assert.ok('shouldperformclearorderRPCcall');
                            returnPromise.resolve();
                        }
                        returnmockLunchRPC({
                            infos:Object.assign({},self.regularInfos,{
                                lines:[
                                    {
                                        product:[1,"Tunasandwich","3.00"],
                                        toppings:[],
                                    },
                                ],
                            }),
                            userLocation:self.data['lunch.location'].records[0].id,
                        }).apply(this,arguments);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            const$widgetSecondColumn=kanban.$('.o_lunch_widget.o_lunch_widget_info:eq(1)');

            awaittestUtils.dom.click($widgetSecondColumn.find('button.o_lunch_widget_unlink'));

            kanban.destroy();
        });

        QUnit.test('validateorder:success',asyncfunction(assert){
            assert.expect(1);

            constself=this;
            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:function(route){
                    if(route.startsWith('/lunch')){
                        if(route==='/lunch/pay'){
                            assert.ok("shouldperformpayorderRPCcall");
                            returnPromise.resolve(true);
                        }
                        returnmockLunchRPC({
                            infos:Object.assign({},self.regularInfos,{
                                lines:[
                                    {
                                        product:[1,"Tunasandwich","3.00"],
                                        toppings:[],
                                    },
                                ],
                            }),
                            userLocation:self.data['lunch.location'].records[0].id,
                        }).apply(this,arguments);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            const$widgetThirdColumn=kanban.$('.o_lunch_widget.o_lunch_widget_info:eq(2)');

            awaittestUtils.dom.click($widgetThirdColumn.find('button.o_lunch_widget_order_button'));

            kanban.destroy();
        });

        QUnit.test('validateorder:failure',asyncfunction(assert){
            assert.expect(5);

            constself=this;
            constkanban=awaitcreateLunchView({
                View:LunchKanbanView,
                model:'product',
                data:this.data,
                arch:`
                    <kanban>
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>
                `,
                mockRPC:function(route){
                    if(route.startsWith('/lunch')){
                        if(route==='/lunch/pay'){
                            assert.ok('shouldperformpayorderRPCcall');
                            returnPromise.resolve(false);
                        }
                        if(route==='/lunch/payment_message'){
                            assert.ok('shouldperformpaymentmessageRPCcall');
                            returnPromise.resolve({message:'Thisisapaymentmessage.'});
                        }
                        returnmockLunchRPC({
                            infos:Object.assign({},self.regularInfos,{
                                lines:[
                                    {
                                        product:[1,"Tunasandwich","3.00"],
                                        toppings:[],
                                    },
                                ],
                            }),
                            userLocation:self.data['lunch.location'].records[0].id,
                        }).apply(this,arguments);
                    }
                    returnthis._super.apply(this,arguments);
                },
            });

            const$widgetThirdColumn=kanban.$('.o_lunch_widget.o_lunch_widget_info:eq(2)');

            awaittestUtils.dom.click($widgetThirdColumn.find('button.o_lunch_widget_order_button'));

            assert.containsOnce(document.body,'.modal',"shouldopenaDialogbox");
            assert.strictEqual($('.modal-title').text().trim(),
                "Notenoughmoneyinyourwallet","shouldhaveaDialog'stitle");
            assert.strictEqual($('.modal-body').text().trim(),
                "Thisisapaymentmessage.","shouldhaveaDialog'smessage");

            kanban.destroy();
        });
    });
});

});
