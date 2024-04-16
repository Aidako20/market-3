flectra.define('mail/static/src/models/messaging/messaging_tests.js',function(require){
'usestrict';

const{afterEach,beforeEach,start}=require('mail/static/src/utils/test_utils.js');

QUnit.module('mail',{},function(){
QUnit.module('models',{},function(){
QUnit.module('messaging',{},function(){
QUnit.module('messaging_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.start=asyncparams=>{
            const{env,widget}=awaitstart(Object.assign({},params,{
                data:this.data,
            }));
            this.env=env;
            this.widget=widget;
        };
    },
    afterEach(){
        afterEach(this);
    },
},function(){

QUnit.test('openChat:displaynotificationforpartnerwithoutuser',asyncfunction(assert){
    assert.expect(2);

    this.data['res.partner'].records.push({id:14});
    awaitthis.start();

    awaitthis.env.messaging.openChat({partnerId:14});
    assert.containsOnce(
        document.body,
        '.toast.o_notification_content',
        "shoulddisplayatoastnotificationafterfailingtoopenchat"
    );
    assert.strictEqual(
        document.querySelector('.o_notification_content').textContent,
        "Youcanonlychatwithpartnersthathaveadedicateduser.",
        "shoulddisplaythecorrectinformationinthenotification"
    );
});

QUnit.test('openChat:displaynotificationforwronguser',asyncfunction(assert){
    assert.expect(2);

    awaitthis.start();

    //useridnotinthis.data
    awaitthis.env.messaging.openChat({userId:14});
    assert.containsOnce(
        document.body,
        '.toast.o_notification_content',
        "shoulddisplayatoastnotificationafterfailingtoopenchat"
    );
    assert.strictEqual(
        document.querySelector('.o_notification_content').textContent,
        "Youcanonlychatwithexistingusers.",
        "shoulddisplaythecorrectinformationinthenotification"
    );
});

QUnit.test('openChat:opennewchatforuser',asyncfunction(assert){
    assert.expect(3);

    this.data['res.partner'].records.push({id:14});
    this.data['res.users'].records.push({id:11,partner_id:14});
    awaitthis.start();

    constexistingChat=this.env.models['mail.thread'].find(thread=>
        thread.channel_type==='chat'&&
        thread.correspondent&&
        thread.correspondent.id===14&&
        thread.model==='mail.channel'&&
        thread.public==='private'
    );
    assert.notOk(existingChat,'achatshouldnotexistwiththetargetpartnerinitially');

    awaitthis.env.messaging.openChat({partnerId:14});
    constchat=this.env.models['mail.thread'].find(thread=>
        thread.channel_type==='chat'&&
        thread.correspondent&&
        thread.correspondent.id===14&&
        thread.model==='mail.channel'&&
        thread.public==='private'
    );
    assert.ok(chat,'achatshouldexistwiththetargetpartner');
    assert.strictEqual(chat.threadViews.length,1,'thechatshouldbedisplayedina`mail.thread_view`');
});

QUnit.test('openChat:openexistingchatforuser',asyncfunction(assert){
    assert.expect(5);

    this.data['res.partner'].records.push({id:14});
    this.data['res.users'].records.push({id:11,partner_id:14});
    this.data['mail.channel'].records.push({
        channel_type:"chat",
        id:10,
        members:[this.data.currentPartnerId,14],
        public:'private',
    });
    awaitthis.start();
    constexistingChat=this.env.models['mail.thread'].find(thread=>
        thread.channel_type==='chat'&&
        thread.correspondent&&
        thread.correspondent.id===14&&
        thread.model==='mail.channel'&&
        thread.public==='private'
    );
    assert.ok(existingChat,'achatshouldinitiallyexistwiththetargetpartner');
    assert.strictEqual(existingChat.threadViews.length,0,'thechatshouldnotbedisplayedina`mail.thread_view`');

    awaitthis.env.messaging.openChat({partnerId:14});
    assert.ok(existingChat,'achatshouldstillexistwiththetargetpartner');
    assert.strictEqual(existingChat.id,10,'thechatshouldbetheexistingchat');
    assert.strictEqual(existingChat.threadViews.length,1,'thechatshouldnowbedisplayedina`mail.thread_view`');
});

});

});
});
});

});
