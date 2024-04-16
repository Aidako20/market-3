flectra.define('im_livechat/static/src/components/thread_textual_typing_status/thread_textual_typing_status_tests.js',function(require){
'usestrict';

constcomponents={
    ThreadTextualTypingStatus:require('mail/static/src/components/thread_textual_typing_status/thread_textual_typing_status.js'),
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
QUnit.module('thread_textual_typing_status',{},function(){
QUnit.module('thread_textual_typing_status_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.createThreadTextualTypingStatusComponent=asyncthread=>{
            awaitcreateRootComponent(this,components.ThreadTextualTypingStatus,{
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

QUnit.test('receivevisitortypingstatus"istyping"',asyncfunction(assert){
    assert.expect(2);

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
    awaitthis.createThreadTextualTypingStatusComponent(thread);

    assert.strictEqual(
        document.querySelector('.o_ThreadTextualTypingStatus').textContent,
        "",
        "Shoulddisplaynooneiscurrentlytyping"
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
    assert.strictEqual(
        document.querySelector('.o_ThreadTextualTypingStatus').textContent,
        "Visitor20istyping...",
        "Shoulddisplaythatvisitoristyping"
    );
});

});
});
});

});
