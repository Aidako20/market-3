flectra.define('web.groupby_menu_generator_tests',function(require){
    "usestrict";

    constCustomGroupByItem=require('web.CustomGroupByItem');
    constActionModel=require('web/static/src/js/views/action_model.js');
    consttestUtils=require('web.test_utils');

    const{createComponent}=testUtils;

    QUnit.module('Components',{},function(){

        QUnit.module('CustomGroupByItem');

        QUnit.test('clickonaddcustomgrouptogglegroupselector',asyncfunction(assert){
            assert.expect(6);

            constcgi=awaitcreateComponent(CustomGroupByItem,{
                props:{
                    fields:[
                        {sortable:true,name:"date",string:'SuperDate',type:'date'},
                    ],
                },
                env:{
                    searchModel:newActionModel(),
                },
            });

            assert.strictEqual(cgi.el.innerText.trim(),"AddCustomGroup");
            assert.hasClass(cgi.el,'o_generator_menu');
            assert.strictEqual(cgi.el.children.length,1);

            awaittestUtils.dom.click(cgi.el.querySelector('.o_generator_menubutton.o_add_custom_group_by'));

            //Singleselectnodewithasingleoption
            assert.containsOnce(cgi,'div>select.o_group_by_selector');
            assert.strictEqual(cgi.el.querySelector('div>select.o_group_by_selectoroption').innerText.trim(),
                "SuperDate");

            //Buttonapply
            assert.containsOnce(cgi,'button.o_apply_group_by');

            cgi.destroy();
        });

        QUnit.test('selectafieldnameinAddCustomGroupmenuproperlytriggerthecorrespondingfield',asyncfunction(assert){
            assert.expect(4);

            constfields=[
                {sortable:true,name:'candlelight',string:'Candlelight',type:'boolean'},
            ];
            classMockedSearchModelextendsActionModel{
                dispatch(method,...args){
                    assert.strictEqual(method,'createNewGroupBy');
                    constfield=args[0];
                    assert.deepEqual(field,fields[0]);
                }
            }
            constsearchModel=newMockedSearchModel();
            constcgi=awaitcreateComponent(CustomGroupByItem,{
                props:{fields},
                env:{searchModel},
            });

            awaittestUtils.dom.click(cgi.el.querySelector('.o_generator_menubutton.o_add_custom_group_by'));
            awaittestUtils.dom.click(cgi.el.querySelector('.o_generator_menubutton.o_apply_group_by'));

            //Theonlythingvisibleshouldbethebutton'AddCustomeGroup';
            assert.strictEqual(cgi.el.children.length,1);
            assert.containsOnce(cgi,'button.o_add_custom_group_by');

            cgi.destroy();
        });
    });
});
