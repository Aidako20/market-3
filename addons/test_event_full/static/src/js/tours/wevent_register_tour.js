flectra.define('test_event_full.tour.register',function(require){
"usestrict";

vartour=require('web_tour.tour');

/**
 *TALKSSTEPS
 */

vardiscoverTalkSteps=function(talkName,fromList,reminderOn,toggleReminder){
    varsteps;
    if(fromList){
        steps=[{
            content:'Goon"'+talkName+'"talkinList',
            trigger:'a:contains("'+talkName+'")',
        }];
    }
    else{
        steps=[{
            content:'ClickonLiveTrack',
            trigger:'articlespan:contains("'+talkName+'")',
            run:'click',
        }];
    }
    if(reminderOn){
        steps=steps.concat([{
            content:"CheckFavoriteison",
            trigger:'div.o_wetrack_js_reminderi.fa-bell',
            extra_trigger:'span.o_wetrack_js_reminder_text:contains("FavoriteOn")',
            run:function(){},//it'sacheck
        }]);
    }
    else{
        steps=steps.concat([{
            content:"CheckFavoriteisOff",
            trigger:'span.o_wetrack_js_reminder_text:contains("SetFavorite")',
            run:function(){},//it'sacheck
        }]);
        if(toggleReminder){
            steps=steps.concat([{
                content:"SetFavorite",
                trigger:'span.o_wetrack_js_reminder_text',
                run:'click',
            },{
                content:"CheckFavoriteisOn",
                trigger:'div.o_wetrack_js_reminderi.fa-bell',
                extra_trigger:'span.o_wetrack_js_reminder_text:contains("FavoriteOn")',
                run:function(){},//it'sacheck
            }]);
        }
    }
    returnsteps;
};


/**
 *ROOMSSTEPS
 */

vardiscoverRoomSteps=function(roomName){
    varsteps=[{
        content:'Goon"'+roomName+'"roominList',
        trigger:'a.o_wevent_meeting_room_cardh4:contains("'+roomName+'")',
        run:function(){
            //can'tclickonit,itwilltrytolaunchJitsiandfailonchromeheadless
        },
    }];
    returnsteps;
};


/**
 *REGISTERSTEPS
 */

varregisterSteps=[{
    content:'GoonRegister',
    trigger:'a.btn-primary:contains("Register")',
},{
    content:"Select2unitsof'Standard'tickettype",
    trigger:'#o_wevent_tickets_collapse.row:has(.o_wevent_registration_multi_select:contains("Free"))select',
    run:'text2',
},{
    content:"Clickon'Register'button",
    trigger:'#o_wevent_tickets.btn-primary:contains("Register"):not(:disabled)',
    run:'click',
},{
    content:"Fillattendeesdetails",
    trigger:'form[id="attendee_registration"].btn:contains("Continue")',
    run:function(){
        $("input[name='1-name']").val("RaoulettePoiluchette");
        $("input[name='1-phone']").val("0456112233");
        $("input[name='1-email']").val("raoulette@example.com");
        $("select[name*='question_answer-1']").val($("select[name*='question_answer-1']option:contains('Consumers')").val());
        $("input[name='2-name']").val("MichelTractopelle");
        $("input[name='2-phone']").val("0456332211");
        $("input[name='2-email']").val("michel@example.com");
        $("select[name*='question_answer-2']").val($("select[name*='question_answer-1']option:contains('Research')").val());
        $("textarea[name*='question_answer']").text("Anunicorntoldmeaboutyou.Iateitafterwards.");
    },
},{
    content:"Validateattendeesdetails",
    extra_trigger:"input[name='1-name'],input[name='2-name'],input[name='3-name']",
    trigger:'button:contains("Continue")',
    run:'click',
},{
    trigger:'div.o_wereg_confirmed_attendeesspan:contains("RaoulettePoiluchette")',
    run:function(){}//check
},{
    trigger:'div.o_wereg_confirmed_attendeesspan:contains("MichelTractopelle")',
    run:function(){}//check
}, {
    content:"Clickon'registerfavoritestalks'button",
    trigger:'a:contains("registertoyourfavoritestalksnow")',
    run:'click',
}, {
    trigger:'h1:contains("Bookyourtalks")',
    run:function(){},
}];

/**
 *MAINSTEPS
 */

varinitTourSteps=function(eventName){
    return[{
        content:'Goon"'+eventName+'"page',
        trigger:'a[href*="/event"]:contains("'+eventName+'"):first',
    }];
};

varbrowseTalksSteps=[{
    content:'BrowseTalks',
    trigger:'a:contains("Talks")',
}];

varbrowseExhibitorsSteps=[{
    content:'BrowseExhibitors',
    trigger:'a:contains("Exhibitors")',
}];

varbrowseMeetSteps=[{
    content:'BrowseMeet',
    trigger:'a:contains("Community")',
}];


tour.register('wevent_register',{
    url:'/event',
    test:true
},[].concat(
        initTourSteps('OnlineReveal'),
        browseTalksSteps,
        discoverTalkSteps('WhatThisEventIsAllAbout',true,true),
        browseTalksSteps,
        discoverTalkSteps('LiveTestimonial',false,false,false),
        browseTalksSteps,
        discoverTalkSteps('OurLastDayTogether!',true,false,true),
        browseMeetSteps,
        discoverRoomSteps('Bestwoodforfurniture'),
        registerSteps,
    )
);

});
