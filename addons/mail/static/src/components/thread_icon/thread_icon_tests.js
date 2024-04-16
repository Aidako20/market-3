flectra.define('mail/static/src/components/thread_icon/thread_icon_tests.js',function(require){
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

QUnit.module('mail',{},function(){
QUnit.module('components',{},function(){
QUnit.module('thread_icon',{},function(){
QUnit.module('thread_icon_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.createThreadIcon=asyncthread=>{
            awaitcreateRootComponent(this,components.ThreadIcon,{
                props:{threadLocalId:thread.localId},
                target:this.widget.el
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

QUnit.test('chat:correspondentistyping',asyncfunction(assert){
    assert.expect(5);

    this.data['res.partner'].records.push({
        id:17,
        im_status:'online',
        name:'Demo',
    });
    this.data['mail.channel'].records.push({
        channel_type:'chat',
        id:20,
        members:[this.data.currentPartnerId,17],
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
        '.o_ThreadIcon_online',
        "shouldhavethreadiconwithpartnerimstatusicon'online'"
    );

    //simulatereceivetypingnotificationfromdemo"istyping"
    awaitafterNextRender(()=>{
        consttypingData={
            info:'typing_status',
            is_typing:true,
            partner_id:17,
            partner_name:"Demo",
        };
        constnotification=[[false,'mail.channel',20],typingData];
        this.widget.call('bus_service','trigger','notification',[notification]);
    });
    assert.containsOnce(
        document.body,
        '.o_ThreadIcon_typing',
        "shouldhavethreadiconwithpartnercurrentlytyping"
    );
    assert.strictEqual(
        document.querySelector('.o_ThreadIcon_typing').title,
        "Demoistyping...",
        "titleoficonshouldtelldemoiscurrentlytyping"
    );

    //simulatereceivetypingnotificationfromdemo"nolongeristyping"
    awaitafterNextRender(()=>{
        consttypingData={
            info:'typing_status',
            is_typing:false,
            partner_id:17,
            partner_name:"Demo",
        };
        constnotification=[[false,'mail.channel',20],typingData];
        this.widget.call('bus_service','trigger','notification',[notification]);
    });
    assert.containsOnce(
        document.body,
        '.o_ThreadIcon_online',
        "shouldhavethreadiconwithpartnerimstatusicon'online'(nolongertyping)"
    );
});

});
});
});

});
