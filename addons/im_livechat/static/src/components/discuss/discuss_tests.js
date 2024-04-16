flectra.define('im_livechat/static/src/components/discuss/discuss_tests.js',function(require){
'usestrict';

const{
    afterEach,
    afterNextRender,
    beforeEach,
    nextAnimationFrame,
    start,
}=require('mail/static/src/utils/test_utils.js');

QUnit.module('im_livechat',{},function(){
QUnit.module('components',{},function(){
QUnit.module('discuss',{},function(){
QUnit.module('discuss_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.start=asyncparams=>{
            const{env,widget}=awaitstart(Object.assign({},params,{
                autoOpenDiscuss:true,
                data:this.data,
                hasDiscuss:true,
            }));
            this.env=env;
            this.widget=widget;
        };
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.test('livechatinthesidebar:basicrendering',asyncfunction(assert){
    assert.expect(5);

    this.data['mail.channel'].records.push({
        anonymous_name:"Visitor11",
        channel_type:'livechat',
        id:11,
        livechat_operator_id:this.data.currentPartnerId,
        members:[this.data.currentPartnerId,this.data.publicPartnerId],
    });
    awaitthis.start();
    assert.containsOnce(document.body,'.o_Discuss_sidebar',
        "shouldhaveasidebarsection"
    );
    constgroupLivechat=document.querySelector('.o_DiscussSidebar_groupLivechat');
    assert.ok(groupLivechat,
        "shouldhaveachannelgrouplivechat"
    );
    constgrouptitle=groupLivechat.querySelector('.o_DiscussSidebar_groupTitle');
    assert.strictEqual(
        grouptitle.textContent.trim(),
        "Livechat",
        "shouldhaveachannelgroupnamed'Livechat'"
    );
    constlivechat=groupLivechat.querySelector(`
        .o_DiscussSidebarItem[data-thread-local-id="${
            this.env.models['mail.thread'].findFromIdentifyingData({
                id:11,
                model:'mail.channel',
            }).localId
        }"]
    `);
    assert.ok(
        livechat,
        "shouldhavealivechatinsidebar"
    );
    assert.strictEqual(
        livechat.textContent,
        "Visitor11",
        "shouldhave'Visitor11'aslivechatname"
    );
});

QUnit.test('livechatinthesidebar:existinguserwithcountry',asyncfunction(assert){
    assert.expect(3);

    this.data['res.country'].records.push({
        code:'be',
        id:10,
        name:"Belgium",
    });
    this.data['res.partner'].records.push({
        country_id:10,
        id:10,
        name:"Jean",
    });
    this.data['mail.channel'].records.push({
        channel_type:'livechat',
        id:11,
        livechat_operator_id:this.data.currentPartnerId,
        members:[this.data.currentPartnerId,10],
    });
    awaitthis.start();
    assert.containsOnce(
        document.body,
        '.o_DiscussSidebar_groupLivechat',
        "shouldhaveachannelgrouplivechatinthesidebar"
    );
    constlivechat=document.querySelector('.o_DiscussSidebar_groupLivechat.o_DiscussSidebarItem');
    assert.ok(
        livechat,
        "shouldhavealivechatinsidebar"
    );
    assert.strictEqual(
        livechat.textContent,
        "Jean(Belgium)",
        "shouldhaveusernameandcountryaslivechatname"
    );
});

QUnit.test('donotaddlivechatinthesidebaronvisitoropeninghischat',asyncfunction(assert){
    assert.expect(2);

    constcurrentUser=this.data['res.users'].records.find(user=>
        user.id===this.data.currentUserId
    );
    currentUser.im_status='online';
    this.data['im_livechat.channel'].records.push({
        id:10,
        user_ids:[this.data.currentUserId],
    });
    awaitthis.start();
    assert.containsNone(
        document.body,
        '.o_DiscussSidebar_groupLivechat',
        "shouldnothaveanylivechatinthesidebarinitially"
    );

    //simulatelivechatvisitoropeninghischat
    awaitthis.env.services.rpc({
        route:'/im_livechat/get_session',
        params:{
            context:{
                mockedUserId:false,
            },
            channel_id:10,
        },
    });
    awaitnextAnimationFrame();
    assert.containsNone(
        document.body,
        '.o_DiscussSidebar_groupLivechat',
        "shouldstillnothaveanylivechatinthesidebaraftervisitoropenedhischat"
    );
});

QUnit.test('donotaddlivechatinthesidebaronvisitortyping',asyncfunction(assert){
    assert.expect(2);

    constcurrentUser=this.data['res.users'].records.find(user=>
        user.id===this.data.currentUserId
    );
    currentUser.im_status='online';
    this.data['im_livechat.channel'].records.push({
        id:10,
        user_ids:[this.data.currentUserId],
    });
    this.data['mail.channel'].records.push({
        channel_type:'livechat',
        id:10,
        is_pinned:false,
        livechat_channel_id:10,
        livechat_operator_id:this.data.currentPartnerId,
        members:[this.data.publicPartnerId,this.data.currentPartnerId],
    });
    awaitthis.start();
    assert.containsNone(
        document.body,
        '.o_DiscussSidebar_groupLivechat',
        "shouldnothaveanylivechatinthesidebarinitially"
    );

    //simulatelivechatvisitortyping
    constchannel=this.data['mail.channel'].records.find(channel=>channel.id===10);
    awaitthis.env.services.rpc({
        route:'/im_livechat/notify_typing',
        params:{
            context:{
                mockedPartnerId:this.publicPartnerId,
            },
            is_typing:true,
            uuid:channel.uuid,
        },
    });
    awaitnextAnimationFrame();
    assert.containsNone(
        document.body,
        '.o_DiscussSidebar_groupLivechat',
        "shouldstillnothaveanylivechatinthesidebaraftervisitorstartedtyping"
    );
});

QUnit.test('addlivechatinthesidebaronvisitorsendingfirstmessage',asyncfunction(assert){
    assert.expect(4);

    constcurrentUser=this.data['res.users'].records.find(user=>
        user.id===this.data.currentUserId
    );
    currentUser.im_status='online';
    this.data['res.country'].records.push({
        code:'be',
        id:10,
        name:"Belgium",
    });
    this.data['im_livechat.channel'].records.push({
        id:10,
        user_ids:[this.data.currentUserId],
    });
    this.data['mail.channel'].records.push({
        anonymous_name:"Visitor(Belgium)",
        channel_type:'livechat',
        country_id:10,
        id:10,
        is_pinned:false,
        livechat_channel_id:10,
        livechat_operator_id:this.data.currentPartnerId,
        members:[this.data.publicPartnerId,this.data.currentPartnerId],
    });
    awaitthis.start();
    assert.containsNone(
        document.body,
        '.o_DiscussSidebar_groupLivechat',
        "shouldnothaveanylivechatinthesidebarinitially"
    );

    //simulatelivechatvisitorsendingamessage
    constchannel=this.data['mail.channel'].records.find(channel=>channel.id===10);
    awaitafterNextRender(async()=>this.env.services.rpc({
        route:'/mail/chat_post',
        params:{
            context:{
                mockedUserId:false,
            },
            uuid:channel.uuid,
            message_content:"newmessage",
        },
    }));
    assert.containsOnce(
        document.body,
        '.o_DiscussSidebar_groupLivechat',
        "shouldhaveachannelgrouplivechatinthesidebarafterreceivingfirstmessage"
    );
    assert.containsOnce(
        document.body,
        '.o_DiscussSidebar_groupLivechat.o_DiscussSidebar_item',
        "shouldhavealivechatinthesidebarafterreceivingfirstmessage"
    );
    assert.strictEqual(
        document.querySelector('.o_DiscussSidebar_groupLivechat.o_DiscussSidebar_item').textContent,
        "Visitor(Belgium)",
        "shouldhavevisitornameandcountryaslivechatname"
    );
});

QUnit.test('livechatsaresortedbylastmessagedateinthesidebar:mostrecentatthetop',asyncfunction(assert){
    /**
     *Forsimplicitythecodethatiscoveredinthistestisconsidering
     *messagestobemore/lessrecentthanothersbasedontheiridsinsteadof
     *theiractualcreationdate.
     */
    assert.expect(7);

    this.data['mail.message'].records.push(
        {id:11,channel_ids:[11]},//leastrecentmessageduetosmallerid
        {id:12,channel_ids:[12]},//mostrecentmessageduetohigherid
    );
    this.data['mail.channel'].records.push(
        {
            anonymous_name:"Visitor11",
            channel_type:'livechat',
            id:11,
            livechat_operator_id:this.data.currentPartnerId,
            members:[this.data.currentPartnerId,this.data.publicPartnerId],
        },
        {
            anonymous_name:"Visitor12",
            channel_type:'livechat',
            id:12,
            livechat_operator_id:this.data.currentPartnerId,
            members:[this.data.currentPartnerId,this.data.publicPartnerId],
        },
    );
    awaitthis.start();
    constlivechat11=this.env.models['mail.thread'].findFromIdentifyingData({
        id:11,
        model:'mail.channel',
    });
    constlivechat12=this.env.models['mail.thread'].findFromIdentifyingData({
        id:12,
        model:'mail.channel',
    });
    assert.containsOnce(
        document.body,
        '.o_DiscussSidebar_groupLivechat',
        "shouldhaveachannelgrouplivechat"
    );
    constinitialLivechats=document.querySelectorAll('.o_DiscussSidebar_groupLivechat.o_DiscussSidebarItem');
    assert.strictEqual(
        initialLivechats.length,
        2,
        "shouldhave2livechatsinthesidebar"
    );
    assert.strictEqual(
        initialLivechats[0].dataset.threadLocalId,
        livechat12.localId,
        "firstlivechatshouldbetheonewiththemostrecentmessage"
    );
    assert.strictEqual(
        initialLivechats[1].dataset.threadLocalId,
        livechat11.localId,
        "secondlivechatshouldbetheonewiththeleastrecentmessage"
    );

    //postanewmessageonthelastchannel
    awaitafterNextRender(()=>initialLivechats[1].click());
    awaitafterNextRender(()=>document.execCommand('insertText',false,"Blabla"));
    awaitafterNextRender(()=>document.querySelector('.o_Composer_buttonSend').click());
    constlivechats=document.querySelectorAll('.o_DiscussSidebar_groupLivechat.o_DiscussSidebarItem');
    assert.strictEqual(
        livechats.length,
        2,
        "shouldstillhave2livechatsinthesidebarafterpostinganewmessage"
    );
    assert.strictEqual(
        livechats[0].dataset.threadLocalId,
        livechat11.localId,
        "firstlivechatshouldnowbetheoneonwhichthenewmessagewasposted"
    );
    assert.strictEqual(
        livechats[1].dataset.threadLocalId,
        livechat12.localId,
        "secondlivechatshouldnowbetheoneonwhichthemessagewasnotposted"
    );
});

QUnit.test('livechatswithnomessagesaresortedbycreationdateinthesidebar:mostrecentatthetop',asyncfunction(assert){
    /**
     *Forsimplicitythecodethatiscoveredinthistestisconsidering
     *channelstobemore/lessrecentthanothersbasedontheiridsinsteadof
     *theiractualcreationdate.
     */
    assert.expect(5);

    this.data['mail.message'].records.push(
        {id:13,channel_ids:[13]},
    );
    this.data['mail.channel'].records.push(
        {
            anonymous_name:"Visitor11",
            channel_type:'livechat',
            id:11,//leastrecentchannelduetosmallestid
            livechat_operator_id:this.data.currentPartnerId,
            members:[this.data.currentPartnerId,this.data.publicPartnerId],
        },
        {
            anonymous_name:"Visitor12",
            channel_type:'livechat',
            id:12,//mostrecentchannelthatdoesnothaveamessage
            livechat_operator_id:this.data.currentPartnerId,
            members:[this.data.currentPartnerId,this.data.publicPartnerId],
        },
        {
            anonymous_name:"Visitor13",
            channel_type:'livechat',
            id:13,//mostrecentchannel(butithasamessage)
            livechat_operator_id:this.data.currentPartnerId,
            members:[this.data.currentPartnerId,this.data.publicPartnerId],
        },
    );
    awaitthis.start();
    constlivechat11=this.env.models['mail.thread'].findFromIdentifyingData({
        id:11,
        model:'mail.channel',
    });
    constlivechat12=this.env.models['mail.thread'].findFromIdentifyingData({
        id:12,
        model:'mail.channel',
    });
    constlivechat13=this.env.models['mail.thread'].findFromIdentifyingData({
        id:13,
        model:'mail.channel',
    });
    assert.containsOnce(
        document.body,
        '.o_DiscussSidebar_groupLivechat',
        "shouldhaveachannelgrouplivechat"
    );
    constinitialLivechats=document.querySelectorAll('.o_DiscussSidebar_groupLivechat.o_DiscussSidebarItem');
    assert.strictEqual(
        initialLivechats.length,
        3,
        "shouldhave3livechatsinthesidebar"
    );
    assert.strictEqual(
        initialLivechats[0].dataset.threadLocalId,
        livechat12.localId,
        "firstlivechatshouldbethemostrecentchannelwithoutmessage"
    );
    assert.strictEqual(
        initialLivechats[1].dataset.threadLocalId,
        livechat11.localId,
        "secondlivechatshouldbethesecondmostrecentchannelwithoutmessage"
    );
    assert.strictEqual(
        initialLivechats[2].dataset.threadLocalId,
        livechat13.localId,
        "thirdlivechatshouldbethechannelwithamessage"
    );
});

QUnit.test('invitebuttonshouldbepresentonlivechat',asyncfunction(assert){
    assert.expect(1);

    this.data['mail.channel'].records.push(
        {
            anonymous_name:"Visitor11",
            channel_type:'livechat',
            id:11,
            livechat_operator_id:this.data.currentPartnerId,
            members:[this.data.currentPartnerId,this.data.publicPartnerId],
        },
    );
    awaitthis.start({
        discuss:{
            params:{
                default_active_id:'mail.channel_11',
            },
        },
    });
    assert.containsOnce(
        document.body,
        '.o_widget_Discuss_controlPanelButtonInvite',
        "Invitebuttonshouldbevisibleincontrolpanelwhenlivechatisactivethread"
    );
});

});
});
});

});
