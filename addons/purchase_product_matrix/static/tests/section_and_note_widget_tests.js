flectra.define('purchase_product_matrix.section_and_note_widget_tests',function(require){
"usestrict";

varFormView=require('web.FormView');
vartestUtils=require('web.test_utils');
varcreateView=testUtils.createView;

functiongetGrid(product){
    returnJSON.stringify({
        header:[{name:product.name},{name:"M"},{name:"L"}],
        matrix:[[
            {name:"Men"},
            {ptav_ids:[10,13],qty:0,is_possible_combination:true},
            {ptav_ids:[11,13],qty:0,is_possible_combination:true},
        ],[
            {name:"Women"},
            {ptav_ids:[10,14],qty:0,is_possible_combination:true},
            {ptav_ids:[11,14],qty:0,is_possible_combination:true},
        ]],
    });
}

QUnit.module('section_and_note:purchase_product_matrix',{
    beforeEach:function(){
        this.data={
            purchase_order:{
                fields:{
                    order_line_ids:{
                        string:"Lines",
                        type:'one2many',
                        relation:'order_line',
                        relation_field:'order_id',
                    },
                    grid:{string:"Grid",type:'char'},
                    grid_product_tmpl_id:{string:"GridProduct",type:'many2one',relation:'product'},
                },
                onchanges:{
                    grid_product_tmpl_id:(obj)=>{
                        constproduct=this.data.product.records.find((p)=>{
                            returnp.id===obj.grid_product_tmpl_id;
                        });
                        obj.grid=product?getGrid(product):false;
                    },
                    grid:()=>{},
                },
            },
            order_line:{
                fields:{
                    order_id:{string:"Invoice",type:'many2one',relation:'invoice'},
                    product_template_id:{string:"Product",type:'many2one',relation:'product'},
                },
            },
            product:{
                fields:{
                    name:{string:"Name",type:'char'},
                },
                records:[
                    {id:1,name:'Aconfigurableproduct'},
                ],
            },
        };
    },
},function(){
    QUnit.test('canconfigureaproductwiththematrix',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'purchase_order',
            data:this.data,
            arch:`<form>
                    <fieldname="grid"invisible="1"/>
                    <fieldname="grid_product_tmpl_id"invisible="1"/>
                    <fieldname="order_line_ids"widget="section_and_note_one2many">
                        <treeeditable="bottom">
                            <fieldname="product_template_id"widget="matrix_configurator"/>
                        </tree>
                    </field>
                </form>`,
            mockRPC:function(route,args){
                if(args.method==='onchange'&&args.args[2]==='grid'){
                    //shouldtriggeranonchangeonthegridfieldandletthe
                    //businesslogiccreaterowsaccordingtothematrixcontent
                    assert.deepEqual(args.args[1].grid,JSON.stringify({
                        changes:[{qty:2,ptav_ids:[10,13]},{qty:3,ptav_ids:[11,14]}],
                        product_template_id:1,
                    }));
                }
                if(args.method==='get_single_product_variant'){
                    assert.strictEqual(args.args[0],1);
                    returnPromise.resolve({mode:'matrix'});
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click('.o_field_x2many_list_row_adda');
        awaittestUtils.fields.many2one.searchAndClickItem("product_template_id",{item:'configurable'});

        assert.containsOnce(document.body,'.modal.o_product_variant_matrix');
        const$matrix=$('.modal.o_product_variant_matrix');
        assert.strictEqual($matrix.text().replace(/[\n\r\s\u00a0]+/g,''),
            'AconfigurableproductMLMenWomen');

        //select2M-Menand3L-Women
        awaittestUtils.fields.editInput($matrix.find('.o_matrix_input[ptav_ids="10,13"]'),'2');
        awaittestUtils.fields.editInput($matrix.find('.o_matrix_input[ptav_ids="11,14"]'),'3');
        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

        form.destroy();
    });

    QUnit.test('canopenthematrixtwicewith2differentproducts',asyncfunction(assert){
        assert.expect(5);

        this.data.product.records.push({id:101,name:"ProductA"});
        this.data.product.records.push({id:102,name:"ProductB"});

        constform=awaitcreateView({
            View:FormView,
            model:'purchase_order',
            data:this.data,
            arch:`<form>
                    <fieldname="grid"invisible="1"/>
                    <fieldname="grid_product_tmpl_id"invisible="1"/>
                    <fieldname="order_line_ids"widget="section_and_note_one2many">
                        <treeeditable="bottom">
                            <fieldname="product_template_id"widget="matrix_configurator"/>
                        </tree>
                    </field>
                </form>`,
            mockRPC:function(route,args){
                if(args.method==='onchange'&&args.args[2]==='grid'){
                    //shouldtriggeranonchangeonthegridfieldandletthe
                    //businesslogiccreaterowsaccordingtothematrixcontent
                    assert.deepEqual(args.args[1].grid,JSON.stringify({
                        changes:[{qty:2,ptav_ids:[10,13]},{qty:3,ptav_ids:[11,14]}],
                        product_template_id:102,
                    }));
                }
                if(args.method==='get_single_product_variant'){
                    returnPromise.resolve({mode:'matrix'});
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //openthematrixwith"ProductA"andcloseit
        awaittestUtils.dom.click('.o_field_x2many_list_row_adda');
        awaittestUtils.fields.many2one.searchAndClickItem("product_template_id",{item:'ProductA'});

        assert.containsOnce(document.body,'.modal.o_product_variant_matrix');
        let$matrix=$('.modal.o_product_variant_matrix');
        assert.strictEqual($matrix.text().replace(/[\n\r\s\u00a0]+/g,''),
            'ProductAMLMenWomen');

        awaittestUtils.dom.click($('.modal.modal-footer.btn-secondary'));//close

        //re-openthematrixwith"ProductB"
        awaittestUtils.dom.click('.o_field_x2many_list_row_adda');
        awaittestUtils.fields.many2one.searchAndClickItem("product_template_id",{item:'ProductB'});

        assert.containsOnce(document.body,'.modal.o_product_variant_matrix');
        $matrix=$('.modal.o_product_variant_matrix');
        assert.strictEqual($matrix.text().replace(/[\n\r\s\u00a0]+/g,''),
            'ProductBMLMenWomen');

        //select2M-Menand3L-Women
        awaittestUtils.fields.editInput($matrix.find('.o_matrix_input[ptav_ids="10,13"]'),'2');
        awaittestUtils.fields.editInput($matrix.find('.o_matrix_input[ptav_ids="11,14"]'),'3');
        awaittestUtils.dom.click($('.modal.modal-footer.btn-primary'));

        form.destroy();
    });

    QUnit.test('_onTemplateChangeisexecutedafterproducttemplatequickcreate',asyncfunction(assert){
        assert.expect(1);

        letcreated_product_template;

        constform=awaitcreateView({
            View:FormView,
            model:'purchase_order',
            data:this.data,
            arch:`<form>
                    <fieldname="order_line_ids"widget="section_and_note_one2many">
                        <treeeditable="bottom">
                            <fieldname="product_template_id"widget="matrix_configurator"/>
                        </tree>
                    </field>
                </form>`,
            asyncmockRPC(route,args){
                if(route==='/web/dataset/call_kw/product.template/get_single_product_variant'){
                    assert.strictEqual(args.args[0],created_product_template[0]);
                }

                constresult=awaitthis._super(...arguments);
                if(args.method==='name_create'){
                    created_product_template=result;
                }
                returnresult;
            },
        });

        awaittestUtils.dom.click('.o_field_x2many_list_row_adda');
        awaittestUtils.fields.many2one.searchAndClickItem("product_template_id",{search:'newproduct'});

        form.destroy();
    });

    QUnit.test('draganddroprowscontainingmatrix_configuratormany2one',asyncfunction(assert){
        assert.expect(4);

        this.data.order_line.fields.sequence={string:"Sequence",type:'number'};
        this.data.order_line.fields.order_id.relation='purchase_order';
        this.data.purchase_order.records=[
            {id:1,order_line_ids:[1,2]}
        ];
        this.data.order_line.records=[
            {id:1,sequence:4,product_template_id:1,order_id:1},
            {id:2,sequence:14,product_template_id:2,order_id:1},
        ];
        this.data.product.records.push(
            {id:1,name:"Chair"},
            {id:2,name:"Table"}
        );

        constform=awaitcreateView({
            View:FormView,
            model:'purchase_order',
            data:this.data,
            arch:`<form>
                    <fieldname="order_line_ids"widget="section_and_note_one2many">
                        <treeeditable="bottom">
                            <fieldname="sequence"widget="handle"/>
                            <fieldname="product_template_id"widget="matrix_configurator"/>
                        </tree>
                    </field>
                </form>`,
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.containsN(form,'.o_data_row',2);
        assert.strictEqual(form.$('.o_data_row').text(),'ChairTable');
        assert.containsN(form,'.o_data_row.o_row_handle',2);

        //movefirstrowbelowsecond
        const$firstHandle=form.$('.o_data_row:nth(0).o_row_handle');
        const$secondHandle=form.$('.o_data_row:nth(1).o_row_handle');
        awaittestUtils.dom.dragAndDrop($firstHandle,$secondHandle,{position:'bottom'});

        assert.strictEqual(form.$('.o_data_row').text(),'TableChair');

        form.destroy();
    });
});
});
