flectra.define('mail.systray.ActivityMenuTests',function(require){
"usestrict";

const{
    afterEach,
    afterNextRender,
    beforeEach,
    start,
}=require('mail/static/src/utils/test_utils.js');
varActivityMenu=require('mail.systray.ActivityMenu');

vartestUtils=require('web.test_utils');

QUnit.module('mail',{},function(){
QUnit.module('ActivityMenu',{
    beforeEach(){
        beforeEach(this);

        Object.assign(this.data,{
            'mail.activity.menu':{
                fields:{
                    name:{type:"char"},
                    model:{type:"char"},
                    type:{type:"char"},
                    planned_count:{type:"integer"},
                    today_count:{type:"integer"},
                    overdue_count:{type:"integer"},
                    total_count:{type:"integer"},
                    actions:[{
                        icon:{type:"char"},
                        name:{type:"char"},
                        action_xmlid:{type:"char"},
                    }],
                },
                records:[{
                        name:"Contact",
                        model:"res.partner",
                        type:"activity",
                        planned_count:0,
                        today_count:1,
                        overdue_count:0,
                        total_count:1,
                    },
                    {
                        name:"Task",
                        type:"activity",
                        model:"project.task",
                        planned_count:1,
                        today_count:0,
                        overdue_count:0,
                        total_count:1,
                    },
                    {
                        name:"Issue",
                        type:"activity",
                        model:"project.issue",
                        planned_count:1,
                        today_count:1,
                        overdue_count:1,
                        total_count:3,
                        actions:[{
                            icon:"fa-clock-o",
                            name:"summary",
                        }],
                    },
                    {
                        name:"Note",
                        type:"activity",
                        model:"partner",
                        planned_count:1,
                        today_count:1,
                        overdue_count:1,
                        total_count:3,
                        actions:[{
                            icon:"fa-clock-o",
                            name:"summary",
                            action_xmlid:"mail.mail_activity_type_view_tree",
                        }],
                    }
                ],
            },
        });
        this.session={
            uid:10,
        };
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.test('activitymenuwidget:menuwithnorecords',asyncfunction(assert){
    assert.expect(1);

    const{widget}=awaitstart({
        data:this.data,
        mockRPC:function(route,args){
            if(args.method==='systray_get_activities'){
                returnPromise.resolve([]);
            }
            returnthis._super(route,args);
        },
    });
    constactivityMenu=newActivityMenu(widget);
    awaitactivityMenu.appendTo($('#qunit-fixture'));
    awaittestUtils.nextTick();
    assert.containsOnce(activityMenu,'.o_no_activity');
    widget.destroy();
});

QUnit.test('activitymenuwidget:activitymenuwith3records',asyncfunction(assert){
    assert.expect(10);
    varself=this;

    const{widget}=awaitstart({
        data:this.data,
        mockRPC:function(route,args){
            if(args.method==='systray_get_activities'){
                returnPromise.resolve(self.data['mail.activity.menu']['records']);
            }
            returnthis._super(route,args);
        },
    });
    varactivityMenu=newActivityMenu(widget);
    awaitactivityMenu.appendTo($('#qunit-fixture'));
    awaittestUtils.nextTick();
    assert.hasClass(activityMenu.$el,'o_mail_systray_item','shouldbetheinstanceofwidget');
    //theassertionbelowhasnotbeenreplacebecausethereareincludesofActivityMenuthatmodifythelength.
    assert.ok(activityMenu.$('.o_mail_preview').length);
    assert.containsOnce(activityMenu.$el,'.o_notification_counter',"widgetshouldhavenotificationcounter");
    assert.strictEqual(parseInt(activityMenu.el.innerText),8,"widgetshouldhave8notificationcounter");

    varcontext={};
    testUtils.mock.intercept(activityMenu,'do_action',function(event){
        assert.deepEqual(event.data.action.context,context,"wrongcontextvalue");
    },true);

    //case1:clickon"late"
    context={
        force_search_count:1,
        search_default_activities_overdue:1,
    };
    awaittestUtils.dom.click(activityMenu.$('.dropdown-toggle'));
    assert.hasClass(activityMenu.$el,'show','ActivityMenushouldbeopen');
    awaittestUtils.dom.click(activityMenu.$(".o_activity_filter_button[data-model_name='Issue'][data-filter='overdue']"));
    assert.doesNotHaveClass(activityMenu.$el,'show','ActivityMenushouldbeclosed');
    //case2:clickon"today"
    context={
        force_search_count:1,
        search_default_activities_today:1,
    };
    awaittestUtils.dom.click(activityMenu.$('.dropdown-toggle'));
    awaittestUtils.dom.click(activityMenu.$(".o_activity_filter_button[data-model_name='Issue'][data-filter='today']"));
    //case3:clickon"future"
    context={
        force_search_count:1,
        search_default_activities_upcoming_all:1,
    };
    awaittestUtils.dom.click(activityMenu.$('.dropdown-toggle'));
    awaittestUtils.dom.click(activityMenu.$(".o_activity_filter_button[data-model_name='Issue'][data-filter='upcoming_all']"));
    //case4:clickanywereelse
    context={
        force_search_count:1,
        search_default_activities_overdue:1,
        search_default_activities_today:1,
    };
    awaittestUtils.dom.click(activityMenu.$('.dropdown-toggle'));
    awaittestUtils.dom.click(activityMenu.$(".o_mail_systray_dropdown_items>div[data-model_name='Issue']"));

    widget.destroy();
});

QUnit.test('activitymenuwidget:activityviewicon',asyncfunction(assert){
    assert.expect(12);
    varself=this;

    const{widget}=awaitstart({
        data:this.data,
        mockRPC:function(route,args){
            if(args.method==='systray_get_activities'){
                returnPromise.resolve(self.data['mail.activity.menu'].records);
            }
            returnthis._super(route,args);
        },
        session:this.session,
    });
    varactivityMenu=newActivityMenu(widget);
    awaitactivityMenu.appendTo($('#qunit-fixture'));
    awaittestUtils.nextTick();
    assert.containsN(activityMenu,'.o_mail_activity_action',2,
                       "widgetshouldhave2activityviewicons");

    var$first=activityMenu.$('.o_mail_activity_action').eq(0);
    var$second=activityMenu.$('.o_mail_activity_action').eq(1);
    assert.strictEqual($first.data('model_name'),"Issue",
                       "firstactivityactionshouldlinkto'Issue'");
    assert.hasClass($first,'fa-clock-o',"shoulddisplaytheactivityactionicon");

    assert.strictEqual($second.data('model_name'),"Note",
                       "Secondactivityactionshouldlinkto'Note'");
    assert.hasClass($second,'fa-clock-o',"shoulddisplaytheactivityactionicon");

    testUtils.mock.intercept(activityMenu,'do_action',function(ev){
        if(ev.data.action.name){
            assert.ok(ev.data.action.domain,"shoulddefineadomainontheaction");
            assert.deepEqual(ev.data.action.domain,[["activity_ids.user_id","=",10]],
                "shouldsetdomaintouser'sactivityonly");
            assert.step('do_action:'+ev.data.action.name);
        }else{
            assert.step('do_action:'+ev.data.action);
        }
    },true);

    //clickonthe"Issue"activityicon
    awaittestUtils.dom.click(activityMenu.$('.dropdown-toggle'));
    assert.hasClass(activityMenu.$('.dropdown-menu'),'show',
        "dropdownshouldbeexpanded");

    awaittestUtils.dom.click(activityMenu.$(".o_mail_activity_action[data-model_name='Issue']"));
    assert.doesNotHaveClass(activityMenu.$('.dropdown-menu'),'show',
        "dropdownshouldbecollapsed");

    //clickonthe"Note"activityicon
    awaittestUtils.dom.click(activityMenu.$('.dropdown-toggle'));
    awaittestUtils.dom.click(activityMenu.$(".o_mail_activity_action[data-model_name='Note']"));

    assert.verifySteps([
        'do_action:Issue',
        'do_action:mail.mail_activity_type_view_tree'
    ]);

    widget.destroy();
});

QUnit.test('activitymenuwidget:closeonmessagingmenuclick',asyncfunction(assert){
    assert.expect(2);

    const{widget}=awaitstart({
        data:this.data,
        hasMessagingMenu:true,
        asyncmockRPC(route,args){
            if(args.method==='message_fetch'){
                return[];
            }
            if(args.method==='systray_get_activities'){
                return[];
            }
            returnthis._super(route,args);
        },
    });
    constactivityMenu=newActivityMenu(widget);
    awaitactivityMenu.appendTo($('#qunit-fixture'));
    awaittestUtils.nextTick();

    awaittestUtils.dom.click(activityMenu.$('.dropdown-toggle'));
    assert.hasClass(
        activityMenu.el.querySelector('.o_mail_systray_dropdown'),
        'show',
        "activitymenushouldbeshownafterclickonitself"
    );

    awaitafterNextRender(()=>
        document.querySelector(`.o_MessagingMenu_toggler`).click()
    );
    assert.doesNotHaveClass(
        activityMenu.el.querySelector('.o_mail_systray_dropdown'),
        'show',
        "activitymenushouldbehiddenafterclickonmessagingmenu"
    );

    widget.destroy();
});

});

});
