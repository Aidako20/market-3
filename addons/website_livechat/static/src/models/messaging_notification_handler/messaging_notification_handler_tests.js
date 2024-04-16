flectra.define('website_livechat/static/src/models/messaging_notification_handler/messaging_notification_handler_tests.js',function(require){
'usestrict';

const{
    afterEach,
    afterNextRender,
    beforeEach,
    start,
}=require('mail/static/src/utils/test_utils.js');

constFormView=require('web.FormView');
const{
    mock:{
        intercept,
    },
}=require('web.test_utils');

QUnit.module('website_livechat',{},function(){
QUnit.module('models',{},function(){
QUnit.module('messaging_notification_handler',{},function(){
QUnit.module('messaging_notification_handler_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.start=asyncparams=>{
            const{env,widget}=awaitstart(Object.assign({},{
                data:this.data,
            },params));
            this.env=env;
            this.widget=widget;
        };
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.test('shouldopenchatwindowonsendchatrequesttowebsitevisitor',asyncfunction(assert){
    assert.expect(3);

    this.data['website.visitor'].records.push({
        id:11,
        name:"Visitor#11",
    });
    awaitthis.start({
        data:this.data,
        hasChatWindow:true,
        hasView:true,
        //Viewparams
        View:FormView,
        model:'website.visitor',
        arch:`
            <form>
                <header>
                    <buttonname="action_send_chat_request"string="Sendchatrequest"class="btnbtn-primary"type="button"/>
                </header>
                <fieldname="name"/>
            </form>
        `,
        res_id:11,
    });
    intercept(this.widget,'execute_action',payload=>{
        this.env.services.rpc({
            route:'/web/dataset/call_button',
            params:{
                args:[payload.data.env.resIDs],
                kwargs:{context:payload.data.env.context},
                method:payload.data.action_data.name,
                model:payload.data.env.model,
            }
        });
    });

    awaitafterNextRender(()=>
        document.querySelector('button[name="action_send_chat_request"]').click()
    );
    assert.containsOnce(
        document.body,
        '.o_ChatWindow',
        "shouldhaveachatwindowopenaftersendingchatrequesttowebsitevisitor"
    );
    assert.hasClass(
        document.querySelector('.o_ChatWindow'),
        'o-focused',
        "chatwindowoflivechatshouldbefocusedonopen"
    );
    assert.strictEqual(
        document.querySelector('.o_ChatWindowHeader_name').textContent,
        "Visitor#11",
        "chatwindowoflivechatshouldhavenameofvisitorinthename"
    );
});

});
});
});

});
