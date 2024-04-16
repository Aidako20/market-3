flectra.define('google_calendar.calendar_tests',function(require){
"usestrict";

varGoogleCalendarView=require('calendar.CalendarView');
vartestUtils=require('web.test_utils');

varcreateCalendarView=testUtils.createCalendarView;

varinitialDate=newDate("2016-12-12T08:00:00Z");


QUnit.module('GoogleCalendar',{
    beforeEach:function(){
        this.data={
            'calendar.event':{
                fields:{
                    id:{string:"ID",type:"integer"},
                    user_id:{string:"user",type:"many2one",relation:'user'},
                    partner_id:{string:"user",type:"many2one",relation:'partner',related:'user_id.partner_id'},
                    name:{string:"name",type:"char"},
                    start_date:{string:"startdate",type:"date"},
                    stop_date:{string:"stopdate",type:"date"},
                    start:{string:"startdatetime",type:"datetime"},
                    stop:{string:"stopdatetime",type:"datetime"},
                    allday:{string:"allday",type:"boolean"},
                    partner_ids:{string:"attendees",type:"one2many",relation:'partner'},
                    type:{string:"type",type:"integer"},
                },
                records:[
                    {id:5,user_id:4,partner_id:4,name:"event1",start:"2016-12-1315:55:05",stop:"2016-12-1518:55:05",allday:false,partner_ids:[],type:2},
                    {id:6,user_id:4,partner_id:4,name:"event2",start:"2016-12-1808:00:00",stop:"2016-12-1809:00:00",allday:false,partner_ids:[],type:3}
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
                    image_1920:{string:"image",type:"integer"},
                },
                records:[
                    {id:4,display_name:"user4",partner_id:4},
                ]
            },
            partner:{
                fields:{
                    id:{string:"ID",type:"integer"},
                    display_name:{string:"Displayedname",type:"char"},
                    image_1920:{string:"image",type:"integer"},
                },
                records:[
                    {id:4,display_name:"partner4",image_1920:'DDD'}
                ]
            },
            filter_partner:{
                fields:{
                    id:{string:"ID",type:"integer"},
                    user_id:{string:"user",type:"many2one",relation:'user'},
                    partner_id:{string:"partner",type:"many2one",relation:'partner'},
                },
                records:[
                    {id:3,user_id:4,partner_id:4}
                ]
            },
        };
    }
},function(){

    QUnit.test('syncgooglecalendar',asyncfunction(assert){
        assert.expect(9);

        varcalendar=awaitcreateCalendarView({
            View:GoogleCalendarView,
            model:'calendar.event',
            data:this.data,
            arch:
            '<calendarclass="o_calendar_test"'+
                'js_class="attendee_calendar"'+
                'date_start="start"'+
                'date_stop="stop"'+
                'mode="month">'+
                    '<fieldname="name"/>'+
            '</calendar>',
            viewOptions:{
                initialDate:initialDate,
            },
            mockRPC:function(route,args){
                if(route==='/google_calendar/sync_data'){
                    assert.step(route);
                    this.data['calendar.event'].records.push(
                        {id:7,user_id:4,partner_id:4,name:"eventfromgooglecalendar",start:"2016-12-2815:55:05",stop:"2016-12-2918:55:05",allday:false,partner_ids:[],type:2}
                    );
                    returnPromise.resolve({status:'need_refresh'});
                }elseif(route==='/web/dataset/call_kw/calendar.event/search_read'){
                    assert.step(route);
                }elseif(route==='/microsoft_calendar/sync_data'){
                    returnPromise.resolve();
                }
                returnthis._super.apply(this,arguments);
            },
        });

        assert.containsN(calendar,'.fc-event',3,"shoulddisplay3eventsonthemonth");

        awaittestUtils.dom.click(calendar.$('.o_calendar_button_next'));
        awaittestUtils.dom.click(calendar.$('.o_calendar_button_prev'));

        assert.verifySteps([
            '/google_calendar/sync_data',
            '/web/dataset/call_kw/calendar.event/search_read',
            '/google_calendar/sync_data',
            '/web/dataset/call_kw/calendar.event/search_read',
            '/google_calendar/sync_data',
            '/web/dataset/call_kw/calendar.event/search_read',
        ],'shoulddoasearch_readbeforeandafterthecalltosync_data');

        assert.containsN(calendar,'.fc-event',5,"shouldnowdisplay4eventsonthemonth");

        calendar.destroy();
    });
});
});
