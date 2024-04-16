flectra.define('web.relational_fields_tests',function(require){
"usestrict";

varAbstractStorageService=require('web.AbstractStorageService');
varFormView=require('web.FormView');
varListView=require('web.ListView');
varRamStorage=require('web.RamStorage');
varrelationalFields=require('web.relational_fields');
vartestUtils=require('web.test_utils');

constcpHelpers=testUtils.controlPanel;
varcreateView=testUtils.createView;

QUnit.module('fields',{},function(){

QUnit.module('relational_fields',{
    beforeEach:function(){
        this.data={
            partner:{
                fields:{
                    display_name:{string:"Displayedname",type:"char"},
                    foo:{string:"Foo",type:"char",default:"MylittleFooValue"},
                    bar:{string:"Bar",type:"boolean",default:true},
                    int_field:{string:"int_field",type:"integer",sortable:true},
                    qux:{string:"Qux",type:"float",digits:[16,1]},
                    p:{string:"one2manyfield",type:"one2many",relation:'partner',relation_field:'trululu'},
                    turtles:{string:"one2manyturtlefield",type:"one2many",relation:'turtle',relation_field:'turtle_trululu'},
                    trululu:{string:"Trululu",type:"many2one",relation:'partner'},
                    timmy:{string:"pokemon",type:"many2many",relation:'partner_type'},
                    product_id:{string:"Product",type:"many2one",relation:'product'},
                    color:{
                        type:"selection",
                        selection:[['red',"Red"],['black',"Black"]],
                        default:'red',
                        string:"Color",
                    },
                    date:{string:"SomeDate",type:"date"},
                    datetime:{string:"DatetimeField",type:'datetime'},
                    user_id:{string:"User",type:'many2one',relation:'user'},
                    reference:{string:"ReferenceField",type:'reference',selection:[
                        ["product","Product"],["partner_type","PartnerType"],["partner","Partner"]]},
                },
                records:[{
                    id:1,
                    display_name:"firstrecord",
                    bar:true,
                    foo:"yop",
                    int_field:10,
                    qux:0.44,
                    p:[],
                    turtles:[2],
                    timmy:[],
                    trululu:4,
                    user_id:17,
                    reference:'product,37',
                },{
                    id:2,
                    display_name:"secondrecord",
                    bar:true,
                    foo:"blip",
                    int_field:9,
                    qux:13,
                    p:[],
                    timmy:[],
                    trululu:1,
                    product_id:37,
                    date:"2017-01-25",
                    datetime:"2016-12-1210:55:05",
                    user_id:17,
                },{
                    id:4,
                    display_name:"aaa",
                    bar:false,
                }],
                onchanges:{},
            },
            product:{
                fields:{
                    name:{string:"ProductName",type:"char"}
                },
                records:[{
                    id:37,
                    display_name:"xphone",
                },{
                    id:41,
                    display_name:"xpad",
                }]
            },
            partner_type:{
                fields:{
                    name:{string:"PartnerType",type:"char"},
                    color:{string:"Colorindex",type:"integer"},
                },
                records:[
                    {id:12,display_name:"gold",color:2},
                    {id:14,display_name:"silver",color:5},
                ]
            },
            turtle:{
                fields:{
                    display_name:{string:"Displayedname",type:"char"},
                    turtle_foo:{string:"Foo",type:"char"},
                    turtle_bar:{string:"Bar",type:"boolean",default:true},
                    turtle_int:{string:"int",type:"integer",sortable:true},
                    turtle_description:{string:"Description",type:"text"},
                    turtle_trululu:{string:"Trululu",type:"many2one",relation:'partner'},
                    turtle_ref:{string:"Reference",type:'reference',selection:[
                        ["product","Product"],["partner","Partner"]]},
                    product_id:{string:"Product",type:"many2one",relation:'product',required:true},
                    partner_ids:{string:"Partner",type:"many2many",relation:'partner'},
                },
                records:[{
                    id:1,
                    display_name:"leonardo",
                    turtle_bar:true,
                    turtle_foo:"yop",
                    partner_ids:[],
                },{
                    id:2,
                    display_name:"donatello",
                    turtle_bar:true,
                    turtle_foo:"blip",
                    turtle_int:9,
                    partner_ids:[2,4],
                },{
                    id:3,
                    display_name:"raphael",
                    product_id:37,
                    turtle_bar:false,
                    turtle_foo:"kawa",
                    turtle_int:21,
                    partner_ids:[],
                    turtle_ref:'product,37',
                }],
                onchanges:{},
            },
            user:{
                fields:{
                    name:{string:"Name",type:"char"},
                    partner_ids:{string:"one2manypartnersfield",type:"one2many",relation:'partner',relation_field:'user_id'},
                },
                records:[{
                    id:17,
                    name:"Aline",
                    partner_ids:[1,2],
                },{
                    id:19,
                    name:"Christine",
                }]
            },
        };
    },
},function(){

    QUnit.test('searchmorepagerisresetwhendoinganewsearch',asyncfunction(assert){
        assert.expect(6);

        this.data.partner.records.push(
            ...newArray(170).fill().map((_,i)=>({id:i+10,name:"Partner"+i}))
        );
        this.data.partner.fields.datetime.searchable=true;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="trululu"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'partner,false,list':'<tree><fieldname="display_name"/></tree>',
                'partner,false,search':'<search><fieldname="datetime"/><fieldname="display_name"/></search>',
            },
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);

        awaittestUtils.fields.many2one.clickOpenDropdown('trululu');
        awaittestUtils.fields.many2one.clickItem('trululu','Search');
        awaittestUtils.dom.click($('.modal.o_pager_next'));

        assert.strictEqual($('.o_pager_limit').text(),"1173","thereshouldbe173records");
        assert.strictEqual($('.o_pager_value').text(),"181-160","shoulddisplaythesecondpage");
        assert.strictEqual($('tr.o_data_row').length,80,"shoulddisplay80record");

        awaitcpHelpers.editSearch('.modal',"first");
        awaitcpHelpers.validateSearch('.modal');

        assert.strictEqual($('.o_pager_limit').text(),"11","thereshouldbe1record");
        assert.strictEqual($('.o_pager_value').text(),"11-1","shoulddisplaythefirstpage");
        assert.strictEqual($('tr.o_data_row').length,1,"shoulddisplay1record");
        form.destroy();
    });

    QUnit.test('donotcallname_getifdisplay_namealreadyknown',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.fields.product_id.default=37;
        this.data.partner.onchanges={
            trululu:function(obj){
                obj.trululu=1;
            },
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="trululu"/><fieldname="product_id"/></form>',
            mockRPC:function(route,args){
                assert.step(args.method+'on'+args.model);
                returnthis._super.apply(this,arguments);
            },
        });

        assert.strictEqual(form.$('.o_field_widget[name=trululu]input').val(),'firstrecord');
        assert.strictEqual(form.$('.o_field_widget[name=product_id]input').val(),'xphone');
        assert.verifySteps(['onchangeonpartner']);

        form.destroy();
    });

    QUnit.test('x2manydefault_ordermultiplefields',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.records=[
            {int_field:10,id:1,display_name:"record1"},
            {int_field:12,id:2,display_name:"record2"},
            {int_field:11,id:3,display_name:"record3"},
            {int_field:12,id:4,display_name:"record4"},
            {int_field:10,id:5,display_name:"record5"},
            {int_field:10,id:6,display_name:"record6"},
            {int_field:11,id:7,display_name:"record7"},
        ];

        this.data.partner.records[0].p=[1,7,4,5,2,6,3];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                        '<fieldname="p">'+
                            '<treedefault_order="int_field,id">'+
                                '<fieldname="id"/>'+
                                '<fieldname="int_field"/>'+
                            '</tree>'+
                        '</field>'+
                '</form>',
            res_id:1,
        });

        var$recordList=form.$('.o_field_x2many_list.o_data_row');
        varexpectedOrderId=['1','5','6','3','7','2','4'];

        _.each($recordList,function(record,index){
            var$record=$(record);
            assert.strictEqual($record.find('.o_data_cell').eq(0).text(),expectedOrderId[index],
                'Therecordshouldbetherightplace.Index:'+index);
        });

        form.destroy();
    });

    QUnit.test('focuswhenclosingmany2onemodalinmany2onemodal',asyncfunction(assert){
        assert.expect(12);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="trululu"/>'+
                  '</form>',
            res_id:2,
            archs:{
                'partner,false,form':'<form><fieldname="trululu"/></form>'
            },
            mockRPC:function(route,args){
                if(args.method==='get_formview_id'){
                    returnPromise.resolve(false);
                }
                returnthis._super(route,args);
            },
        });

        //Openmany2onemodal
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_external_button'));

        var$originalModal=$('.modal');
        var$focusedModal=$(document.activeElement).closest('.modal');

        assert.equal($originalModal.length,1,'Thereshouldbeonemodal');
        assert.equal($originalModal[0],$focusedModal[0],'Modalisfocused');
        assert.ok($('body').hasClass('modal-open'),'Modalissaidopened');

        //Openmany2onemodaloffieldinmany2onemodal
        awaittestUtils.dom.click($originalModal.find('.o_external_button'));
        var$modals=$('.modal');
        $focusedModal=$(document.activeElement).closest('.modal');

        assert.equal($modals.length,2,'Thereshouldbetwomodals');
        assert.equal($modals[1],$focusedModal[0],'Lastmodalisfocused');
        assert.ok($('body').hasClass('modal-open'),'Modalissaidopened');

        //Closesecondmodal
        awaittestUtils.dom.click($modals.last().find('button[class="close"]'));
        var$modal=$('.modal');
        $focusedModal=$(document.activeElement).closest('.modal');

        assert.equal($modal.length,1,'Thereshouldbeonemodal');
        assert.equal($modal[0],$originalModal[0],'Firstmodalisstillopened');
        assert.equal($modal[0],$focusedModal[0],'Modalisfocused');
        assert.ok($('body').hasClass('modal-open'),'Modalissaidopened');

        //Closefirstmodal
        awaittestUtils.dom.click($modal.find('button[class="close"]'));
        $modal=$('.modal-dialog.modal-lg');

        assert.equal($modal.length,0,'Thereshouldbenomodal');
        assert.notOk($('body').hasClass('modal-open'),'Modalisnotsaidopened');

        form.destroy();
    });


    QUnit.test('one2manyfromamodelthathasbeensorted',asyncfunction(assert){
        assert.expect(1);

        /*Onastandardlistview,sortyourrecordsbyafield
         *Clickonarecordwhichcontainsax2mwithmultiplerecordsinit
         *Thex2mshouldn'ttaketheorderedByoftheparentrecord(theoneontheform)
         */

        this.data.partner.records[0].turtles=[3,2];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                        '<tree>'+
                            '<fieldname="turtle_foo"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
            context:{
                orderedBy:[{
                    name:'foo',
                    asc:false,
                }]
            },
        });

        assert.strictEqual(form.$('.o_field_one2many[name=turtles]tbody').text().trim(),"kawablip",
            'Theo2mshouldnothavebeensorted.');

        form.destroy();
    });

    QUnit.test('widgetmany2many_checkboxesinasubview',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<notebook>'+
                            '<pagestring="Turtles">'+
                                '<fieldname="turtles"mode="tree">'+
                                    '<tree>'+
                                        '<fieldname="id"/>'+
                                    '</tree>'+
                                '</field>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
            '</form>',
            archs:{
                'turtle,false,form':'<form>'+
                    '<fieldname="partner_ids"widget="many2many_checkboxes"/>'+
                '</form>',
            },
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_data_cell'));
        //editthepartner_idsfieldby(un)checkingboxesonthewidget
        var$firstCheckbox=$('.modal.custom-control-input').first();
        awaittestUtils.dom.click($firstCheckbox);
        assert.ok($firstCheckbox.prop('checked'),"thecheckboxshouldbeticked");
        var$secondCheckbox=$('.modal.custom-control-input').eq(1);
        awaittestUtils.dom.click($secondCheckbox);
        assert.notOk($secondCheckbox.prop('checked'),"thecheckboxshouldbeunticked");
        form.destroy();
    });

    QUnit.test('embeddedreadonlyone2manywithhandlewidget',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records[0].turtles=[1,2,3];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="turtles"readonly="1">'+
                            '<treeeditable="top">'+
                                '<fieldname="turtle_int"widget="handle"/>'+
                                '<fieldname="turtle_foo"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                 '</form>',
            res_id:1,
        });

        assert.strictEqual(form.$('.o_row_handle').length,3,
            "thereshouldbe3handles(oneforeachrow)");
        assert.strictEqual(form.$('.o_row_handle:visible').length,0,
            "thehandlesshouldbehiddeninreadonlymode");

        awaittestUtils.form.clickEdit(form);

        assert.strictEqual(form.$('.o_row_handle').length,3,
            "thehandlesshouldstillbethere");
        assert.strictEqual(form.$('.o_row_handle:visible').length,0,
            "thehandlesshouldstillbehidden(onreadonlyfields)");

        form.destroy();
    });

    QUnit.test('deletearecordwhileaddinganotheroneinamultipage',asyncfunction(assert){
        //inamany2onewithatleast2pages,addanewline.Deletethelineaboveit.
        //(theonchangemakesitsothatthevirtualIDisinsertedinthemiddleofthecurrentResIDs.)
        //itshouldloadthenextlinetodisplayitonthepage.
        assert.expect(2);

        this.data.partner.records[0].turtles=[2,3];
        this.data.partner.onchanges.turtles=function(obj){
           obj.turtles=[[5]].concat(obj.turtles);
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="turtles">'+
                                '<treeeditable="bottom"limit="1"decoration-muted="turtle_bar==False">'+
                                    '<fieldname="turtle_foo"/>'+
                                    '<fieldname="turtle_bar"/>'+
                                '</tree>'+
                            '</field>'+
                        '</group>'+
                    '</sheet>'+
                 '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        //addaline(virtualrecord)
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.owlCompatibilityNextTick();
        awaittestUtils.fields.editInput(form.$('.o_input'),'pi');
        //deletethelineaboveit
        awaittestUtils.dom.click(form.$('.o_list_record_remove').first());
        awaittestUtils.owlCompatibilityNextTick();
        //thenextlineshouldbedisplayedbelowthenewlyaddedone
        assert.strictEqual(form.$('.o_data_row').length,2,"shouldhave2records");
        assert.strictEqual(form.$('.o_data_row.o_data_cell:first-child').text(),'pikawa',
            "shoulddisplaythecorrectrecordsonpage1");

        form.destroy();
    });

    QUnit.test('one2many,onchange,editionandmultipage...',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.onchanges={
            turtles:function(obj){
                obj.turtles=[[5]].concat(obj.turtles);
            }
        };

        this.data.partner.records[0].turtles=[1,2,3];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                        '<treeeditable="bottom"limit="2">'+
                            '<fieldname="turtle_foo"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                assert.step(args.method+''+args.model);
                returnthis._super(route,args);
            },
            viewOptions:{
                mode:'edit',
            },
        });
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));

        assert.verifySteps([
            'readpartner',
            'readturtle',
            'onchangeturtle',
            'onchangepartner',
            'onchangeturtle',
            'onchangepartner',
        ]);
        form.destroy();
    });

    QUnit.test('onchangeonunloadedrecordclearingposteriouschange',asyncfunction(assert){
        //whenwegotonchangeresultforfieldsofrecordthatwerenot
        //alreadyavailablebecausetheywereinainlineviewnotalready
        //opened,inagivenconfigurationthechangewereappliedignoring
        //posteriouslychangeddata,thusanadded/removed/modifiedlinecould
        //beresettotheoriginalonchangedata
        assert.expect(5);

        varnumUserOnchange=0;

        this.data.user.onchanges={
            partner_ids:function(obj){
                //simulateactualserveronchangeaftersaveofmodalwithnewrecord
                if(numUserOnchange===0){
                    obj.partner_ids=_.clone(obj.partner_ids);
                    obj.partner_ids.unshift([5]);
                    obj.partner_ids[1][2].turtles.unshift([5]);
                    obj.partner_ids[2]=[1,2,{
                        display_name:'secondrecord',
                        trululu:1,
                        turtles:[[5]],
                    }];
                }elseif(numUserOnchange===1){
                    obj.partner_ids=_.clone(obj.partner_ids);
                    obj.partner_ids.unshift([5]);
                    obj.partner_ids[1][2].turtles.unshift([5]);
                    obj.partner_ids[2][2].turtles.unshift([5]);
                }
                numUserOnchange++;
            },
        };

        varform=awaitcreateView({
            View:FormView,
            model:'user',
            data:this.data,
            arch:'<form><sheet><group>'+
                      '<fieldname="partner_ids">'+
                          '<form>'+
                              '<fieldname="trululu"/>'+
                              '<fieldname="turtles">'+
                                  '<treeeditable="bottom">'+
                                      '<fieldname="display_name"/>'+
                                  '</tree>'+
                              '</field>'+
                          '</form>'+
                          '<tree>'+
                              '<fieldname="display_name"/>'+
                          '</tree>'+
                      '</field>'+
                  '</group></sheet></form>',
            res_id:17,
        });

        //openfirstpartnerandchangeturtlename
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_data_row:eq(0)'));
        awaittestUtils.dom.click($('.modal.o_data_cell:eq(0)'));
        awaittestUtils.fields.editAndTrigger($('.modalinput[name="display_name"]'),
            'Donatello','change');
        awaittestUtils.dom.click($('.modal.btn-primary'));

        awaittestUtils.dom.click(form.$('.o_data_row:eq(1)'));
        awaittestUtils.dom.click($('.modal.o_field_x2many_list_row_adda'));
        awaittestUtils.fields.editAndTrigger($('.modalinput[name="display_name"]'),
            'Michelangelo','change');
        awaittestUtils.dom.click($('.modal.btn-primary'));

        assert.strictEqual(numUserOnchange,2,
            'thereshould2andonly2onchangefromclosingthepartnermodal');

        //checkfirstrecordstillhaschange
        awaittestUtils.dom.click(form.$('.o_data_row:eq(0)'));
        assert.strictEqual($('.modal.o_data_row').length,1,
            'only1turtleforfirstpartner');
        assert.strictEqual($('.modal.o_data_row').text(),'Donatello',
            'firstpartnerturtleisDonatello');
        awaittestUtils.dom.click($('.modal.o_form_button_cancel'));

        //checksecondrecordstillhaschanges
        awaittestUtils.dom.click(form.$('.o_data_row:eq(1)'));
        assert.strictEqual($('.modal.o_data_row').length,1,
            'only1turtleforsecondpartner');
        assert.strictEqual($('.modal.o_data_row').text(),'Michelangelo',
            'secondpartnerturtleisMichelangelo');
        awaittestUtils.dom.click($('.modal.o_form_button_cancel'));

        form.destroy();
    });

    QUnit.test('quicklyswitchbetweenpagesinone2manylist',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].turtles=[1,2,3];

        varreadDefs=[Promise.resolve(),testUtils.makeTestPromise(),testUtils.makeTestPromise()];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="turtles">'+
                        '<treelimit="1">'+
                            '<fieldname="display_name"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            mockRPC:function(route,args){
                varresult=this._super.apply(this,arguments);
                if(args.method==='read'){
                    varrecordID=args.args[0][0];
                    returnPromise.resolve(readDefs[recordID-1]).then(_.constant(result));
                }
                returnresult;
            },
            res_id:1,
        });

        awaittestUtils.dom.click(form.$('.o_field_widget[name=turtles].o_pager_next'));
        awaittestUtils.dom.click(form.$('.o_field_widget[name=turtles].o_pager_next'));

        readDefs[1].resolve();
        awaittestUtils.nextTick();
        assert.strictEqual(form.$('.o_field_widget[name=turtles].o_data_cell').text(),'donatello');

        readDefs[2].resolve();
        awaittestUtils.nextTick();

        assert.strictEqual(form.$('.o_field_widget[name=turtles].o_data_cell').text(),'raphael');

        form.destroy();
    });

    QUnit.test('many2manyread,fieldcontextisproperlysent',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.fields.timmy.context={hello:'world'};
        this.data.partner.records[0].timmy=[12];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="timmy"widget="many2many_tags"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='read'&&args.model==='partner_type'){
                    assert.step(args.kwargs.context.hello);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.verifySteps(['world']);

        awaittestUtils.form.clickEdit(form);
        var$m2mInput=form.$('.o_field_many2manytagsinput');
        $m2mInput.click();
        awaittestUtils.nextTick();
        $m2mInput.autocomplete('widget').find('li:first()').click();
        awaittestUtils.nextTick();
        assert.verifySteps(['world']);

        form.destroy();
    });

    QUnit.module('FieldStatus');

    QUnit.test('staticstatusbarwidgetonmany2onefield',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.fields.trululu.domain="[('bar','=',True)]";
        this.data.partner.records[1].bar=false;

        varcount=0;
        varnb_fields_fetched;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<header><fieldname="trululu"widget="statusbar"/></header>'+
                    //thefollowingfieldseemuseless,butitspresencewasthe
                    //causeofacrashwhenevaluatingthefielddomain.
                    '<fieldname="timmy"invisible="1"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='search_read'){
                    count++;
                    nb_fields_fetched=args.kwargs.fields.length;
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
            config:{device:{isMobile:false}},
        });

        assert.strictEqual(count,1,'oncesearch_readshouldhavebeendonetofetchtherelationalvalues');
        assert.strictEqual(nb_fields_fetched,1,'search_readshouldonlyfetchfieldid');
        assert.containsN(form,'.o_statusbar_statusbutton:not(.dropdown-toggle)',2);
        assert.containsN(form,'.o_statusbar_statusbutton:disabled',2);
        assert.hasClass(form.$('.o_statusbar_statusbutton[data-value="4"]'),'btn-primary');
        form.destroy();
    });

    QUnit.test('staticstatusbarwidgetonmany2onefieldwithdomain',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<header><fieldname="trululu"domain="[(\'user_id\',\'=\',uid)]"widget="statusbar"/></header>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='search_read'){
                    assert.deepEqual(args.kwargs.domain,['|',['id','=',4],['user_id','=',17]],
                        "search_readshouldsentthecorrectdomain");
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
            session:{user_context:{uid:17}},
        });

        form.destroy();
    });

    QUnit.test('clickablestatusbarwidgetonmany2onefield',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<header><fieldname="trululu"widget="statusbar"options=\'{"clickable":"1"}\'/></header>'+
                '</form>',
            res_id:1,
            config:{device:{isMobile:false}},
        });


        assert.hasClass(form.$('.o_statusbar_statusbutton[data-value="4"]'),'btn-primary');
        assert.hasClass(form.$('.o_statusbar_statusbutton[data-value="4"]'),'disabled');

        assert.containsN(form,'.o_statusbar_statusbutton.btn-secondary:not(.dropdown-toggle):not(:disabled)',2);

        var$clickable=form.$('.o_statusbar_statusbutton.btn-secondary:not(.dropdown-toggle):not(:disabled)');
        awaittestUtils.dom.click($clickable.last());//(lastisvisuallythefirsthere(css))

        assert.hasClass(form.$('.o_statusbar_statusbutton[data-value="1"]'),"btn-primary");
        assert.hasClass(form.$('.o_statusbar_statusbutton[data-value="1"]'),"disabled");

        form.destroy();
    });

    QUnit.test('statusbarwithnostatus',asyncfunction(assert){
        assert.expect(2);

        this.data.product.records=[];
        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<formstring="Partners">
                    <header><fieldname="product_id"widget="statusbar"/></header>
                </form>`,
            res_id:1,
            config:{device:{isMobile:false}},
        });

        assert.doesNotHaveClass(form.$('.o_statusbar_status'),'o_field_empty');
        assert.strictEqual(form.$('.o_statusbar_status').children().length,0,
            'statusbarwidgetshouldbeempty');
        form.destroy();
    });

    QUnit.test('statusbarwithrequiredmodifier',asyncfunction(assert){
        assert.expect(2);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<formstring="Partners">
                    <header><fieldname="product_id"widget="statusbar"required="1"/></header>
                </form>`,
            config:{device:{isMobile:false}},
        });
        testUtils.intercept(form,'call_service',function(ev){
            assert.strictEqual(ev.data.service,'notification',
                "shoulddisplayan'invalidfields'notification");
        },true);

        testUtils.form.clickSave(form);

        assert.containsOnce(form,'.o_form_editable','viewshouldstillbeinedit');

        form.destroy();
    });

    QUnit.test('statusbarwithnovalueinreadonly',asyncfunction(assert){
        assert.expect(2);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`
                <form>
                    <header><fieldname="product_id"widget="statusbar"/></header>
                </form>`,
            res_id:1,
            config:{device:{isMobile:false}},
        });

        assert.doesNotHaveClass(form.$('.o_statusbar_status'),'o_field_empty');
        assert.containsN(form,'.o_statusbar_statusbutton:visible',2);

        form.destroy();
    });

    QUnit.test('statusbarwithdomainbutnovalue(createmode)',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.trululu.domain="[('bar','=',True)]";

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<formstring="Partners">'+
                    '<header><fieldname="trululu"widget="statusbar"/></header>'+
                '</form>',
            config:{device:{isMobile:false}},
        });

        assert.containsN(form,'.o_statusbar_statusbutton:disabled',2);
        form.destroy();
    });

    QUnit.test('clickablestatusbarshouldchangem2ofetchingdomainineditmode',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.trululu.domain="[('bar','=',True)]";

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<formstring="Partners">'+
                    '<header><fieldname="trululu"widget="statusbar"options=\'{"clickable":"1"}\'/></header>'+
                '</form>',
            res_id:1,
            config:{device:{isMobile:false}},
        });

        awaittestUtils.form.clickEdit(form);
        assert.containsN(form,'.o_statusbar_statusbutton:not(.dropdown-toggle)',3);
        awaittestUtils.dom.click(form.$('.o_statusbar_statusbutton:not(.dropdown-toggle)').last());
        assert.containsN(form,'.o_statusbar_statusbutton:not(.dropdown-toggle)',2);

        form.destroy();
    });

    QUnit.test('statusbarfold_fieldoptionandstatusbar_visibleattribute',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].bar=false;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<formstring="Partners">'+
                    '<header><fieldname="trululu"widget="statusbar"options="{\'fold_field\':\'bar\'}"/>'+
                    '<fieldname="color"widget="statusbar"statusbar_visible="red"/></header>'+
                '</form>',
            res_id:1,
            config:{device:{isMobile:false}},
        });

        awaittestUtils.form.clickEdit(form);

        assert.containsOnce(form,'.o_statusbar_status:first.dropdown-menubutton.disabled');
        assert.containsOnce(form,'.o_statusbar_status:lastbutton.disabled');

        form.destroy();
    });

    QUnit.test('statusbarwithdynamicdomain',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.fields.trululu.domain="[('int_field','>',qux)]";
        this.data.partner.records[2].int_field=0;

        varrpcCount=0;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<formstring="Partners">'+
                    '<header><fieldname="trululu"widget="statusbar"/></header>'+
                    '<fieldname="qux"/>'+
                    '<fieldname="foo"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='search_read'){
                    rpcCount++;
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
            config:{device:{isMobile:false}},
        });

        awaittestUtils.form.clickEdit(form);

        assert.containsN(form,'.o_statusbar_statusbutton.disabled',3);
        assert.strictEqual(rpcCount,1,"shouldhavedone1search_readrpc");
        awaittestUtils.fields.editInput(form.$('input[name=qux]'),9.5);
        assert.containsN(form,'.o_statusbar_statusbutton.disabled',2);
        assert.strictEqual(rpcCount,2,"shouldhavedone1moresearch_readrpc");
        awaittestUtils.fields.editInput(form.$('input[name=qux]'),"hey");
        assert.strictEqual(rpcCount,2,"shouldnothavedone1moresearch_readrpc");

        form.destroy();
    });

    QUnit.module('FieldSelection');

    QUnit.test('widgetselectioninalistview',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records.forEach(function(r){
            r.color='red';
        });

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treestring="Colors"editable="top">'+
                        '<fieldname="color"/>'+
                '</tree>',
        });

        assert.strictEqual(list.$('td:contains(Red)').length,3,
            "shouldhave3rowswithcorrectvalue");
        awaittestUtils.dom.click(list.$('td:contains(Red):first'));

        var$td=list.$('tbodytr.o_selected_rowtd:not(.o_list_record_selector)');

        assert.strictEqual($td.find('select').length,1,"tdshouldhaveachild'select'");
        assert.strictEqual($td.contents().length,1,"selecttagshouldbeonlychildoftd");
        list.destroy();
    });

    QUnit.test('widgetselection,editionandonmany2onefield',asyncfunction(assert){
        assert.expect(21);

        this.data.partner.onchanges={product_id:function(){}};
        this.data.partner.records[0].product_id=37;
        this.data.partner.records[0].trululu=false;

        varcount=0;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="product_id"widget="selection"/>'+
                        '<fieldname="trululu"widget="selection"/>'+
                        '<fieldname="color"widget="selection"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                count++;
                assert.step(args.method);
                returnthis._super(route,args);
            },
        });

        assert.containsNone(form.$('.o_form_view'),'select');
        assert.strictEqual(form.$('.o_field_widget[name=product_id]').text(),'xphone',
            "shouldhaverenderedthemany2onefieldcorrectly");
        assert.strictEqual(form.$('.o_field_widget[name=product_id]').attr('raw-value'),'37',
            "shouldhavesettheraw-valueattrformany2onefieldcorrectly");
        assert.strictEqual(form.$('.o_field_widget[name=trululu]').text(),'',
            "shouldhaverenderedtheunsetmany2onefieldcorrectly");
        assert.strictEqual(form.$('.o_field_widget[name=color]').text(),'Red',
            "shouldhaverenderedtheselectionfieldcorrectly");
        assert.strictEqual(form.$('.o_field_widget[name=color]').attr('raw-value'),'red',
            "shouldhavesettheraw-valueattrforselectionfieldcorrectly");

        awaittestUtils.form.clickEdit(form);

        assert.containsN(form.$('.o_form_view'),'select',3);
        assert.containsOnce(form,'select[name="product_id"]option:contains(xphone)',
            "shouldhavefetchedxphoneoption");
        assert.containsOnce(form,'select[name="product_id"]option:contains(xpad)',
            "shouldhavefetchedxpadoption");
        assert.strictEqual(form.$('select[name="product_id"]').val(),"37",
            "shouldhavecorrectproduct_idvalue");
        assert.strictEqual(form.$('select[name="trululu"]').val(),"false",
            "shouldnothaveanyvalueintrululufield");
        awaittestUtils.fields.editSelect(form.$('select[name="product_id"]'),41);

        assert.strictEqual(form.$('select[name="product_id"]').val(),"41",
            "shouldhaveavalueofxphone");

        assert.strictEqual(form.$('select[name="color"]').val(),"\"red\"",
            "shouldhavecorrectvalueincolorfield");

        assert.verifySteps(['read','name_search','name_search','onchange']);
        count=0;
        awaitform.reload();
        assert.strictEqual(count,1,"shouldnotreloadproduct_idrelation");
        assert.verifySteps(['read']);

        form.destroy();
    });

    QUnit.test('unsetselectionfieldwith0askey',asyncfunction(assert){
        //Theserverdoesn'tmakeadistinctionbetweenfalsevalue(thefield
        //isunset),andselection0,asinthatcasethevalueitreturnsis
        //false.Sotheclientmustconvertfalsetovalue0ifitexists.
        assert.expect(2);

        this.data.partner.fields.selection={
            type:"selection",
            selection:[[0,"ValueO"],[1,"Value1"]],
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="selection"/>'+
                '</form>',
            res_id:1,
        });

        assert.strictEqual(form.$('.o_field_widget').text(),'ValueO',
            "thedisplayedvalueshouldbe'ValueO'");
        assert.doesNotHaveClass(form.$('.o_field_widget'),'o_field_empty',
            "shouldnothaveclasso_field_empty");

        form.destroy();
    });

    QUnit.test('unsetselectionfieldwithstringkeys',asyncfunction(assert){
        //Theserverdoesn'tmakeadistinctionbetweenfalsevalue(thefield
        //isunset),andselection0,asinthatcasethevalueitreturnsis
        //false.Sotheclientmustconvertfalsetovalue0ifitexists.In
        //thistest,itdoesn'texistaskeysarestrings.
        assert.expect(2);

        this.data.partner.fields.selection={
            type:"selection",
            selection:[['0',"ValueO"],['1',"Value1"]],
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="selection"/>'+
                '</form>',
            res_id:1,
        });

        assert.strictEqual(form.$('.o_field_widget').text(),'',
            "thereshouldbenodisplayedvalue");
        assert.hasClass(form.$('.o_field_widget'),'o_field_empty',
            "shouldhaveclasso_field_empty");

        form.destroy();
    });

    QUnit.test('unsetselectiononamany2onefield',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="trululu"widget="selection"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual(args.args[1].trululu,false,
                        "shouldsend'false'astrululuvalue");
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        awaittestUtils.fields.editSelect(form.$('.o_form_viewselect'),'false');
        awaittestUtils.form.clickSave(form);

        form.destroy();
    });

    QUnit.test('fieldselectionwithmany2onesandspecialcharacters',asyncfunction(assert){
        assert.expect(1);

        //editthepartnerwithid=4
        this.data.partner.records[2].display_name='<span>hey</span>';
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="trululu"widget="selection"/>'+
                '</form>',
            res_id:1,
            viewOptions:{mode:'edit'},
        });
        assert.strictEqual(form.$('selectoption[value="4"]').text(),'<span>hey</span>');

        form.destroy();
    });

    QUnit.test('widgetselectiononamany2one:domainupdatedbyanonchange',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.onchanges={
            int_field:function(){},
        };

        vardomain=[];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="trululu"widget="selection"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    domain=[['id','in',[10]]];
                    returnPromise.resolve({
                        domain:{
                            trululu:domain,
                        }
                    });
                }
                if(args.method==='name_search'){
                    assert.deepEqual(args.args[1],domain,
                        "sentdomainshouldbecorrect");
                }
                returnthis._super(route,args);
            },
            viewOptions:{
                mode:'edit',
            },
        });

        assert.containsN(form,'.o_field_widget[name=trululu]option',4,
            "shouldbe4optionsintheselection");

        //triggeranonchangethatwillupdatethedomain
        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=int_field]'),2);

        assert.containsOnce(form,'.o_field_widget[name=trululu]option',
            "shouldbe1optionintheselection");

        form.destroy();
    });

    QUnit.test('requiredselectionwidgetshouldnothaveblankoption',asyncfunction(assert){
        assert.expect(12);

        this.data.partner.fields.feedback_value={
            type:"selection",
            required:true,
            selection:[['good','Good'],['bad','Bad']],
            default:'good',
            string:'Good'
        };
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                        '<fieldname="feedback_value"/>'+
                        '<fieldname="color"attrs="{\'required\':[(\'feedback_value\',\'=\',\'bad\')]}"/>'+
                '</form>',
            res_id:1
        });

        awaittestUtils.form.clickEdit(form);

        var$colorField=form.$('.o_field_widget[name=color]');
        assert.containsN($colorField,'option',3,"Threeoptionsinnonrequiredfield");

        assert.hasAttrValue($colorField.find('option:first()'),'style',"",
            "Shouldnothavedisplay=none");
        assert.hasAttrValue($colorField.find('option:eq(1)'),'style',"",
            "Shouldnothavedisplay=none");
        assert.hasAttrValue($colorField.find('option:eq(2)'),'style',"",
            "Shouldnothavedisplay=none");

        const$requiredSelect=form.$('.o_field_widget[name=feedback_value]');

        assert.containsN($requiredSelect,'option',3,"Threeoptionsinrequiredfield");
        assert.hasAttrValue($requiredSelect.find('option:first()'),'style',"display:none",
            "Shouldhavedisplay=none");
        assert.hasAttrValue($requiredSelect.find('option:eq(1)'),'style',"",
            "Shouldnothavedisplay=none");
        assert.hasAttrValue($requiredSelect.find('option:eq(2)'),'style',"",
            "Shouldnothavedisplay=none");

        //changevaluetoupdatewidgetmodifiervalues
        awaittestUtils.fields.editSelect($requiredSelect,'"bad"');
        $colorField=form.$('.o_field_widget[name=color]');

        assert.containsN($colorField,'option',3,"Threeoptionsinrequiredfield");
        assert.hasAttrValue($colorField.find('option:first()'),'style',"display:none",
            "Shouldhavedisplay=none");
        assert.hasAttrValue($colorField.find('option:eq(1)'),'style',"",
            "Shouldnothavedisplay=none");
        assert.hasAttrValue($colorField.find('option:eq(2)'),'style',"",
            "Shouldnothavedisplay=none");

        form.destroy();
    });

    QUnit.module('FieldMany2ManyTags');

    QUnit.test('fieldmany2manytagswithandwithoutcolor',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.fields.partner_ids={string:"Partner",type:"many2many",relation:'partner'};
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="partner_ids"widget="many2many_tags"options="{\'color_field\':\'color\'}"/>'+
                    '<fieldname="timmy"widget="many2many_tags"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='read'&&args.model==='partner_type'){
                    assert.deepEqual(args.args,[[12],['display_name']],"shouldnotreadanycolorfield");
                }elseif(args.method==='read'&&args.model==='partner'){
                    assert.deepEqual(args.args,[[1],['display_name','color']],"shouldreadcolorfield");
                }
                returnthis._super.apply(this,arguments);
            }
        });

        //addatagonfieldpartner_ids
        awaittestUtils.fields.many2one.clickOpenDropdown('partner_ids');
        awaittestUtils.fields.many2one.clickHighlightedItem('partner_ids');

        //addatagonfieldtimmy
        awaittestUtils.fields.many2one.clickOpenDropdown('timmy');
        var$input=form.$('.o_field_many2manytags[name="timmy"]input');
        assert.strictEqual($input.autocomplete('widget').find('li').length,3,
            "autocompletedropdownshouldhave3entries(2values+'SearchandEdit...')");
        awaittestUtils.fields.many2one.clickHighlightedItem('timmy');
        assert.containsOnce(form,'.o_field_many2manytags[name="timmy"].badge',
            "shouldcontain1tag");
        assert.containsOnce(form,'.o_field_many2manytags[name="timmy"].badge:contains("gold")',
            "shouldcontainnewlyaddedtag'gold'");

        form.destroy();
    });

    QUnit.test('fieldmany2manytagswithcolor:renderingandedition',asyncfunction(assert){
        assert.expect(28);

        this.data.partner.records[0].timmy=[12,14];
        this.data.partner_type.records.push({id:13,display_name:"red",color:8});
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="timmy"widget="many2many_tags"options="{\'color_field\':\'color\',\'no_create_edit\':True}"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/write'){
                    varcommands=args.args[1].timmy;
                    assert.strictEqual(commands.length,1,"shouldhavegeneratedonecommand");
                    assert.strictEqual(commands[0][0],6,"generatedcommandshouldbeREPLACEWITH");
                    assert.ok(_.isEqual(_.sortBy(commands[0][2],_.identity.bind(_)),[12,13]),
                        "newvalueshouldbe[12,13]");
                }
                if(args.method==='read'&&args.model==='partner_type'){
                    assert.deepEqual(args.args[1],['display_name','color'],"shouldreadthecolorfield");
                }
                returnthis._super.apply(this,arguments);
            },
        });
        assert.containsN(form,'.o_field_many2manytags.badge.dropdown-toggle',2,
            "shouldcontain2tags");
        assert.ok(form.$('.badge.dropdown-toggle:contains(gold)').length,
            'shouldhavefetchedandrenderedgoldpartnertag');
        assert.ok(form.$('.badge.dropdown-toggle:contains(silver)').length,
            'shouldhavefetchedandrenderedsilverpartnertag');
        assert.strictEqual(form.$('.badge:first()').data('color'),2,
            'shouldhavecorrectlyfetchedthecolor');

        awaittestUtils.form.clickEdit(form);

        assert.containsN(form,'.o_field_many2manytags.badge.dropdown-toggle',2,
            "shouldstillcontain2tagsineditmode");
        assert.ok(form.$('.o_tag_color_2.o_badge_text:contains(gold)').length,
            'firsttagshouldstillcontain"gold"andbecolor2ineditmode');
        assert.containsN(form,'.o_field_many2manytags.o_delete',2,
            "tagsshouldcontainadeletebutton");

        //addanotherexistingtag
        var$input=form.$('.o_field_many2manytagsinput');
        awaittestUtils.fields.many2one.clickOpenDropdown('timmy');
        assert.strictEqual($input.autocomplete('widget').find('li').length,2,
            "autocompletedropdownshouldhave2entry");
        assert.strictEqual($input.autocomplete('widget').find('lia:contains("red")').length,1,
            "autocompletedropdownshouldcontain'red'");
        awaittestUtils.fields.many2one.clickHighlightedItem('timmy');
        assert.containsN(form,'.o_field_many2manytags.badge.dropdown-toggle',3,
            "shouldcontain3tags");
        assert.ok(form.$('.o_field_many2manytags.badge.dropdown-toggle:contains("red")').length,
            "shouldcontainnewlyaddedtag'red'");
        assert.ok(form.$('.o_field_many2manytags.badge[data-color=8].dropdown-toggle:contains("red")').length,
            "shouldhavefetchedthecolorofaddedtag");

        //removetagwithid14
        awaittestUtils.dom.click(form.$('.o_field_many2manytags.badge[data-id=14].o_delete'));
        assert.containsN(form,'.o_field_many2manytags.badge.dropdown-toggle',2,
            "shouldcontain2tags");
        assert.ok(!form.$('.o_field_many2manytags.badge.dropdown-toggle:contains("silver")').length,
            "shouldnotcontaintag'silver'anymore");

        //savetherecord(shoulddothewriteRPCwiththecorrectcommands)
        awaittestUtils.form.clickSave(form);

        //checkbox'HideinKanban'
        $input=form.$('.o_field_many2manytags.badge[data-id=13].dropdown-toggle');//selects'red'tag
        awaittestUtils.dom.click($input);
        var$checkBox=form.$('.o_field_many2manytags.badge[data-id=13].custom-checkboxinput');
        assert.strictEqual($checkBox.length,1,"shouldhaveacheckboxinthecolorpickerdropdownmenu");
        assert.notOk($checkBox.is(':checked'),"shouldhaveuntickedcheckboxincolorpickerdropdownmenu");

        awaittestUtils.fields.editAndTrigger($checkBox,null,['mouseenter','mousedown']);

        $input=form.$('.o_field_many2manytags.badge[data-id=13].dropdown-toggle');//refresh
        awaittestUtils.dom.click($input);
        $checkBox=form.$('.o_field_many2manytags.badge[data-id=13].custom-checkboxinput');//refresh
        assert.equal($input.parent().data('color'),"0","shouldbecometransparentwhentogglingoncheckbox");
        assert.ok($checkBox.is(':checked'),"shouldhaveatickedcheckboxincolorpickerdropdownmenuaftermousedown");

        awaittestUtils.fields.editAndTrigger($checkBox,null,['mouseenter','mousedown']);

        $input=form.$('.o_field_many2manytags.badge[data-id=13].dropdown-toggle');//refresh
        awaittestUtils.dom.click($input);
        $checkBox=form.$('.o_field_many2manytags.badge[data-id=13].custom-checkboxinput');//refresh
        assert.equal($input.parent().data('color'),"8","shouldreverttooldcolorwhentogglingoffcheckbox");
        assert.notOk($checkBox.is(':checked'),"shouldhaveanuntickedcheckboxincolorpickerdropdownmenuafter2ndclick");

        //TODO:itwouldbenicetotestthebehaviorsoftheautocompletedropdown
        //(likerefiningtheresearch,creatingnewtags...),butui-autocomplete
        //makesitdifficulttotest
        form.destroy();
    });

    QUnit.test('fieldmany2manytagsintreeview',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records[0].timmy=[12,14];
        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treestring="Partners">'+
                '<fieldname="timmy"widget="many2many_tags"options="{\'color_field\':\'color\'}"/>'+
                '</tree>',
        });
        assert.containsN(list,'.o_field_many2manytags.badge',2,"thereshouldbe2tags");
        assert.containsNone(list,'.badge.dropdown-toggle',"thetagsshouldnotbedropdowns");

        testUtils.intercept(list,'switch_view',function(event){
            assert.strictEqual(event.data.view_type,"form","shouldswitchtoformview");
        });
        //clickonthetag:shoulddonothingandopentheformview
        testUtils.dom.click(list.$('.o_field_many2manytags.badge:first'));

        list.destroy();
    });

    QUnit.test('fieldmany2manytagsviewadomain',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.fields.timmy.domain=[['id','<',50]];
        this.data.partner.records[0].timmy=[12];
        this.data.partner_type.records.push({id:99,display_name:"red",color:8});

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="timmy"widget="many2many_tags"options="{\'no_create_edit\':True}"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='name_search'){
                    assert.deepEqual(args.kwargs.args,[['id','<',50],['id','notin',[12]]],
                        "domainsenttoname_searchshouldbecorrect");
                    returnPromise.resolve([[14,'silver']]);
                }
                returnthis._super.apply(this,arguments);
            }
        });
        assert.containsOnce(form,'.o_field_many2manytags.badge',
            "shouldcontain1tag");
        assert.ok(form.$('.badge:contains(gold)').length,
            'shouldhavefetchedandrenderedgoldpartnertag');

        awaittestUtils.form.clickEdit(form);

        //addanotherexistingtag
        var$input=form.$('.o_field_many2manytagsinput');
        awaittestUtils.fields.many2one.clickOpenDropdown('timmy');
        assert.strictEqual($input.autocomplete('widget').find('li').length,2,
        "autocompletedropdownshouldhave2entry");
        assert.strictEqual($input.autocomplete('widget').find('lia:contains("silver")').length,1,
        "autocompletedropdownshouldcontain'silver'");
        awaittestUtils.fields.many2one.clickHighlightedItem('timmy');
        assert.containsN(form,'.o_field_many2manytags.badge',2,
            "shouldcontain2tags");
        assert.ok(form.$('.o_field_many2manytags.badge:contains("silver")').length,
            "shouldcontainnewlyaddedtag'silver'");

        form.destroy();
    });

    QUnit.test('fieldmany2manytagsinanewrecord',asyncfunction(assert){
        assert.expect(7);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="timmy"widget="many2many_tags"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/create'){
                    varcommands=args.args[0].timmy;
                    assert.strictEqual(commands.length,1,"shouldhavegeneratedonecommand");
                    assert.strictEqual(commands[0][0],6,"generatedcommandshouldbeREPLACEWITH");
                    assert.ok(_.isEqual(commands[0][2],[12]),"newvalueshouldbe[12]");
                }
                returnthis._super.apply(this,arguments);
            }
        });
        assert.hasClass(form.$('.o_form_view'),'o_form_editable',"formshouldbeineditmode");

        awaittestUtils.fields.many2one.clickOpenDropdown('timmy');
        assert.strictEqual(form.$('.o_field_many2manytagsinput').autocomplete('widget').find('li').length,3,
            "autocompletedropdownshouldhave3entries(2values+'SearchandEdit...')");
        awaittestUtils.fields.many2one.clickHighlightedItem('timmy');

        assert.containsOnce(form,'.o_field_many2manytags.badge',
            "shouldcontain1tag");
        assert.ok(form.$('.o_field_many2manytags.badge:contains("gold")').length,
            "shouldcontainnewlyaddedtag'gold'");

        //savetherecord(shoulddothewriteRPCwiththecorrectcommands)
        awaittestUtils.form.clickSave(form);
        form.destroy();
    });

    QUnit.test('fieldmany2manytags:updatecolor',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.records[0].timmy=[12,14];
        this.data.partner_type.records[0].color=0;

        varcolor;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="timmy"widget="many2many_tags"options="{\'color_field\':\'color\'}"/>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(args.args[1],{color:color},
                        "shoudwritethenewcolor");
                }
                returnthis._super.apply(this,arguments);
            },
            res_id:1,
        });

        //Firstchecksthatdefaultcolor0isrenderedas0color
        assert.ok(form.$('.badge.dropdown:first()').is('.o_tag_color_0'),
            'firsttagcolorshouldbe0');

        //Updatethecolorinreadonly
        color=1;
        awaittestUtils.dom.click(form.$('.badge:first().dropdown-toggle'));
        awaittestUtils.dom.triggerEvents($('.o_colorpickera[data-color="'+color+'"]'),['mousedown']);
        awaittestUtils.nextTick();
        assert.strictEqual(form.$('.badge:first()').data('color'),color,
            'shouldhavecorrectlyupdatedthecolor(inreadonly)');

        //Updatethecolorinedit
        color=6;
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.badge:first().dropdown-toggle'));
        awaittestUtils.dom.triggerEvents($('.o_colorpickera[data-color="'+color+'"]'),['mousedown']);//choosecolor6
        awaittestUtils.nextTick();
        assert.strictEqual(form.$('.badge:first()').data('color'),color,
            'shouldhavecorrectlyupdatedthecolor(inedit)');

        form.destroy();
    });

    QUnit.test('fieldmany2manytagswithno_edit_coloroption',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[0].timmy=[12];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="timmy"widget="many2many_tags"options="{\'color_field\':\'color\',\'no_edit_color\':1}"/>'+
                '</form>',
            res_id:1,
        });

        //Clicktotrytoopencolorpicker
        awaittestUtils.dom.click(form.$('.badge:first().dropdown-toggle'));
        assert.containsNone(document.body,'.o_colorpicker');

        form.destroy();
    });

    QUnit.test('fieldmany2manytagsineditablelist',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.records[0].timmy=[12];

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            context:{take:'five'},
            arch:'<treeeditable="bottom">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="timmy"widget="many2many_tags"/>'+
                '</tree>',
            mockRPC:function(route,args){
                if(args.method==='read'&&args.model==='partner_type'){
                    assert.deepEqual(args.kwargs.context,{take:'five'},
                        'ThecontextshouldbepassedtotheRPC');
                }
            returnthis._super.apply(this,arguments);
            }
        });

        assert.containsOnce(list,'.o_data_row:first.o_field_many2manytags.badge',
            "m2mfieldshouldcontainonetag");

        //editfirstrow
        awaittestUtils.dom.click(list.$('.o_data_row:firsttd:nth(2)'));

        var$m2o=list.$('.o_data_row:first.o_field_many2manytags.o_field_many2one');
        assert.strictEqual($m2o.length,1,"amany2onewidgetshouldhavebeeninstantiated");

        //addatag
        awaittestUtils.fields.many2one.clickOpenDropdown('timmy');
        awaittestUtils.fields.many2one.clickHighlightedItem('timmy');

        assert.containsN(list,'.o_data_row:first.o_field_many2manytags.badge',2,
            "m2mfieldshouldcontain2tags");

        //leaveedition
        awaittestUtils.dom.click(list.$('.o_data_row:nth(1)td:nth(2)'));

        assert.containsN(list,'.o_data_row:first.o_field_many2manytags.badge',2,
            "m2mfieldshouldcontain2tags");

        list.destroy();
    });

    QUnit.test('searchmoreinmany2one:groupandusethepager',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records.push({
            id:5,
            display_name:"Partner4",
        },{
            id:6,
            display_name:"Partner5",
        },{
            id:7,
            display_name:"Partner6",
        },{
            id:8,
            display_name:"Partner7",
        },{
            id:9,
            display_name:"Partner8",
        },{
            id:10,
            display_name:"Partner9",
        });
        this.data.partner.fields.datetime.searchable=true;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="trululu"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',

            res_id:1,
            archs:{
                'partner,false,list':'<treelimit="7"><fieldname="display_name"/></tree>',
                'partner,false,search':'<search><group>'+
                       '   <filtername="bar"string="Bar"context="{\'group_by\':\'bar\'}"/>'+
                        '</group></search>',
            },
            viewOptions:{
                mode:'edit',
            },
        });
        awaittestUtils.fields.many2one.clickOpenDropdown('trululu');
        awaittestUtils.fields.many2one.clickItem('trululu','Search');
        awaitcpHelpers.toggleGroupByMenu('.modal');
        awaitcpHelpers.toggleMenuItem('.modal',"Bar");

        awaittestUtils.dom.click($('.modal.o_group_header:first'));

        assert.strictEqual($('.modaltbody:nth(1).o_data_row').length,7,
            "shoulddisplay7recordsinthefirstpage");
        awaittestUtils.dom.click($('.modal.o_group_header:first.o_pager_next'));
        assert.strictEqual($('.modaltbody:nth(1).o_data_row').length,1,
            "shoulddisplay1recordinthesecondpage");

        form.destroy();
    });

    QUnit.test('many2many_tagscanloadmorethan40records',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.partner_ids={string:"Partner",type:"many2many",relation:'partner'};
        this.data.partner.records[0].partner_ids=[];
        for(vari=15;i<115;i++){
            this.data.partner.records.push({id:i,display_name:'walter'+i});
            this.data.partner.records[0].partner_ids.push(i);
        }
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="partner_ids"widget="many2many_tags"/>'+
                '</form>',
            res_id:1,
        });
        assert.containsN(form,'.o_field_widget[name="partner_ids"].badge',100,
            'shouldhaverendered100tags');
        form.destroy();
    });

    QUnit.test('many2many_tagsloadsrecordsaccordingtolimitdefinedonwidgetprototype',asyncfunction(assert){
        assert.expect(1);

        constM2M_LIMIT=relationalFields.FieldMany2ManyTags.prototype.limit;
        relationalFields.FieldMany2ManyTags.prototype.limit=30;
        this.data.partner.fields.partner_ids={string:"Partner",type:"many2many",relation:'partner'};
        this.data.partner.records[0].partner_ids=[];
        for(vari=15;i<50;i++){
            this.data.partner.records.push({id:i,display_name:'walter'+i});
            this.data.partner.records[0].partner_ids.push(i);
        }
        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="partner_ids"widget="many2many_tags"/></form>',
            res_id:1,
        });

        assert.strictEqual(form.$('.o_field_widget[name="partner_ids"].badge').length,30,
            'shouldhaverendered30tagseventhough35recordslinked');

        relationalFields.FieldMany2ManyTags.prototype.limit=M2M_LIMIT;
        form.destroy();
    });

    QUnit.test('fieldmany2many_tagskeepsfocuswhenbeingedited',asyncfunction(assert){
        assert.expect(7);

        this.data.partner.records[0].timmy=[12];
        this.data.partner.onchanges.foo=function(obj){
            obj.timmy=[[5]];//DELETEcommand
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="foo"/>'+
                    '<fieldname="timmy"widget="many2many_tags"/>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'.o_field_many2manytags.badge',
            "shouldcontainonetag");

        //updatefoo,whichwilltriggeranonchangeandupdatetimmy
        //->m2mtagsinputshouldnothavetakenthefocus
        form.$('input[name=foo]').focus();
        awaittestUtils.fields.editInput(form.$('input[name=foo]'),'triggeronchange');
        assert.containsNone(form,'.o_field_many2manytags.badge',
            "shouldcontainnotags");
        assert.strictEqual(form.$('input[name=foo]').get(0),document.activeElement,
            "fooinputshouldhavekeptthefocus");

        //addatag->m2mtagsinputshouldstillhavethefocus
        awaittestUtils.fields.many2one.clickOpenDropdown('timmy');
        awaittestUtils.fields.many2one.clickHighlightedItem('timmy');


        assert.containsOnce(form,'.o_field_many2manytags.badge',
            "shouldcontainatag");
        assert.strictEqual(form.$('.o_field_many2manytagsinput').get(0),document.activeElement,
            "m2mtagsinputshouldhavekeptthefocus");

        //removeatag->m2mtagsinputshouldstillhavethefocus
        awaittestUtils.dom.click(form.$('.o_field_many2manytags.o_delete'));
        assert.containsNone(form,'.o_field_many2manytags.badge',
            "shouldcontainnotags");
        assert.strictEqual(form.$('.o_field_many2manytagsinput').get(0),document.activeElement,
            "m2mtagsinputshouldhavekeptthefocus");

        form.destroy();
    });

    QUnit.test('widgetmany2many_tagsinone2manywithdisplay_name',asyncfunction(assert){
        assert.expect(4);
        this.data.turtle.records[0].partner_ids=[2];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="turtles">'+
                            '<tree>'+
                                '<fieldname="partner_ids"widget="many2many_tags"/>'+ //willusedisplay_name
                            '</tree>'+
                            '<form>'+
                                '<sheet>'+
                                    '<fieldname="partner_ids"/>'+
                                '</sheet>'+
                            '</form>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'partner,false,list':'<tree><fieldname="foo"/></tree>',
            },
            res_id:1,
        });

        assert.strictEqual(form.$('.o_field_one2many[name="turtles"].o_list_view.o_field_many2manytags[name="partner_ids"]').text().replace(/\s/g,''),
            "secondrecordaaa","thetagsshouldbecorrectlyrendered");

        //openthex2mformview
        awaittestUtils.dom.click(form.$('.o_field_one2many[name="turtles"].o_list_viewtd.o_data_cell:first'));
        assert.strictEqual($('.modal.o_form_view.o_field_many2many[name="partner_ids"].o_list_view.o_data_cell').text(),
            "blipMylittleFooValue","thelistviewshouldbecorrectlyrenderedwithfoo");

        awaittestUtils.dom.click($('.modalbutton.o_form_button_cancel'));
        assert.strictEqual(form.$('.o_field_one2many[name="turtles"].o_list_view.o_field_many2manytags[name="partner_ids"]').text().replace(/\s/g,''),
            "secondrecordaaa","thetagsshouldstillbecorrectlyrendered");

        awaittestUtils.form.clickEdit(form);
        assert.strictEqual(form.$('.o_field_one2many[name="turtles"].o_list_view.o_field_many2manytags[name="partner_ids"]').text().replace(/\s/g,''),
            "secondrecordaaa","thetagsshouldstillbecorrectlyrendered");

        form.destroy();
    });

    QUnit.test('widgetmany2many_tags:tagstitleattribute',asyncfunction(assert){
        assert.expect(1);
        this.data.turtle.records[0].partner_ids=[2];

        varform=awaitcreateView({
            View:FormView,
            model:'turtle',
            data:this.data,
            arch:'<formstring="Turtles">'+
                    '<sheet>'+
                        '<fieldname="display_name"/>'+
                        '<fieldname="partner_ids"widget="many2many_tags"/>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.deepEqual(
            form.$('.o_field_many2manytags.o_field_widget.badge.o_badge_text').attr('title'),
            'secondrecord','thetitleshouldbefilledin'
        );

        form.destroy();
    });

    QUnit.test('widgetmany2many_tags:togglecolorpickermultipletimes',asyncfunction(assert){
        assert.expect(11);

        this.data.partner.records[0].timmy=[12];
        this.data.partner_type.records[0].color=0;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="timmy"widget="many2many_tags"options="{\'color_field\':\'color\'}"/>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.strictEqual($('.o_field_many2manytags.badge').length,1,
            "shouldhaveonetag");
        assert.strictEqual($('.o_field_many2manytags.badge').data('color'),0,
            "tagshouldhavecolor0");
        assert.strictEqual($('.o_colorpicker:visible').length,0,
            "colorpickershouldbeclosed");

        //clickonthebadgetoopencolorpicker
        awaittestUtils.dom.click(form.$('.o_field_many2manytags.badge.dropdown-toggle'));

        assert.strictEqual($('.o_colorpicker:visible').length,1,
            "colorpickershouldbeopen");

        //clickonthebadgeagaintoclosecolorpicker
        awaittestUtils.dom.click(form.$('.o_field_many2manytags.badge.dropdown-toggle'));

        assert.strictEqual($('.o_field_many2manytags.badge').data('color'),0,
            "tagshouldstillhavecolor0");
        assert.strictEqual($('.o_colorpicker:visible').length,0,
            "colorpickershouldbeclosed");

        //clickonthebadgetoopencolorpicker
        awaittestUtils.dom.click(form.$('.o_field_many2manytags.badge.dropdown-toggle'));

        assert.strictEqual($('.o_colorpicker:visible').length,1,
            "colorpickershouldbeopen");

        //clickonthecolorpicker,butnotonacolor
        awaittestUtils.dom.click(form.$('.o_colorpicker'));

        assert.strictEqual($('.o_field_many2manytags.badge').data('color'),0,
            "tagshouldstillhavecolor0");
        assert.strictEqual($('.o_colorpicker:visible').length,0,
            "colorpickershouldbeclosed");

        //clickonthebadgetoopencolorpicker
        awaittestUtils.dom.click(form.$('.o_field_many2manytags.badge.dropdown-toggle'));

        //clickonacolorinthecolorpicker
        awaittestUtils.dom.triggerEvents(form.$('.o_colorpicker.o_tag_color_2'),['mousedown']);

        assert.strictEqual($('.o_field_many2manytags.badge').data('color'),2,
            "tagshouldhavecolor2");
        assert.strictEqual($('.o_colorpicker:visible').length,0,
            "colorpickershouldbeclosed");

        form.destroy();
    });

    QUnit.test('widgetmany2many_tags_avatar',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'turtle',
            data:this.data,
            arch:'<form>'+
                    '<sheet>'+
                        '<fieldname="partner_ids"widget="many2many_tags_avatar"/>'+
                    '</sheet>'+
                '</form>',
            res_id:2,
        });

        assert.containsN(form,'.o_field_many2manytags.avatar.o_field_widget.badge',2,"shouldhave2records");
        assert.strictEqual(form.$('.o_field_many2manytags.avatar.o_field_widget.badge:firstimg').data('src'),'/web/image/partner/2/image_128',
            "shouldhavecorrectavatarimage");

        form.destroy();
    });

    QUnit.test('fieldmany2manytags:quickcreateanewrecord',asyncfunction(assert){
        assert.expect(3);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<form><fieldname="timmy"widget="many2many_tags"/></form>`,
        });

        assert.containsNone(form,'.o_field_many2manytags.badge');

        awaittestUtils.fields.many2one.searchAndClickItem('timmy',{search:'newvalue'});

        assert.containsOnce(form,'.o_field_many2manytags.badge');

        awaittestUtils.form.clickSave(form);

        assert.strictEqual(form.el.querySelector('.o_field_many2manytags').innerText.trim(),"newvalue");

        form.destroy();
    });

    QUnit.module('FieldRadio');

    QUnit.test('fieldradiowidgetonamany2oneinanewrecord',asyncfunction(assert){
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="product_id"widget="radio"/>'+
                '</form>',
        });

        assert.ok(form.$('div.o_radio_item').length,"shouldhaverenderedouterdiv");
        assert.containsN(form,'input.o_radio_input',2,"shouldhave2possiblechoices");
        assert.ok(form.$('label.o_form_label:contains(xphone)').length,"oneofthemshouldbexphone");
        assert.containsNone(form,'input:checked',"noneoftheinputshouldbechecked");

        awaittestUtils.dom.click(form.$("input.o_radio_input:first"));

        assert.containsOnce(form,'input:checked',"oneoftheinputshouldbechecked");

        awaittestUtils.form.clickSave(form);

        varnewRecord=_.last(this.data.partner.records);
        assert.strictEqual(newRecord.product_id,37,"shouldhavesavedrecordwithcorrectvalue");
        form.destroy();
    });

    QUnit.test('fieldradiochangevaluebyonchange',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.onchanges={bar:function(obj){
            obj.product_id=obj.bar?41:37;
            obj.color=obj.bar?'red':'black';
        }};

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="product_id"widget="radio"/>'+
                    '<fieldname="color"widget="radio"/>'+
                '</form>',
        });

        awaittestUtils.dom.click(form.$("input[type='checkbox']"));
        assert.containsOnce(form,'input.o_radio_input[data-value="37"]:checked',"oneoftheinputshouldbechecked");
        assert.containsOnce(form,'input.o_radio_input[data-value="black"]:checked',"theotheroftheinputshouldbechecked");
        awaittestUtils.dom.click(form.$("input[type='checkbox']"));
        assert.containsOnce(form,'input.o_radio_input[data-value="41"]:checked',"theotheroftheinputshouldbechecked");
        assert.containsOnce(form,'input.o_radio_input[data-value="red"]:checked',"oneoftheinputshouldbechecked");

        form.destroy();
    });

    QUnit.test('fieldradiowidgetonaselectioninanewrecord',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="color"widget="radio"/>'+
                '</form>',
        });


        assert.ok(form.$('div.o_radio_item').length,"shouldhaverenderedouterdiv");
        assert.containsN(form,'input.o_radio_input',2,"shouldhave2possiblechoices");
        assert.ok(form.$('label.o_form_label:contains(Red)').length,"oneofthemshouldbeRed");

        //clickon2ndoption
        awaittestUtils.dom.click(form.$("input.o_radio_input").eq(1));

        awaittestUtils.form.clickSave(form);

        varnewRecord=_.last(this.data.partner.records);
        assert.strictEqual(newRecord.color,'black',"shouldhavesavedrecordwithcorrectvalue");
        form.destroy();
    });

    QUnit.test('fieldradiowidgethaso_horizontaloro_verticalclass',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.fields.color2=this.data.partner.fields.color;

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                    '<fieldname="color"widget="radio"/>'+
                    '<fieldname="color2"widget="radio"options="{\'horizontal\':True}"/>'+
                    '</group>'+
                '</form>',
        });

        varbtn1=form.$('div.o_field_radio.o_vertical');
        varbtn2=form.$('div.o_field_radio.o_horizontal');

        assert.strictEqual(btn1.length,1,"shouldhaveo_verticalclass");
        assert.strictEqual(btn2.length,1,"shouldhaveo_horizontalclass");
        form.destroy();
    });

    QUnit.test('fieldradiowidgetwithnumericalkeysencodedasstrings',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.fields.selection={
            type:'selection',
            selection:[['0',"Red"],['1',"Black"]],
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="selection"widget="radio"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.strictEqual(args.args[1].selection,'1',
                        "shouldwritecorrectvalue");
                }
                returnthis._super.apply(this,arguments);
            },
        });


        assert.strictEqual(form.$('.o_field_widget').text(),'',
            "fieldshouldbeunset");

        awaittestUtils.form.clickEdit(form);

        assert.containsNone(form,'.o_radio_input:checked',
            "novalueshouldbechecked");

        awaittestUtils.dom.click(form.$("input.o_radio_input:nth(1)"));

        awaittestUtils.form.clickSave(form);

        assert.strictEqual(form.$('.o_field_widget').text(),'Black',
            "valueshouldbe'Black'");

        awaittestUtils.form.clickEdit(form);

        assert.containsOnce(form,'.o_radio_input[data-index=1]:checked',
            "'Black'shouldbechecked");

        form.destroy();
    });

    QUnit.test('widgetradioonamany2one:domainupdatedbyanonchange',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.onchanges={
            int_field:function(){},
        };

        vardomain=[];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="trululu"widget="radio"/>'+
                '</form>',
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='onchange'){
                    domain=[['id','in',[10]]];
                    returnPromise.resolve({
                        value:{
                            trululu:false,
                        },
                        domain:{
                            trululu:domain,
                        },
                    });
                }
                if(args.method==='search_read'){
                    assert.deepEqual(args.kwargs.domain,domain,
                        "sentdomainshouldbecorrect");
                }
                returnthis._super(route,args);
            },
            viewOptions:{
                mode:'edit',
            },
        });

        assert.containsN(form,'.o_field_widget[name=trululu].o_radio_item',3,
            "shouldbe3radiobuttons");

        //triggeranonchangethatwillupdatethedomain
        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=int_field]'),2);
        assert.containsNone(form,'.o_field_widget[name=trululu].o_radio_item',
            "shouldbenomoreradiobutton");

        form.destroy();
    });


    QUnit.module('FieldSelectionBadge');

    QUnit.test('FieldSelectionBadgewidgetonamany2oneinanewrecord',asyncfunction(assert){
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="product_id"widget="selection_badge"/>'+
                '</form>',
        });

        assert.ok(form.$('span.o_selection_badge').length,"shouldhaverenderedouterdiv");
        assert.containsN(form,'span.o_selection_badge',2,"shouldhave2possiblechoices");
        assert.ok(form.$('span.o_selection_badge:contains(xphone)').length,"oneofthemshouldbexphone");
        assert.containsNone(form,'span.active',"noneoftheinputshouldbechecked");

        awaittestUtils.dom.click($("span.o_selection_badge:first"));

        assert.containsOnce(form,'span.active',"oneoftheinputshouldbechecked");

        awaittestUtils.form.clickSave(form);

        varnewRecord=_.last(this.data.partner.records);
        assert.strictEqual(newRecord.product_id,37,"shouldhavesavedrecordwithcorrectvalue");
        form.destroy();
    });

    QUnit.test('FieldSelectionBadgewidgetonaselectioninanewrecord',asyncfunction(assert){
        assert.expect(4);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="color"widget="selection_badge"/>'+
                '</form>',
        });

        assert.ok(form.$('span.o_selection_badge').length,"shouldhaverenderedouterdiv");
        assert.containsN(form,'span.o_selection_badge',2,"shouldhave2possiblechoices");
        assert.ok(form.$('span.o_selection_badge:contains(Red)').length,"oneofthemshouldbeRed");

        //clickon2ndoption
        awaittestUtils.dom.click(form.$("span.o_selection_badge").eq(1));

        awaittestUtils.form.clickSave(form);

        varnewRecord=_.last(this.data.partner.records);
        assert.strictEqual(newRecord.color,'black',"shouldhavesavedrecordwithcorrectvalue");
        form.destroy();
    });

    QUnit.test('FieldSelectionBadgewidgetonaselectioninareadonlymode',asyncfunction(assert){
        assert.expect(1);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="color"widget="selection_badge"readonly="1"/>'+
                '</form>',
        });

        assert.containsOnce(form,'span.o_readonly_modifier',"shouldhave1possiblevalueinreadonlymode");
        form.destroy();
    });

    QUnit.module('FieldSelectionFont');

    QUnit.test('FieldSelectionFontdisplaysthecorrectfontsonoptions',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.fields.fonts={
            type:"selection",
            selection:[['Lato',"Lato"],['Oswald',"Oswald"]],
            default:'Lato',
            string:"Fonts",
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="fonts"widget="font"/>'+
                '</form>',
        });
        varoptions=form.$('.o_field_widget[name="fonts"]>option');

        assert.strictEqual(form.$('.o_field_widget[name="fonts"]').css('fontFamily'),'Lato',
            "Widgetfontshouldbedefault(Lato)");
        assert.strictEqual($(options[0]).css('fontFamily'),'Lato',
            "Option0shouldhavethecorrectfont(Lato)");
        assert.strictEqual($(options[1]).css('fontFamily'),'Oswald',
            "Option1shouldhavethecorrectfont(Oswald)");

        awaittestUtils.fields.editSelect(form.$('.o_field_widget[name="fonts"]'),'"Oswald"');
        assert.strictEqual(form.$('.o_field_widget[name="fonts"]').css('fontFamily'),'Oswald',
            "Widgetfontshouldbeupdated(Oswald)");

        form.destroy();
    });

    QUnit.module('FieldMany2ManyCheckBoxes');

    QUnit.test('widgetmany2many_checkboxes',asyncfunction(assert){
        assert.expect(10);

        this.data.partner.records[0].timmy=[12];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="timmy"widget="many2many_checkboxes"/></group>'+
                '</form>',
            res_id:1,
        });

        assert.containsN(form,'div.o_field_widgetdiv.custom-checkbox',2,
            "shouldhavefetchedanddisplayedthe2valuesofthemany2many");

        assert.ok(form.$('div.o_field_widgetdiv.custom-checkboxinput').eq(0).prop('checked'),
            "firstcheckboxshouldbechecked");
        assert.notOk(form.$('div.o_field_widgetdiv.custom-checkboxinput').eq(1).prop('checked'),
            "secondcheckboxshouldnotbechecked");

        assert.ok(form.$('div.o_field_widgetdiv.custom-checkboxinput').prop('disabled'),
            "thecheckboxesshouldbedisabled");

        awaittestUtils.form.clickEdit(form);

        assert.notOk(form.$('div.o_field_widgetdiv.custom-checkboxinput').prop('disabled'),
            "thecheckboxesshouldnotbedisabled");

        //addam2mvaluebyclickingoninput
        awaittestUtils.dom.click(form.$('div.o_field_widgetdiv.custom-checkboxinput').eq(1));
        awaittestUtils.form.clickSave(form);
        assert.deepEqual(this.data.partner.records[0].timmy,[12,14],
            "shouldhaveaddedthesecondelementtothemany2many");
        assert.containsN(form,'input:checked',2,
            "bothcheckboxesshouldbechecked");

        //removeam2mvaluebyclinkingonlabel
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('div.o_field_widgetdiv.custom-checkbox>label').eq(0));
        awaittestUtils.form.clickSave(form);
        assert.deepEqual(this.data.partner.records[0].timmy,[14],
            "shouldhaveremovedthefirstelementtothemany2many");
        assert.notOk(form.$('div.o_field_widgetdiv.custom-checkboxinput').eq(0).prop('checked'),
            "firstcheckboxshouldbechecked");
        assert.ok(form.$('div.o_field_widgetdiv.custom-checkboxinput').eq(1).prop('checked'),
            "secondcheckboxshouldnotbechecked");

        form.destroy();
    });

    QUnit.test('widgetmany2many_checkboxes:startnonempty,thenremovetwice',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.records[0].timmy=[12,14];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<group><fieldname="timmy"widget="many2many_checkboxes"/></group>'+
                '</form>',
            res_id:1,
            viewOptions:{mode:'edit'},
        });

        awaittestUtils.dom.click(form.$('div.o_field_widgetdiv.custom-checkboxinput').eq(0));
        awaittestUtils.dom.click(form.$('div.o_field_widgetdiv.custom-checkboxinput').eq(1));
        awaittestUtils.form.clickSave(form);
        assert.notOk(form.$('div.o_field_widgetdiv.custom-checkboxinput').eq(0).prop('checked'),
            "firstcheckboxshouldnotbechecked");
        assert.notOk(form.$('div.o_field_widgetdiv.custom-checkboxinput').eq(1).prop('checked'),
            "secondcheckboxshouldnotbechecked");

        form.destroy();
    });

    QUnit.test('widgetmany2many_checkboxes:valuesareupdatedwhendomainchanges',asyncfunction(assert){
        assert.expect(5);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<form>
                    <fieldname="int_field"/>
                    <fieldname="timmy"widget="many2many_checkboxes"domain="[['id','>',int_field]]"/>
                </form>`,
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
        });

        assert.strictEqual(form.$('.o_field_widget[name=int_field]').val(),'10');
        assert.containsN(form,'.o_field_widget[name=timmy].custom-checkbox',2);
        assert.strictEqual(form.$('.o_field_widget[name=timmy].o_form_label').text(),'goldsilver');

        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=int_field]'),13);

        assert.containsOnce(form,'.o_field_widget[name=timmy].custom-checkbox');
        assert.strictEqual(form.$('.o_field_widget[name=timmy].o_form_label').text(),'silver');

        form.destroy();
    });

    QUnit.test('widgetmany2many_checkboxeswith40+values',asyncfunction(assert){
        //40isthedefaultlimitforx2manyfields.However,themany2many_checkboxesisa
        //specialfieldthatfetchesitsdatathroughthefetchSpecialDatamechanism,andit
        //usesthename_searchserver-sidelimitof100.Thistestcomeswithafixforabug
        //thatoccurredwhentheuser(un)selectedacheckboxthatwasn'tinthe40firstcheckboxes,
        //becausethepieceofdatacorrespondingtothatcheckboxhadn'tbeenprocessedbythe
        //BasicModel,whereasthecodehandlingthechangeassumedithad.
        assert.expect(3);

        constrecords=[];
        for(letid=1;id<=90;id++){
            records.push({
                id,
                display_name:`type${id}`,
                color:id%7,
            });
        }
        this.data.partner_type.records=records;
        this.data.partner.records[0].timmy=records.map((r)=>r.id);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="timmy"widget="many2many_checkboxes"/></form>',
            res_id:1,
            asyncmockRPC(route,args){
                if(args.method==='write'){
                    constexpectedIds=records.map((r)=>r.id);
                    expectedIds.pop();
                    assert.deepEqual(args.args[1].timmy,[[6,false,expectedIds]]);
                }
                returnthis._super(...arguments);
            },
            viewOptions:{
                mode:'edit',
            },
        });

        assert.containsN(form,'.o_field_widget[name=timmy]input[type=checkbox]:checked',90);

        //togglethelastvalue
        awaittestUtils.dom.click(form.$('.o_field_widget[name=timmy]input[type=checkbox]:last'));
        assert.notOk(form.$('.o_field_widget[name=timmy]input[type=checkbox]:last').is(':checked'));

        awaittestUtils.form.clickSave(form);

        form.destroy();
    });

    QUnit.test('widgetmany2many_checkboxeswith100+values',asyncfunction(assert){
        //Themany2many_checkboxeswidgetlimitsthedisplayedvaluesto100(thisisthe
        //server-sidename_searchlimit).Thistestencodesascenariowheretherearemorethan
        //100recordsintheco-model,andallvaluesinthemany2manyrelationshiparen't
        //displayedinthewidget(duetothelimit).Iftheuser(un)selectsacheckbox,wedon't
        //wanttoremoveallvaluesthataren'tdisplayedfromtherelation.
        assert.expect(5);

        constrecords=[];
        for(letid=1;id<150;id++){
            records.push({
                id,
                display_name:`type${id}`,
                color:id%7,
            });
        }
        this.data.partner_type.records=records;
        this.data.partner.records[0].timmy=records.map((r)=>r.id);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form><fieldname="timmy"widget="many2many_checkboxes"/></form>',
            res_id:1,
            asyncmockRPC(route,args){
                if(args.method==='write'){
                    constexpectedIds=records.map((r)=>r.id);
                    expectedIds.shift();
                    assert.deepEqual(args.args[1].timmy,[[6,false,expectedIds]]);
                }
                constresult=awaitthis._super(...arguments);
                if(args.method==='name_search'){
                    assert.strictEqual(result.length,100,
                        "sanitycheck:name_searchautomaticallysetsthelimitto100");
                }
                returnresult;
            },
            viewOptions:{
                mode:'edit',
            },
        });

        assert.containsN(form,'.o_field_widget[name=timmy]input[type=checkbox]',100,
            "shouldonlydisplay100checkboxes");
        assert.ok(form.$('.o_field_widget[name=timmy]input[type=checkbox]:first').is(':checked'));

        //togglethefirstvalue
        awaittestUtils.dom.click(form.$('.o_field_widget[name=timmy]input[type=checkbox]:first'));
        assert.notOk(form.$('.o_field_widget[name=timmy]input[type=checkbox]:first').is(':checked'));

        awaittestUtils.form.clickSave(form);

        form.destroy();
    });

    QUnit.module('FieldMany2ManyBinaryMultiFiles');

    QUnit.test('widgetmany2many_binary',asyncfunction(assert){
        assert.expect(16);
        this.data['ir.attachment']={
            fields:{
                name:{string:"Name",type:"char"},
                mimetype:{string:"Mimetype",type:"char"},
            },
            records:[{
                id:17,
                name:'Marley&Me.jpg',
                mimetype:'jpg',
            }],
        };
        this.data.turtle.fields.picture_ids={
            string:"Pictures",
            type:"many2many",
            relation:'ir.attachment',
        };
        this.data.turtle.records[0].picture_ids=[17];

        varform=awaitcreateView({
            View:FormView,
            model:'turtle',
            data:this.data,
            arch:'<formstring="Turtles">'+
                    '<group><fieldname="picture_ids"widget="many2many_binary"options="{\'accepted_file_extensions\':\'image/*\'}"/></group>'+
                '</form>',
            archs:{
                'ir.attachment,false,list':'<treestring="Pictures"><fieldname="name"/></tree>',
            },
            res_id:1,
            mockRPC:function(route,args){
                assert.step(route);
                if(route==='/web/dataset/call_kw/ir.attachment/read'){
                    assert.deepEqual(args.args[1],['name','mimetype']);
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsOnce(form,'div.o_field_widget.oe_fileupload',
            "thereshouldbetheattachmentwidget");
        assert.strictEqual(form.$('div.o_field_widget.oe_fileupload.o_attachments').children().length,1,
            "thereshouldbenoattachment");
        assert.containsNone(form,'div.o_field_widget.oe_fileupload.o_attach',
            "thereshouldnotbeanAddbutton(readonly)");
        assert.containsNone(form,'div.o_field_widget.oe_fileupload.o_attachment.o_attachment_delete',
            "thereshouldnotbeaDeletebutton(readonly)");

        //toeditmode
        awaittestUtils.form.clickEdit(form);
        assert.containsOnce(form,'div.o_field_widget.oe_fileupload.o_attach',
            "thereshouldbeanAddbutton");
        assert.strictEqual(form.$('div.o_field_widget.oe_fileupload.o_attach').text().trim(),"Pictures",
            "thebuttonshouldbecorrectlynamed");
        assert.containsOnce(form,'div.o_field_widget.oe_fileupload.o_hidden_input_fileform',
            "thereshouldbeahiddenformtouploadattachments");

        assert.strictEqual(form.$('input.o_input_file').attr('accept'),'image/*',
            "thereshouldbeanattribute\"accept\"ontheinput")

        //TODO:addanattachment
        //noideahowtotestthis

        //deletetheattachment
        awaittestUtils.dom.click(form.$('div.o_field_widget.oe_fileupload.o_attachment.o_attachment_delete'));

        assert.verifySteps([
            '/web/dataset/call_kw/turtle/read',
            '/web/dataset/call_kw/ir.attachment/read',
        ]);

        awaittestUtils.form.clickSave(form);

        assert.strictEqual(form.$('div.o_field_widget.oe_fileupload.o_attachments').children().length,0,
            "thereshouldbenoattachment");

        assert.verifySteps([
            '/web/dataset/call_kw/turtle/write',
            '/web/dataset/call_kw/turtle/read',
        ]);

        form.destroy();
    });

    QUnit.test('name_createinformdialog',asyncfunction(assert){
        assert.expect(2);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<group>'+
                        '<fieldname="p">'+
                            '<tree>'+
                                '<fieldname="bar"/>'+
                            '</tree>'+
                            '<form>'+
                                '<fieldname="product_id"/>'+
                            '</form>'+
                        '</field>'+
                    '</group>'+
                '</form>',
            mockRPC:function(route,args){
                if(args.method==='name_create'){
                    assert.step('name_create');
                }
                returnthis._super.apply(this,arguments);
            },
        });

        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        awaittestUtils.owlCompatibilityNextTick();
        awaittestUtils.fields.many2one.searchAndClickItem('product_id',
            {selector:'.modal',search:'newrecord'});

        assert.verifySteps(['name_create']);

        form.destroy();
    });

    QUnit.module('FieldReference');

    QUnit.test('Referencefieldcanquickcreatemodels',asyncfunction(assert){
        assert.expect(8);

        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<form><fieldname="reference"/></form>`,
            mockRPC(route,args){
                assert.step(args.method||route);
                returnthis._super(...arguments);
            },
        });

        awaittestUtils.fields.editSelect(form.$('select'),'partner');
        awaittestUtils.fields.many2one.searchAndClickItem('reference',{search:'newpartner'});
        awaittestUtils.form.clickSave(form);

        assert.verifySteps([
            'onchange',
            'name_search',//fortheselect
            'name_search',//forthespawnedmany2one
            'name_create',
            'create',
            'read',
            'name_get'
        ],"Thename_createmethodshouldhavebeencalled");

        form.destroy();
    });

    QUnit.test('Referencefieldinmodalreadonlymode',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records[0].p=[2];
        this.data.partner.records[1].trululu=1;
        this.data.partner.records[1].reference='product,41';

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="reference"/>'+
                    '<fieldname="p"/>'+
                '</form>',
            archs:{
                'partner,false,form':'<form><fieldname="reference"/></form>',
                'partner,false,list':'<tree><fieldname="display_name"/></tree>',
            },
            res_id:1,
        });

        //CurrentForm
        assert.equal(form.$('.o_form_uri.o_field_widget[name=reference]').text(),'xphone',
            'thefieldreferenceoftheformshouldhavetherightvalue');

        var$cell_o2m=form.$('.o_data_cell');
        assert.equal($cell_o2m.text(),'secondrecord',
            'thelistshouldhaveonerecord');

        awaittestUtils.dom.click($cell_o2m);

        //Inmodal
        var$modal=$('.modal-lg');
        assert.equal($modal.length,1,
            'thereshouldbeonemodalopened');

        assert.equal($modal.find('.o_form_uri.o_field_widget[name=reference]').text(),'xpad',
            'Thefieldreferenceinthemodalshouldhavetherightvalue');

        awaittestUtils.dom.click($modal.find('.o_form_button_cancel'));

        form.destroy();
    });

    QUnit.test('Referencefieldinmodalwritemode',asyncfunction(assert){
        assert.expect(5);

        this.data.partner.records[0].p=[2];
        this.data.partner.records[1].trululu=1;
        this.data.partner.records[1].reference='product,41';

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="reference"/>'+
                    '<fieldname="p"/>'+
                '</form>',
            archs:{
                'partner,false,form':'<form><fieldname="reference"/></form>',
                'partner,false,list':'<tree><fieldname="display_name"/></tree>',
            },
            res_id:1,
        });

        //currentform
        awaittestUtils.form.clickEdit(form);

        var$fieldRef=form.$('.o_field_widget.o_field_many2one[name=reference]');
        assert.equal($fieldRef.find('option:selected').text(),'Product',
            'Thereferencefield\'smodelshouldbeProduct');
        assert.equal($fieldRef.find('.o_input.ui-autocomplete-input').val(),'xphone',
            'Thereferencefield\'srecordshouldbexphone');

        awaittestUtils.dom.click(form.$('.o_data_cell'));

        //Inmodal
        var$modal=$('.modal-lg');
        assert.equal($modal.length,1,
            'thereshouldbeonemodalopened');

        var$fieldRefModal=$modal.find('.o_field_widget.o_field_many2one[name=reference]');

        assert.equal($fieldRefModal.find('option:selected').text(),'Product',
            'Thereferencefield\'smodelshouldbeProduct');
        assert.equal($fieldRefModal.find('.o_input.ui-autocomplete-input').val(),'xpad',
            'Thereferencefield\'srecordshouldbexpad');

        form.destroy();
    });

    QUnit.test('referenceinformview',asyncfunction(assert){
        assert.expect(15);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="reference"string="customlabel"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            archs:{
                'product,false,form':'<formstring="Product"><fieldname="display_name"/></form>',
            },
            res_id:1,
            mockRPC:function(route,args){
                if(args.method==='get_formview_action'){
                    assert.deepEqual(args.args[0],[37],"shouldcallget_formview_actionwithcorrectid");
                    returnPromise.resolve({
                        res_id:17,
                        type:'ir.actions.act_window',
                        target:'current',
                        res_model:'res.partner'
                    });
                }
                if(args.method==='get_formview_id'){
                    assert.deepEqual(args.args[0],[37],"shouldcallget_formview_idwithcorrectid");
                    returnPromise.resolve(false);
                }
                if(args.method==='name_search'){
                    assert.strictEqual(args.model,'partner_type',
                        "thename_searchshouldbedoneonthenewlysetmodel");
                }
                if(args.method==='write'){
                    assert.strictEqual(args.model,'partner',
                        "shouldwriteonthecurrentmodel");
                    assert.deepEqual(args.args,[[1],{reference:'partner_type,12'}],
                        "shouldwritethecorrectvalue");
                }
                returnthis._super(route,args);
            },
        });

        testUtils.mock.intercept(form,'do_action',function(event){
            assert.strictEqual(event.data.action.res_id,17,
                "shoulddoado_actionwithcorrectparameters");
        });

        assert.strictEqual(form.$('a.o_form_uri:contains(xphone)').length,1,
                        "shouldcontainalink");
        awaittestUtils.dom.click(form.$('a.o_form_uri'));

        awaittestUtils.form.clickEdit(form);

        assert.containsN(form,'.o_field_widget',2,
            "shouldcontaintwofieldwidgets(selectionandmany2one)");
        assert.containsOnce(form,'.o_field_many2one',
            "shouldcontainonemany2one");
        assert.strictEqual(form.$('.o_field_widgetselect').val(),"product",
            "widgetshouldcontainoneselectwiththemodel");
        assert.strictEqual(form.$('.o_field_widgetinput').val(),"xphone",
            "widgetshouldcontainoneinputwiththerecord");

        varoptions=_.map(form.$('.o_field_widgetselect>option'),function(el){
            return$(el).val();
        });
        assert.deepEqual(options,['','product','partner_type','partner'],
            "theoptionsshouldbecorrectlyset");

        awaittestUtils.dom.click(form.$('.o_external_button'));

        assert.strictEqual($('.modal.modal-title').text().trim(),'Open:customlabel',
                        "dialogtitleshoulddisplaythecustomstringlabel");
        awaittestUtils.dom.click($('.modal.o_form_button_cancel'));

        awaittestUtils.fields.editSelect(form.$('.o_field_widgetselect'),'partner_type');
        assert.strictEqual(form.$('.o_field_widgetinput').val(),"",
            "many2onevalueshouldberesetaftermodelchange");

        awaittestUtils.fields.many2one.clickOpenDropdown('reference');
        awaittestUtils.fields.many2one.clickHighlightedItem('reference');


        awaittestUtils.form.clickSave(form);
        assert.strictEqual(form.$('a.o_form_uri:contains(gold)').length,1,
                        "shouldcontainalinkwiththenewvalue");

        form.destroy();
    });

    QUnit.test('interactwithreferencefieldchangedbyonchange',asyncfunction(assert){
        assert.expect(2);

        this.data.partner.onchanges={
            bar:function(obj){
                if(!obj.bar){
                    obj.reference='partner,1';
                }
            },
        };
        constform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:`<form>
                    <fieldname="bar"/>
                    <fieldname="reference"/>
                </form>`,
            mockRPC:function(route,args){
                if(args.method==='create'){
                    assert.deepEqual(args.args[0],{
                        bar:false,
                        reference:'partner,4',
                    });
                }
                returnthis._super.apply(this,arguments);
            },
        });

        //triggertheonchangetosetavalueforthereferencefield
        awaittestUtils.dom.click(form.$('.o_field_booleaninput'));

        assert.strictEqual(form.$('.o_field_widget[name=reference]select').val(),'partner');

        //manuallyupdatereferencefield
        awaittestUtils.fields.many2one.searchAndClickItem('reference',{search:'aaa'});

        //save
        awaittestUtils.form.clickSave(form);

        form.destroy();
    });

    QUnit.test('default_getandonchangewithareferencefield',asyncfunction(assert){
        assert.expect(8);

        this.data.partner.fields.reference.default='product,37';
        this.data.partner.onchanges={
            int_field:function(obj){
                if(obj.int_field){
                    obj.reference='partner_type,'+obj.int_field;
                }
            },
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="int_field"/>'+
                            '<fieldname="reference"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                if(args.method==='name_get'){
                    assert.step(args.model);
                }
                returnthis._super(route,args);
            },
        });

        assert.verifySteps(['product'],"thefirstname_getshouldhavebeendone");
        assert.strictEqual(form.$('.o_field_widget[name="reference"]select').val(),"product",
            "referencefieldmodelshouldbecorrectlyset");
        assert.strictEqual(form.$('.o_field_widget[name="reference"]input').val(),"xphone",
            "referencefieldvalueshouldbecorrectlyset");

        //triggeronchange
        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=int_field]'),12);

        assert.verifySteps(['partner_type'],"thesecondname_getshouldhavebeendone");
        assert.strictEqual(form.$('.o_field_widget[name="reference"]select').val(),"partner_type",
            "referencefieldmodelshouldbecorrectlyset");
        assert.strictEqual(form.$('.o_field_widget[name="reference"]input').val(),"gold",
            "referencefieldvalueshouldbecorrectlyset");
        form.destroy();
    });

    QUnit.test('default_getareferencefieldinax2m',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.fields.turtles.default=[
            [0,false,{turtle_ref:'product,37'}]
        ];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="turtles">'+
                            '<tree>'+
                                '<fieldname="turtle_ref"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            viewOptions:{
                mode:'edit',
            },
            archs:{
                'turtle,false,form':'<form><fieldname="display_name"/><fieldname="turtle_ref"/></form>',
            },
        });
        assert.strictEqual(form.$('.o_field_one2many[name="turtles"].o_data_row:first').text(),"xphone",
            "thedefaultvalueshouldbecorrectlyhandled");
        form.destroy();
    });

    QUnit.test('widgetreferenceoncharfield,resetbyonchange',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records[0].foo='product,37';
        this.data.partner.onchanges={
            int_field:function(obj){
                obj.foo='product,'+obj.int_field;
            },
        };

        varnbNameGet=0;
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="int_field"/>'+
                            '<fieldname="foo"widget="reference"readonly="1"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            viewOptions:{
                mode:'edit',
            },
            mockRPC:function(route,args){
                if(args.model==='product'&&args.method==='name_get'){
                    nbNameGet++;
                }
                returnthis._super(route,args);
            },
        });

        assert.strictEqual(nbNameGet,1,
            "thefirstname_getshouldhavebeendone");
        assert.strictEqual(form.$('a[name="foo"]').text(),"xphone",
            "foofieldshouldbecorrectlyset");

        //triggeronchange
        awaittestUtils.fields.editInput(form.$('.o_field_widget[name=int_field]'),41);

        assert.strictEqual(nbNameGet,2,
            "thesecondname_getshouldhavebeendone");
        assert.strictEqual(form.$('a[name="foo"]').text(),"xpad",
            "foofieldshouldhavebeenupdated");
        form.destroy();
    });

    QUnit.test('referenceandlistnavigation',asyncfunction(assert){
        assert.expect(2);

        varlist=awaitcreateView({
            View:ListView,
            model:'partner',
            data:this.data,
            arch:'<treeeditable="bottom"><fieldname="reference"/></tree>',
        });

        //editfirstrow
        awaittestUtils.dom.click(list.$('.o_data_row.o_data_cell').first());
        assert.strictEqual(list.$('.o_data_row:eq(0).o_field_widget[name="reference"]input')[0],document.activeElement,
            'inputoffirstdatarowshouldbeselected');

        //pressTABtogotonextline
        awaittestUtils.dom.triggerEvents(list.$('.o_data_row:eq(0)input:eq(1)'),[$.Event('keydown',{
            which:$.ui.keyCode.TAB,
            keyCode:$.ui.keyCode.TAB,
        })]);
        assert.strictEqual(list.$('.o_data_row:eq(1).o_field_widget[name="reference"]select')[0],document.activeElement,
            'selectofseconddatarowshouldbeselected');

        list.destroy();
    });

    QUnit.test('one2manywithextrafieldfromservernotinform',asyncfunction(assert){
        assert.expect(6);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="p">'+
                        '<tree>'+
                            '<fieldname="datetime"/>'+
                            '<fieldname="display_name"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
            archs:{
                'partner,false,form':'<form>'+
                                        '<fieldname="display_name"/>'+
                                    '</form>'},
            mockRPC:function(route,args){
                if(route==='/web/dataset/call_kw/partner/write'){
                    args.args[1].p[0][2].datetime='2018-04-0512:00:00';
                }
                returnthis._super.apply(this,arguments);
            }
        });

        awaittestUtils.form.clickEdit(form);

        varx2mList=form.$('.o_field_x2many_list[name=p]');

        //Addarecordinthelist
        awaittestUtils.dom.click(x2mList.find('.o_field_x2many_list_row_adda'));

        varmodal=$('.modal-lg');

        varnameInput=modal.find('input.o_input[name=display_name]');
        awaittestUtils.fields.editInput(nameInput,'michelangelo');

        //Savetherecordinthemodal(thoughitisstillvirtual)
        awaittestUtils.dom.click(modal.find('.btn-primary').first());

        assert.equal(x2mList.find('.o_data_row').length,1,
            'Thereshouldbe1recordsinthex2mlist');

        varnewlyAdded=x2mList.find('.o_data_row').eq(0);

        assert.equal(newlyAdded.find('.o_data_cell').first().text(),'',
            'Thecreate_datefieldshouldbeempty');
        assert.equal(newlyAdded.find('.o_data_cell').eq(1).text(),'michelangelo',
            'Thedisplaynamefieldshouldhavetherightvalue');

        //Savethewholething
        awaittestUtils.form.clickSave(form);

        x2mList=form.$('.o_field_x2many_list[name=p]');

        //RedoassertsinROmodeaftersaving
        assert.equal(x2mList.find('.o_data_row').length,1,
            'Thereshouldbe1recordsinthex2mlist');

        newlyAdded=x2mList.find('.o_data_row').eq(0);

        assert.equal(newlyAdded.find('.o_data_cell').first().text(),'04/05/201812:00:00',
            'Thecreate_datefieldshouldhavetherightvalue');
        assert.equal(newlyAdded.find('.o_data_cell').eq(1).text(),'michelangelo',
            'Thedisplaynamefieldshouldhavetherightvalue');

        form.destroy();
    });

    QUnit.test('one2manyinvisibledependsonparentfield',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records[0].p=[2];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="product_id"/>'+
                        '</group>'+
                        '<notebook>'+
                            '<pagestring="Partnerpage">'+
                                '<fieldname="bar"/>'+
                                '<fieldname="p">'+
                                    '<tree>'+
                                        '<fieldname="foo"attrs="{\'column_invisible\':[(\'parent.product_id\',\'!=\',False)]}"/>'+
                                        '<fieldname="bar"attrs="{\'column_invisible\':[(\'parent.bar\',\'=\',False)]}"/>'+
                                    '</tree>'+
                                '</field>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });
        assert.containsN(form,'th',2,
            "shouldbe2columnsintheone2many");
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.many2one.clickOpenDropdown("product_id");
        awaittestUtils.fields.many2one.clickHighlightedItem("product_id");
        awaittestUtils.owlCompatibilityNextTick();
        assert.containsOnce(form,'th:not(.o_list_record_remove_header)',
            "shouldbe1columnwhentheproduct_idisset");
        awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2one[name="product_id"]input'),
            '','keyup');
        awaittestUtils.owlCompatibilityNextTick();
        assert.containsN(form,'th:not(.o_list_record_remove_header)',2,
            "shouldbe2columnsintheone2manywhenproduct_idisnotset");
        awaittestUtils.dom.click(form.$('.o_field_boolean[name="bar"]input'));
        awaittestUtils.owlCompatibilityNextTick();
        assert.containsOnce(form,'th:not(.o_list_record_remove_header)',
            "shouldbe1columnafterthevaluechange");
        form.destroy();
    });

    QUnit.test('one2manycolumnvisiblitydependsononchangeofparentfield',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records[0].p=[2];
        this.data.partner.records[0].bar=false;

        this.data.partner.onchanges.p=function(obj){
            //setbartotruewhenlineisadded
            if(obj.p.length>1&&obj.p[1][2].foo==='Newline'){
                obj.bar=true;
            }
        };

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<form>'+
                    '<fieldname="bar"/>'+
                    '<fieldname="p">'+
                        '<treeeditable="bottom">'+
                            '<fieldname="foo"/>'+
                            '<fieldname="int_field"attrs="{\'column_invisible\':[(\'parent.bar\',\'=\',False)]}"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
        });

        //barisfalsesothereshouldbe1column
        assert.containsOnce(form,'th',
            "shouldbeonly1column('foo')intheone2many");
        assert.containsOnce(form,'.o_list_view.o_data_row',"shouldcontainonerow");

        awaittestUtils.form.clickEdit(form);

        //addanewo2mrecord
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        form.$('.o_field_one2manyinput:first').focus();
        awaittestUtils.fields.editInput(form.$('.o_field_one2manyinput:first'),'Newline');
        awaittestUtils.dom.click(form.$el);

        assert.containsN(form,'th:not(.o_list_record_remove_header)',2,
            "shouldbe2columns('foo'+'int_field')");

        form.destroy();
    });

    QUnit.test('one2manycolumn_invisibleonviewnotinline',asyncfunction(assert){
        assert.expect(4);

        this.data.partner.records[0].p=[2];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="product_id"/>'+
                        '</group>'+
                        '<notebook>'+
                            '<pagestring="Partnerpage">'+
                                '<fieldname="bar"/>'+
                                '<fieldname="p"/>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            archs:{
                'partner,false,list':'<tree>'+
                    '<fieldname="foo"attrs="{\'column_invisible\':[(\'parent.product_id\',\'!=\',False)]}"/>'+
                    '<fieldname="bar"attrs="{\'column_invisible\':[(\'parent.bar\',\'=\',False)]}"/>'+
                '</tree>',
            },
        });
        assert.containsN(form,'th',2,
            "shouldbe2columnsintheone2many");
        awaittestUtils.form.clickEdit(form);
        awaittestUtils.dom.click(form.$('.o_field_many2one[name="product_id"]input'));
        awaittestUtils.fields.many2one.clickHighlightedItem("product_id");
        awaittestUtils.owlCompatibilityNextTick();
        assert.containsOnce(form,'th:not(.o_list_record_remove_header)',
            "shouldbe1columnwhentheproduct_idisset");
        awaittestUtils.fields.editAndTrigger(form.$('.o_field_many2one[name="product_id"]input'),
            '','keyup');
        awaittestUtils.owlCompatibilityNextTick();
        assert.containsN(form,'th:not(.o_list_record_remove_header)',2,
            "shouldbe2columnsintheone2manywhenproduct_idisnotset");
        awaittestUtils.dom.click(form.$('.o_field_boolean[name="bar"]input'));
        awaittestUtils.owlCompatibilityNextTick();
        assert.containsOnce(form,'th:not(.o_list_record_remove_header)',
            "shouldbe1columnafterthevaluechange");
        form.destroy();
    });

    QUnit.test('one2manyfieldineditmodewithoptionalfieldsandtrashicon',asyncfunction(assert){
        assert.expect(13);

        varRamStorageService=AbstractStorageService.extend({
            storage:newRamStorage(),
        });

        this.data.partner.records[0].p=[2];
        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<fieldname="p"/>'+
                '</form>',
            res_id:1,
            archs:{
                'partner,false,list':'<treeeditable="top">'+
                    '<fieldname="foo"optional="show"/>'+
                    '<fieldname="bar"optional="hide"/>'+
                '</tree>',
            },
            services:{
                local_storage:RamStorageService,
            },
        });

        //shouldhave2columns1forfooand1foradvanceddropdown
        assert.containsN(form.$('.o_field_one2many'),'th',1,
            "shouldbe1thintheone2manyinreadonlymode");
        assert.containsOnce(form.$('.o_field_one2manytable'),'.o_optional_columns_dropdown_toggle',
            "shouldhavetheoptionalcolumnsdropdowntoggleinsidethetable");
        awaittestUtils.form.clickEdit(form);
        //shouldhave2columns1forfooand1fortrashicon,dropdownisdisplayed
        //ontrashiconcell,noseparatecellcreatedfortrashiconandadvancedfielddropdown
        assert.containsN(form.$('.o_field_one2many'),'th',2,
            "shouldbe2thintheone2manyeditmode");
        assert.containsN(form.$('.o_field_one2many'),'.o_data_row:first>td',2,
            "shouldbe2cellsintheone2manyineditmode");

        awaittestUtils.dom.click(form.$('.o_field_one2manytable.o_optional_columns_dropdown_toggle'));
        assert.containsN(form.$('.o_field_one2many'),'div.o_optional_columnsdiv.dropdown-item:visible',2,
            "dropdownhave2advancedfieldfoowithcheckedandbarwithunchecked");
        awaittestUtils.dom.click(form.$('div.o_optional_columnsdiv.dropdown-item:eq(1)input'));
        assert.containsN(form.$('.o_field_one2many'),'th',3,
            "shouldbe3thintheone2manyafterenablingbarcolumnfromadvanceddropdown");

        awaittestUtils.dom.click(form.$('div.o_optional_columnsdiv.dropdown-item:firstinput'));
        assert.containsN(form.$('.o_field_one2many'),'th',2,
            "shouldbe2thintheone2manyafterdisablingfoocolumnfromadvanceddropdown");

        assert.containsN(form.$('.o_field_one2many'),'div.o_optional_columnsdiv.dropdown-item:visible',2,
            "dropdownisstillopen");
        awaittestUtils.dom.click(form.$('.o_field_x2many_list_row_adda'));
        //useofowlCompatibilityNextTickbecausethex2manyfieldisreset,meaningthat
        //1)itslistrendererisupdated(updateStateiscalled):thisisasyncandasit
        //containsaFieldBoolean,whichiswritteninOwl,itcompletesinthenextAnimationFrame
        //2)whenthisisdone,thecontrolpanelisupdated:asitiswritteninowl,thisis
        //doneinthenextAnimationFrame
        //->weneedtowaitfor2nextAnimationFrametoensurethateverythingisfine
        awaittestUtils.owlCompatibilityNextTick();
        assert.containsN(form.$('.o_field_one2many'),'div.o_optional_columnsdiv.dropdown-item:visible',0,
            "dropdownisclosed");
        var$selectedRow=form.$('.o_field_one2manytr.o_selected_row');
        assert.strictEqual($selectedRow.length,1,"shouldhaveselectedrowi.e.editionmode");

        awaittestUtils.dom.click(form.$('.o_field_one2manytable.o_optional_columns_dropdown_toggle'));
        awaittestUtils.dom.click(form.$('div.o_optional_columnsdiv.dropdown-item:firstinput'));
        $selectedRow=form.$('.o_field_one2manytr.o_selected_row');
        assert.strictEqual($selectedRow.length,0,
            "currenteditionmodediscardedwhenselectingadvancedfield");
        assert.containsN(form.$('.o_field_one2many'),'th',3,
            "shouldbe3thintheone2manyafterre-enablingfoocolumnfromadvanceddropdown");

        //checkafterformreloadadvancedcolumnhiddenorshownarestillpreserved
        awaitform.reload();
        assert.containsN(form.$('.o_field_one2many.o_list_view'),'th',3,
            "shouldstillhave3thintheone2manyafterreloadingwholeformview");

        form.destroy();
    });

    QUnit.module('TabNavigation');
    QUnit.test('whenNavigatingtoamany2onewithtabs,itreceivesthefocusandaddsanewline',asyncfunction(assert){
         assert.expect(3);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            viewOptions:{
                mode:'edit',
            },
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="qux"/>'+
                        '</group>'+
                        '<notebook>'+
                            '<pagestring="Partnerpage">'+
                                '<fieldname="turtles">'+
                                    '<treeeditable="bottom">'+
                                        '<fieldname="turtle_foo"/>'+
                                    '</tree>'+
                                '</field>'+
                            '</page>'+
                        '</notebook>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.strictEqual(form.$el.find('input[name="qux"]')[0],
                            document.activeElement,
                            "initially,thefocusshouldbeonthe'qux'fieldbecauseitisthefirstinput");
        awaittestUtils.fields.triggerKeydown(form.$el.find('input[name="qux"]'),'tab');
        assert.strictEqual(assert.strictEqual(form.$el.find('input[name="turtle_foo"]')[0],
                            document.activeElement,
                            "aftertab,thefocusshouldbeonthemany2oneonthefirstinputofthenewlyaddedline"));

        form.destroy();
    });

    QUnit.test('whenNavigatingtoamanytoonewithtabs,itplacesthefocusonthefirstvisiblefield',asyncfunction(assert){
        assert.expect(3);

       varform=awaitcreateView({
           View:FormView,
           model:'partner',
           viewOptions:{
               mode:'edit',
           },
           data:this.data,
           arch:'<formstring="Partners">'+
                   '<sheet>'+
                       '<group>'+
                           '<fieldname="qux"/>'+
                       '</group>'+
                       '<notebook>'+
                           '<pagestring="Partnerpage">'+
                               '<fieldname="turtles">'+
                                   '<treeeditable="bottom">'+
                                       '<fieldname="turtle_bar"invisible="1"/>'+
                                       '<fieldname="turtle_foo"/>'+
                                   '</tree>'+
                               '</field>'+
                           '</page>'+
                       '</notebook>'+
                   '</sheet>'+
               '</form>',
           res_id:1,
       });

       assert.strictEqual(form.$el.find('input[name="qux"]')[0],
                           document.activeElement,
                           "initially,thefocusshouldbeonthe'qux'fieldbecauseitisthefirstinput");
       form.$el.find('input[name="qux"]').trigger($.Event('keydown',{
           which:$.ui.keyCode.TAB,
           keyCode:$.ui.keyCode.TAB,
       }));
       awaittestUtils.owlCompatibilityNextTick();
       awaittestUtils.dom.click(document.activeElement);
       assert.strictEqual(assert.strictEqual(form.$el.find('input[name="turtle_foo"]')[0],
                           document.activeElement,
                           "aftertab,thefocusshouldbeonthemany2one"));

       form.destroy();
    });

    QUnit.test('whenNavigatingtoamany2onewithtabs,notfillinganyfieldandhittingtab,'+
            'weshouldnotaddafirstlinebutnavigatetothenextcontrol',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records[0].turtles=[];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            viewOptions:{
                mode:'edit',
            },
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="qux"/>'+
                        '</group>'+
                        '<notebook>'+
                            '<pagestring="Partnerpage">'+
                                '<fieldname="turtles">'+
                                    '<treeeditable="bottom">'+
                                        '<fieldname="turtle_foo"/>'+
                                        '<fieldname="turtle_description"/>'+
                                    '</tree>'+
                                '</field>'+
                            '</page>'+
                        '</notebook>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
        });

        assert.strictEqual(form.$el.find('input[name="qux"]')[0],
            document.activeElement,
            "initially,thefocusshouldbeonthe'qux'fieldbecauseitisthefirstinput");
        awaittestUtils.fields.triggerKeydown(form.$el.find('input[name="qux"]'),'tab');

        //skipsthefirstfieldoftheone2many
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'tab');
        //skipsthesecond(andlast)fieldoftheone2many
        awaittestUtils.fields.triggerKeydown($(document.activeElement),'tab');
        assert.strictEqual(assert.strictEqual(form.$el.find('input[name="foo"]')[0],
            document.activeElement,
            "aftertab,thefocusshouldbeonthemany2one"));

        form.destroy();
    });

    QUnit.test('whenNavigatingtoamanytoonewithtabs,editinginapopup,thepopupshouldreceivethefocusthengiveitback',asyncfunction(assert){
        assert.expect(3);

        this.data.partner.records[0].turtles=[];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            viewOptions:{
                mode:'edit',
            },
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<group>'+
                            '<fieldname="qux"/>'+
                        '</group>'+
                        '<notebook>'+
                            '<pagestring="Partnerpage">'+
                                '<fieldname="turtles">'+
                                    '<tree>'+
                                        '<fieldname="turtle_foo"/>'+
                                        '<fieldname="turtle_description"/>'+
                                    '</tree>'+
                                '</field>'+
                            '</page>'+
                        '</notebook>'+
                        '<group>'+
                            '<fieldname="foo"/>'+
                        '</group>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            archs:{
                'turtle,false,form':'<form><group><fieldname="turtle_foo"/><fieldname="turtle_int"/></group></form>',
            },
        });

        assert.strictEqual(form.$el.find('input[name="qux"]')[0],
            document.activeElement,
            "initially,thefocusshouldbeonthe'qux'fieldbecauseitisthefirstinput");
        awaittestUtils.fields.triggerKeydown(form.$el.find('input[name="qux"]'),'tab');
        assert.strictEqual($.find('input[name="turtle_foo"]')[0],
            document.activeElement,
            "whentheone2manyreceivedthefocus,thepopupshouldopenbecauseitautomaticallyaddsanewline");

        awaittestUtils.fields.triggerKeydown($('input[name="turtle_foo"]'),'escape');
        assert.strictEqual(form.$el.find('.o_field_x2many_list_row_adda')[0],
            document.activeElement,
            "afterescape,thefocusshouldbebackontheaddnewlinelink");

       form.destroy();
    });

    QUnit.test('whencreatinganewmany2oneonax2manythendiscardingitimmediatelywithESCAPE,itshouldnotcrash',asyncfunction(assert){
        assert.expect(1);

        this.data.partner.records[0].turtles=[];

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            viewOptions:{
                mode:'edit',
            },
            data:this.data,
            arch:'<formstring="Partners">'+
                    '<sheet>'+
                        '<fieldname="turtles">'+
                            '<treeeditable="top">'+
                                '<fieldname="turtle_foo"/>'+
                                '<fieldname="turtle_trululu"/>'+
                            '</tree>'+
                        '</field>'+
                    '</sheet>'+
                '</form>',
            res_id:1,
            archs:{
                'partner,false,form':'<form><group><fieldname="foo"/><fieldname="bar"/></group></form>'
            },
        });

        //addanewline
        awaittestUtils.dom.click(form.$el.find('.o_field_x2many_list_row_add>a'));

        //openthefieldturtle_trululu(one2many)
        varM2O_DELAY=relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY;
        relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=0;
        awaittestUtils.dom.click(form.$el.find('.o_input_dropdown>input'));

        awaittestUtils.fields.editInput(form.$('.o_field_many2oneinput'),'ABC');
        //clickcreateandedit
        awaittestUtils.dom.click($('.ui-autocomplete.ui-menu-itema:contains(Createand)').trigger('mouseenter'));

        //hitescapeimmediately
        varescapeKey=$.ui.keyCode.ESCAPE;
        $(document.activeElement).trigger(
            $.Event('keydown',{which:escapeKey,keyCode:escapeKey}));

        assert.ok('didnotcrash');
        relationalFields.FieldMany2One.prototype.AUTOCOMPLETE_DELAY=M2O_DELAY;
        form.destroy();
    });

    QUnit.test('navigatingthroughaneditablelistwithcustomcontrols[REQUIREFOCUS]',asyncfunction(assert){
        assert.expect(5);

        varform=awaitcreateView({
            View:FormView,
            model:'partner',
            data:this.data,
            arch:
                '<form>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="p">'+
                        '<treeeditable="bottom">'+
                            '<control>'+
                                '<createstring="Custom1"context="{\'default_foo\':\'1\'}"/>'+
                                '<createstring="Custom2"context="{\'default_foo\':\'2\'}"/>'+
                            '</control>'+
                            '<fieldname="foo"/>'+
                        '</tree>'+
                    '</field>'+
                    '<fieldname="int_field"/>'+
                '</form>',
            viewOptions:{
                mode:'edit',
            },
        });

        assert.strictEqual(document.activeElement,form.$('.o_field_widget[name="display_name"]')[0],
            "firstinputshouldbefocusedbydefault");

        //presstabtonavigatetothelist
        awaittestUtils.fields.triggerKeydown(
            form.$('.o_field_widget[name="display_name"]'),'tab');
        //pressESCtocancel1stcontrolclick(create)
        awaittestUtils.fields.triggerKeydown(
            form.$('.o_data_cellinput'),'escape');
        assert.strictEqual(document.activeElement,form.$('.o_field_x2many_list_row_adda:first')[0],
            "firsteditablelistcontrolshouldnowhavethefocus");

        //pressrighttofocusthesecondcontrol
        awaittestUtils.fields.triggerKeydown(
            form.$('.o_field_x2many_list_row_adda:first'),'right');
        assert.strictEqual(document.activeElement,form.$('.o_field_x2many_list_row_adda:nth(1)')[0],
            "secondeditablelistcontrolshouldnowhavethefocus");

        //presslefttocomebacktofirstcontrol
        awaittestUtils.fields.triggerKeydown(
            form.$('.o_field_x2many_list_row_adda:nth(1)'),'left');
        assert.strictEqual(document.activeElement,form.$('.o_field_x2many_list_row_adda:first')[0],
            "firsteditablelistcontrolshouldnowhavethefocus");

        //presstabtoleavethelist
        awaittestUtils.fields.triggerKeydown(
            form.$('.o_field_x2many_list_row_adda:first'),'tab');
        assert.strictEqual(document.activeElement,form.$('.o_field_widget[name="int_field"]')[0],
            "lastinputshouldnowbefocused");

        form.destroy();
    });
    QUnit.test('Checkonchangewithtwoconsecutivemany2one',asyncfunction(assert){
        assert.expect(2);
        this.data.product.fields.product_partner_ids={string:"User",type:'one2many',relation:'partner'};
        this.data.product.records[0].product_partner_ids=[1];
        this.data.product.records[1].product_partner_ids=[2];
        this.data.turtle.fields.product_ids={string:"Product",type:"one2many",relation:'product'};
        this.data.turtle.fields.user_ids={string:"Product",type:"one2many",relation:'user'};
        this.data.turtle.onchanges={
            turtle_trululu:function(record){
                record.product_ids=[37];
                record.user_ids=[17,19];
            },
        };
        varform=awaitcreateView({
            View:FormView,
            model:'turtle',
            data:this.data,
            arch:
                '<formstring="Turtles">'+
                    '<fieldstring="Product"name="turtle_trululu"/>'+
                    '<fieldreadonly="1"string="Relatedfield"name="product_ids">'+
                        '<tree>'+
                            '<fieldwidget="many2many_tags"name="product_partner_ids"/>'+
                        '</tree>'+
                    '</field>'+
                    '<fieldreadonly="1"string="Secondrelatedfield"name="user_ids">'+
                        '<tree>'+
                            '<fieldwidget="many2many_tags"name="partner_ids"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
            res_id:1,
        });

        awaittestUtils.form.clickEdit(form);
        awaittestUtils.fields.many2one.clickOpenDropdown("turtle_trululu");
        awaittestUtils.fields.many2one.searchAndClickItem('turtle_trululu',{search:'firstrecord'});

        constgetElementTextContent=name=>[...document.querySelectorAll(`.o_field_many2manytags[name="${name}"].badge.o_tag_color_0>span`)]
            .map(x=>x.textContent);
        assert.deepEqual(
            getElementTextContent('product_partner_ids'),
            ['firstrecord'],
            "shouldhavethecorrectvalueinthemany2manytagwidget");
        assert.deepEqual(
            getElementTextContent('partner_ids'),
            ['firstrecord','secondrecord'],
            "shouldhavethecorrectvaluesinthemany2manytagwidget");
        form.destroy();
    });
});
});
});
