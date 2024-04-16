flectra.define('mail/static/src/components/discuss_mobile_mailbox_selection/discuss_mobile_mailbox_selection_tests.js',function(require){
'usestrict';

const{
    afterEach,
    afterNextRender,
    beforeEach,
    start,
}=require('mail/static/src/utils/test_utils.js');

QUnit.module('mail',{},function(){
QUnit.module('components',{},function(){
QUnit.module('discuss_mobile_mailbox_selection',{},function(){
QUnit.module('discuss_mobile_mailbox_selection_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.start=asyncparams=>{
            const{env,widget}=awaitstart(Object.assign(
                {
                    autoOpenDiscuss:true,
                    data:this.data,
                    env:{
                        browser:{
                            innerHeight:640,
                            innerWidth:360,
                        },
                        device:{
                            isMobile:true,
                        },
                    },
                    hasDiscuss:true,
                },
                params,
            ));
            this.env=env;
            this.widget=widget;
        };
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.test('selectanothermailbox',asyncfunction(assert){
    assert.expect(7);

    awaitthis.start();
    assert.containsOnce(
        document.body,
        '.o_Discuss',
        "shoulddisplaydiscussinitially"
    );
    assert.hasClass(
        document.querySelector('.o_Discuss'),
        'o-mobile',
        "discussshouldbeopenedinmobilemode"
    );
    assert.containsOnce(
        document.body,
        '.o_Discuss_thread',
        "discussshoulddisplayathreadinitially"
    );
    assert.strictEqual(
        document.querySelector('.o_Discuss_thread').dataset.threadLocalId,
        this.env.messaging.inbox.localId,
        "inboxmailboxshouldbeopenedinitially"
    );
    assert.containsOnce(
        document.body,
        `.o_DiscussMobileMailboxSelection_button[
            data-mailbox-local-id="${this.env.messaging.starred.localId}"
        ]`,
        "shouldhaveabuttontoopenstarredmailbox"
    );

    awaitafterNextRender(()=>
        document.querySelector(`.o_DiscussMobileMailboxSelection_button[
            data-mailbox-local-id="${this.env.messaging.starred.localId}"]
        `).click()
    );
    assert.containsOnce(
        document.body,
        '.o_Discuss_thread',
        "discussshouldstillhaveathreadafterclickingonstarredmailbox"
    );
    assert.strictEqual(
        document.querySelector('.o_Discuss_thread').dataset.threadLocalId,
        this.env.messaging.starred.localId,
        "starredmailboxshouldbeopenedafterclickingonit"
    );
});

QUnit.test('auto-select"Inbox"whendiscusshadchannelasactivethread',asyncfunction(assert){
    assert.expect(3);

    this.data['mail.channel'].records.push({id:20});
    awaitthis.start({
        discuss:{
            context:{
                active_id:20,
            },
        }
    });
    assert.hasClass(
        document.querySelector('.o_MobileMessagingNavbar_tab[data-tab-id="channel"]'),
        'o-active',
        "'channel'tabshouldbeactiveinitiallywhenloadingdiscusswithchannelidasactive_id"
    );

    awaitafterNextRender(()=>document.querySelector('.o_MobileMessagingNavbar_tab[data-tab-id="mailbox"]').click());
    assert.hasClass(
        document.querySelector('.o_MobileMessagingNavbar_tab[data-tab-id="mailbox"]'),
        'o-active',
        "'mailbox'tabshouldbeselectedafterclickonmailboxtab"
    );
    assert.hasClass(
        document.querySelector(`.o_DiscussMobileMailboxSelection_button[data-mailbox-local-id="${
            this.env.messaging.inbox.localId
        }"]`),
        'o-active',
        "'Inbox'mailboxshouldbeauto-selectedafterclickonmailboxtab"
    );
});

});
});
});

});
