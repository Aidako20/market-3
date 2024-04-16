flectra.define('web.domain_selector_tests',function(require){
"usestrict";

varDomainSelector=require("web.DomainSelector");
vartestUtils=require("web.test_utils");

QUnit.module('widgets',{},function(){

QUnit.module('DomainSelector',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    foo:{string:"Foo",type:"char",searchable:true},
                    bar:{string:"Bar",type:"boolean",searchable:true},
                    nice_datetime:{string:"Datetime",type:"datetime",searchable:true},
                    product_id:{string:"Product",type:"many2one",relation:"product",searchable:true},
                },
                records:[{
                    id:1,
                    foo:"yop",
                    bar:true,
                    product_id:37,
                },{
                    id:2,
                    foo:"blip",
                    bar:true,
                    product_id:false,
                },{
                    id:4,
                    foo:"abc",
                    bar:false,
                    product_id:41,
                }],
                onchanges:{},
            },
            product:{
                fields:{
                    name:{string:"ProductName",type:"char",searchable:true}
                },
                records:[{
                    id:37,
                    display_name:"xphone",
                },{
                    id:41,
                    display_name:"xpad",
                }]
            },
        };
    },
},function(){

    QUnit.test("creatingadomainfromscratch",asyncfunction(assert){
        assert.expect(13);

        var$target=$("#qunit-fixture");

        //Createthedomainselectoranditsmockenvironment
        vardomainSelector=newDomainSelector(null,"partner",[],{
            readonly:false,
            debugMode:true,
        });
        awaittestUtils.mock.addMockEnvironment(domainSelector,{data:this.data});
        awaitdomainSelector.appendTo($target);

        //Aswegaveanemptydomain,thereshouldbeavisiblebuttontoadd
        //thefirstdomainpart
        var$domainAddFirstNodeButton=domainSelector.$(".o_domain_add_first_node_button:visible");
        assert.strictEqual($domainAddFirstNodeButton.length,1,
            "thereshouldbeabuttontocreatefirstdomainelement");

        //Clickingonthebuttonshouldaddavisiblefieldselectorinthe
        //widgetsothattheusercanchangethefieldchain
        awaittestUtils.dom.click($domainAddFirstNodeButton);
        var$fieldSelector=domainSelector.$(".o_field_selector:visible");
        assert.strictEqual($fieldSelector.length,1,
            "thereshouldbeafieldselector");

        //Focusingthefieldselectorinputshouldopenafieldselectorpopover
        $fieldSelector.trigger('focusin');
        awaittestUtils.nextTick();
        var$fieldSelectorPopover=$fieldSelector.find(".o_field_selector_popover:visible");
        assert.strictEqual($fieldSelectorPopover.length,1,
            "fieldselectorpopovershouldbevisible");

        //Thefieldselectorpopovershouldcontainthelistof"partner"
        //fields."Bar"shouldbeamongthem.
        var$lis=$fieldSelectorPopover.find("li");
        var$barLi=$();
        $lis.each(function(){
            var$li=$(this);
            if($li.html().indexOf("Bar")>=0){
                $barLi=$li;
            }
        });
        assert.strictEqual($barLi.length,1,
            "fieldselectorpopovershouldcontainthe'Bar'field");

        //Clickingthe"Bar"fieldshouldchangetheinternaldomainandthis
        //shouldbedisplayedinthedebuginput
        awaittestUtils.dom.click($barLi);
        assert.strictEqual(
            domainSelector.$(".o_domain_debug_input").val(),
            '[["bar","=",True]]',
            "thedomaininputshouldcontainadomainwith'bar'"
        );

        //Thereshouldbea"+"buttontoaddadomainpart;clickingonit
        //shouldaddthedefault"['id','=',1]"domain
        var$plus=domainSelector.$(".fa-plus-circle");
        assert.strictEqual($plus.length,1,"thereshouldbea'+'button");
        awaittestUtils.dom.click($plus);
        assert.strictEqual(
            domainSelector.$(".o_domain_debug_input").val(),
            '["&",["bar","=",True],["id","=",1]]',
            "thedomaininputshouldcontainadomainwith'bar'and'id'");

        //Thereshouldbetwo"..."buttonstoaddadomaingroup;clickingon
        //thefirstone,shouldaddthisgroupwithdefaults"['id','=',1]"
        //domainsandthe"|"operator
        var$dots=domainSelector.$(".fa-ellipsis-h");
        assert.strictEqual($dots.length,2,"thereshouldbetwo'...'buttons");
        awaittestUtils.dom.click($dots.first());
        assert.strictEqual(
            domainSelector.$(".o_domain_debug_input").val(),
            '["&","&",["bar","=",True],"|",["id","=",1],["id","=",1],["id","=",1]]',
            "thedomaininputshouldcontainadomainwith'bar','id'andasubgroup"
        );

        //Changingthedomaininputtoupdatethesubgrouptousethe"foo"
        //fieldinsteadof"id"shouldrerenderthewidgetandadaptthe
        //widgetsuggestions
        domainSelector.$(".o_domain_debug_input").val('["&","&",["bar","=",True],"|",["foo","=","hello"],["id","=",1],["id","=",1]]').change();
        awaittestUtils.nextTick();
        assert.strictEqual(domainSelector.$(".o_field_selector").eq(1).find("input.o_field_selector_debug").val(),"foo",
            "thesecondfieldselectorshouldnowcontainthe'foo'value");
        assert.ok(domainSelector.$(".o_domain_leaf_operator_select").eq(1).html().indexOf("contains")>=0,
            "thesecondoperatorselectorshouldnowcontainthe'contains'operator");

        //Thereshouldbefive"-"buttonstoremovedomainpart;clickingon
        //thetwolastones,shouldleaveadomainwithonlythe"bar"and
        //"foo"fields,withtheinitial"&"operator
        var$minus=domainSelector.$(".o_domain_delete_node_button");
        assert.strictEqual($minus.length,5,"thereshouldbefive'x'buttons");
        awaittestUtils.dom.click($minus.last());
        awaittestUtils.dom.click(domainSelector.$(".o_domain_delete_node_button").last());
        assert.strictEqual(
            domainSelector.$(".o_domain_debug_input").val(),
            '["&",["bar","=",True],["foo","=","hello"]]',
            "thedomaininputshouldcontainadomainwith'bar'and'foo'"
        );
        domainSelector.destroy();
    });

    QUnit.test("buildingadomainwithadatetime",asyncfunction(assert){
        assert.expect(2);

        var$target=$("#qunit-fixture");

        //Createthedomainselectoranditsmockenvironment
        vardomainSelector=newDomainSelector(null,"partner",[["nice_datetime","=","2017-03-2715:42:00"]],{
            readonly:false,
        });
        awaittestUtils.mock.addMockEnvironment(domainSelector,{data:this.data});
        awaitdomainSelector.appendTo($target);

        //Checkthatthereisadatepickertochoosethedate
        var$datepicker=domainSelector.$(".o_datepicker:visible");
        assert.strictEqual($datepicker.length,1,
            "thereshouldbeadatepicker");

        varval=$datepicker.find('input').val();
        awaittestUtils.dom.openDatepicker($datepicker);
        awaittestUtils.dom.clickFirst($('.bootstrap-datetimepicker-widget:not(.today)[data-action="selectDay"]'));
        assert.notEqual(domainSelector.$(".o_datepicker:visibleinput").val(),val,
            "datepickervalueshouldhavechanged");
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widgeta[data-action=close]'));

        domainSelector.destroy();
    });

    QUnit.test("buildingadomainwitham2owithoutfollowingtherelation",asyncfunction(assert){
        assert.expect(1);

        var$target=$("#qunit-fixture");

        //Createthedomainselectoranditsmockenvironment
        vardomainSelector=newDomainSelector(null,"partner",[["product_id","ilike",1]],{
            debugMode:true,
            readonly:false,
        });
        awaittestUtils.mock.addMockEnvironment(domainSelector,{data:this.data});
        awaitdomainSelector.appendTo($target);

        awaittestUtils.fields.editAndTrigger(domainSelector.$('.o_domain_leaf_value_input'),
            'pad',['input','change']);
        assert.strictEqual(domainSelector.$('.o_domain_debug_input').val(),'[["product_id","ilike","pad"]]',
            "stringshouldhavebeenallowedasm2ovalue");

        domainSelector.destroy();
    });

    QUnit.test("editingadomainwith`parent`key",asyncfunction(assert){
        assert.expect(1);

        var$target=$("#qunit-fixture");

        //Createthedomainselectoranditsmockenvironment
        vardomainSelector=newDomainSelector(null,"product","[['name','=',parent.foo]]",{
            debugMode:true,
            readonly:false,
        });
        awaittestUtils.mock.addMockEnvironment(domainSelector,{data:this.data});
        awaitdomainSelector.appendTo($target);

        assert.strictEqual(domainSelector.$el.text(),"Thisdomainisnotsupported.",
            "anerrormessageshouldbedisplayedbecauseofthe`parent`key");

        domainSelector.destroy();
    });

    QUnit.test("creatingadomainwithadefaultoption",asyncfunction(assert){
        assert.expect(1);

        var$target=$("#qunit-fixture");

        //Createthedomainselectoranditsmockenvironment
        vardomainSelector=newDomainSelector(null,"partner",[],{
            readonly:false,
            debugMode:true,
            default:[["foo","=","kikou"]],
        });
        awaittestUtils.mock.addMockEnvironment(domainSelector,{data:this.data});
        awaitdomainSelector.appendTo($target);

        //Clickingonthebuttonshouldaddavisiblefieldselectorinthe
        //widgetsothattheusercanchangethefieldchain
        awaittestUtils.dom.click(domainSelector.$(".o_domain_add_first_node_button:visible"));

        assert.strictEqual(
            domainSelector.$(".o_domain_debug_input").val(),
            '[["foo","=","kikou"]]',
            "thedomaininputshouldcontainthedefaultdomain");

        domainSelector.destroy();
    });
});
});
});
