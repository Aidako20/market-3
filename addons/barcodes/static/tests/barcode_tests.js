flectra.define('barcodes.tests',function(require){
"usestrict";

varbarcodeEvents=require('barcodes.BarcodeEvents');

varAbstractField=require('web.AbstractField');
varfieldRegistry=require('web.field_registry');
varFormController=require('web.FormController');
varFormView=require('web.FormView');
vartestUtils=require('web.test_utils');
varNotificationService=require('web.NotificationService');

varcreateView=testUtils.createView;
vartriggerKeypressEvent=testUtils.dom.triggerKeypressEvent;

QUnit.module('Barcodes',{
    beforeEach:function(){
        this.data={
            order:{
                fields:{
                    _barcode_scanned:{string:'Barcodescanned',type:'char'},
                    line_ids:{string:'Orderlines',type:'one2many',relation:'order_line'},
                },
                records:[
                    {id:1,line_ids:[1,2]},
                ],
            },
            order_line:{
                fields:{
                    product_id:{string:'Product',type:'many2one',relation:'product'},
                    product_barcode:{string:'ProductBarcode',type:'char'},
                    quantity:{string:'Quantity',type:'integer'},
                },
                records:[
                    {id:1,product_id:1,quantity:0,product_barcode:'1234567890'},
                    {id:2,product_id:2,quantity:0,product_barcode:'0987654321'},
                ],
            },
            product:{
                fields:{
                    name:{string:"Productname",type:"char"},
                    int_field:{string:"Integer",type:"integer"},
                    barcode:{string:"Barcode",type:"char"},
                },
                records:[
                    {id:1,name:"LargeCabinet",barcode:'1234567890'},
                    {id:2,name:"CabinetwithDoors",barcode:'0987654321'},
                ],
            },
        };
    }
});

QUnit.test('Buttonwithbarcode_trigger',asyncfunction(assert){
    assert.expect(2);

    varform=awaitcreateView({
        View:FormView,
        model:'product',
        data:this.data,
        arch:'<form>'+
                '<header>'+
                    '<buttonname="do_something"string="Validate"type="object"barcode_trigger="doit"/>'+
                    '<buttonname="do_something_else"string="Validate"type="object"invisible="1"barcode_trigger="dothat"/>'+
                '</header>'+
            '</form>',
        res_id:2,
        services:{
            notification:NotificationService.extend({
                notify:function(params){
                    assert.step(params.type);
                }
            }),
        },
        intercepts:{
            execute_action:function(event){
                assert.strictEqual(event.data.action_data.name,'do_something',
                    "do_somethingmethodcallverified");
            },
        },
    });

    //O-BTN.doit
    _.each(['O','-','B','T','N','.','d','o','i','t','Enter'],triggerKeypressEvent);
    //O-BTN.dothat(shouldnotcallexecute_actionasthebuttonisn'tvisible)
    _.each(['O','-','B','T','N','.','d','o','t','h','a','t','Enter'],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.verifySteps([],"nowarningshouldbedisplayed");

    form.destroy();
});

QUnit.test('edit,saveandcancelbuttons',asyncfunction(assert){
    assert.expect(6);

    varform=awaitcreateView({
        View:FormView,
        model:'product',
        data:this.data,
        arch:'<form><fieldname="display_name"/></form>',
        mockRPC:function(route,args){
            if(args.method==='write'){
                assert.step('save');
            }
            returnthis._super.apply(this,arguments);
        },
        res_id:1,
    });

    //O-CMD.EDIT
    _.each(["O","-","C","M","D",".","E","D","I","T","Enter"],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.containsOnce(form,".o_form_editable",
        "shouldhaveswitchedto'edit'mode");
    //dummychangetocheckthatitactuallysaves
    awaittestUtils.fields.editInput(form.$('.o_field_widget'),'test');
    //O-CMD.SAVE
    _.each(["O","-","C","M","D",".","S","A","V","E","Enter"],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.containsOnce(form,".o_form_readonly",
        "shouldhaveswitchedto'readonly'mode");
    assert.verifySteps(['save'],'shouldhavesaved');

    //O-CMD.EDIT
    _.each(["O","-","C","M","D",".","E","D","I","T","Enter"],triggerKeypressEvent);
    awaittestUtils.nextTick();
    //dummychangetocheckthatitcorrectlydiscards
    awaittestUtils.fields.editInput(form.$('.o_field_widget'),'test');
    //O-CMD.CANCEL
    _.each(["O","-","C","M","D",".","D","I","S","C","A","R","D","Enter"],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.containsOnce(form,".o_form_readonly",
        "shouldhaveswitchedto'readonly'mode");
    assert.verifySteps([],'shouldnothavesaved');

    form.destroy();
});

QUnit.test('pagerbuttons',asyncfunction(assert){
    assert.expect(5);

    varform=awaitcreateView({
        View:FormView,
        model:'product',
        data:this.data,
        arch:'<form><fieldname="display_name"/></form>',
        res_id:1,
        viewOptions:{
            ids:[1,2],
            index:0,
        },
    });

    assert.strictEqual(form.$('.o_field_widget').text(),'LargeCabinet');
    //O-CMD.PAGER-NEXT
    _.each(["O","-","C","M","D",".","N","E","X","T","Enter"],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.strictEqual(form.$('.o_field_widget').text(),'CabinetwithDoors');
    //O-CMD.PAGER-PREV
    _.each(["O","-","C","M","D",".","P","R","E","V","Enter"],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.strictEqual(form.$('.o_field_widget').text(),'LargeCabinet');
    //O-CMD.PAGER-LAST
    _.each(["O","-","C","M","D",".","P","A","G","E","R","-","L","A","S","T","Enter"],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.strictEqual(form.$('.o_field_widget').text(),'CabinetwithDoors');
    //O-CMD.PAGER-FIRST
    _.each(["O","-","C","M","D",".","P","A","G","E","R","-","F","I","R","S","T","Enter"],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.strictEqual(form.$('.o_field_widget').text(),'LargeCabinet');

    form.destroy();
});

QUnit.test('donoupdateformtwiceafteracommandbarcodescanned',asyncfunction(assert){
    assert.expect(7);

    vardelay=barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms;
    barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms=0;
    testUtils.mock.patch(FormController,{
        update:function(){
            assert.step('update');
            returnthis._super.apply(this,arguments);
        },
    });

    varform=awaitcreateView({
        View:FormView,
        model:'product',
        data:this.data,
        arch:'<form>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="int_field"widget="field_float_scannable"/>'+
                '</form>',
        mockRPC:function(route,args){
            if(args.method==='read'){
                assert.step('read');
            }
            returnthis._super.apply(this,arguments);
        },
        res_id:1,
        viewOptions:{
            ids:[1,2],
            index:0,
        },
    });

    assert.verifySteps(['read'],"updateshouldnothavebeencalledyet");

    //switchtonextrecord
    _.each(["O","-","C","M","D",".","N","E","X","T","Enter"],triggerKeypressEvent);
    awaittestUtils.nextTick();
    //afirstupdateisdonetoreloadthedata(thusfollowedbyaread),but
    //updateshouldn'tbecalledafterwards
    assert.verifySteps(['update','read']);

    _.each(['5','4','3','9','8','2','6','7','1','2','5','2','Enter'],triggerKeypressEvent);
    awaittestUtils.nextTick();
    //arealbarcodehasbeenscanned->anupdateshouldberequested(with
    //optionreload='false',soitisn'tfollowedbyaread)
    assert.verifySteps(['update']);

    form.destroy();
    barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms=delay;
    testUtils.mock.unpatch(FormController);
});

QUnit.test('widgetfield_float_scannable',asyncfunction(assert){
    vardone=assert.async();
    assert.expect(11);

    vardelay=barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms;
    barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms=0;

    this.data.product.records[0].int_field=4;
    this.data.product.onchanges={
        int_field:function(){},
    };

    varform=awaitcreateView({
        View:FormView,
        model:'product',
        data:this.data,
        arch:'<form>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="int_field"widget="field_float_scannable"/>'+
                '</form>',
        mockRPC:function(route,args){
            if(args.method==='onchange'){
                assert.step('onchange');
                assert.strictEqual(args.args[1].int_field,426,
                    "shouldsendcorrectvalueforint_field");
            }
            returnthis._super.apply(this,arguments);
        },
        fieldDebounce:1000,
        res_id:1,
    });

    assert.strictEqual(form.$('.o_field_widget[name=int_field]').text(),'4',
        "shoulddisplaythecorrectvalueinreadonly");

    awaittestUtils.form.clickEdit(form);

    assert.strictEqual(form.$('.o_field_widget[name=int_field]').val(),'4',
        "shoulddisplaythecorrectvalueinedit");

    //simulateskeypresseventsintheinputtoreplace0.00by26(shouldnottriggeronchanges)
    form.$('.o_field_widget[name=int_field]').focus();
    assert.strictEqual(form.$('.o_field_widget[name=int_field]').get(0),document.activeElement,
        "intfieldshouldbefocused");
    form.$('.o_field_widget[name=int_field]').trigger({type:'keypress',which:50,keyCode:50});//2
    awaittestUtils.nextTick();
    assert.strictEqual(form.$('.o_field_widget[name=int_field]').get(0),document.activeElement,
        "intfieldshouldstillbefocused");
    form.$('.o_field_widget[name=int_field]').trigger({type:'keypress',which:54,keyCode:54});//6
    awaittestUtils.nextTick();
    assert.strictEqual(form.$('.o_field_widget[name=int_field]').get(0),document.activeElement,
        "intfieldshouldstillbefocused");

    setTimeout(asyncfunction(){
        assert.strictEqual(form.$('.o_field_widget[name=int_field]').val(),'426',
            "shoulddisplaythecorrectvalueinedit");
        assert.strictEqual(form.$('.o_field_widget[name=int_field]').get(0),document.activeElement,
        "intfieldshouldstillbefocused");

        assert.verifySteps([],'shouldnothavedoneanyonchangeRPC');

        form.$('.o_field_widget[name=int_field]').trigger('change');//shouldtriggertheonchange
        awaittestUtils.nextTick();

        assert.verifySteps(['onchange'],'shouldhavedonetheonchangeRPC');

        form.destroy();
        barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms=delay;
        done();
    });
});

QUnit.test('widgetbarcode_handler',asyncfunction(assert){
    assert.expect(4);

    vardelay=barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms;
    barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms=0;

    this.data.product.fields.barcode_scanned={string:"Scannedbarcode",type:"char"};
    this.data.product.onchanges={
        barcode_scanned:function(obj){
            //simulateanonchangethatincrementtheint_fieldvalue
            //ateachbarcodescanned
            obj.int_field=obj.int_field+1;
        },
    };

    varform=awaitcreateView({
        View:FormView,
        model:'product',
        data:this.data,
        arch:'<form>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="int_field"/>'+
                    '<fieldname="barcode_scanned"widget="barcode_handler"/>'+
                '</form>',
        mockRPC:function(route,args){
            if(args.method==='onchange'){
                assert.step('onchange');
            }
            returnthis._super.apply(this,arguments);
        },
        res_id:1,
        viewOptions:{
            mode:'edit',
        },
    });

    assert.strictEqual(form.$('.o_field_widget[name=int_field]').val(),'0',
        "initialvalueshouldbecorrect");

    _.each(['5','4','3','9','8','2','6','7','1','2','5','2','Enter'],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.strictEqual(form.$('.o_field_widget[name=int_field]').val(),'1',
        "valueshouldhavebeenincremented");

    assert.verifySteps(['onchange'],"anonchangeshouldhavebeendone");

    form.destroy();
    barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms=delay;
});

QUnit.test('specificationofwidgetbarcode_handler',asyncfunction(assert){
    assert.expect(5);

    vardelay=barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms;
    barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms=0;

    //Defineaspecificbarcode_handlerwidgetforthistestcase
    varTestBarcodeHandler=AbstractField.extend({
        init:function(){
            this._super.apply(this,arguments);

            this.trigger_up('activeBarcode',{
                name:'test',
                fieldName:'line_ids',
                quantity:'quantity',
                commands:{
                    barcode:'_barcodeAddX2MQuantity',
                }
            });
        },
    });
    fieldRegistry.add('test_barcode_handler',TestBarcodeHandler);

    varform=awaitcreateView({
        View:FormView,
        model:'order',
        data:this.data,
        arch:'<form>'+
                    '<fieldname="_barcode_scanned"widget="test_barcode_handler"/>'+
                    '<fieldname="line_ids">'+
                        '<tree>'+
                            '<fieldname="product_id"/>'+
                            '<fieldname="product_barcode"invisible="1"/>'+
                            '<fieldname="quantity"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
        mockRPC:function(route,args){
            if(args.method==='onchange'){
                assert.notOK(true,"shouldnotdoanyonchangeRPC");
            }
            if(args.method==='write'){
                assert.deepEqual(args.args[1].line_ids,[
                    [1,1,{quantity:2}],[1,2,{quantity:1}],
                ],"shouldhavegeneratedthecorrectcommands");
            }
            returnthis._super.apply(this,arguments);
        },
        res_id:1,
        viewOptions:{
            mode:'edit',
        },
    });

    assert.containsN(form,'.o_data_row',2,
        "one2manyshouldcontain2rows");

    //scantwiceproduct1
    _.each(['1','2','3','4','5','6','7','8','9','0','Enter'],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.strictEqual(form.$('.o_data_row:first.o_data_cell:nth(1)').text(),'1',
        "quantityoflineoneshouldhavebeenincremented");
    _.each(['1','2','3','4','5','6','7','8','9','0','Enter'],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.strictEqual(form.$('.o_data_row:first.o_data_cell:nth(1)').text(),'2',
        "quantityoflineoneshouldhavebeenincremented");

    //scanonceproduct2
    _.each(['0','9','8','7','6','5','4','3','2','1','Enter'],triggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.strictEqual(form.$('.o_data_row:nth(1).o_data_cell:nth(1)').text(),'1',
        "quantityoflineoneshouldhavebeenincremented");

    awaittestUtils.form.clickSave(form);

    form.destroy();
    barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms=delay;
    deletefieldRegistry.map.test_barcode_handler;
});

QUnit.test('specificationofwidgetbarcode_handlerwithkeypressandnotifyChange',asyncfunction(assert){
    assert.expect(6);
    vardone=assert.async();

    vardelay=barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms;
    barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms=0;

    this.data.order.onchanges={
        _barcode_scanned:function(){},
    };

    //Defineaspecificbarcode_handlerwidgetforthistestcase
    varTestBarcodeHandler=AbstractField.extend({
        init:function(){
            this._super.apply(this,arguments);

            this.trigger_up('activeBarcode',{
                name:'test',
                fieldName:'line_ids',
                notifyChange:false,
                setQuantityWithKeypress:true,
                quantity:'quantity',
                commands:{
                    barcode:'_barcodeAddX2MQuantity',
                }
            });
        },
    });
    fieldRegistry.add('test_barcode_handler',TestBarcodeHandler);

    varform=awaitcreateView({
        View:FormView,
        model:'order',
        data:this.data,
        arch:'<form>'+
                    '<fieldname="_barcode_scanned"widget="test_barcode_handler"/>'+
                    '<fieldname="line_ids">'+
                        '<tree>'+
                            '<fieldname="product_id"/>'+
                            '<fieldname="product_barcode"invisible="1"/>'+
                            '<fieldname="quantity"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
        mockRPC:function(route,args){
            assert.step(args.method);
            returnthis._super.apply(this,arguments);
        },
        res_id:1,
        viewOptions:{
            mode:'edit',
        },
    });
    _.each(['1','2','3','4','5','6','7','8','9','0','Enter'],triggerKeypressEvent);
    awaittestUtils.nextTick();
    //Quantitylistenershouldopenadialog.
    triggerKeypressEvent('5');
    awaittestUtils.nextTick();

    setTimeout(asyncfunction(){
        varkeycode=$.ui.keyCode.ENTER;

        assert.strictEqual($('.modal.modal-body').length,1,'shouldopenamodalwithaquantityasinput');
        assert.strictEqual($('.modal.modal-body.o_set_qty_input').val(),'5','thequantitybydefaultinthemodalshoudbe5');

        $('.modal.modal-body.o_set_qty_input').val('7');
        awaittestUtils.nextTick();

        $('.modal.modal-body.o_set_qty_input').trigger($.Event('keypress',{which:keycode,keyCode:keycode}));
        awaittestUtils.nextTick();
        assert.strictEqual(form.$('.o_data_row.o_data_cell:nth(1)').text(),'7',
            "quantitycheckedshouldbe7");

        assert.verifySteps(['read','read']);

        form.destroy();
        barcodeEvents.BarcodeEvents.max_time_between_keys_in_ms=delay;
        deletefieldRegistry.map.test_barcode_handler;
        done();
    });
});
QUnit.test('barcode_scannedonlytriggererrorforactiveview',asyncfunction(assert){
    assert.expect(2);

    this.data.order_line.fields._barcode_scanned={string:'Barcodescanned',type:'char'};

    varform=awaitcreateView({
        View:FormView,
        model:'order',
        data:this.data,
        arch:'<form>'+
                    '<fieldname="_barcode_scanned"widget="barcode_handler"/>'+
                    '<fieldname="line_ids">'+
                        '<tree>'+
                            '<fieldname="product_id"/>'+
                            '<fieldname="product_barcode"invisible="1"/>'+
                            '<fieldname="quantity"/>'+
                        '</tree>'+
                    '</field>'+
                '</form>',
        archs:{
            "order_line,false,form":
                '<formstring="orderline">'+
                    '<fieldname="_barcode_scanned"widget="barcode_handler"/>'+
                    '<fieldname="product_id"/>'+
                '</form>',
        },
        res_id:1,
        services:{
            notification:NotificationService.extend({
                notify:function(params){
                    assert.step(params.type);
                }
            }),
        },
        viewOptions:{
            mode:'edit',
        },
    });

    awaittestUtils.dom.click(form.$('.o_data_row:first'));

    //Wedonottriggeronthebodysincemodaland
    //formviewarebothinsideit.
    functionmodalTriggerKeypressEvent(char){
        varkeycode;
        if(char==="Enter"){
            keycode=$.ui.keyCode.ENTER;
        }else{
            keycode=char.charCodeAt(0);
        }
        return$('.modal').trigger($.Event('keypress',{which:keycode,keyCode:keycode}));
    }
    _.each(['O','-','B','T','N','.','c','a','n','c','e','l','Enter'],modalTriggerKeypressEvent);
    awaittestUtils.nextTick();
    assert.verifySteps(['danger'],"onlyoneeventshouldbetriggered");
    form.destroy();
});
});
