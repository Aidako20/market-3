flectra.define('lunch.lunchKanbanMobileTests',function(require){
"usestrict";

constLunchKanbanView=require('lunch.LunchKanbanView');

consttestUtils=require('web.test_utils');
const{createLunchView,mockLunchRPC}=require('lunch.test_utils');

QUnit.module('Views');

QUnit.module('LunchKanbanViewMobile',{
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
        };
        this.regularInfos={
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
        assert.containsOnce(kanban,'.o_content>.o_lunch_content',
            "shouldhavea'kanbanlunchwrapper'column");
        assert.containsOnce(kanban,'.o_lunch_content>.o_kanban_view',
            "shouldhavea'classicalkanbanview'column");
        assert.hasClass(kanban.$('.o_kanban_view'),'o_lunch_kanban_view',
            "shouldhaveclassname'o_lunch_kanban_view'");
        assert.containsOnce($('.o_lunch_content'),'>details',
            "shouldhavea'lunchkanban'details/summarydiscolurepanel");
        assert.hasClass($('.o_lunch_content>details'),'fixed-bottom',
            "shouldhaveclassname'fixed-bottom'");
        assert.isNotVisible($('.o_lunch_content>details.o_lunch_banner'),
            "shouldn'thaveavisible'lunchkanban'banner");

        kanban.destroy();
    });

    QUnit.module('LunchWidget',function(){
        QUnit.test('toggle',asyncfunction(assert){
            assert.expect(6);

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
                    }),
                    userLocation:this.data['lunch.location'].records[0].id,
                }),
            });

            const$details=$('.o_lunch_content>details');
            assert.isNotVisible($details.find('.o_lunch_banner'),
                "shouldn'thaveavisible'lunchkanban'banner");
            assert.isVisible($details.find('>summary'),
                "shouldhavaavisiblecarttogglebutton");
            assert.containsOnce($details,'>summary:contains(Yourcart)',
                "shouldhave'Yourcart'inthebuttontext");
            assert.containsOnce($details,'>summary:contains(3.00)',
                "shouldhave'3.00'inthebuttontext");

            awaittestUtils.dom.click($details.find('>summary'));
            assert.isVisible($details.find('.o_lunch_banner'),
                "shouldhaveavisible'lunchkanban'banner");

            awaittestUtils.dom.click($details.find('>summary'));
            assert.isNotVisible($details.find('.o_lunch_banner'),
                "shouldn'thaveavisible'lunchkanban'banner");

            kanban.destroy();
        });

        QUnit.test('keepopenwhenaddingquantities',asyncfunction(assert){
            assert.expect(6);

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

            const$details=$('.o_lunch_content>details');
            assert.isNotVisible($details.find('.o_lunch_banner'),
                "shouldn'thaveavisible'lunchkanban'banner");
            assert.isVisible($details.find('>summary'),
                "shouldhavaavisiblecarttogglebutton");

            awaittestUtils.dom.click($details.find('>summary'));
            assert.isVisible($details.find('.o_lunch_banner'),
                "shouldhaveavisible'lunchkanban'banner");

            const$widgetSecondColumn=kanban.$('.o_lunch_widget.o_lunch_widget_info:eq(1)');

            assert.containsOnce($widgetSecondColumn,'.o_lunch_widget_lines>li',
                "shouldhave1orderline");

            let$firstLine=$widgetSecondColumn.find('.o_lunch_widget_lines>li:first');

            awaittestUtils.dom.click($firstLine.find('button.o_add_product'));
            assert.isVisible($('.o_lunch_content>details.o_lunch_banner'),
                "addquantityshouldkeep'lunchkanban'banneropen");

            $firstLine=kanban.$('.o_lunch_widget.o_lunch_widget_info:eq(1).o_lunch_widget_lines>li:first');

            awaittestUtils.dom.click($firstLine.find('button.o_remove_product'));
            assert.isVisible($('.o_lunch_content>details.o_lunch_banner'),
                "removequantityshouldkeep'lunchkanban'banneropen");

            kanban.destroy();
        });
    });
});

});
