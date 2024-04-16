flectra.define('web.calendar_tests',function(require){
"usestrict";

constAbstractField=require('web.AbstractField');
constfieldRegistry=require('web.field_registry');
varAbstractStorageService=require('web.AbstractStorageService');
varCalendarView=require('web.CalendarView');
varCalendarRenderer=require('web.CalendarRenderer');
varDialog=require('web.Dialog');
varViewDialogs=require('web.view_dialogs');
varfieldUtils=require('web.field_utils');
varmixins=require('web.mixins');
varRamStorage=require('web.RamStorage');
vartestUtils=require('web.test_utils');
varsession=require('web.session');

varcreateActionManager=testUtils.createActionManager;

CalendarRenderer.include({
    getAvatars:function(){
        varres=this._super.apply(this,arguments);
        for(varkinres){
            res[k]=res[k].replace(/src="([^"]+)"/,'data-src="\$1"');
        }
        returnres;
    }
});


varcreateCalendarView=testUtils.createCalendarView;

//2016-12-1208:00:00
varinitialDate=newDate(2016,11,12,8,0,0);
initialDate=newDate(initialDate.getTime()-initialDate.getTimezoneOffset()*60*1000);

function_preventScroll(ev){
    ev.stopImmediatePropagation();
}

QUnit.module('Views',{
    beforeEach:function(){
        window.addEventListener('scroll',_preventScroll,true);
        session.uid=-1;//TOCHECK
        this.data={
            event:{
                fields:{
                    id:{string:"ID",type:"integer"},
                    user_id:{string:"user",type:"many2one",relation:'user',default:session.uid},
                    partner_id:{string:"user",type:"many2one",relation:'partner',related:'user_id.partner_id',default:1},
                    name:{string:"name",type:"char"},
                    start_date:{string:"startdate",type:"date"},
                    stop_date:{string:"stopdate",type:"date"},
                    start:{string:"startdatetime",type:"datetime"},
                    stop:{string:"stopdatetime",type:"datetime"},
                    delay:{string:"delay",type:"float"},
                    allday:{string:"allday",type:"boolean"},
                    partner_ids:{string:"attendees",type:"one2many",relation:'partner',default:[[6,0,[1]]]},
                    type:{string:"type",type:"integer"},
                    event_type_id:{string:"Event_Type",type:"many2one",relation:'event_type'},
                    color: {string:"Color",type:"integer",related:'event_type_id.color'},
                },
                records:[
                    {id:1,user_id:session.uid,partner_id:1,name:"event1",start:"2016-12-1100:00:00",stop:"2016-12-1100:00:00",allday:false,partner_ids:[1,2,3],type:1},
                    {id:2,user_id:session.uid,partner_id:1,name:"event2",start:"2016-12-1210:55:05",stop:"2016-12-1214:55:05",allday:false,partner_ids:[1,2],type:3},
                    {id:3,user_id:4,partner_id:4,name:"event3",start:"2016-12-1215:55:05",stop:"2016-12-1216:55:05",allday:false,partner_ids:[1],type:2},
                    {id:4,user_id:session.uid,partner_id:1,name:"event4",start:"2016-12-1415:55:05",stop:"2016-12-1418:55:05",allday:true,partner_ids:[1],type:2},
                    {id:5,user_id:4,partner_id:4,name:"event5",start:"2016-12-1315:55:05",stop:"2016-12-2018:55:05",allday:false,partner_ids:[2,3],type:2},
                    {id:6,user_id:session.uid,partner_id:1,name:"event6",start:"2016-12-1808:00:00",stop:"2016-12-1809:00:00",allday:false,partner_ids:[3],type:3},
                    {id:7,user_id:session.uid,partner_id:1,name:"event7",start:"2016-11-1408:00:00",stop:"2016-11-1617:00:00",allday:false,partner_ids:[2],type:1},
                ],
                check_access_rights:function(){
                    returnPromise.resolve(true);
                }
            },
            user:{
                fields:{
                    id:{string:"ID",type:"integer"},
                    display_name:{string:"Displayedname",type:"char"},
                    partner_id:{string:"partner",type:"many2one",relation:'partner'},
                    image:{string:"image",type:"integer"},
                },
                records:[
                    {id:session.uid,display_name:"user1",partner_id:1},
                    {id:4,display_name:"user4",partner_id:4},
                ]
            },
            partner:{
                fields:{
                    id:{string:"ID",type:"integer"},
                    display_name:{string:"Displayedname",type:"char"},
                    image:{string:"image",type:"integer"},
                },
                records:[
                    {id:1,display_name:"partner1",image:'AAA'},
                    {id:2,display_name:"partner2",image:'BBB'},
                    {id:3,display_name:"partner3",image:'CCC'},
                    {id:4,display_name:"partner4",image:'DDD'}
                ]
            },
            event_type:{
                fields:{
                    id:{string:"ID",type:"integer"},
                    display_name:{string:"Displayedname",type:"char"},
                    color:{string:"Color",type:"integer"},
                },
                records:[
                    {id:1,display_name:"EventType1",color:1},
                    {id:2,display_name:"EventType2",color:2},
                    {id:3,display_name:"EventType3(color4)",color:4},
                ]
            },
            filter_partner:{
                fields:{
                    id:{string:"ID",type:"integer"},
                    user_id:{string:"user",type:"many2one",relation:'user'},
                    partner_id:{string:"partner",type:"many2one",relation:'partner'},
                },
                records:[
                    {id:1,user_id:session.uid,partner_id:1},
                    {id:2,user_id:session.uid,partner_id:2},
                    {id:3,user_id:4,partner_id:3}
                ]
            },
        };
    },
    afterEach:function(){
        window.removeEventListener('scroll',_preventScroll,true);
    },
},function(){

    QUnit.module('CalendarView');

    vararchs={
        "event,false,form":
            '<form>'+
                '<fieldname="name"/>'+
                '<fieldname="allday"/>'+
                '<groupattrs=\'{"invisible":[["allday","=",True]]}\'>'+
                    '<fieldname="start"/>'+
                    '<fieldname="stop"/>'+
                '</group>'+
                '<groupattrs=\'{"invisible":[["allday","=",False]]}\'>'+
                    '<fieldname="start_date"/>'+
                    '<fieldname="stop_date"/>'+
                '</group>'+
            '</form>',
        "event,1,form":
            '<form>'+
                '<fieldname="allday"invisible="1"/>'+
                '<fieldname="start"attrs=\'{"invisible":[["allday","=",false]]}\'/>'+
                '<fieldname="stop"attrs=\'{"invisible":[["allday","=",true]]}\'/>'+
            '</form>',
    };

    QUnit.test('simplecalendarrendering',asyncfunction(assert){
        assert.expect(24);

        this.data.event.records.push({
            id:8,
            user_id:session.uid,
            partner_id:false,
            name:"event7",
            start:"2016-12-1809:00:00",
            stop:"2016-12-1810:00:00",
            allday:false,
            partner_ids:[2],
            type:1
        });

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week"'+
                'attendee="partner_ids"'+
                'color="partner_id">'+
                    '<filtername="user_id"avatar_field="image"/>'+
                    '<fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>'+
                    '<fieldname="partner_id"filters="1"invisible="1"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        assert.ok(calendar.$('.o_calendar_view').find('.fc-view-container').length,
            "shouldinstanceoffullcalendar");

        var$sidebar=calendar.$('.o_calendar_sidebar');

        //testviewscales
        assert.containsN(calendar,'.fc-event',9,
            "shoulddisplay9eventsontheweek(4event+5daysevent)");
        assert.containsN($sidebar,'tr:has(.ui-state-active)td',7,
            "weekscaleshouldhighlight7daysinminicalendar");

        awaittestUtils.dom.click(calendar.$buttons.find('.o_calendar_button_day'));//displayonlyoneday
        assert.containsN(calendar,'.fc-event',2,"shoulddisplay2eventsontheday");
        assert.containsOnce($sidebar,'.o_selected_range',
            "shouldhighlightthetargetdayinminicalendar");

        awaittestUtils.dom.click(calendar.$buttons.find('.o_calendar_button_month'));//displayallthemonth
        assert.containsN(calendar,'.fc-event',7,
            "shoulddisplay7eventsonthemonth(5events+2weekevent-1'event6'isfiltered+1'Undefinedevent')");
        assert.containsN($sidebar,'tda',31,
            "monthscaleshouldhighlightalldaysinminicalendar");

        //testfilters
        assert.containsN($sidebar,'.o_calendar_filter',2,"shoulddisplay2filters");

        var$typeFilter= $sidebar.find('.o_calendar_filter:has(h5:contains(user))');
        assert.ok($typeFilter.length,"shoulddisplay'user'filter");
        assert.containsN($typeFilter,'.o_calendar_filter_item',3,"shoulddisplay3filteritemsfor'user'");

        //filterswhichhasnovalueshouldshowwithstring"Undefined",shouldnothaveanyuserimageandshouldshowatthelast
        assert.strictEqual($typeFilter.find('.o_calendar_filter_item:last').data('value'),false,"filtershavingfalsevalueshouldbedisplayedatlastinfilteritems");
        assert.strictEqual($typeFilter.find('.o_calendar_filter_item:last.o_cw_filter_title').text(),"Undefined","filtershavingfalsevalueshoulddisplay'Undefined'string");
        assert.strictEqual($typeFilter.find('.o_calendar_filter_item:lastlabelimg').length,0,"filtershavingfalsevalueshouldnothaveanyuserimage");

        var$attendeesFilter= $sidebar.find('.o_calendar_filter:has(h5:contains(attendees))');
        assert.ok($attendeesFilter.length,"shoulddisplay'attendees'filter");
        assert.containsN($attendeesFilter,'.o_calendar_filter_item',3,"shoulddisplay3filteritemsfor'attendees'whousewrite_model(2saved+Everything)");
        assert.ok($attendeesFilter.find('.o_field_many2one').length,"shoulddisplayone2manysearchbarfor'attendees'filter");

        assert.containsN(calendar,'.fc-event',7,
            "shoulddisplay7events('event5'countsfor2becauseitspanstwoweeksandthusgeneratetwofc-eventelements)");
        awaittestUtils.dom.click(calendar.$('.o_calendar_filterinput[type="checkbox"]').first());
        assert.containsN(calendar,'.fc-event',4,"shouldnowonlydisplay4event");
        awaittestUtils.dom.click(calendar.$('.o_calendar_filterinput[type="checkbox"]').eq(1));
        assert.containsNone(calendar,'.fc-event',"shouldnotdisplayanyeventanymore");

        //testsearchbarinfilter
        awaittestUtils.dom.click($sidebar.find('input[type="text"]'));
        assert.strictEqual($('ul.ui-autocompleteli:not(.o_m2o_dropdown_option)').length,2,"shoulddisplay2choicesinone2manyautocomplete");//TODO:remove:not(.o_m2o_dropdown_option)becausecan'thave"create&edit"choice
        awaittestUtils.dom.click($('ul.ui-autocompleteli:first'));
        assert.containsN($sidebar,'.o_calendar_filter:has(h5:contains(attendees)).o_calendar_filter_item',4,"shoulddisplay4filteritemsfor'attendees'");
        awaittestUtils.dom.click($sidebar.find('input[type="text"]'));
        assert.strictEqual($('ul.ui-autocompleteli:not(.o_m2o_dropdown_option)').text(),"partner4","shoulddisplaythelastchoiceinone2manyautocomplete");//TODO:remove:not(.o_m2o_dropdown_option)becausecan'thave"create&edit"choice
        awaittestUtils.dom.click($sidebar.find('.o_calendar_filter_item.o_remove').first(),{allowInvisible:true});
        assert.ok($('.modal-footerbutton.btn:contains(Ok)').length,"shoulddisplaytheconfirmmessage");
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Ok)'));
        assert.containsN($sidebar,'.o_calendar_filter:has(h5:contains(attendees)).o_calendar_filter_item',3,"clickonremovethenshoulddisplay3filteritemsfor'attendees'");
        calendar.destroy();
    });

    QUnit.test('deleteattributeoncalendardoesn\'tshowdeletebuttoninpopover',asyncfunction(assert){
        assert.expect(2);

        constcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
                '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'delete="0"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        awaittestUtils.dom.click(calendar.$('.fc-event:contains(event4).fc-content'));

        assert.containsOnce(calendar,'.o_cw_popover',
            "shouldopenapopoverclickingonevent");
        assert.containsNone(calendar,'.o_cw_popover.o_cw_popover_delete',
            "shouldnothavethe'Delete'Button");

        calendar.destroy();
    });

    QUnit.test('breadcrumbsareupdatedwiththedisplayedperiod',asyncfunction(assert){
        assert.expect(4);

        vararchs={
            'event,1,calendar':'<calendardate_start="start"date_stop="stop"all_day="allday"/>',
            'event,false,search':'<search></search>',
        };

        varactions=[{
            id:1,
            flags:{
                initialDate:initialDate,
            },
            name:'MeetingsTest',
            res_model:'event',
            type:'ir.actions.act_window',
            views:[[1,'calendar']],
        }];

        varactionManager=awaitcreateActionManager({
            actions:actions,
            archs:archs,
            data:this.data,
        });

        awaitactionManager.doAction(1);
        awaittestUtils.nextTick();

        //displaysmonthmodebydefault
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),
            'MeetingsTest(Dec11–17,2016)',"shoulddisplaythecurrentweek");

        //switchtodaymode
        awaittestUtils.dom.click($('.o_control_panel.o_calendar_button_day'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),
            'MeetingsTest(December12,2016)',"shoulddisplaythecurrentday");

        //switchtomonthmode
        awaittestUtils.dom.click($('.o_control_panel.o_calendar_button_month'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),
            'MeetingsTest(December2016)',"shoulddisplaythecurrentmonth");

        //switchtoyearmode
        awaittestUtils.dom.click($('.o_control_panel.o_calendar_button_year'));
        assert.strictEqual($('.o_control_panel.breadcrumb-item').text(),
            'MeetingsTest(2016)',"shoulddisplaythecurrentyear");

        actionManager.destroy();
    });

    QUnit.test('createandchangeevents',asyncfunction(assert){
        assert.expect(28);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="month"/>',
            archs:archs,
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(args.args[1],{name:'event4modified'},"shouldupdatetherecord");
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                initialDate:initialDate,
            },
        });

        assert.ok(calendar.$('.fc-dayGridMonth-view').length,"shoulddisplayinmonthmode");

        //clickonanexistingeventtoopentheformViewDialog

        awaittestUtils.dom.click(calendar.$('.fc-event:contains(event4).fc-content'));

        assert.ok(calendar.$('.o_cw_popover').length,"shouldopenapopoverclickingonevent");
        assert.ok(calendar.$('.o_cw_popover.o_cw_popover_edit').length,"popovershouldhaveaneditbutton");
        assert.ok(calendar.$('.o_cw_popover.o_cw_popover_delete').length,"popovershouldhaveadeletebutton");
        assert.ok(calendar.$('.o_cw_popover.o_cw_popover_close').length,"popovershouldhaveaclosebutton");

        awaittestUtils.dom.click(calendar.$('.o_cw_popover.o_cw_popover_edit'));

        assert.ok($('.modal-body').length,"shouldopentheformviewindialogwhenclickonevent");

        awaittestUtils.fields.editInput($('.modal-bodyinput:first'),'event4modified');
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Save)'));

        assert.notOk($('.modal-body').length,"savebuttonshouldclosethemodal");

        //createanewevent,quickcreateonly

        var$cell=calendar.$('.fc-day-grid.fc-row:eq(2).fc-day:eq(2)');

        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();

        assert.ok($('.modal-sm').length,"shouldopenthequickcreatedialog");

        awaittestUtils.fields.editInput($('.modal-bodyinput:first'),'neweventinquickcreate');
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Create)'));

        assert.strictEqual(calendar.$('.fc-event:contains(neweventinquickcreate)').length,1,"shoulddisplaythenewrecordafterquickcreate");
        assert.containsN(calendar,'td.fc-event-container[colspan]',2,"shouldthenewrecordhaveonlyoneday");

        //createanewevent,quickcreateonly(validatedbypressingenterkey)

        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();

        assert.ok($('.modal-sm').length,"shouldopenthequickcreatedialog");

        awaittestUtils.fields.editInput($('.modal-bodyinput:first'),
            'neweventinquickcreatevalidatedbypressingenterkey.');
        $('.modal-bodyinput:first')
            .val('neweventinquickcreatevalidatedbypressingenterkey.')
            .trigger($.Event('keyup',{keyCode:$.ui.keyCode.ENTER}))
            .trigger($.Event('keyup',{keyCode:$.ui.keyCode.ENTER}));
        awaittestUtils.nextTick();
        assert.containsOnce(calendar,'.fc-event:contains(neweventinquickcreatevalidatedbypressingenterkey.)',
            "shoulddisplaythenewrecordbypressingenterkey");


        //createaneweventandeditit

        $cell=calendar.$('.fc-day-grid.fc-row:eq(4).fc-day:eq(2)');

        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();

        assert.strictEqual($('.modal-sm').length,1,"shouldopenthequickcreatedialog");

        testUtils.fields.editInput($('.modal-bodyinput:first'),'coucou');
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Edit)'));

        assert.strictEqual($('.modal-lg.o_form_view').length,1,"shouldopentheslowcreatedialog");
        assert.strictEqual($('.modal-lg.modal-title').text(),"Create:Events",
            "shouldusethestringattributeasmodaltitle");
        assert.strictEqual($('.modal-lg.o_form_viewinput[name="name"]').val(),"coucou",
            "shouldhavesetthenamefromthequickcreatedialog");

        awaittestUtils.dom.click($('.modal-lgbutton.btn:contains(Save)'));

        assert.strictEqual(calendar.$('.fc-event:contains(coucou)').length,1,
            "shoulddisplaythenewrecordwithstringattribute");

        //createaneweventwith2days

        $cell=calendar.$('.fc-day-grid.fc-row:eq(3).fc-day:eq(2)');

        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell.next(),"mousemove");
        testUtils.dom.triggerMouseEvent($cell.next(),"mouseup");
        awaittestUtils.nextTick();

        testUtils.fields.editInput($('.modal-dialoginput:first'),'neweventinquickcreate2');
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Edit)'));

        assert.strictEqual($('.modal-lginput:first').val(),'neweventinquickcreate2',
            "shouldopentheformViewDialogwithdefaultvalues");

        awaittestUtils.dom.click($('.modal-lgbutton.btn:contains(Save)'));

        assert.notOk($('.modal').length,"shouldclosedialogs");
        var$newevent2=calendar.$('.fc-event:contains(neweventinquickcreate2)');
        assert.ok($newevent2.length,"shoulddisplaythe2daysnewrecord");
        assert.hasAttrValue($newevent2.closest('.fc-event-container'),
            'colspan',"2","thenewrecordshouldhave2days");

        awaittestUtils.dom.click(calendar.$('.fc-event:contains(neweventinquickcreate2).fc-content'));
        var$popover_description=calendar.$('.o_cw_popover.o_cw_body.list-group-item');
        assert.strictEqual($popover_description.children()[1].textContent,'December20-21,2016',
            "Thepopoverdescriptionshouldindicatethecorrectrange");
        assert.strictEqual($popover_description.children()[2].textContent,'(2days)',
            "Thepopoverdescriptionshouldindicate2days");
        awaittestUtils.dom.click(calendar.$('.o_cw_popover.fa-close'));

        //deletethearecord

        awaittestUtils.dom.click(calendar.$('.fc-event:contains(event4).fc-content'));
        awaittestUtils.dom.click(calendar.$('.o_cw_popover.o_cw_popover_delete'));
        assert.ok($('.modal-footerbutton.btn:contains(Ok)').length,"shoulddisplaytheconfirmmessage");
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Ok)'));
        assert.notOk(calendar.$('.fc-event:contains(event4).fc-content').length,"therecordshouldbedeleted");

        assert.containsN(calendar,'.fc-event-container.fc-event',10,"shoulddisplay10events");
        //movetonextmonth
        awaittestUtils.dom.click(calendar.$buttons.find('.o_calendar_button_next'));

        assert.containsNone(calendar,'.fc-event-container.fc-event',"shoulddisplay0events");

        calendar.destroy();
    });

    QUnit.test('quickcreateswitchingtoactualcreateforrequiredfields',asyncfunction(assert){
        assert.expect(4);

        varevent=$.Event();
        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                if(args.method==="create"){
                    returnPromise.reject({
                        message:{
                            code:200,
                            data:{},
                            message:"Flectraservererror",
                        },
                        event:event
                    });
                }
                returnthis._super(route,args);
            },
        });

        //createanewevent
        var$cell=calendar.$('.fc-day-grid.fc-row:eq(2).fc-day:eq(2)');
        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();

        assert.strictEqual($('.modal-sm.modal-title').text(),'Create:Events',
            "shouldopenthequickcreatedialog");

        awaittestUtils.fields.editInput($('.modal-bodyinput:first'),'neweventinquickcreate');
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Create)'));
        awaittestUtils.nextTick();

        //Iftheeventisnotdefault-prevented,atracebackwillberaised,whichwedonotwant
        assert.ok(event.isDefaultPrevented(),"faildeferredeventshouldhavebeendefault-prevented");

        assert.strictEqual($('.modal-lg.modal-title').text(),'Create:Events',
            "shouldhaveswitchedtoabiggermodalforanactualcreateratherthanquickcreate");
        assert.strictEqual($('.modal-lgmain.o_form_view.o_form_editable').length,1,
            "shouldopenthefulleventformviewinadialog");

        calendar.destroy();
    });

    QUnit.test('openmultipleeventformatthesametime',asyncfunction(assert){
        assert.expect(2);

        varprom=testUtils.makeTestPromise();
        varcounter=0;
        testUtils.mock.patch(ViewDialogs.FormViewDialog,{
            open:function(){
                counter++;
                this.options=_.omit(this.options,'fields_view'); //forceloadFieldView
                returnthis._super.apply(this,arguments);
            },
            loadFieldView:function(){
                varself=this;
                varargs=arguments;
                var_super=this._super;
                returnprom.then(function(){
                    return_super.apply(self,args);
                });
            },
        });

        varevent=$.Event();
        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'quick_add="False"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="month">'+
                    '<fieldname="name"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        var$cell=calendar.$('.fc-day-grid.fc-row:eq(2).fc-day:eq(2)');
        for(vari=0;i<5;i++){
            awaittestUtils.dom.triggerMouseEvent($cell,"mousedown");
            awaittestUtils.dom.triggerMouseEvent($cell,"mouseup");
        }
        prom.resolve();
        awaittestUtils.nextTick();
        assert.equal(counter,5,"thereshouldhadbeen5attempstoopenamodal");
        assert.containsOnce($('body'),'.modal',"thereshouldbeonlyoneopenmodal");

        calendar.destroy();
        testUtils.mock.unpatch(ViewDialogs.FormViewDialog);
    });

    QUnit.test('createeventwithtimezoneinweekmodeEuropeanlocale',asyncfunction(assert){
        assert.expect(5);

        this.data.event.records=[];

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week">'+
                    '<fieldname="name"/>'+
                    '<fieldname="start"/>'+
                    '<fieldname="allday"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
            translateParameters:{//Avoidissuesduetolocalizationformats
                time_format:"%H:%M:%S",
            },
            mockRPC:function(route,args){
                if(args.method==="create"){
                    assert.deepEqual(args.kwargs.context,{
                        "default_start":"2016-12-1306:00:00",
                        "default_stop":"2016-12-1308:00:00",
                        "default_allday":null
                    },
                    "shouldsendthecontexttocreateevents");
                }
                returnthis._super(route,args);
            },
        },{positionalClicks:true});

        vartop=calendar.$('.fc-axis:contains(8:00)').offset().top+5;
        varleft=calendar.$('.fc-day:eq(2)').offset().left+5;

        try{
            testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }

        testUtils.dom.triggerPositionalMouseEvent(left,top+60,"mousemove");

        assert.strictEqual(calendar.$('.fc-content.fc-time').text(),"8:00-10:00",
            "shoulddisplaythetimeinthecalendarsticker");

        awaittestUtils.dom.triggerPositionalMouseEvent(left,top+60,"mouseup");
        awaittestUtils.nextTick();
        awaittestUtils.fields.editInput($('.modalinput:first'),'newevent');
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Create)'));
        var$newevent=calendar.$('.fc-event:contains(newevent)');

        assert.strictEqual($newevent.find('.o_event_title').text(),"newevent",
            "shoulddisplaytheneweventwithtitle");

        assert.deepEqual($newevent[0].fcSeg.eventRange.def.extendedProps.record,
            {
                display_name:"newevent",
                start:fieldUtils.parse.datetime("2016-12-1306:00:00",this.data.event.fields.start,{isUTC:true}),
                stop:fieldUtils.parse.datetime("2016-12-1308:00:00",this.data.event.fields.stop,{isUTC:true}),
                allday:false,
                name:"newevent",
                id:1
            },
            "thenewrecordshouldhavetheutcdatetime(quickCreate)");

        //deleterecord

        awaittestUtils.dom.click($newevent);
        awaittestUtils.dom.click(calendar.$('.o_cw_popover.o_cw_popover_delete'));
        awaittestUtils.dom.click($('.modalbutton.btn-primary:contains(Ok)'));
        assert.containsNone(calendar,'.fc-content',"shoulddeletetherecord");

        calendar.destroy();
    });

    QUnit.test('defaultweekstart(US)',function(assert){
        //ifnotgivenanyoption,defaultweekstartisonSunday
        assert.expect(3);
        vardone=assert.async();

        createCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="week">'+
            '</calendar>',
            archs:archs,

            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                if(args.method==='search_read'&&args.model==='event'){
                    assert.deepEqual(args.kwargs.domain,[
                        ["start","<=","2016-12-1723:59:59"],
                        ["stop",">=","2016-12-1100:00:00"]
                    ],
                    'Thedomaintosearcheventsinshouldbecorrect');
                }
                returnthis._super.apply(this,arguments);
            }
        }).then(function(calendar){
            assert.strictEqual(calendar.$('.fc-day-header').first().text(),"Sun11",
                "ThefirstdayoftheweekshouldbeSunday");
            assert.strictEqual(calendar.$('.fc-day-header').last().text(),"Sat17",
                "ThelastdayoftheweekshouldbeSaturday");
            calendar.destroy();
            done();
        });
    });

    QUnit.test('Europeanweekstart',function(assert){
        //theweekstartdependsonthelocale
        assert.expect(3);
        vardone=assert.async();

        createCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="week">'+
            '</calendar>',
            archs:archs,

            viewOptions:{
                initialDate:initialDate,
            },
            translateParameters:{
                week_start:1,
            },
            mockRPC:function(route,args){
                if(args.method==='search_read'&&args.model==='event'){
                    assert.deepEqual(args.kwargs.domain,[
                        ["start","<=","2016-12-1823:59:59"],
                        ["stop",">=","2016-12-1200:00:00"]
                    ],
                    'Thedomaintosearcheventsinshouldbecorrect');
                }
                returnthis._super.apply(this,arguments);
            }
        }).then(function(calendar){
            assert.strictEqual(calendar.$('.fc-day-header').first().text(),"Mon12",
                "ThefirstdayoftheweekshouldbeMonday");
            assert.strictEqual(calendar.$('.fc-day-header').last().text(),"Sun18",
                "ThelastdayoftheweekshouldbeSunday");
            calendar.destroy();
            done();
        });
    });

    QUnit.test('weeknumbering',function(assert){
        //weeknumberdependsontheweekstart,whichdependsonthelocale
        //thecalendarlibraryusesnumbers[0..6],whileFlectrauses[1..7]
        //soifthemoduloisnotdone,theweeknumberisincorrect
        assert.expect(1);
        vardone=assert.async();

        createCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="week">'+
            '</calendar>',
            archs:archs,

            viewOptions:{
                initialDate:initialDate,
            },
            translateParameters:{
                week_start:7,
            },
        }).then(function(calendar){
            assert.strictEqual(calendar.$('.fc-week-number').text(),"Week51",
                "Weshouldbeonthe51stweek");
            calendar.destroy();
            done();
        });
    });

    QUnit.test('renderpopover',asyncfunction(assert){
        assert.expect(14);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week">'+
                    '<fieldname="name"string="CustomName"/>'+
                    '<fieldname="partner_id"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        awaittestUtils.dom.click($('.fc-event:contains(event4)'));

        assert.containsOnce(calendar,'.o_cw_popover',"shouldopenapopoverclickingonevent");
        assert.strictEqual(calendar.$('.o_cw_popover.popover-header').text(),'event4',"popovershouldhaveatitle'event4'");
        assert.containsOnce(calendar,'.o_cw_popover.o_cw_popover_edit',"popovershouldhaveaneditbutton");
        assert.containsOnce(calendar,'.o_cw_popover.o_cw_popover_delete',"popovershouldhaveadeletebutton");
        assert.containsOnce(calendar,'.o_cw_popover.o_cw_popover_close',"popovershouldhaveaclosebutton");

        assert.strictEqual(calendar.$('.o_cw_popover.list-group-item:firstb.text-capitalize').text(),'Wednesday,December14,2016',"shoulddisplaydate'Wednesday,December14,2016'");
        assert.containsN(calendar,'.o_cw_popover.o_cw_popover_fields_secondary.list-group-item',2,"popovershouldhaveatwofields");

        assert.containsOnce(calendar,'.o_cw_popover.o_cw_popover_fields_secondary.list-group-item:first.o_field_char',"shouldapplycharwidget");
        assert.strictEqual(calendar.$('.o_cw_popover.o_cw_popover_fields_secondary.list-group-item:firststrong').text(),'CustomName:',"labelshouldbea'CustomName'");
        assert.strictEqual(calendar.$('.o_cw_popover.o_cw_popover_fields_secondary.list-group-item:first.o_field_char').text(),'event4',"valueshouldbea'event4'");

        assert.containsOnce(calendar,'.o_cw_popover.o_cw_popover_fields_secondary.list-group-item:last.o_form_uri',"shouldapplym20widget");
        assert.strictEqual(calendar.$('.o_cw_popover.o_cw_popover_fields_secondary.list-group-item:laststrong').text(),'user:',"labelshouldbea'user'");
        assert.strictEqual(calendar.$('.o_cw_popover.o_cw_popover_fields_secondary.list-group-item:last.o_form_uri').text(),'partner1',"valueshouldbea'partner1'");

        awaittestUtils.dom.click($('.o_cw_popover.o_cw_popover_close'));
        assert.containsNone(calendar,'.o_cw_popover',"shouldcloseapopover");

        calendar.destroy();
    });

    QUnit.test('renderpopoverwithmodifiers',asyncfunction(assert){
        assert.expect(3);

        this.data.event.fields.priority={string:"Priority",type:"selection",selection:[['0','Normal'],['1','Important']],};

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week">'+
                '<fieldname="priority"widget="priority"readonly="1"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        awaittestUtils.dom.click($('.fc-event:contains(event4)'));

        assert.containsOnce(calendar,'.o_cw_popover',"shouldopenapopoverclickingonevent");
        assert.containsOnce(calendar,'.o_cw_popover.o_priorityspan.o_priority_star',"priorityfieldshouldnotbeeditable");

        awaittestUtils.dom.click($('.o_cw_popover.o_cw_popover_close'));
        assert.containsNone(calendar,'.o_cw_popover',"shouldcloseapopover");

        calendar.destroy();
    });

    QUnit.test('attributeshide_dateandhide_time',asyncfunction(assert){
        assert.expect(1);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'hide_date="true"'+
                'hide_time="true"'+
                'mode="month">'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        awaittestUtils.dom.click($('.fc-event:contains(event4)'));
        assert.containsNone(calendar,'.o_cw_popover.list-group-item',"popovershouldnotcontaindate/time");

        calendar.destroy();
    });

    QUnit.test('createeventwithtimezoneinweekmodewithformViewDialogEuropeanlocale',asyncfunction(assert){
        assert.expect(8);

        this.data.event.records=[];
        this.data.event.onchanges={
            allday:function(obj){
                if(obj.allday){
                    obj.start_date=obj.start&&obj.start.split('')[0]||obj.start_date;
                    obj.stop_date=obj.stop&&obj.stop.split('')[0]||obj.stop_date||obj.start_date;
                }else{
                    obj.start=obj.start_date&&(obj.start_date+'00:00:00')||obj.start;
                    obj.stop=obj.stop_date&&(obj.stop_date+'00:00:00')||obj.stop||obj.start;
                }
            }
        };

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week">'+
                    '<fieldname="name"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
            translateParameters:{//Avoidissuesduetolocalizationformats
                time_format:"%H:%M:%S",
            },
            mockRPC:function(route,args){
                if(args.method==="create"){
                    assert.deepEqual(args.kwargs.context,{
                        "default_name":"newevent",
                        "default_start":"2016-12-1306:00:00",
                        "default_stop":"2016-12-1308:00:00",
                        "default_allday":null
                    },
                    "shouldsendthecontexttocreateevents");
                }
                if(args.method==="write"){
                    assert.deepEqual(args.args[1],expectedEvent,
                        "shouldmovetheevent");
                }
                returnthis._super(route,args);
            },
        },{positionalClicks:true});

        vartop=calendar.$('.fc-axis:contains(8:00)').offset().top+5;
        varleft=calendar.$('.fc-day:eq(2)').offset().left+5;

        try{
            testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }
        testUtils.dom.triggerPositionalMouseEvent(left,top+60,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(left,top+60,"mouseup");
        awaittestUtils.nextTick();
        awaittestUtils.fields.editInput($('.modalinput:first'),'newevent');
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Edit)'));

        assert.strictEqual($('.o_field_widget[name="start"]input').val(),
            "12/13/201608:00:00","shoulddisplaythedatetime");

        awaittestUtils.dom.click($('.modal-lg.o_field_boolean[name="allday"]input'));
        awaittestUtils.nextTick();
        assert.strictEqual($('input[name="start_date"]').val(),
            "12/13/2016","shoulddisplaythedate");

        awaittestUtils.dom.click($('.modal-lg.o_field_boolean[name="allday"]input'));

        assert.strictEqual($('.o_field_widget[name="start"]input').val(),
            "12/13/201602:00:00","shoulddisplaythedatetimefromthedatewiththetimezone");

        //usedatepickertoenteradate:12/13/201608:00:00
        testUtils.dom.openDatepicker($('.o_field_widget[name="start"].o_datepicker'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="togglePicker"]'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker.timepicker-hour'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-hourstd.hour:contains(08)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="close"]'));

        //usedatepickertoenteradate:12/13/201610:00:00
        testUtils.dom.openDatepicker($('.o_field_widget[name="stop"].o_datepicker'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="togglePicker"]'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker.timepicker-hour'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-hourstd.hour:contains(10)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="close"]'));

        awaittestUtils.dom.click($('.modal-lgbutton.btn:contains(Save)'));
        var$newevent=calendar.$('.fc-event:contains(newevent)');

        assert.strictEqual($newevent.find('.o_event_title').text(),"newevent",
            "shoulddisplaytheneweventwithtitle");

        assert.deepEqual($newevent[0].fcSeg.eventRange.def.extendedProps.record,
            {
                display_name:"newevent",
                start:fieldUtils.parse.datetime("2016-12-1306:00:00",this.data.event.fields.start,{isUTC:true}),
                stop:fieldUtils.parse.datetime("2016-12-1308:00:00",this.data.event.fields.stop,{isUTC:true}),
                allday:false,
                name:"newevent",
                id:1
            },
            "thenewrecordshouldhavetheutcdatetime(formViewDialog)");

        varpos=calendar.$('.fc-content').offset();
        left=pos.left+5;
        top=pos.top+5;

        //Modethiseventtoanotherday
        varexpectedEvent={
          "allday":false,
          "start":"2016-12-1206:00:00",
          "stop":"2016-12-1208:00:00"
        };
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        left=calendar.$('.fc-day:eq(1)').offset().left+15;
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mouseup");
        awaittestUtils.nextTick();

        //Moveto"Allday"
        expectedEvent={
          "allday":true,
          "start":"2016-12-1200:00:00",
          "stop":"2016-12-1200:00:00"
        };
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        top=calendar.$('.fc-day:eq(1)').offset().top+15;
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mouseup");
        awaittestUtils.nextTick();

        calendar.destroy();
    });

    QUnit.test('createeventwithtimezoneinweekmodeAmericanlocale',asyncfunction(assert){
        assert.expect(5);

        this.data.event.records=[];

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week">'+
                    '<fieldname="name"/>'+
                    '<fieldname="start"/>'+
                    '<fieldname="allday"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
            translateParameters:{//Avoidissuesduetolocalizationformats
                time_format:"%I:%M:%S",
            },
            mockRPC:function(route,args){
                if(args.method==="create"){
                    assert.deepEqual(args.kwargs.context,{
                        "default_start":"2016-12-1306:00:00",
                        "default_stop":"2016-12-1308:00:00",
                        "default_allday":null
                    },
                    "shouldsendthecontexttocreateevents");
                }
                returnthis._super(route,args);
            },
        },{positionalClicks:true});

        vartop=calendar.$('.fc-axis:contains(8am)').offset().top+5;
        varleft=calendar.$('.fc-day:eq(2)').offset().left+5;

        try{
            testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }

        testUtils.dom.triggerPositionalMouseEvent(left,top+60,"mousemove");

        assert.strictEqual(calendar.$('.fc-content.fc-time').text(),"8:00-10:00",
            "shoulddisplaythetimeinthecalendarsticker");

        testUtils.dom.triggerPositionalMouseEvent(left,top+60,"mouseup");
        awaittestUtils.nextTick();
        testUtils.fields.editInput($('.modalinput:first'),'newevent');
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Create)'));
        var$newevent=calendar.$('.fc-event:contains(newevent)');

        assert.strictEqual($newevent.find('.o_event_title').text(),"newevent",
            "shoulddisplaytheneweventwithtitle");

        assert.deepEqual($newevent[0].fcSeg.eventRange.def.extendedProps.record,
            {
                display_name:"newevent",
                start:fieldUtils.parse.datetime("2016-12-1306:00:00",this.data.event.fields.start,{isUTC:true}),
                stop:fieldUtils.parse.datetime("2016-12-1308:00:00",this.data.event.fields.stop,{isUTC:true}),
                allday:false,
                name:"newevent",
                id:1
            },
            "thenewrecordshouldhavetheutcdatetime(quickCreate)");

        //deleterecord

        awaittestUtils.dom.click($newevent);
        awaittestUtils.dom.click(calendar.$('.o_cw_popover.o_cw_popover_delete'));
        awaittestUtils.dom.click($('.modalbutton.btn-primary:contains(Ok)'));
        assert.containsNone(calendar,'.fc-content',"shoulddeletetherecord");

        calendar.destroy();
    });

    QUnit.test('fetcheventwhenbeingintimezone',asyncfunction(assert){
        assert.expect(3);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="week">'+
                    '<fieldname="name"/>'+
                    '<fieldname="start"/>'+
                    '<fieldname="allday"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return660;
                },
            },

            mockRPC:asyncfunction(route,args){
                if(args.method==='search_read'&&args.model==='event'){
                    assert.deepEqual(args.kwargs.domain,[
                        ["start","<=","2016-12-1712:59:59"],//inUTC.whichis2016-12-1723:59:59inTZSydney11hourslater
                        ["stop",">=","2016-12-1013:00:00"]  //inUTC.whichis2016-12-1100:00:00inTZSydney11hourslater
                    ],'Thedomainshouldcontaintherightrange');
                }
                returnthis._super(route,args);
            },
        });

        assert.strictEqual(calendar.$('.fc-day-header:first').text(),'Sun11',
            'Thecalendarstartdateshouldbe2016-12-11');
        assert.strictEqual(calendar.$('.fc-day-header:last()').text(),'Sat17',
            'Thecalendarstartdateshouldbe2016-12-17');

        calendar.destroy();
    });

    QUnit.test('createeventwithtimezoneinweekmodewithformViewDialogAmericanlocale',asyncfunction(assert){
        assert.expect(8);

        this.data.event.records=[];
        this.data.event.onchanges={
            allday:function(obj){
                if(obj.allday){
                    obj.start_date=obj.start&&obj.start.split('')[0]||obj.start_date;
                    obj.stop_date=obj.stop&&obj.stop.split('')[0]||obj.stop_date||obj.start_date;
                }else{
                    obj.start=obj.start_date&&(obj.start_date+'00:00:00')||obj.start;
                    obj.stop=obj.stop_date&&(obj.stop_date+'00:00:00')||obj.stop||obj.start;
                }
            }
        };

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week">'+
                    '<fieldname="name"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
            translateParameters:{//Avoidissuesduetolocalizationformats
                time_format:"%I:%M:%S",
            },
            mockRPC:function(route,args){
                if(args.method==="create"){
                    assert.deepEqual(args.kwargs.context,{
                        "default_name":"newevent",
                        "default_start":"2016-12-1306:00:00",
                        "default_stop":"2016-12-1308:00:00",
                        "default_allday":null
                    },
                    "shouldsendthecontexttocreateevents");
                }
                if(args.method==="write"){
                    assert.deepEqual(args.args[1],expectedEvent,
                        "shouldmovetheevent");
                }
                returnthis._super(route,args);
            },
        },{positionalClicks:true});

        vartop=calendar.$('.fc-axis:contains(8am)').offset().top+5;
        varleft=calendar.$('.fc-day:eq(2)').offset().left+5;

        try{
            testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }
        testUtils.dom.triggerPositionalMouseEvent(left,top+60,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(left,top+60,"mouseup");
        awaittestUtils.nextTick();
        testUtils.fields.editInput($('.modalinput:first'),'newevent');
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Edit)'));

        assert.strictEqual($('.o_field_widget[name="start"]input').val(),"12/13/201608:00:00",
            "shoulddisplaythedatetime");

        awaittestUtils.dom.click($('.modal-lg.o_field_boolean[name="allday"]input'));

        assert.strictEqual($('.o_field_widget[name="start_date"]input').val(),"12/13/2016",
            "shoulddisplaythedate");

        awaittestUtils.dom.click($('.modal-lg.o_field_boolean[name="allday"]input'));

        assert.strictEqual($('.o_field_widget[name="start"]input').val(),"12/13/201602:00:00",
            "shoulddisplaythedatetimefromthedatewiththetimezone");

        //usedatepickertoenteradate:12/13/201608:00:00
        testUtils.dom.openDatepicker($('.o_field_widget[name="start"].o_datepicker'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="togglePicker"]'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker.timepicker-hour'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-hourstd.hour:contains(08)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="close"]'));

        //usedatepickertoenteradate:12/13/201610:00:00
        testUtils.dom.openDatepicker($('.o_field_widget[name="stop"].o_datepicker'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="togglePicker"]'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker.timepicker-hour'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-hourstd.hour:contains(10)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="close"]'));

        awaittestUtils.dom.click($('.modal-lgbutton.btn:contains(Save)'));
        var$newevent=calendar.$('.fc-event:contains(newevent)');

        assert.strictEqual($newevent.find('.o_event_title').text(),"newevent",
            "shoulddisplaytheneweventwithtitle");

        assert.deepEqual($newevent[0].fcSeg.eventRange.def.extendedProps.record,
            {
                display_name:"newevent",
                start:fieldUtils.parse.datetime("2016-12-1306:00:00",this.data.event.fields.start,{isUTC:true}),
                stop:fieldUtils.parse.datetime("2016-12-1308:00:00",this.data.event.fields.stop,{isUTC:true}),
                allday:false,
                name:"newevent",
                id:1
            },
            "thenewrecordshouldhavetheutcdatetime(formViewDialog)");

        varpos=calendar.$('.fc-content').offset();
        left=pos.left+5;
        top=pos.top+5;

        //Modethiseventtoanotherday
        varexpectedEvent={
          "allday":false,
          "start":"2016-12-1206:00:00",
          "stop":"2016-12-1208:00:00"
        };
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        left=calendar.$('.fc-day:eq(1)').offset().left+15;
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mouseup");
        awaittestUtils.nextTick();

        //Moveto"Allday"
        expectedEvent={
          "allday":true,
          "start":"2016-12-1200:00:00",
          "stop":"2016-12-1200:00:00"
        };
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        top=calendar.$('.fc-day:eq(1)').offset().top+15;
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mouseup");
        awaittestUtils.nextTick();

        calendar.destroy();
    });

    QUnit.test('checkcalendarweekcolumntimeformat',asyncfunction(assert){
        assert.expect(2);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendardate_start="start"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            translateParameters:{
                time_format:"%I:%M:%S",
            },
        });

        assert.strictEqual(calendar.$('.fc-axis:contains(8am)').length,1,"calendarshouldshowaccordingtotimeformat");
        assert.strictEqual(calendar.$('.fc-axis:contains(11pm)').length,1,
            "eventtimeformatshould12hour");

        calendar.destroy();
    });

    QUnit.test("alldayeventattribute",asyncfunction(assert){
        assert.expect(5);

        this.data.event.fields.boolfield={string:"booleanfield",type:"boolean"};
        this.data.event.records[0].boolfield=true;
        constcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:`
                <calendardate_start="start"date_stop="stop"all_day="boolfield"mode="month">
                    <fieldname="name"/>
                </calendar>
            `,
            archs:archs,
            viewOptions:{initialDate},
            session:{getTZOffset:()=>120},
        });

        assert.containsOnce(calendar,".fc-event[data-event-id=1]");
        assert.containsNone(calendar,".fc-event[data-event-id=1].o_cw_nobg","firsteventisanalldayevent");

        assert.containsOnce(calendar,".fc-event[data-event-id=2].o_cw_nobg","secondeventisnotanalldayevent");

        assert.containsN(calendar,".fc-event[data-event-id=5]",2);
        assert.containsNone(calendar,".fc-event[data-event-id=5].o_cw_nobg",2,"fiftheventisanalldayevent");

        calendar.destroy();
    });

    QUnit.test('createalldayeventinweekmode',asyncfunction(assert){
        assert.expect(3);

        this.data.event.records=[];

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week">'+
                    '<fieldname="name"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
        },{positionalClicks:true});

        varpos=calendar.$('.fc-bgtd:eq(4)').offset();
        try{
            testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mousedown");
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }
        pos=calendar.$('.fc-bgtd:eq(5)').offset();
        testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mouseup");
        awaittestUtils.nextTick();

        testUtils.fields.editInput($('.modalinput:first'),'newevent');
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Create)'));
        var$newevent=calendar.$('.fc-event:contains(newevent)');

        assert.strictEqual($newevent.text().replace(/[\s\n\r]+/g,''),"newevent",
            "shoulddisplaytheneweventwithtimeandtitle");
        assert.hasAttrValue($newevent.parent(),'colspan',"2",
            "shouldappearovertwodays.");

        assert.deepEqual($newevent[0].fcSeg.eventRange.def.extendedProps.record,
            {
                display_name:"newevent",
                start:fieldUtils.parse.datetime("2016-12-1400:00:00",this.data.event.fields.start,{isUTC:true}),
                stop:fieldUtils.parse.datetime("2016-12-1500:00:00",this.data.event.fields.stop,{isUTC:true}),
                allday:true,
                name:"newevent",
                id:1
            },
            "thenewrecordshouldhavetheutcdatetime(quickCreate)");

        calendar.destroy();
    });

    QUnit.test('createeventwithdefaultcontext(noquickCreate)',asyncfunction(assert){
        assert.expect(3);

        this.data.event.records=[];

        constcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            `<calendar
                class="o_calendar_test"
                date_start="start"
                date_stop="stop"
                mode="week"
                all_day="allday"
                quick_add="False"/>`,
            archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset(){
                    return120;
                },
            },
            context:{
                default_name:'New',
            },
            intercepts:{
                do_action(ev){
                    assert.step('do_action');
                    assert.deepEqual(ev.data.action.context,{
                        default_name:"New",
                        default_start:"2016-12-1400:00:00",
                        default_stop:"2016-12-1500:00:00",
                        default_allday:true,
                    },
                    "shouldsendthecorrectdatatocreateevents");
                },
            },
        },{positionalClicks:true});

        varpos=calendar.$('.fc-bgtd:eq(4)').offset();
        try{
            testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mousedown");
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }
        pos=calendar.$('.fc-bgtd:eq(5)').offset();
        testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mouseup");
        assert.verifySteps(['do_action']);

        calendar.destroy();
    });

    QUnit.test('createalldayeventinweekmode(noquickCreate)',asyncfunction(assert){
        assert.expect(1);

        this.data.event.records=[];

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="week"'+
                'all_day="allday"'+
                'quick_add="False"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
            intercepts:{
                do_action:function(event){
                    assert.deepEqual(event.data.action.context,{
                            default_start:"2016-12-1400:00:00",
                            default_stop:"2016-12-1500:00:00",
                            default_allday:true,
                    },
                    "shouldsendthecorrectdatatocreateevents");
                },
            },
        },{positionalClicks:true});

        varpos=calendar.$('.fc-bgtd:eq(4)').offset();
        try{
            testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mousedown");
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }
        pos=calendar.$('.fc-bgtd:eq(5)').offset();
        testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mouseup");

        calendar.destroy();
    });

    QUnit.test('createeventinmonthmode',asyncfunction(assert){
        assert.expect(4);

        this.data.event.records=[];

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="month">'+
                    '<fieldname="name"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
            mockRPC:function(route,args){
                if(args.method==="create"){
                    assert.deepEqual(args.args[0],{
                        "name":"newevent",
                        "start":"2016-12-1405:00:00",
                        "stop":"2016-12-1517:00:00",
                    },
                    "shouldsendthecorrectdatatocreateevents");
                }
                returnthis._super(route,args);
            },
        },{positionalClicks:true});

        varpos=calendar.$('.fc-bgtd:eq(17)').offset();
        try{
            testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mousedown");
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }
        pos=calendar.$('.fc-bgtd:eq(18)').offset();
        testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(pos.left+15,pos.top+15,"mouseup");
        awaittestUtils.nextTick();

        testUtils.fields.editInput($('.modalinput:first'),'newevent');
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Create)'));
        var$newevent=calendar.$('.fc-event:contains(newevent)');

        assert.strictEqual($newevent.text().replace(/[\s\n\r]+/g,''),"newevent",
            "shoulddisplaytheneweventwithtimeandtitle");
        assert.hasAttrValue($newevent.parent(),'colspan',"2",
            "shouldappearovertwodays.");

        assert.deepEqual($newevent[0].fcSeg.eventRange.def.extendedProps.record,{
            display_name:"newevent",
            start:fieldUtils.parse.datetime("2016-12-1405:00:00",this.data.event.fields.start,{isUTC:true}),
            stop:fieldUtils.parse.datetime("2016-12-1517:00:00",this.data.event.fields.stop,{isUTC:true}),
            name:"newevent",
            id:1
        },"thenewrecordshouldhavetheutcdatetime(quickCreate)");

        calendar.destroy();
    });

    QUnit.test('useminicalendar',asyncfunction(assert){
        assert.expect(12);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return120;
                },
            },
        });

        assert.containsOnce(calendar,'.fc-timeGridWeek-view',"shouldbeinweekmode");
        assert.containsN(calendar,'.fc-event',9,"shoulddisplay9eventsontheweek(4event+5daysevent)");
        awaittestUtils.dom.click(calendar.$('.o_calendar_minia:contains(19)'));
        //Clickingonadayinanotherweekshouldswitchtotheotherweekview
        assert.containsOnce(calendar,'.fc-timeGridWeek-view',"shouldbeinweekmode");
        assert.containsN(calendar,'.fc-event',4,"shoulddisplay4eventsontheweek(1event+3daysevent)");
        //Clickingonadayinthesameweekshouldswitchtothatparticulardayview
        awaittestUtils.dom.click(calendar.$('.o_calendar_minia:contains(18)'));
        assert.containsOnce(calendar,'.fc-timeGridDay-view',"shouldbeindaymode");
        assert.containsN(calendar,'.fc-event',2,"shoulddisplay2eventsontheday");
        //Clickingonthesamedayshouldtogglebetweenday,monthandweekviews
        awaittestUtils.dom.click(calendar.$('.o_calendar_minia:contains(18)'));
        assert.containsOnce(calendar,'.fc-dayGridMonth-view',"shouldbeinmonthmode");
        assert.containsN(calendar,'.fc-event',7,"shoulddisplay7eventsonthemonth(event5isonmultipleweeksandgeneratesto.fc-event)");
        awaittestUtils.dom.click(calendar.$('.o_calendar_minia:contains(18)'));
        assert.containsOnce(calendar,'.fc-timeGridWeek-view',"shouldbeinweekmode");
        assert.containsN(calendar,'.fc-event',4,"shoulddisplay4eventsontheweek(1event+3daysevent)");
        awaittestUtils.dom.click(calendar.$('.o_calendar_minia:contains(18)'));
        assert.containsOnce(calendar,'.fc-timeGridDay-view',"shouldbeindaymode");
        assert.containsN(calendar,'.fc-event',2,"shoulddisplay2eventsontheday");

        calendar.destroy();
    });

    QUnit.test('rendering,withmany2many',asyncfunction(assert){
        assert.expect(5);

        this.data.event.fields.partner_ids.type='many2many';
        this.data.event.records[0].partner_ids=[1,2,3,4,5];
        this.data.partner.records.push({id:5,display_name:"partner5",image:'EEE'});

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday">'+
                    '<fieldname="partner_ids"widget="many2many_tags_avatar"avatar_field="image"write_model="filter_partner"write_field="partner_id"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        assert.containsN(calendar,'.o_calendar_filter_items.o_cw_filter_avatar',3,
            "shouldhave3avatarsinthesidebar");

        //Event1
        awaittestUtils.dom.click(calendar.$('.fc-event:first'));
        assert.ok(calendar.$('.o_cw_popover').length,"shouldopenapopoverclickingonevent");
        assert.strictEqual(calendar.$('.o_cw_popover').find('img').length,1,"shouldhave1avatar");

        //Event2
        awaittestUtils.dom.click(calendar.$('.fc-event:eq(1)'));
        assert.ok(calendar.$('.o_cw_popover').length,"shouldopenapopoverclickingonevent");
        assert.strictEqual(calendar.$('.o_cw_popover').find('img').length,5,"shouldhave5avatar");

        calendar.destroy();
    });

    QUnit.test('openformview',asyncfunction(assert){
        assert.expect(3);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                if(args.method==="get_formview_id"){
                    returnPromise.resolve('Aview');
                }
                returnthis._super(route,args);
            },
        });

        //clickonanexistingeventtoopentheformview

        testUtils.mock.intercept(calendar,'do_action',function(event){
            assert.deepEqual(event.data.action,
                {
                    type:"ir.actions.act_window",
                    res_id:4,
                    res_model:"event",
                    views:[['Aview',"form"]],
                    target:"current",
                    context:{}
                },
                "shouldopentheformview");
        });
        awaittestUtils.dom.click(calendar.$('.fc-event:contains(event4).fc-content'));
        awaittestUtils.dom.click(calendar.$('.o_cw_popover.o_cw_popover_edit'));

        //createaneweventandeditit

        var$cell=calendar.$('.fc-day-grid.fc-row:eq(4).fc-day:eq(2)');
        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();
        testUtils.fields.editInput($('.modal-bodyinput:first'),'coucou');

        testUtils.mock.intercept(calendar,'do_action',function(event){
            assert.deepEqual(event.data.action,
                {
                    type:"ir.actions.act_window",
                    res_model:"event",
                    views:[[false,"form"]],
                    target:"current",
                    context:{
                        "default_name":"coucou",
                        "default_start":"2016-12-2700:00:00",
                        "default_stop":"2016-12-2700:00:00",
                        "default_allday":true
                    }
                },
                "shouldopentheformviewwiththecontextdefaultvalues");
        });

        testUtils.dom.click($('.modalbutton.btn:contains(Edit)'));

        calendar.destroy();

        assert.strictEqual($('#ui-datepicker-div:empty').length,0,"shouldhaveacleanbody");
    });

    QUnit.test('createandediteventinmonthmode(all_day:false)',asyncfunction(assert){
        assert.expect(2);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return-240;
                },
            },
        });

        //createaneweventandeditit
        var$cell=calendar.$('.fc-day-grid.fc-row:eq(4).fc-day:eq(2)');
        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();
        awaittestUtils.fields.editInput($('.modal-bodyinput:first'),'coucou');

        testUtils.mock.intercept(calendar,'do_action',function(event){
            assert.deepEqual(event.data.action,
                {
                    type:"ir.actions.act_window",
                    res_model:"event",
                    views:[[false,"form"]],
                    target:"current",
                    context:{
                        "default_name":"coucou",
                        "default_start":"2016-12-2711:00:00",//7:00+4h
                        "default_stop":"2016-12-2723:00:00",//19:00+4h
                    }
                },
                "shouldopentheformviewwiththecontextdefaultvalues");
        });

        awaittestUtils.dom.click($('.modalbutton.btn:contains(Edit)'));

        calendar.destroy();
        assert.strictEqual($('#ui-datepicker-div:empty').length,0,"shouldhaveacleanbody");
    });

    QUnit.test('showstarttimeofsingledayeventformonthmode',asyncfunction(assert){
        assert.expect(4);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return-240;
                },
            },
        });

        assert.strictEqual(calendar.$('.fc-event:contains(event2).fc-content.fc-time').text(),"06:55",
            "shouldhaveacorrecttime06:55AMinmonthmode");
        assert.strictEqual(calendar.$('.fc-event:contains(event4).fc-content.fc-time').text(),"",
            "shouldnotdisplayatimeforalldayevent");
        assert.strictEqual(calendar.$('.fc-event:contains(event5).fc-content.fc-time').text(),"",
            "shouldnotdisplayatimeformultipledaysevent");
        //switchtoweekmode
        awaittestUtils.dom.click(calendar.$('.o_calendar_button_week'));
        assert.strictEqual(calendar.$('.fc-event:contains(event2).fc-content.fc-time').text(),"",
            "shouldnotshowtimeinweekmodeasweekmodealreadyhavetimeony-axis");

        calendar.destroy();
    });

    QUnit.test('starttimeshouldnotshownfordatetypefield',asyncfunction(assert){
        assert.expect(1);

        this.data.event.fields.start.type="date";

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return-240;
                },
            },
        });

        assert.strictEqual(calendar.$('.fc-event:contains(event2).fc-content.fc-time').text(),"",
            "shouldnotshowtimefordatetypefield");

        calendar.destroy();
    });

    QUnit.test('starttimeshouldnotshowninmonthmodeifhide_timeistrue',asyncfunction(assert){
        assert.expect(1);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'hide_time="True"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return-240;
                },
            },
        });

        assert.strictEqual(calendar.$('.fc-event:contains(event2).fc-content.fc-time').text(),"",
            "shouldnotshowtimeforhide_timeattribute");

        calendar.destroy();
    });

    QUnit.test('readonlydate_startfield',asyncfunction(assert){
        assert.expect(4);

        this.data.event.fields.start.readonly=true;

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                if(args.method==="get_formview_id"){
                    returnPromise.resolve(false);
                }
                returnthis._super(route,args);
            },
        });

        assert.containsNone(calendar,'.fc-resizer',"shouldnothaveresizebutton");

        //clickonanexistingeventtoopentheformview

        testUtils.mock.intercept(calendar,'do_action',function(event){
            assert.deepEqual(event.data.action,
                {
                    type:"ir.actions.act_window",
                    res_id:4,
                    res_model:"event",
                    views:[[false,"form"]],
                    target:"current",
                    context:{}
                },
                "shouldopentheformview");
        });
        awaittestUtils.dom.click(calendar.$('.fc-event:contains(event4).fc-content'));
        awaittestUtils.dom.click(calendar.$('.o_cw_popover.o_cw_popover_edit'));

        //createaneweventandeditit

        var$cell=calendar.$('.fc-day-grid.fc-row:eq(4).fc-day:eq(2)');
        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();
        awaittestUtils.fields.editInput($('.modal-bodyinput:first'),'coucou');

        testUtils.mock.intercept(calendar,'do_action',function(event){
            assert.deepEqual(event.data.action,
                {
                    type:"ir.actions.act_window",
                    res_model:"event",
                    views:[[false,"form"]],
                    target:"current",
                    context:{
                        "default_name":"coucou",
                        "default_start":"2016-12-2700:00:00",
                        "default_stop":"2016-12-2700:00:00",
                        "default_allday":true
                    }
                },
                "shouldopentheformviewwiththecontextdefaultvalues");
        });

        awaittestUtils.dom.click($('.modalbutton.btn:contains(Edit)'));

        calendar.destroy();

        assert.strictEqual($('#ui-datepicker-div:empty').length,0,"shouldhaveacleanbody");
    });

    QUnit.test('"all"filter',asyncfunction(assert){
        assert.expect(6);

        varinterval=[
            ["start","<=","2016-12-1723:59:59"],
            ["stop",">=","2016-12-1100:00:00"],
        ];

        vardomains=[
            interval.concat([["partner_ids","in",[2,1]]]),
            interval.concat([["partner_ids","in",[1]]]),
            interval,
        ];

        vari=0;

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week"'+
                'attendee="partner_ids"'+
                'color="partner_id">'+
                    '<filtername="user_id"avatar_field="image"/>'+
                    '<fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>'+
            '</calendar>',
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                if(args.method==='search_read'&&args.model==='event'){
                    assert.deepEqual(args.kwargs.domain,domains[i]);
                    i++;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(calendar,'.fc-event',9,
            "shoulddisplay9eventsontheweek");

        //Selecttheeventsonlyassociatedwithpartner2
        awaittestUtils.dom.click(calendar.$('.o_calendar_filter_item[data-id=2]input'));
        assert.containsN(calendar,'.fc-event',4,
            "shoulddisplay4eventsontheweek");

        //Clickonthe'all'filtertoreloadallevents
        awaittestUtils.dom.click(calendar.$('.o_calendar_filter_item[data-value=all]input'));
        assert.containsN(calendar,'.fc-event',9,
            "shoulddisplay9eventsontheweek");

        calendar.destroy();
    });

    QUnit.test('Addfiltersandspecificcolor',asyncfunction(assert){
        assert.expect(8);

        this.data.event_type.records.push(
            {id:4,display_name:"EventTypenocolor",color:0},
        );

        this.data.event.records.push(
            {id:8,user_id:4,partner_id:1,name:"event8",start:"2016-12-1109:00:00",stop:"2016-12-1110:00:00",allday:false,partner_ids:[1,2,3],event_type_id:3,color:4},
            {id:9,user_id:4,partner_id:1,name:"event9",start:"2016-12-1119:00:00",stop:"2016-12-1120:00:00",allday:false,partner_ids:[1,2,3],event_type_id:1,color:1},
            {id:10,user_id:4,partner_id:1,name:"event10",start:"2016-12-1112:00:00",stop:"2016-12-1113:00:00",allday:false,partner_ids:[1,2,3],event_type_id:4,color:0},
        );

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week"'+
                'color="color">'+
                    '<fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>'+
                    '<fieldname="event_type_id"filters="1"color="color"/>'+
            '</calendar>',
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                varresult=this._super(route,args);
                if(args.method==="search_read"&&args.model==="event_type"&&args.args[1][0]==="color"){
                    assert.step('color_search_read');
                }
                returnresult;
            },
        });

        assert.containsN(calendar,'.o_calendar_filter',2,"shoulddisplay2filters");

        var$typeFilter= calendar.$('.o_calendar_filter:has(h5:contains(Event_Type))');
        assert.ok($typeFilter.length,"shoulddisplay'EventType'filter");
        assert.containsN($typeFilter,'.o_calendar_filter_item',4,"shoulddisplay4filteritemsfor'EventType'");

        assert.containsOnce($typeFilter,'.o_calendar_filter_item[data-value=3].o_cw_filter_color_4',"Filterforeventtype3musthavethecolor4");
        assert.containsOnce(calendar,'.fc-event[data-event-id=8].o_calendar_color_4',"Eventofeventtype3musthavethecolor4");
        assert.containsOnce(calendar,'.fc-event[data-event-id=10].o_calendar_color_1',"Thefirstcolorisusedwhennoneisprovided(defaultintfieldvaluebeing0)")
        assert.verifySteps(['color_search_read'],"Thecolorattributeonafieldshouldtriggerasearch_read")
        calendar.destroy();
    });

    QUnit.test('createeventwithfilters',asyncfunction(assert){
        assert.expect(7);

        this.data.event.fields.user_id.default=5;
        this.data.event.fields.partner_id.default=3;
        this.data.user.records.push({id:5,display_name:"user5",partner_id:3});

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week"'+
                'attendee="partner_ids"'+
                'color="partner_id">'+
                    '<filtername="user_id"avatar_field="image"/>'+
                    '<fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>'+
                    '<fieldname="partner_id"filters="1"invisible="1"/>'+
            '</calendar>',
            viewOptions:{
                initialDate:initialDate,
            },
        },{positionalClicks:true});

        awaittestUtils.dom.click(calendar.$('.o_calendar_filter_item[data-value=4]input'));

        assert.containsN(calendar,'.o_calendar_filter_item',5,"shoulddisplay5filteritems");
        assert.containsN(calendar,'.fc-event',3,"shoulddisplay3events");

        //quickcreatearecord
        varleft=calendar.$('.fc-bgtd:eq(4)').offset().left+15;
        vartop=calendar.$('.fc-slatstr:eq(12)td:first').offset().top+15;
        try{
            testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }
        testUtils.dom.triggerPositionalMouseEvent(left,top+200,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(left,top+200,"mouseup");
        awaittestUtils.nextTick();

        awaittestUtils.fields.editInput($('.modal-bodyinput:first'),'coucou');
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Create)'));

        assert.containsN(calendar,'.o_calendar_filter_item',6,"shouldaddthemissingfilter(active)");
        assert.containsN(calendar,'.fc-event',4,"shoulddisplaythecreateditem");
        awaittestUtils.nextTick();

        //changedefaultvalueforquickcreateanhiderecord
        this.data.event.fields.user_id.default=4;
        this.data.event.fields.partner_id.default=4;

        //quickcreateandotherrecord
        left=calendar.$('.fc-bgtd:eq(3)').offset().left+15;
        top=calendar.$('.fc-slatstr:eq(12)td:first').offset().top+15;
        testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        testUtils.dom.triggerPositionalMouseEvent(left,top+200,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(left,top+200,"mouseup");
        awaittestUtils.nextTick();

        testUtils.fields.editInput($('.modal-bodyinput:first'),'coucou2');
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Create)'));

        assert.containsN(calendar,'.o_calendar_filter_item',6,"shouldhavethesamefilters");
        assert.containsN(calendar,'.fc-event',4,"shouldnotdisplaythecreateditem");

        awaittestUtils.dom.click(calendar.$('.o_calendar_filter_item[data-value=4]input'));

        assert.containsN(calendar,'.fc-event',11,"shoulddisplayallrecords");

        calendar.destroy();
    });

    QUnit.test('createeventwithfilters(noquickCreate)',asyncfunction(assert){
        assert.expect(4);

        this.data.event.fields.user_id.default=5;
        this.data.event.fields.partner_id.default=3;
        this.data.user.records.push({
            id:5,
            display_name:"user5",
            partner_id:3
        });

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week"'+
                'attendee="partner_ids"'+
                'color="partner_id">'+
                    '<filtername="user_id"avatar_field="image"/>'+
                    '<fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>'+
                    '<fieldname="partner_id"filters="1"invisible="1"/>'+
            '</calendar>',
            archs:{
                "event,false,form":
                    '<form>'+
                        '<group>'+
                            '<fieldname="name"/>'+
                            '<fieldname="start"/>'+
                            '<fieldname="stop"/>'+
                            '<fieldname="user_id"/>'+
                            '<fieldname="partner_id"invisible="1"/>'+
                        '</group>'+
                    '</form>',
            },
            viewOptions:{
                initialDate:initialDate,
            },
        },{positionalClicks:true});

        awaittestUtils.dom.click(calendar.$('.o_calendar_filter_item[data-value=4]input'));

        assert.containsN(calendar,'.o_calendar_filter_item',5,"shoulddisplay5filteritems");
        assert.containsN(calendar,'.fc-event',3,"shoulddisplay3events");
        awaittestUtils.nextTick();

        //quickcreatearecord
        varleft=calendar.$('.fc-bgtd:eq(4)').offset().left+15;
        vartop=calendar.$('.fc-slatstr:eq(12)td:first').offset().top+15;
        try{
            testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }
        testUtils.dom.triggerPositionalMouseEvent(left,top+200,"mousemove");
        testUtils.dom.triggerPositionalMouseEvent(left,top+200,"mouseup");
        awaittestUtils.nextTick();

        awaittestUtils.fields.editInput($('.modal-bodyinput:first'),'coucou');

        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Edit)'));
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Save)'));

        assert.containsN(calendar,'.o_calendar_filter_item',6,"shouldaddthemissingfilter(active)");
        assert.containsN(calendar,'.fc-event',4,"shoulddisplaythecreateditem");

        calendar.destroy();
    });

    QUnit.test('Updateeventwithfilters',asyncfunction(assert){
        assert.expect(6);

        varrecords=this.data.user.records;
        records.push({
            id:5,
            display_name:"user5",
            partner_id:3
        });

        this.data.event.onchanges={
            user_id:function(obj){
                obj.partner_id=_.findWhere(records,{id:obj.user_id}).partner_id;
            }
        };

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week"'+
                'attendee="partner_ids"'+
                'color="partner_id">'+
                    '<filtername="user_id"avatar_field="image"/>'+
                    '<fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>'+
                    '<fieldname="partner_id"filters="1"invisible="1"/>'+
            '</calendar>',
            archs:{
                "event,false,form":
                    '<form>'+
                        '<group>'+
                            '<fieldname="name"/>'+
                            '<fieldname="start"/>'+
                            '<fieldname="stop"/>'+
                            '<fieldname="user_id"/>'+
                            '<fieldname="partner_ids"widget="many2many_tags"/>'+
                        '</group>'+
                    '</form>',
            },
            viewOptions:{
                initialDate:initialDate,
            },
        });

        awaittestUtils.dom.click(calendar.$('.o_calendar_filter_item[data-value=4]input'));

        assert.containsN(calendar,'.o_calendar_filter_item',5,"shoulddisplay5filteritems");
        assert.containsN(calendar,'.fc-event',3,"shoulddisplay3events");

        awaittestUtils.dom.click(calendar.$('.fc-event:contains(event2).fc-content'));
        assert.ok(calendar.$('.o_cw_popover').length,"shouldopenapopoverclickingonevent");
        awaittestUtils.dom.click(calendar.$('.o_cw_popover.o_cw_popover_edit'));
        assert.strictEqual($('.modal.modal-title').text(),'Open:event2',"dialogshouldhaveavalidtitle");
        awaittestUtils.dom.click($('.modal.o_field_widget[name="user_id"]input'));
        awaittestUtils.dom.click($('.ui-menu-itema:contains(user5)').trigger('mouseenter'));
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Save)'));

        assert.containsN(calendar,'.o_calendar_filter_item',6,"shouldaddthemissingfilter(active)");
        assert.containsN(calendar,'.fc-event',3,"shoulddisplaytheupdateditem");

        calendar.destroy();
    });

    QUnit.test('changepagerwithfilters',asyncfunction(assert){
        assert.expect(3);

        this.data.user.records.push({
            id:5,
            display_name:"user5",
            partner_id:3
        });
        this.data.event.records.push({
            id:8,
            user_id:5,
            partner_id:3,
            name:"event8",
            start:"2016-12-0604:00:00",
            stop:"2016-12-0608:00:00",
            allday:false,
            partner_ids:[1,2,3],
            type:1
        },{
            id:9,
            user_id:session.uid,
            partner_id:1,
            name:"event9",
            start:"2016-12-0704:00:00",
            stop:"2016-12-0708:00:00",
            allday:false,
            partner_ids:[1,2,3],
            type:1
        },{
            id:10,
            user_id:4,
            partner_id:4,
            name:"event10",
            start:"2016-12-0804:00:00",
            stop:"2016-12-0808:00:00",
            allday:false,
            partner_ids:[1,2,3],
            type:1
        });

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="week"'+
                'attendee="partner_ids"'+
                'color="partner_id">'+
                    '<filtername="user_id"avatar_field="image"/>'+
                    '<fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>'+
                    '<fieldname="partner_id"filters="1"invisible="1"/>'+
            '</calendar>',
            viewOptions:{
                initialDate:initialDate,
            },
        });

        awaittestUtils.dom.click(calendar.$('.o_calendar_filter_item[data-value=4]input'));
        awaittestUtils.dom.click($('.o_calendar_button_prev'));

        assert.containsN(calendar,'.o_calendar_filter_item',6,"shoulddisplay6filteritems");
        assert.containsN(calendar,'.fc-event',2,"shoulddisplay2events");
        assert.strictEqual(calendar.$('.fc-event.o_event_title').text().replace(/\s/g,''),"event8event9",
            "shoulddisplay2events");

        calendar.destroy();
    });

    QUnit.test('ensureeventsarestillshowniffiltersgiveanemptydomain',asyncfunction(assert){
        assert.expect(2);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:'<calendarmode="week"date_start="start">'+
                    '<fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>'+
                '</calendar>',
            viewOptions:{
                initialDate:initialDate,
            },
        });

        assert.containsN(calendar,'.fc-event',5,
            "shoulddisplay5events");
        awaittestUtils.dom.click(calendar.$('.o_calendar_filter_item[data-value=all]input[type=checkbox]'));
        assert.containsN(calendar,'.fc-event',5,
            "shoulddisplay5events");
        calendar.destroy();
    });

    QUnit.test('eventsstartingatmidnight',asyncfunction(assert){
        assert.expect(3);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:'<calendarmode="week"date_start="start"/>',
            viewOptions:{
                initialDate:initialDate,
            },
            translateParameters:{//Avoidissuesduetolocalizationformats
                time_format:"%H:%M:%S",
            },
        },{positionalClicks:true});

        //Resetthescrollto0aswewanttocreateaneventfrommidnight
        assert.ok(calendar.$('.fc-scroller')[0].scrollTop>0,
            "shouldscrollto6:00bydefault(thisistrueatleastforresolutionsupto1900x1600)");
        calendar.$('.fc-scroller')[0].scrollTop=0;

        //ClickonTuesday12am
        vartop=calendar.$('.fc-axis:contains(0:00)').offset().top+5;
        varleft=calendar.$('.fc-day:eq(2)').offset().left+5;
        try{
            testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
            testUtils.dom.triggerPositionalMouseEvent(left,top,"mouseup");
            awaittestUtils.nextTick();
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailedtosimulateaclickonthescreen.'+
                'Yourscreenisprobablytoosmalloryourdevtoolsareopen.');
        }
        assert.ok($('.modal-dialog.modal-sm').length,
            "shouldopenthequickcreatedialog");

        //Creatingtheevent
        testUtils.fields.editInput($('.modal-bodyinput:first'),'neweventinquickcreate');
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Create)'));
        assert.strictEqual(calendar.$('.fc-event:contains(neweventinquickcreate)').length,1,
            "shoulddisplaythenewrecordafterquickcreatedialog");

        calendar.destroy();
    });

    QUnit.test('seteventasalldaywhenfieldisdate',asyncfunction(assert){
        assert.expect(2);

        this.data.event.records[0].start_date="2016-12-14";

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start_date"'+
                'all_day="allday"'+
                'mode="week"'+
                'attendee="partner_ids"'+
                'color="partner_id">'+
                    '<filtername="user_id"avatar_field="image"/>'+
                    '<fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return-480;
                }
            },
        });
        assert.containsOnce(calendar,'.fc-day-grid.fc-event-container',
            "shouldbeoneeventinthealldayrow");
        assert.strictEqual(moment(calendar.model.data.data[0].r_start).date(),14,
            "thedateshouldbe14");
        calendar.destroy();
    });

    QUnit.test('seteventasalldaywhenfieldisdate(withoutall_daymapping)',asyncfunction(assert){
        assert.expect(1);

        this.data.event.records[0].start_date="2016-12-14";

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:`<calendardate_start="start_date"mode="week"></calendar>`,
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });
        assert.containsOnce(calendar,'.fc-day-grid.fc-event-container',
            "shouldbeoneeventinthealldayrow");
        calendar.destroy();
    });

    QUnit.test('quickcreateavoiddoubleeventcreation',asyncfunction(assert){
        assert.expect(1);
        varcreateCount=0;
        varprom=testUtils.makeTestPromise();
        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:'<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                varresult=this._super(route,args);
                if(args.method==="create"){
                    createCount++;
                    returnprom.then(_.constant(result));
                }
                returnresult;
            },
        });

        //createanewevent
        var$cell=calendar.$('.fc-day-grid.fc-row:eq(2).fc-day:eq(2)');
        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();

        var$input=$('.modalinput:first');
        awaittestUtils.fields.editInput($input,'neweventinquickcreate');
        //SimulateENTERpressedonCreatebutton(afteraTAB)
        $input.trigger($.Event('keyup',{
            which:$.ui.keyCode.ENTER,
            keyCode:$.ui.keyCode.ENTER,
        }));
        awaittestUtils.nextTick();
        awaittestUtils.dom.click($('.modal-footerbutton:first'));
        prom.resolve();
        awaittestUtils.nextTick();
        assert.strictEqual(createCount,1,
            "shouldcreateonlyoneevent");

        calendar.destroy();
    });

    QUnit.test('checkiftheviewdestroysallwidgetsandinstances',asyncfunction(assert){
        assert.expect(2);

        varinstanceNumber=0;
        testUtils.mock.patch(mixins.ParentedMixin,{
            init:function(){
                instanceNumber++;
                returnthis._super.apply(this,arguments);
            },
            destroy:function(){
                if(!this.isDestroyed()){
                    instanceNumber--;
                }
                returnthis._super.apply(this,arguments);
            }
        });

        varparams={
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'event_open_popup="true"'+
                'date_start="start_date"'+
                'all_day="allday"'+
                'mode="week"'+
                'attendee="partner_ids"'+
                'color="partner_id">'+
                    '<filtername="user_id"avatar_field="image"/>'+
                    '<fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        };

        varcalendar=awaitcreateCalendarView(params);
        assert.ok(instanceNumber>0);

        calendar.destroy();
        assert.strictEqual(instanceNumber,0);

        testUtils.mock.unpatch(mixins.ParentedMixin);
    });

    QUnit.test('createanevent(asyncdialog)[REQUIREFOCUS]',asyncfunction(assert){
        assert.expect(3);

        varprom=testUtils.makeTestPromise();
        testUtils.mock.patch(Dialog,{
            open:function(){
                var_super=this._super.bind(this);
                prom.then(_super);
                returnthis;
            },
        });
        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'event_open_popup="true"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        //createanevent
        var$cell=calendar.$('.fc-day-grid.fc-row:eq(2).fc-day:eq(2)');
        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();

        assert.strictEqual($('.modal').length,0,
            "shouldnothaveopenedthedialogyet");

        prom.resolve();
        awaittestUtils.nextTick();

        assert.strictEqual($('.modal').length,1,
            "shouldhaveopenedthedialog");
        assert.strictEqual($('.modalinput')[0],document.activeElement,
            "shouldfocustheinputinthedialog");

        calendar.destroy();
        testUtils.mock.unpatch(Dialog);
    });

    QUnit.test('calendarisconfiguredtohavenogroupBymenu',asyncfunction(assert){
        assert.expect(1);

        vararchs={
            'event,1,calendar':'<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'all_day="allday"/>',
            'event,false,search':'<search></search>',
        };

        varactions=[{
            id:1,
            name:'someaction',
            res_model:'event',
            type:'ir.actions.act_window',
            views:[[1,'calendar']]
        }];

        varactionManager=awaitcreateActionManager({
            actions:actions,
            archs:archs,
            data:this.data,
        });

        awaitactionManager.doAction(1);
        assert.containsNone(actionManager.$('.o_control_panel.o_search_optionsspan.fa.fa-bars'),
            "thecontrolpanelhasnogroupBymenu");
        actionManager.destroy();
    });

    QUnit.test('timezonedoesnotaffectcurrentday',asyncfunction(assert){
        assert.expect(2);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendardate_start="start_date"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            session:{
                getTZOffset:function(){
                    return-2400;//40hourstimezone
                },
            },

        });

        var$sidebar=calendar.$('.o_calendar_sidebar');

        assert.strictEqual($sidebar.find('.ui-datepicker-current-day').text(),"12","shouldhighlightthetargetday");

        //gotopreviousday
        awaittestUtils.dom.click($sidebar.find('.ui-datepicker-current-day').prev());

        assert.strictEqual($sidebar.find('.ui-datepicker-current-day').text(),"11","shouldhighlighttheselectedday");

        calendar.destroy();
    });

    QUnit.test('timezonedoesnotaffectdraganddrop',asyncfunction(assert){
        assert.expect(10);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendardate_start="start"mode="month">'+
                '<fieldname="name"/>'+
                '<fieldname="start"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                if(args.method==="write"){
                    assert.deepEqual(args.args[0],[6],"event6ismoved")
                    assert.deepEqual(args.args[1].start,"2016-11-2908:00:00",
                        "eventmovedto27thnov16h00+40hourstimezone")
                }
                returnthis._super(route,args);
            },
            session:{
                getTZOffset:function(){
                    return-2400;//40hourstimezone
                },
            },
        });

        assert.strictEqual(calendar.$('.fc-event:eq(0)').text().replace(/\s/g,''),"08:00event1");
        awaittestUtils.dom.click(calendar.$('.fc-event:eq(0)'));
        assert.strictEqual(calendar.$('.o_field_widget[name="start"]').text(),"12/09/201608:00:00");

        assert.strictEqual(calendar.$('.fc-event:eq(5)').text().replace(/\s/g,''),"16:00event6");
        awaittestUtils.dom.click(calendar.$('.fc-event:eq(5)'));
        assert.strictEqual(calendar.$('.o_field_widget[name="start"]').text(),"12/16/201616:00:00");

        //Moveevent6asonfirstdayofmonthview(27thnovember2016)
        awaittestUtils.dragAndDrop(
            calendar.$('.fc-event').eq(5),
            calendar.$('.fc-day-top').first()
        );
        awaittestUtils.nextTick();

        assert.strictEqual(calendar.$('.fc-event:eq(0)').text().replace(/\s/g,''),"16:00event6");
        awaittestUtils.dom.click(calendar.$('.fc-event:eq(0)'));
        assert.strictEqual(calendar.$('.o_field_widget[name="start"]').text(),"11/27/201616:00:00");

        assert.strictEqual(calendar.$('.fc-event:eq(1)').text().replace(/\s/g,''),"08:00event1");
        awaittestUtils.dom.click(calendar.$('.fc-event:eq(1)'));
        assert.strictEqual(calendar.$('.o_field_widget[name="start"]').text(),"12/09/201608:00:00");

        calendar.destroy();
    });

    QUnit.test('timzeonedoesnotaffectcalendarwithdatefield',asyncfunction(assert){
        assert.expect(11);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendardate_start="start_date"mode="month">'+
                '<fieldname="name"/>'+
                '<fieldname="start_date"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                if(args.method==="create"){
                    assert.strictEqual(args.args[0].start_date,"2016-12-2000:00:00");
                }
                if(args.method==="write"){
                    assert.step(args.args[1].start_date);
                }
                returnthis._super(route,args);
            },
            session:{
                getTZOffset:function(){
                    return120;//2hourstimezone
                },
            },
        });

        //Createevent(on20december)
        var$cell=calendar.$('.fc-day-grid.fc-row:eq(3).fc-day:eq(2)');
        awaittestUtils.triggerMouseEvent($cell,"mousedown");
        awaittestUtils.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();
        var$input=$('.modal-bodyinput:first');
        awaittestUtils.fields.editInput($input,"Anevent");
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Create)'));
        awaittestUtils.nextTick();

        awaittestUtils.dom.click(calendar.$('.fc-event:contains(Anevent)'));
        assert.ok(calendar.$('.o_cw_popover').length,"shouldopenapopoverclickingonevent");
        assert.strictEqual(calendar.$('.o_cw_popover.o_cw_popover_fields_secondary.list-group-item:last.o_field_date').text(),'12/20/2016',"shouldhavecorrectstartdate");

        //Moveeventtoanotherday(on27november)
        awaittestUtils.dragAndDrop(
            calendar.$('.fc-event').first(),
            calendar.$('.fc-day-top').first()
        );
        awaittestUtils.nextTick();
        assert.verifySteps(["2016-11-2700:00:00"]);
        awaittestUtils.dom.click(calendar.$('.fc-event:contains(Anevent)'));
        assert.ok(calendar.$('.o_cw_popover').length,"shouldopenapopoverclickingonevent");
        assert.strictEqual(calendar.$('.o_cw_popover.o_cw_popover_fields_secondary.list-group-item:last.o_field_date').text(),'11/27/2016',"shouldhavecorrectstartdate");

        //Moveeventtolastday(on7january)
        awaittestUtils.dragAndDrop(
            calendar.$('.fc-event').first(),
            calendar.$('.fc-day-top').last()
        );
        awaittestUtils.nextTick();
        assert.verifySteps(["2017-01-0700:00:00"]);
        awaittestUtils.dom.click(calendar.$('.fc-event:contains(Anevent)'));
        assert.ok(calendar.$('.o_cw_popover').length,"shouldopenapopoverclickingonevent");
        assert.strictEqual(calendar.$('.o_cw_popover.o_cw_popover_fields_secondary.list-group-item:last.o_field_date').text(),'01/07/2017',"shouldhavecorrectstartdate");
        calendar.destroy();
    });

    QUnit.test("draganddroponmonthmode",asyncfunction(assert){
        assert.expect(3);

        constcalendar=awaitcreateCalendarView({
            arch:
                `<calendardate_start="start"date_stop="stop"mode="month"event_open_popup="true"quick_add="False">
                    <fieldname="name"/>
                    <fieldname="partner_id"/>
                </calendar>`,
            archs:archs,
            data:this.data,
            model:'event',
            View:CalendarView,
            viewOptions:{initialDate:initialDate},
        });

        //Createevent(on20december)
        var$cell=calendar.$('.fc-day-grid.fc-row:eq(3).fc-day:eq(2)');
        testUtils.triggerMouseEvent($cell,"mousedown");
        testUtils.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();
        var$input=$('.modal-bodyinput:first');
        awaittestUtils.fields.editInput($input,"Anevent");
        awaittestUtils.dom.click($('.modalbutton.btn-primary'));
        awaittestUtils.nextTick();

        awaittestUtils.dragAndDrop(
            calendar.$('.fc-event:contains("event1")'),
            calendar.$('.fc-day-grid.fc-row:eq(3).fc-day-top:eq(1)'),
            {disableDrop:true},
        );
        assert.hasClass(calendar.$('.o_calendar_widget>[data-event-id="1"]'),'dayGridMonth',
            "shouldhavedayGridMonthclass");

        //Moveeventtoanotherday(on19december)
        awaittestUtils.dragAndDrop(
            calendar.$('.fc-event:contains("Anevent")'),
            calendar.$('.fc-day-grid.fc-row:eq(3).fc-day-top:eq(1)')
        );
        awaittestUtils.nextTick();
        awaittestUtils.dom.click(calendar.$('.fc-event:contains("Anevent")'));

        assert.containsOnce(calendar,'.popover:contains("07:00")',
            "starthourshouldn'thavebeenchanged");
        assert.containsOnce(calendar,'.popover:contains("19:00")',
            "endhourshouldn'thavebeenchanged");

        calendar.destroy();
    });

    QUnit.test("draganddroponmonthmodewithall_daymapping",asyncfunction(assert){
        //SametestasbeforebutincalendarEventToRecord(calendar_model.js)thereis
        //differentconditionbranchingwithall_daymappingornot
        assert.expect(2);

        constcalendar=awaitcreateCalendarView({
            arch:
                `<calendardate_start="start"date_stop="stop"mode="month"event_open_popup="true"quick_add="False"all_day="allday">
                    <fieldname="name"/>
                    <fieldname="partner_id"/>
                </calendar>`,
            archs:archs,
            data:this.data,
            model:'event',
            View:CalendarView,
            viewOptions:{initialDate:initialDate},
        });

        //Createevent(on20december)
        var$cell=calendar.$('.fc-day-grid.fc-row:eq(3).fc-day:eq(2)');
        testUtils.triggerMouseEvent($cell,"mousedown");
        testUtils.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();
        var$input=$('.modal-bodyinput:first');
        awaittestUtils.fields.editInput($input,"Anevent");
        awaittestUtils.dom.click($('.o_field_widget[name="allday"]input'));
        awaittestUtils.nextTick();

        //usedatepickertoenteradate:12/20/201607:00:00
        testUtils.dom.openDatepicker($('.o_field_widget[name="start"].o_datepicker'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="togglePicker"]'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker.timepicker-hour'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-hourstd.hour:contains(07)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="close"]'));

        //usedatepickertoenteradate:12/20/201619:00:00
        testUtils.dom.openDatepicker($('.o_field_widget[name="stop"].o_datepicker'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="togglePicker"]'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker.timepicker-hour'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.timepicker-hourstd.hour:contains(19)'));
        awaittestUtils.dom.click($('.bootstrap-datetimepicker-widget.picker-switcha[data-action="close"]'));

        awaittestUtils.dom.click($('.modalbutton.btn-primary'));
        awaittestUtils.nextTick();

        //Moveeventtoanotherday(on19december)
        awaittestUtils.dom.dragAndDrop(
            calendar.$('.fc-event:contains("Anevent")'),
            calendar.$('.fc-day-grid.fc-row:eq(3).fc-day-top:eq(1)')
        );
        awaittestUtils.nextTick();
        awaittestUtils.dom.click(calendar.$('.fc-event:contains("Anevent")'));

        assert.containsOnce(calendar,'.popover:contains("07:00")',
            "starthourshouldn'thavebeenchanged");
        assert.containsOnce(calendar,'.popover:contains("19:00")',
            "endhourshouldn'thavebeenchanged");

        calendar.destroy();
    });

    QUnit.test('draganddroponmonthmodewithdate_startanddate_delay',asyncfunction(assert){
        assert.expect(1);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendardate_start="start"date_delay="delay"mode="month">'+
                '<fieldname="name"/>'+
                '<fieldname="start"/>'+
                '<fieldname="delay"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                if(args.method==="write"){
                    //delayshouldnotbewrittenatdraganddrop
                    assert.equal(args.args[1].delay,undefined)
                }
                returnthis._super(route,args);
            },
        });

        //Createevent(on20december)
        var$cell=calendar.$('.fc-day-grid.fc-row:eq(3).fc-day:eq(2)');
        awaittestUtils.triggerMouseEvent($cell,"mousedown");
        awaittestUtils.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();
        var$input=$('.modal-bodyinput:first');
        awaittestUtils.fields.editInput($input,"Anevent");
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Create)'));
        awaittestUtils.nextTick();

        //Moveeventtoanotherday(on27november)
        awaittestUtils.dragAndDrop(
            calendar.$('.fc-event').first(),
            calendar.$('.fc-day-top').first()
        );
        awaittestUtils.nextTick();

        calendar.destroy();
    });

    QUnit.test('form_view_idattributeworks(forcreatingevents)',asyncfunction(assert){
        assert.expect(1);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:'<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="month"'+
                'form_view_id="42"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                if(args.method==="create"){
                    //wesimulateherethecasewhereacreatecallwithjust
                    //thefieldnamefails. Thisisanormalflow,theserver
                    //rejectthecreaterpc(quickcreate),thenthewebclient
                    //fallbacktoaformview.Thishappenstypicallywhena
                    //modelhasrequiredfields
                    returnPromise.reject('Noneshallpass!');
                }
                returnthis._super(route,args);
            },
            intercepts:{
                do_action:function(event){
                    assert.strictEqual(event.data.action.views[0][0],42,
                        "shoulddoado_actionwithviewid42");
                },
            },
        });

        var$cell=calendar.$('.fc-day-grid.fc-row:eq(2).fc-day:eq(2)');
        awaittestUtils.dom.triggerMouseEvent($cell,"mousedown");
        awaittestUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();

        var$input=$('.modal-bodyinput:first');
        awaittestUtils.fields.editInput($input,"It'sjustafleshwound");
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Create)'));
        awaittestUtils.nextTick();//waitalittlebeforetofinishthetest
        calendar.destroy();
    });

    QUnit.test('form_view_idattributeworkswithpopup(forcreatingevents)',asyncfunction(assert){
        assert.expect(1);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:'<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="month"'+
                'event_open_popup="true"'+
                'quick_add="false"'+
                'form_view_id="1">'+
                    '<fieldname="name"/>'+
            '</calendar>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                if(args.method==="load_views"){
                    assert.strictEqual(args.kwargs.views[0][0],1,
                        "shouldloadviewwithid1");
                }
                returnthis._super(route,args);
            },
        });

        var$cell=calendar.$('.fc-day-grid.fc-row:eq(2).fc-day:eq(2)');
        awaittestUtils.dom.triggerMouseEvent($cell,"mousedown");
        awaittestUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();
        calendar.destroy();
    });

    QUnit.test('calendarfallbacktoformviewidinactionifnecessary',asyncfunction(assert){
        assert.expect(1);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:'<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
                action:{views:[{viewID:1,type:'kanban'},{viewID:43,type:'form'}]}
            },
            mockRPC:function(route,args){
                if(args.method==="create"){
                    //wesimulateherethecasewhereacreatecallwithjust
                    //thefieldnamefails. Thisisanormalflow,theserver
                    //rejectthecreaterpc(quickcreate),thenthewebclient
                    //fallbacktoaformview.Thishappenstypicallywhena
                    //modelhasrequiredfields
                    returnPromise.reject('Noneshallpass!');
                }
                returnthis._super(route,args);
            },
            intercepts:{
                do_action:function(event){
                    assert.strictEqual(event.data.action.views[0][0],43,
                        "shoulddoado_actionwithviewid43");
                },
            },
        });

        var$cell=calendar.$('.fc-day-grid.fc-row:eq(2).fc-day:eq(2)');
        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();

        var$input=$('.modal-bodyinput:first');
        awaittestUtils.fields.editInput($input,"It'sjustafleshwound");
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Create)'));
        calendar.destroy();
    });

    QUnit.test('fullcalendarinitializeswithrightlocale',asyncfunction(assert){
        assert.expect(1);

        varinitialLocale=moment.locale();
        //Thiswillsetthelocaletozz
        moment.defineLocale('zz',{
            longDateFormat:{
                L:'DD/MM/YYYY'
            },
            weekdaysShort:["zz1.","zz2.","zz3.","zz4.","zz5.","zz6.","zz7."],
        });

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:'<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="week"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
                action:{views:[{viewID:1,type:'kanban'},{viewID:43,type:'form'}]}
            },

        });

        assert.strictEqual(calendar.$('.fc-day-header:first').text(),"zz1.11",
            'Thedayshouldbeinthegivenlocalespecificformat');

        moment.locale(initialLocale);

        calendar.destroy();
    });

    QUnit.test('defaultweekstart(US)monthmode',asyncfunction(assert){
        //ifnotgivenanyoption,defaultweekstartisonSunday
        assert.expect(8);

        //2019-09-1208:00:00
        varinitDate=newDate(2019,8,12,8,0,0);
        initDate=newDate(initDate.getTime()-initDate.getTimezoneOffset()*60*1000);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="month">'+
            '</calendar>',
            archs:archs,

            viewOptions:{
                initialDate:initDate,
            },
            mockRPC:function(route,args){
                if(args.method==='search_read'&&args.model==='event'){
                    assert.deepEqual(args.kwargs.domain,[
                        ["start","<=","2019-10-1223:59:59"],
                        ["stop",">=","2019-09-0100:00:00"]
                    ],
                    'Thedomaintosearcheventsinshouldbecorrect');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.strictEqual(calendar.$('.fc-day-header').first().text(),"Sunday",
            "ThefirstdayoftheweekshouldbeSunday");
        assert.strictEqual(calendar.$('.fc-day-header').last().text(),"Saturday",
            "ThelastdayoftheweekshouldbeSaturday");

        var$firstDay=calendar.$('.fc-day-top').first();

        assert.strictEqual($firstDay.find('.fc-week-number').text(),"36",
            "Thenumberoftheweekshouldbecorrect");
        assert.strictEqual($firstDay.find('.fc-day-number').text(),"1",
            "Thefirstdayoftheweekshouldbe2019-09-01");
        assert.strictEqual($firstDay.data('date'),"2019-09-01",
            "Thefirstdayoftheweekshouldbe2019-09-01");

        var$lastDay=calendar.$('.fc-day-top').last();
        assert.strictEqual($lastDay.text(),"12",
            "Thelastdayoftheweekshouldbe2019-10-12");
        assert.strictEqual($lastDay.data('date'),"2019-10-12",
            "Thelastdayoftheweekshouldbe2019-10-12");

        calendar.destroy();
    });

    QUnit.test('Europeanweekstartmonthmode',asyncfunction(assert){
        assert.expect(8);

        //2019-09-1208:00:00
        varinitDate=newDate(2019,8,15,8,0,0);
        initDate=newDate(initDate.getTime()-initDate.getTimezoneOffset()*60*1000);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="month">'+
            '</calendar>',
            archs:archs,

            viewOptions:{
                initialDate:initDate,
            },
            translateParameters:{
                week_start:1,
            },
            mockRPC:function(route,args){
                if(args.method==='search_read'&&args.model==='event'){
                    assert.deepEqual(args.kwargs.domain,[
                        ["start","<=","2019-10-0623:59:59"],
                        ["stop",">=","2019-08-2600:00:00"]
                    ],
                    'Thedomaintosearcheventsinshouldbecorrect');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.strictEqual(calendar.$('.fc-day-header').first().text(),"Monday",
            "ThefirstdayoftheweekshouldbeMonday");
        assert.strictEqual(calendar.$('.fc-day-header').last().text(),"Sunday",
            "ThelastdayoftheweekshouldbeSunday");

        var$firstDay=calendar.$('.fc-day-top').first();
        assert.strictEqual($firstDay.find('.fc-week-number').text(),"35",
            "Thenumberoftheweekshouldbecorrect");
        assert.strictEqual($firstDay.find('.fc-day-number').text(),"26",
            "Thefirstdayoftheweekshouldbe2019-09-01");
        assert.strictEqual($firstDay.data('date'),"2019-08-26",
            "Thefirstdayoftheweekshouldbe2019-08-26");

        var$lastDay=calendar.$('.fc-day-top').last();
        assert.strictEqual($lastDay.text(),"6",
            "Thelastdayoftheweekshouldbe2019-10-06");
        assert.strictEqual($lastDay.data('date'),"2019-10-06",
            "Thelastdayoftheweekshouldbe2019-10-06");

        calendar.destroy();
    });

    QUnit.test('Mondayweekstartweekmode',asyncfunction(assert){
        assert.expect(3);

        //2019-09-1208:00:00
        varinitDate=newDate(2019,8,15,8,0,0);
        initDate=newDate(initDate.getTime()-initDate.getTimezoneOffset()*60*1000);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="week">'+
            '</calendar>',
            archs:archs,

            viewOptions:{
                initialDate:initDate,
            },
            translateParameters:{
                week_start:1,
            },
            mockRPC:function(route,args){
                if(args.method==='search_read'&&args.model==='event'){
                    assert.deepEqual(args.kwargs.domain,[
                        ["start","<=","2019-09-1523:59:59"],
                        ["stop",">=","2019-09-0900:00:00"]
                    ],
                    'Thedomaintosearcheventsinshouldbecorrect');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.strictEqual(calendar.$('.fc-day-header').first().text(),"Mon9",
            "ThefirstdayoftheweekshouldbeMondaythe9th");
        assert.strictEqual(calendar.$('.fc-day-header').last().text(),"Sun15",
            "ThelastdayoftheweekshouldbeSundaythe15th");

        calendar.destroy();
    });

    QUnit.test('Saturdayweekstartweekmode',asyncfunction(assert){
        assert.expect(3);

        //2019-09-1208:00:00
        varinitDate=newDate(2019,8,12,8,0,0);
        initDate=newDate(initDate.getTime()-initDate.getTimezoneOffset()*60*1000);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="week">'+
            '</calendar>',
            archs:archs,

            viewOptions:{
                initialDate:initDate,
            },
            translateParameters:{
                week_start:6,
            },
            mockRPC:function(route,args){
                if(args.method==='search_read'&&args.model==='event'){
                    assert.deepEqual(args.kwargs.domain,[
                        ["start","<=","2019-09-1323:59:59"],
                        ["stop",">=","2019-09-0700:00:00"]
                    ],
                    'Thedomaintosearcheventsinshouldbecorrect');
                }
                returnthis._super.apply(this,arguments);
            }
        });

        assert.strictEqual(calendar.$('.fc-day-header').first().text(),"Sat7",
            "ThefirstdayoftheweekshouldbeSaturdaythe7th");
        assert.strictEqual(calendar.$('.fc-day-header').last().text(),"Fri13",
            "ThelastdayoftheweekshouldbeFridaythe13th");

        calendar.destroy();
    });

    QUnit.test('editrecordandattempttocreatearecordwith"create"attributesettofalse',asyncfunction(assert){
        assert.expect(8);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'event_open_popup="true"'+
                'create="false"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="month"/>',
            archs:archs,
            mockRPC:function(route,args){
                if(args.method==='write'){
                    assert.deepEqual(args.args[1],{name:'event4modified'},"shouldupdatetherecord");
                }
                returnthis._super.apply(this,arguments);
            },
            viewOptions:{
                initialDate:initialDate,
            },
        });

        //editingexistingeventsshouldstillbepossible
        //clickonanexistingeventtoopentheformViewDialog

        awaittestUtils.dom.click(calendar.$('.fc-event:contains(event4).fc-content'));

        assert.ok(calendar.$('.o_cw_popover').length,"shouldopenapopoverclickingonevent");
        assert.ok(calendar.$('.o_cw_popover.o_cw_popover_edit').length,"popovershouldhaveaneditbutton");
        assert.ok(calendar.$('.o_cw_popover.o_cw_popover_delete').length,"popovershouldhaveadeletebutton");
        assert.ok(calendar.$('.o_cw_popover.o_cw_popover_close').length,"popovershouldhaveaclosebutton");

        awaittestUtils.dom.click(calendar.$('.o_cw_popover.o_cw_popover_edit'));

        assert.ok($('.modal-body').length,"shouldopentheformviewindialogwhenclickonedit");

        awaittestUtils.fields.editInput($('.modal-bodyinput:first'),'event4modified');
        awaittestUtils.dom.click($('.modal-footerbutton.btn:contains(Save)'));

        assert.notOk($('.modal-body').length,"savebuttonshouldclosethemodal");

        //creatinganeventshouldnotbepossible
        //attempttocreateaneweventwithcreatesettofalse

        var$cell=calendar.$('.fc-day-grid.fc-row:eq(2).fc-day:eq(2)');

        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();

        assert.notOk($('.modal-sm').length,"shouldn'topenaquickcreatedialogforcreatinganeweventwithcreateattributesettofalse");

        calendar.destroy();
    });


    QUnit.test('attempttocreaterecordwith"create"and"quick_add"attributessettofalse',asyncfunction(assert){
        assert.expect(1);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'string="Events"'+
                'create="false"'+
                'event_open_popup="true"'+
                'quick_add="false"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="month"/>',
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        //attempttocreateaneweventwithcreatesettofalse

        var$cell=calendar.$('.fc-day-grid.fc-row:eq(5).fc-day:eq(2)');

        testUtils.dom.triggerMouseEvent($cell,"mousedown");
        testUtils.dom.triggerMouseEvent($cell,"mouseup");
        awaittestUtils.nextTick();

        assert.strictEqual($('.modal').length,0,"shouldn'topenaformviewforcreatinganeweventwithcreateattributesettofalse");

        calendar.destroy();
    });

    QUnit.test('attempttocreatemultipleseventsandthesamedayandchecktheorderingonmonthview',asyncfunction(assert){
        assert.expect(3);
        /*
         Thistestaimstoverifythattheorderoftheeventinmonthviewiscoherentwiththeirstartdate.
         */
        varinitDate=newDate(2020,2,12,8,0,0);//12ofMarch
        this.data.event.records=[
            {id:1,name:"Secondevent",start:"2020-03-1205:00:00",stop:"2020-03-1207:00:00",allday:false},
            {id:2,name:"Firstevent",start:"2020-03-1202:00:00",stop:"2020-03-1203:00:00",allday:false},
            {id:3,name:"Thirdevent",start:"2020-03-1208:00:00",stop:"2020-03-1209:00:00",allday:false},
        ];
        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:`<calendardate_start="start"date_stop="stop"all_day="allday"mode="month"/>`,
            archs:archs,
            viewOptions:{
                initialDate:initDate,
            },
        });
        assert.ok(calendar.$('.o_calendar_view').find('.fc-view-container').length,"shoulddisplayinthecalendar");//OK
        //Testingtheorderoftheevents:bystartdate
        assert.strictEqual(calendar.$('.o_event_title').length,3,"3eventsshouldbeavailable");//OK
        assert.strictEqual(calendar.$('.o_event_title').first().text(),'Firstevent',"Firsteventshouldbeontop");
        calendar.destroy();
    });

    QUnit.test("draganddrop24heventonweekmode",asyncfunction(assert){
        assert.expect(1);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:`
                <calendar
                    event_open_popup="true"
                    quick_add="False"
                    date_start="start"
                    date_stop="stop"
                    all_day="allday"
                    mode="week"
                 />
            `,
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        },{positionalClicks:true});

        vartop=calendar.$('.fc-axis:contains(8:00)').offset().top+5;
        varleft=calendar.$('.fc-day:eq(2)').offset().left+5;

        try{
            testUtils.dom.triggerPositionalMouseEvent(left,top,"mousedown");
        }catch(e){
            calendar.destroy();
            thrownewError('Thetestfailstosimulateaclickinthescreen.Yourscreenisprobablytoosmalloryourdevtoolsisopen.');
        }

        top=calendar.$('.fc-axis:contains(8:00)').offset().top-5;
        varleftNextDay=calendar.$('.fc-day:eq(3)').offset().left+5;
        testUtils.dom.triggerPositionalMouseEvent(leftNextDay,top,"mousemove");
        awaittestUtils.dom.triggerPositionalMouseEvent(leftNextDay,top,"mouseup");
        awaittestUtils.nextTick();
        assert.equal($('.o_field_boolean.o_field_widget[name=allday]input').is(':checked'),false,
            "Theeventmustnothavetheall_dayactive");
        awaittestUtils.dom.click($('.modalbutton.btn:contains(Discard)'));

        calendar.destroy();
    });

    QUnit.test('correctlydisplayyearview',asyncfunction(assert){
        assert.expect(27);

        constcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:`
                <calendar
                    create="false"
                    event_open_popup="true"
                    date_start="start"
                    date_stop="stop"
                    all_day="allday"
                    mode="year"
                    attendee="partner_ids"
                    color="partner_id"
                >
                    <fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>
                    <fieldname="partner_id"filters="1"invisible="1"/>
                </calendar>`,
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        },{positionalClicks:true});

        //Checkview
        assert.containsN(calendar,'.fc-month',12);
        assert.strictEqual(
            calendar.el.querySelector('.fc-month:first-child.fc-header-toolbar').textContent,
            'Jan2016'
        );
        assert.containsN(calendar.el,'.fc-bgevent',7,
            'Thereshouldbe6eventsdisplayedbutthereis1spliton2weeks');

        asyncfunctionclickDate(date){
            constel=calendar.el.querySelector(`.fc-day-top[data-date="${date}"]`);
            el.scrollIntoView();//scrolltoitasthecalendarcouldbetoosmall

            testUtils.dom.triggerMouseEvent(el,"mousedown");
            testUtils.dom.triggerMouseEvent(el,"mouseup");

            awaittestUtils.nextTick();
        }

        assert.notOk(calendar.el.querySelector('.fc-day-top[data-date="2016-11-17"]')
            .classList.contains('fc-has-event'));
        awaitclickDate('2016-11-17');
        assert.containsNone(calendar,'.o_cw_popover');

        assert.ok(calendar.el.querySelector('.fc-day-top[data-date="2016-11-16"]')
            .classList.contains('fc-has-event'));
        awaitclickDate('2016-11-16');
        assert.containsOnce(calendar,'.o_cw_popover');
        letpopoverText=calendar.el.querySelector('.o_cw_popover')
            .textContent.replace(/\s{2,}/g,'').trim();
        assert.strictEqual(popoverText,'November14-16,2016event7');
        awaittestUtils.dom.click(calendar.el.querySelector('.o_cw_popover_close'));
        assert.containsNone(calendar,'.o_cw_popover');

        assert.ok(calendar.el.querySelector('.fc-day-top[data-date="2016-11-14"]')
            .classList.contains('fc-has-event'));
        awaitclickDate('2016-11-14');
        assert.containsOnce(calendar,'.o_cw_popover');
        popoverText=calendar.el.querySelector('.o_cw_popover')
            .textContent.replace(/\s{2,}/g,'').trim();
        assert.strictEqual(popoverText,'November14-16,2016event7');
        awaittestUtils.dom.click(calendar.el.querySelector('.o_cw_popover_close'));
        assert.containsNone(calendar,'.o_cw_popover');

        assert.notOk(calendar.el.querySelector('.fc-day-top[data-date="2016-11-13"]')
            .classList.contains('fc-has-event'));
        awaitclickDate('2016-11-13');
        assert.containsNone(calendar,'.o_cw_popover');

        assert.notOk(calendar.el.querySelector('.fc-day-top[data-date="2016-12-10"]')
            .classList.contains('fc-has-event'));
        awaitclickDate('2016-12-10');
        assert.containsNone(calendar,'.o_cw_popover');

        assert.ok(calendar.el.querySelector('.fc-day-top[data-date="2016-12-12"]')
            .classList.contains('fc-has-event'));
        awaitclickDate('2016-12-12');
        assert.containsOnce(calendar,'.o_cw_popover');
        popoverText=calendar.el.querySelector('.o_cw_popover')
            .textContent.replace(/\s{2,}/g,'').trim();
        assert.strictEqual(popoverText,'December12,2016event2event3');
        awaittestUtils.dom.click(calendar.el.querySelector('.o_cw_popover_close'));
        assert.containsNone(calendar,'.o_cw_popover');

        assert.ok(calendar.el.querySelector('.fc-day-top[data-date="2016-12-14"]')
            .classList.contains('fc-has-event'));
        awaitclickDate('2016-12-14');
        assert.containsOnce(calendar,'.o_cw_popover');
        popoverText=calendar.el.querySelector('.o_cw_popover')
            .textContent.replace(/\s{2,}/g,'').trim();
        assert.strictEqual(popoverText,
            'December14,2016event4December13-20,2016event5');
        awaittestUtils.dom.click(calendar.el.querySelector('.o_cw_popover_close'));
        assert.containsNone(calendar,'.o_cw_popover');

        assert.notOk(calendar.el.querySelector('.fc-day-top[data-date="2016-12-21"]')
            .classList.contains('fc-has-event'));
        awaitclickDate('2016-12-21');
        assert.containsNone(calendar,'.o_cw_popover');

        calendar.destroy();
    });

    QUnit.test('togglefiltersinyearview',asyncfunction(assert){
        assert.expect(42);

        constcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:`
                <calendar
                    event_open_popup="true"
                    date_start="start"
                    date_stop="stop"
                    all_day="allday"
                    mode="year"
                    attendee="partner_ids"
                    color="partner_id"
                >
                    <fieldname="partner_ids"write_model="filter_partner"write_field="partner_id"/>
                    <fieldname="partner_id"filters="1"invisible="1"/>
                '</calendar>`,
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        functioncheckEvents(countMap){
            for(const[id,count]ofObject.entries(countMap)){
                assert.containsN(calendar,`.fc-bgevent[data-event-id="${id}"]`,count);
            }
        }

        checkEvents({1:1,2:1,3:1,4:1,5:2,7:1,});
        awaittestUtils.dom.click(calendar.el.querySelector(
            '#o_cw_filter_collapse_attendees.o_calendar_filter_item[data-value="2"]label'));
        checkEvents({1:1,2:1,3:1,4:1,5:0,7:0,});
        awaittestUtils.dom.click(calendar.el.querySelector(
            '#o_cw_filter_collapse_user.o_calendar_filter_item[data-value="1"]label'));
        checkEvents({1:0,2:0,3:1,4:0,5:0,7:0,});
        awaittestUtils.dom.click(calendar.el.querySelector(
            '#o_cw_filter_collapse_user.o_calendar_filter_item[data-value="4"]label'));
        checkEvents({1:0,2:0,3:0,4:0,5:0,7:0,});
        awaittestUtils.dom.click(calendar.el.querySelector(
            '#o_cw_filter_collapse_attendees.o_calendar_filter_item[data-value="1"]label'));
        checkEvents({1:0,2:0,3:0,4:0,5:0,7:0,});
        awaittestUtils.dom.click(calendar.el.querySelector(
            '#o_cw_filter_collapse_attendees.o_calendar_filter_item[data-value="2"]label'));
        checkEvents({1:0,2:0,3:0,4:0,5:0,7:0,});
        awaittestUtils.dom.click(calendar.el.querySelector(
            '#o_cw_filter_collapse_user.o_calendar_filter_item[data-value="4"]label'));
        checkEvents({1:0,2:0,3:0,4:0,5:2,7:0,});

        calendar.destroy();
    });

    QUnit.test('allowedscales',asyncfunction(assert){
        assert.expect(8);

        letcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
                `<calendar
                    date_start="start"
                    date_stop="stop"
                    all_day="allday"/>`,
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        assert.containsOnce(calendar,'.o_calendar_scale_buttons.o_calendar_button_day');
        assert.containsOnce(calendar,'.o_calendar_scale_buttons.o_calendar_button_week');
        assert.containsOnce(calendar,'.o_calendar_scale_buttons.o_calendar_button_month');
        assert.containsOnce(calendar,'.o_calendar_scale_buttons.o_calendar_button_year');

        calendar.destroy();

        calendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
                `<calendar
                    date_start="start"
                    date_stop="stop"
                    all_day="allday"
                    scales="day,week"/>`,
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        assert.containsOnce(calendar,'.o_calendar_scale_buttons.o_calendar_button_day');
        assert.containsOnce(calendar,'.o_calendar_scale_buttons.o_calendar_button_week');
        assert.containsNone(calendar,'.o_calendar_scale_buttons.o_calendar_button_month');
        assert.containsNone(calendar,'.o_calendar_scale_buttons.o_calendar_button_year');

        calendar.destroy();
    });

    QUnit.test('clickoutsidethepopupshouldcloseit',asyncfunction(assert){
        assert.expect(4);

        varcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
                `<calendar
                    create="false"
                    event_open_popup="true"
                    quick_add="false"
                    date_start="start"
                    date_stop="stop"
                    all_day="allday"
                    mode="month"/>`,
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        assert.containsNone(calendar,'.o_cw_popover');

        awaittestUtils.dom.click(calendar.el.querySelector('.fc-event.fc-content'));
        assert.containsOnce(calendar,'.o_cw_popover',
            'openpopupwhenclickonevent');

        awaittestUtils.dom.click(calendar.el.querySelector('.o_cw_body'));
        assert.containsOnce(calendar,'.o_cw_popover',
            'keeppopupopennedwhenclickinsidepopup');

        awaittestUtils.dom.click(calendar.el.querySelector('.o_content'));
        assert.containsNone(calendar,'.o_cw_popover',
            'closepopupwhenclickoutsidepopup');

        calendar.destroy();
    });

    QUnit.test("fieldsareaddedintherightorderinpopover",asyncfunction(assert){
        assert.expect(3);

        constdef=testUtils.makeTestPromise();
        constDeferredWidget=AbstractField.extend({
            asyncstart(){
                awaitthis._super(...arguments);
                awaitdef;
            }
        });
        fieldRegistry.add("deferred_widget",DeferredWidget);

        constcalendar=awaitcreateCalendarView({
            View:CalendarView,
            model:'event',
            data:this.data,
            arch:
                `<calendar
                    date_start="start"
                    date_stop="stop"
                    all_day="allday"
                    mode="month"
                >
                    <fieldname="user_id"widget="deferred_widget"/>
                    <fieldname="name"/>
                </calendar>`,
            archs:archs,
            viewOptions:{
                initialDate:initialDate,
            },
        });

        awaittestUtils.dom.click(calendar.$(`[data-event-id="4"]`));
        assert.containsNone(calendar,".o_cw_popover");

        def.resolve();
        awaittestUtils.nextTick();
        assert.containsOnce(calendar,".o_cw_popover");

        assert.strictEqual(
            calendar.$(".o_cw_popover.o_cw_popover_fields_secondary").text(),
            "user:name:event4"
        );

        calendar.destroy();
        deletefieldRegistry.map.deferred_widget;
    });

});

});
