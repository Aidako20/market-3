flectra.define('mail/static/src/widgets/notification_alert/notification_alert_tests.js',function(require){
'usestrict';

const{afterEach,beforeEach,start}=require('mail/static/src/utils/test_utils.js');

constFormView=require('web.FormView');

QUnit.module('mail',{},function(){
QUnit.module('widgets',{},function(){
QUnit.module('notification_alert',{},function(){
QUnit.module('notification_alert_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.start=asyncparams=>{
            let{widget}=awaitstart(Object.assign({
                data:this.data,
                hasView:true,
                //Viewparams
                View:FormView,
                model:'mail.message',
                arch:`
                    <form>
                        <widgetname="notification_alert"/>
                    </form>
                `,
            },params));
            this.widget=widget;
        };
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.skip('notification_alertwidget:displayblockednotificationalert',asyncfunction(assert){
    //FIXME:Testshouldwork,butforsomereasonsOWLalwaysflagsthe
    //componentasnotmounted,eventhoughitisintheDOMandit'sstate
    //isgoodforrendering...task-227947
    assert.expect(1);

    awaitthis.start({
        env:{
            browser:{
                Notification:{
                    permission:'denied',
                },
            },
        },
    });

    assert.containsOnce(
        document.body,
        '.o_notification_alert',
        "Blockednotificationalertshouldbedisplayed"
    );
});

QUnit.test('notification_alertwidget:nonotificationalertwhengranted',asyncfunction(assert){
    assert.expect(1);

    awaitthis.start({
        env:{
            browser:{
                Notification:{
                    permission:'granted',
                },
            },
        },
    });

    assert.containsNone(
        document.body,
        '.o_notification_alert',
        "Blockednotificationalertshouldnotbedisplayed"
    );
});

QUnit.test('notification_alertwidget:nonotificationalertwhendefault',asyncfunction(assert){
    assert.expect(1);

    awaitthis.start({
        env:{
            browser:{
                Notification:{
                    permission:'default',
                },
            },
        },
    });

    assert.containsNone(
        document.body,
        '.o_notification_alert',
        "Blockednotificationalertshouldnotbedisplayed"
    );
});

});
});
});

});
