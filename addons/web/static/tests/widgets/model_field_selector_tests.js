flectra.define('web.model_field_selector_tests',function(require){
"usestrict";

varModelFieldSelector=require("web.ModelFieldSelector");
vartestUtils=require("web.test_utils");

QUnit.module('widgets',{},function(){

QUnit.module('ModelFieldSelector',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    foo:{string:"Foo",type:"char",searchable:true},
                    bar:{string:"Bar",type:"boolean",searchable:true},
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

    QUnit.test("creatingafieldchainfromscratch",asyncfunction(assert){
        assert.expect(14);

        var$target=$("#qunit-fixture");

        //Createthefieldselectoranditsmockenvironment
        varfieldSelector=newModelFieldSelector(null,"partner",[],{
            readonly:false,
            debugMode:true,
        });
        awaittestUtils.mock.addMockEnvironment(fieldSelector,{data:this.data});
        awaitfieldSelector.appendTo($target);
        var$value=fieldSelector.$(">.o_field_selector_value");

        //Focusingthefieldselectorinputshouldopenafieldselectorpopover
        fieldSelector.$el.trigger('focusin');
        var$fieldSelectorPopover=fieldSelector.$(".o_field_selector_popover:visible");
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

        //Clickingthe"Bar"fieldshouldclosethepopoverandsetthefield
        //chainto"bar"asitisabasicfield
        awaittestUtils.dom.click($barLi);
        assert.notOk($fieldSelectorPopover.is("visible"),
            "fieldselectorpopovershouldbeclosednow");
        assert.strictEqual(getValueFromDOM($value),"Bar",
            "fieldselectorvalueshouldbedisplayedwitha'Bar'tag");

        assert.deepEqual(fieldSelector.getSelectedField(),{
            model:"partner",
            name:"bar",
            searchable:true,
            string:"Bar",
            type:"boolean",
        },"theselectedfieldshouldbecorrectlyset");

        //Focusingtheinputagainshouldopenthesamepopover
        fieldSelector.$el.trigger('focusin');
        awaittestUtils.nextTick();
        assert.ok($fieldSelectorPopover.is(":visible"),
            "fieldselectorpopovershouldbevisible");

        //Thefieldselectorpopovershouldcontainthelistof"partner"
        //fields."Product"shouldbeamongthem.
        $lis=$fieldSelectorPopover.find("li");
        var$productLi=$();
        $lis.each(function(){
            var$li=$(this);
            if($li.html().indexOf("Product")>=0){
                $productLi=$li;
            }
        });
        assert.strictEqual($productLi.length,1,
            "fieldselectorpopovershouldcontainthe'Product'field");

        //Clickingonthe"Product"fieldshouldupdatethepopovertoshow
        //theproductfields(soonly"ProductName"shouldbethere)
        awaittestUtils.dom.click($productLi);
        $lis=$fieldSelectorPopover.find("li");
        assert.strictEqual($lis.length,1,
            "thereshouldbeonlyonefieldpropositionfor'product'model");
        assert.ok($lis.first().html().indexOf("ProductName")>=0,
            "thenameoftheonlysuggestionshouldbe'ProductName'");

        //Clickingon"ProductName"shouldclosethepopoverandsetthechain
        //to"product_id.name"
        awaittestUtils.dom.click($lis.first());
        assert.notOk($fieldSelectorPopover.is("visible"),
            "fieldselectorpopovershouldbeclosednow");
        assert.strictEqual(getValueFromDOM($value),"Product->ProductName",
            "fieldselectorvalueshouldbedisplayedwithtwotags:'Product'and'ProductName'");

        //Removethecurrentselectionandrecreateitagain
        fieldSelector.$el.trigger('focusin');
        awaittestUtils.nextTick();
        awaittestUtils.dom.click(fieldSelector.$('.o_field_selector_prev_page'));
        awaittestUtils.dom.click(fieldSelector.$('.o_field_selector_close'));

        fieldSelector.$el.trigger('focusin');
        awaittestUtils.nextTick();
        $fieldSelectorPopover=fieldSelector.$(".o_field_selector_popover:visible");
        $lis=$fieldSelectorPopover.find("li");
        $productLi=$();
        $lis.each(function(){
            var$li=$(this);
            if($li.html().indexOf("Product")>=0){
                $productLi=$li;
            }
        });
        assert.strictEqual($productLi.length,1,
            "fieldselectorpopovershouldcontainthe'Product'field");

        awaittestUtils.dom.click($productLi);
        $lis=$fieldSelectorPopover.find("li");
        awaittestUtils.dom.click($lis.first());
        assert.notOk($fieldSelectorPopover.is("visible"),
            "fieldselectorpopovershouldbeclosednow");
        assert.strictEqual(getValueFromDOM($value),"Product->ProductName",
            "fieldselectorvalueshouldbedisplayedwithtwotags:'Product'and'ProductName'");

        fieldSelector.destroy();

        functiongetValueFromDOM($dom){
            return_.map($dom.find(".o_field_selector_chain_part"),function(part){
                return$(part).text().trim();
            }).join("->");
        }
    });

    QUnit.test("defaultfieldchainshouldsetthepagedatacorrectly",asyncfunction(assert){
        assert.expect(3);

        var$target=$("#qunit-fixture");

        //Createthefieldselectoranditsmockenvironment
        //passing'product_id'asaprefilledfield-chain
        varfieldSelector=newModelFieldSelector(null,"partner",['product_id'],{
            readonly:false,
            debugMode:true,
        });
        awaittestUtils.addMockEnvironment(fieldSelector,{data:this.data});
        awaitfieldSelector.appendTo($target);

        //Focusingthefieldselectorinputshouldopenafieldselectorpopover
        fieldSelector.$el.trigger('focusin');
        var$fieldSelectorPopover=fieldSelector.$(".o_field_selector_popover:visible");
        assert.strictEqual($fieldSelectorPopover.length,1,
            "fieldselectorpopovershouldbevisible");

        //Thefieldselectorpopovershouldcontainthelistof"product"
        //fields."ProductName"shouldbeamongthem.
        var$lis=$fieldSelectorPopover.find("li");
        assert.strictEqual($lis.length,1,
            "thereshouldbeonlyonefieldpropositionfor'product'model");
        assert.ok($lis.first().html().indexOf("ProductName")>=0,
            "thenameoftheonlysuggestionshouldbe'ProductName'");


        fieldSelector.destroy();
    });

    QUnit.test("usethefilteroption",asyncfunction(assert){
        assert.expect(2);

        var$target=$("#qunit-fixture");

        //Createthefieldselectoranditsmockenvironment
        varfieldSelector=newModelFieldSelector(null,"partner",[],{
            readonly:false,
            filter:function(field){
                returnfield.type==='many2one';
            },
        });
        awaittestUtils.mock.addMockEnvironment(fieldSelector,{data:this.data});
        awaitfieldSelector.appendTo($target);

        fieldSelector.$el.trigger('focusin');
        awaittestUtils.nextTick();
        var$fieldSelectorPopover=fieldSelector.$(".o_field_selector_popover:visible");
        var$lis=$fieldSelectorPopover.find("li");
        assert.strictEqual($lis.length,1,"thereshouldonlybeoneelement");
        assert.strictEqual($lis.text().trim(),"Product","theavailablefieldshouldbethemany2one");

        fieldSelector.destroy();
    });

    QUnit.test("default`showSearchInput`option",asyncfunction(assert){
        assert.expect(6);

        var$target=$("#qunit-fixture");

        //Createthefieldselectoranditsmockenvironment
        varfieldSelector=newModelFieldSelector(null,"partner",[],{
            readonly:false,
        });
        awaittestUtils.mock.addMockEnvironment(fieldSelector,{data:this.data});
        awaitfieldSelector.appendTo($target);

        fieldSelector.$el.trigger('focusin');
        awaittestUtils.nextTick();
        var$fieldSelectorPopover=fieldSelector.$(".o_field_selector_popover:visible");
        var$searchInput=$fieldSelectorPopover.find(".o_field_selector_searchinput");
        assert.strictEqual($searchInput.length,1,"thereshouldbeasearchinput");

        //withoutsearch
        assert.strictEqual($fieldSelectorPopover.find("li").length,3,"thereshouldbethreeavailablefields");
        assert.strictEqual($fieldSelectorPopover.find("li").text().trim().replace(/\s+/g,''),"BarFooProduct","theavailablefieldshouldbecorrect");
        awaittestUtils.fields.editAndTrigger($searchInput,'xx','keyup');

        assert.strictEqual($fieldSelectorPopover.find("li").length,0,"thereshouldn'tbeanyelement");
        awaittestUtils.fields.editAndTrigger($searchInput,'Pro','keyup');
        assert.strictEqual($fieldSelectorPopover.find("li").length,1,"thereshouldonlybeoneelement");
        assert.strictEqual($fieldSelectorPopover.find("li").text().trim().replace(/\s+/g,''),"Product","theavailablefieldshouldbetheProduct");

        fieldSelector.destroy();
    });

    QUnit.test("false`showSearchInput`option",asyncfunction(assert){
        assert.expect(1);

        var$target=$("#qunit-fixture");

        //Createthefieldselectoranditsmockenvironment
        varfieldSelector=newModelFieldSelector(null,"partner",[],{
            readonly:false,
            showSearchInput:false,
        });
        awaittestUtils.mock.addMockEnvironment(fieldSelector,{data:this.data});
        awaitfieldSelector.appendTo($target);

        fieldSelector.$el.trigger('focusin');
        awaittestUtils.nextTick();
        var$fieldSelectorPopover=fieldSelector.$(".o_field_selector_popover:visible");
        var$searchInput=$fieldSelectorPopover.find(".o_field_selector_searchinput");
        assert.strictEqual($searchInput.length,0,"thereshouldbenosearchinput");

        fieldSelector.destroy();
    });

    QUnit.test("createafieldchainwithvalue1i.e.TRUE_LEAF",asyncfunction(assert){
        assert.expect(1);

        var$target=$("#qunit-fixture");

        //createthefieldselectorwithdomainvalue["1"]
        varfieldSelector=newModelFieldSelector(null,"partner",["1"],{
            readonly:false,
            showSearchInput:false,
        });
        awaittestUtils.mock.addMockEnvironment(fieldSelector,{data:this.data});
        awaitfieldSelector.appendTo($target);

        var$fieldName=fieldSelector.$('.o_field_selector_chain_part');
        assert.strictEqual($fieldName.text().trim(),"1",
            "fieldnamevalueshouldbe1.");

        fieldSelector.destroy();
    });

    QUnit.test("createafieldchainwithvalue0i.e.FALSE_LEAF",asyncfunction(assert){
        assert.expect(1);

        var$target=$("#qunit-fixture");

        //createthefieldselectorwithdomainvalue["0"]
        varfieldSelector=newModelFieldSelector(null,"partner",["0"],{
            readonly:false,
            showSearchInput:false,
        });
        awaittestUtils.mock.addMockEnvironment(fieldSelector,{data:this.data});
        awaitfieldSelector.appendTo($target);

        var$fieldName=fieldSelector.$('.o_field_selector_chain_part');
        assert.strictEqual($fieldName.text().trim(),"0",
            "fieldnamevalueshouldbe0.");

        fieldSelector.destroy();
    });
});
});
});
