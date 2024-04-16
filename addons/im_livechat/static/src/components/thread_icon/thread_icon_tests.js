flectra.define('im_livechat/static/src/components/thread_icon/thread_icon_tests.js',function(require){
'usestrict';

constcomponents={
    ThreadIcon:require('mail/static/src/components/thread_icon/thread_icon.js'),
};
const{
    afterEach,
    afterNextRender,
    beforeEach,
    createRootComponent,
    start,
}=require('mail/static/src/utils/test_utils.js');

QUnit.module('im_livechat',{},function(){
QUnit.module('components',{},function(){
QUnit.module('thread_icon',{},function(){
QUnit.module('thread_icon_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.createThreadIcon=asyncthread=>{
            awaitcreateRootComponent(this,components.ThreadIcon,{
                props:{threadLocalId:thread.localId},
                target:this.widget.el,
            });
        };

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
});

QUnit.test('livechat:publicwebsitevisitoristyping',asyncfunction(assert){
    assert.expect(4);

    this.data['mail.channel'].records.push({
        anonymous_name:"Visitor20",
        channel_type:'livechat',
        id:20,
        livechat_operator_id:this.data.currentPartnerId,
        members:[this.data.currentPartnerId,this.data.publicPartnerId],
    });
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({
        id:20,
        model:'mail.channel',
    });
    awaitthis.createThreadIcon(thread);
    assert.containsOnce(
        document.body,
        '.o_ThreadIcon',
        "shouldhavethreadicon"
    );
    assert.containsOnce(
        document.body,
        '.o_ThreadIcon.fa.fa-comments',
        "shouldhavedefaultlivechaticon"
    );

    //simulatereceivetypingnotificationfromlivechatvisitor"istyping"
    awaitafterNextRender(()=>{
        consttypingData={
            info:'typing_status',
            is_typing:true,
            partner_id:this.env.messaging.publicPartner.id,
            partner_name:this.env.messaging.publicPartner.name,
        };
        constnotification=[[false,'mail.channel',20],typingData];
        this.widget.call('bus_service','trigger','notification',[notification]);
    });
    assert.containsOnce(
        document.body,
        '.o_ThreadIcon_typing',
        "shouldhavethreadiconwithvisitorcurrentlytyping"
    );
    assert.strictEqual(
        document.querySelector('.o_ThreadIcon_typing').title,
        "Visitor20istyping...",
        "titleoficonshouldtellvisitoriscurrentlytyping"
    );
});

});
});
});

});
