flectra.define('calendar.systray.ActivityMenuTests',function(require){
"usestrict";

const{afterEach,beforeEach,start}=require('mail/static/src/utils/test_utils.js');
varActivityMenu=require('mail.systray.ActivityMenu');

vartestUtils=require('web.test_utils');

QUnit.module('calendar',{},function(){
QUnit.module('ActivityMenu',{
    beforeEach(){
        beforeEach(this);

        Object.assign(this.data,{
            'calendar.event':{
                fields:{//thoseareallfake,thisisthemockofaformatter
                    meetings:{type:'binary'},
                    model:{type:'char'},
                    name:{type:'char',required:true},
                    type:{type:'char'},
                },
                records:[{
                    name:"Today'smeeting(3)",
                    model:"calendar.event",
                    type:'meeting',
                    meetings:[{
                        id:1,
                        res_model:"calendar.event",
                        name:"meeting1",
                        start:"2018-04-2006:30:00",
                        allday:false,
                    },{
                        id:2,
                        res_model:"calendar.event",
                        name:"meeting2",
                        start:"2018-04-2009:30:00",
                        allday:false,
                    }]
                }],
            },
        });
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.test('activitymenuwidget:todaymeetings',asyncfunction(assert){
    assert.expect(6);
    varself=this;

    const{widget}=awaitstart({
        data:this.data,
        mockRPC:function(route,args){
            if(args.method==='systray_get_activities'){
                returnPromise.resolve(self.data['calendar.event']['records']);
            }
            returnthis._super(route,args);
        },
    });

    constactivityMenu=newActivityMenu(widget);
    awaitactivityMenu.appendTo($('#qunit-fixture'));

    assert.hasClass(activityMenu.$el,'o_mail_systray_item','shouldbetheinstanceofwidget');

    awaittestUtils.dom.click(activityMenu.$('.dropdown-toggle'));

    testUtils.mock.intercept(activityMenu,'do_action',function(event){
        assert.strictEqual(event.data.action,"calendar.action_calendar_event",'shouldopenmeetingcalendarviewindaymode');
    });
    awaittestUtils.dom.click(activityMenu.$('.o_mail_preview'));

    assert.ok(activityMenu.$('.o_meeting_filter'),"shouldbeameeting");
    assert.containsN(activityMenu,'.o_meeting_filter',2,'thereshouldbe2meetings');
    assert.hasClass(activityMenu.$('.o_meeting_filter').eq(0),'o_meeting_bold','thismeetingisyettostart');
    assert.doesNotHaveClass(activityMenu.$('.o_meeting_filter').eq(1),'o_meeting_bold','thismeetinghasbeenstarted');
    widget.destroy();
});
});

});
