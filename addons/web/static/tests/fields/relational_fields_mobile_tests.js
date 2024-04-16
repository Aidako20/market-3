flectra.define("web.relational_fields_mobile_tests",function(require){
"usestrict";

constFormView=require("web.FormView");
consttestUtils=require("web.test_utils");

QUnit.module("fields",{},function(){
    QUnit.module("relational_fields",{
        beforeEach(){
            this.data={
                partner:{
                    fields:{
                        display_name:{string:"Displayedname",type:"char"},
                        p:{string:"one2manyfield",type:"one2many",relation:"partner",relation_field:"trululu"},
                        trululu:{string:"Trululu",type:"many2one",relation:"partner"},
                    },
                    records:[{
                        id:1,
                        display_name:"firstrecord",
                        p:[2,4],
                        trululu:4,
                    },{
                        id:2,
                        display_name:"secondrecord",
                        p:[],
                        trululu:1,
                    },{
                        id:4,
                        display_name:"aaa",
                    }],
                },
            };
        },
    },function(){
        QUnit.module("FieldOne2Many");

        QUnit.test("one2manyonmobile:displaylistifpresentwithoutkanbanview",asyncfunction(assert){
            assert.expect(2);

            constform=awaittestUtils.createView({
                View:FormView,
                model:"partner",
                data:this.data,
                arch:`
                    <form>
                        <fieldname="p">
                            <tree>
                                <fieldname="display_name"/>
                            </tree>
                        </field>
                    </form>
                `,
                res_id:1,
            });

            awaittestUtils.form.clickEdit(form);
            assert.containsOnce(form,".o_field_x2many_list",
                "shoulddisplayone2many'slist");
            assert.containsN(form,".o_field_x2many_list.o_data_row",2,
                "shoulddisplay2recordsinone2many'slist");

            form.destroy();
        });
    });
});
});
