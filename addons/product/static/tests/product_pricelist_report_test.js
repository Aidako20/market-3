flectra.define('product.pricelist.report.tests',function(require){
"usestrict";
constcore=require('web.core');
constGeneratePriceList=require('product.generate_pricelist').GeneratePriceList;
constNotificationService=require('web.NotificationService');
consttestUtils=require('web.test_utils');
constcreateActionManager=testUtils.createActionManager;
consttestUtilsMock=require('web.test_utils_mock');

QUnit.module('ProductPricelist',{
    beforeEach:function(){
            this.data={
                'product.product':{
                    fields:{
                        id:{type:'integer'}
                    },
                    records:[{
                        id:42,
                        display_name:"CustomizableDesk"
                    }]
                },
                'product.pricelist':{
                    fields:{
                        id:{type:'integer'}
                    },
                    records:[{
                        id:1,
                        display_name:"PublicPricelist"
                    },{
                        id:2,
                        display_name:"Test"
                    }]
                }
            };
        },
},function(){
    QUnit.test('PricelistClientAction',asyncfunction(assert){
        assert.expect(21);

        constself=this;
        letQty=[1,5,10];//defaultquantities
        testUtils.mock.patch(GeneratePriceList,{
            _onFieldChanged:function(event){
                assert.step('field_changed');
                returnthis._super.apply(this,arguments);
            },
            _onQtyChanged:function(event){
                assert.deepEqual(event.data.quantities,Qty.sort((a,b)=>a-b),"changedquantityshouldbesame.");
                assert.step('qty_changed');
                returnthis._super.apply(this,arguments);
            },
        });

        constactionManager=awaitcreateActionManager({
            data:this.data,
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/report.product.report_pricelist/get_html'){
                    returnPromise.resolve("");
                }
                returnthis._super(route,args);
            },
            services:{
                notification:NotificationService,
            },
        });

        awaitactionManager.doAction({
            id:1,
            name:'GeneratePricelist',
            tag:'generate_pricelist',
            type:'ir.actions.client',
            context:{
                'default_pricelist':1,
                'active_ids':[42],
                'active_id':42,
                'active_model':'product.product'
            }
        });

        //checkingdefaultpricelist
        assert.strictEqual(actionManager.$('.o_field_many2oneinput').val(),"PublicPricelist",
            "shouldhavedefaultpricelist");

        //changingpricelist
        awaittestUtils.fields.many2one.clickOpenDropdown("pricelist_id");
        awaittestUtils.fields.many2one.clickItem("pricelist_id","Test");

        //checkwhertherpricelistvaluehasbeenupdatedornot.alongwiththatcheckdefaultquantitiesshouldbethere.
        assert.strictEqual(actionManager.$('.o_field_many2oneinput').val(),"Test",
            "Afterpricelistchange,thepricelist_idfieldshouldbeupdated");
        assert.strictEqual(actionManager.$('.o_badges>.badge').length,3,
            "Thereshouldbe3defaultQuantities");

        //existingquantitycannotbeadded.
        awaittestUtils.dom.click(actionManager.$('.o_add_qty'));
        letnotificationElement=document.body.querySelector('.o_notification_manager.o_notification.bg-info');
        assert.strictEqual(notificationElement.querySelector('.o_notification_content').textContent,
            "Quantityalreadypresent(1).","ExistingQuantitycannotbeadded");

        //addingfewmorequantitiestocheck.
        actionManager.$('.o_product_qty').val(2);
        Qty.push(2);
        awaittestUtils.dom.click(actionManager.$('.o_add_qty'));
        actionManager.$('.o_product_qty').val(3);
        Qty.push(3);
        awaittestUtils.dom.click(actionManager.$('.o_add_qty'));

        //shouldnotbeaddedmorethen5quantities.
        actionManager.$('.o_product_qty').val(4);
        awaittestUtils.dom.click(actionManager.$('.o_add_qty'));

        notificationElement=document.body.querySelector('.o_notification_manager.o_notification.bg-warning');
        assert.strictEqual(notificationElement.querySelector('.o_notification_content').textContent,
            "Atmost5quantitiescanbedisplayedsimultaneously.Removeaselectedquantitytoaddothers.",
            "Cannotaddmorethen5quantities");

        //removingallthequantitiesshouldwork
        Qty.pop(10);
        awaittestUtils.dom.click(actionManager.$('.o_badges.badge:contains("10").o_remove_qty'));
        Qty.pop(5);
        awaittestUtils.dom.click(actionManager.$('.o_badges.badge:contains("5").o_remove_qty'));
        Qty.pop(3);
        awaittestUtils.dom.click(actionManager.$('.o_badges.badge:contains("3").o_remove_qty'));
        Qty.pop(2);
        awaittestUtils.dom.click(actionManager.$('.o_badges.badge:contains("2").o_remove_qty'));
        Qty.pop(1);
        awaittestUtils.dom.click(actionManager.$('.o_badges.badge:contains("1").o_remove_qty'));

        assert.verifySteps([
            'field_changed',
            'qty_changed',
            'qty_changed',
            'qty_changed',
            'qty_changed',
            'qty_changed',
            'qty_changed',
            'qty_changed'
        ]);

        testUtils.mock.unpatch(GeneratePriceList);
        actionManager.destroy();
    });
}

);
});
