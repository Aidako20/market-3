flectra.define('account.section_and_note_tests',function(require){
"usestrict";

varFormView=require('web.FormView');
vartestUtils=require('web.test_utils');
varcreateView=testUtils.createView;

QUnit.module('section_and_note',{
    beforeEach:function(){
        this.data={
            invoice:{
                fields:{
                    invoice_line_ids:{
                        string:"Lines",
                        type:'one2many',
                        relation:'invoice_line',
                        relation_field:'invoice_id'
                    },
                },
                records:[
                    {id:1,invoice_line_ids:[1,2]},
                ],
            },
            invoice_line:{
                fields:{
                    display_type:{
                        string:'Type',
                        type:'selection',
                        selection:[['line_section',"Section"],['line_note',"Note"]]
                    },
                    invoice_id:{
                        string:"Invoice",
                        type:'many2one',
                        relation:'invoice'
                    },
                    name:{
                        string:"Name",
                        type:'text'
                    },
                },
                records:[
                    {id:1,display_type:false,invoice_id:1,name:'product\n2lines'},
                    {id:2,display_type:'line_section',invoice_id:1,name:'section'},
                ]
            },
        };
    },
},function(){
    QUnit.test('correctdisplayofsectionandnotefields',asyncfunction(assert){
        assert.expect(5);
        varform=awaitcreateView({
            View:FormView,
            model:'invoice',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="invoice_line_ids"widget="section_and_note_one2many"/>'+
                '</form>',
            archs:{
                'invoice_line,false,list':'<treeeditable="bottom">'+
                    '<fieldname="display_type"invisible="1"/>'+
                    '<fieldname="name"widget="section_and_note_text"/>'+
                '</tree>',
            },
            res_id:1,
        });

        assert.hasClass(form.$('[name="invoice_line_ids"]table'),'o_section_and_note_list_view');

        //sectionshouldbedisplayedcorrectly
        var$tr0=form.$('tr.o_data_row:eq(0)');

        assert.doesNotHaveClass($tr0,'o_is_line_section',
            "shouldnothaveasectionclass");

        var$tr1=form.$('tr.o_data_row:eq(1)');

        assert.hasClass($tr1,'o_is_line_section',
            "shouldhaveasectionclass");

        //entereditmode
        awaittestUtils.form.clickEdit(form);

        //editinglineshouldbetextarea
        $tr0=form.$('tr.o_data_row:eq(0)');
        awaittestUtils.dom.click($tr0.find('td.o_data_cell'));
        assert.containsOnce($tr0,'td.o_data_celltextarea[name="name"]',
            "editinglineshouldbetextarea");

        //editingsectionshouldbeinput
        $tr1=form.$('tr.o_data_row:eq(1)');
        awaittestUtils.dom.click($tr1.find('td.o_data_cell'));
        assert.containsOnce($tr1,'td.o_data_cellinput[name="name"]',
            "editingsectionshouldbeinput");

        form.destroy();
    });
});
});
