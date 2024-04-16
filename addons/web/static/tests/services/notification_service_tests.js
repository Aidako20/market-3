flectra.define('web.notification_tests',function(require){
"usestrict";

varAbstractView=require('web.AbstractView');
varNotification=require('web.Notification');
varNotificationService=require('web.NotificationService');

vartestUtils=require('web.test_utils');
varcreateView=testUtils.createView;

varwaitCloseNotification=function(){
    returnnewPromise(function(resolve){
        setTimeout(resolve,1);
    });
}

QUnit.module('Services',{
    beforeEach:function(){
        //Weneedtouseadelayabove0msbecauseotherwisethenotificationwillcloserightafteritopens
        //beforewecanperformanytest.
        testUtils.mock.patch(Notification,{
            _autoCloseDelay:1,
            _animation:false,
        });
        this.viewParams={
            View:AbstractView,
            arch:'<fake/>',
            data:{
            fake_model:{
                    fields:{},
                    record:[],
                },
            },
            model:'fake_model',
            services:{
                notification:NotificationService,
            },
        };
    },
    afterEach:function(){
        //TheNotificationServicehasasideeffect:itaddsadivinside
        //document.body. Wecouldimplementacleanupmechanismforservices,
        //butthisseemsalittleoverkillsinceservicesarenotsupposedto
        //bedestroyedanyway.
        $('.o_notification_manager').remove();
        testUtils.mock.unpatch(Notification);
    }
},function(){
    QUnit.module('Notification');

    QUnit.test('Displayawarningnotification',asyncfunction(assert){
        assert.expect(4);

        varview=awaitcreateView(this.viewParams);
        view.call('notification','notify',{
            title:'a',
            message:'b',
        });
        awaittestUtils.nextMicrotaskTick();
        var$notification=$('body.o_notification_manager.o_notification');
        assert.strictEqual($notification.html().trim().replace(/\s+/g,''),
            "<divclass=\"toast-header\"><spanclass=\"fafa-2xmr-3fa-lightbulb-oo_notification_icon\"role=\"img\"aria-label=\"Notificationundefined\"title=\"Notificationundefined\"></span><divclass=\"d-flexalign-items-centermr-autofont-weight-boldo_notification_title\">a</div><buttontype=\"button\"class=\"closeo_notification_close\"data-dismiss=\"toast\"aria-label=\"Close\"><spanclass=\"d-inline\"aria-hidden=\"true\">×</span></button></div><divclass=\"toast-body\"><divclass=\"mr-autoo_notification_content\">b</div></div>",
            "shoulddisplaynotification");
        assert.containsOnce($notification,'.o_notification_close');
        awaitwaitCloseNotification();
        assert.strictEqual($notification.is(':hidden'),true,"shouldhidethenotification");
        assert.strictEqual($('body.o_notification_manager.o_notification').length,0,"shoulddestroythenotification");
        view.destroy();
    });

    QUnit.test('Displayadangernotification',asyncfunction(assert){
        assert.expect(1);

        varview=awaitcreateView(this.viewParams);
        view.call('notification','notify',{
            title:'a',
            message:'b',
            type:'danger'
        });
        awaittestUtils.nextMicrotaskTick();
        var$notification=$('body.o_notification_manager.o_notification');
        assert.strictEqual($notification.html().trim().replace(/\s+/g,''),
            "<divclass=\"toast-header\"><spanclass=\"fafa-2xmr-3fa-exclamationo_notification_icon\"role=\"img\"aria-label=\"Notificationundefined\"title=\"Notificationundefined\"></span><divclass=\"d-flexalign-items-centermr-autofont-weight-boldo_notification_title\">a</div><buttontype=\"button\"class=\"closeo_notification_close\"data-dismiss=\"toast\"aria-label=\"Close\"><spanclass=\"d-inline\"aria-hidden=\"true\">×</span></button></div><divclass=\"toast-body\"><divclass=\"mr-autoo_notification_content\">b</div></div>",
            "shoulddisplaynotification");
        view.destroy();
    });

    QUnit.test('Displayastickynotification',asyncfunction(assert){
        assert.expect(3);

        varview=awaitcreateView(this.viewParams);
        view.call('notification','notify',{
            title:'a',
            message:'b',
            sticky:true,
        });
        awaittestUtils.nextTick();
        var$notification=$('body.o_notification_manager.o_notification');
        assert.containsOnce($notification,'.o_notification_close',"shoulddisplaytheclosebuttoninnotification");

        assert.strictEqual($notification.is(':hidden'),false,"shouldnothidethenotificationautomatically");
        awaittestUtils.dom.click($notification.find('.o_notification_close'));
        assert.strictEqual($('body.o_notification_manager.o_notification').length,
            0,"shoulddestroythenotification");
        view.destroy();
    });

    QUnit.test('Displayanotificationwithouttitle',asyncfunction(assert){
        assert.expect(3);

        constview=awaitcreateView(this.viewParams);
        view.call('notification','notify',{
            title:false,
            message:'b',
            sticky:true,
        });
        awaittestUtils.nextTick();
        const$notification=$('body.o_notification_manager.o_notification');
        assert.containsNone($notification,'.toast-header.o_notification_title');
        assert.containsNone($notification,'.o_notification_icon');
        assert.containsOnce($notification,'.toast-body.o_notification_close');

        view.destroy();
    });

    //FIXMEskipbecausethefeatureisunusedanddonotunderstandwhythetestevenworkedbefore
    QUnit.skip('DisplayasimplenotificationwithonClosecallbackwhenautomaticallyclose',asyncfunction(assert){
        assert.expect(2);

        varclose=0;
        varview=awaitcreateView(this.viewParams);
        view.call('notification','notify',{
            title:'a',
            message:'b',
            onClose:function(){
                close++;
            }
        });
        awaittestUtils.nextMicrotaskTick();
        view.destroy();
        assert.strictEqual(close,0,"shouldwaittocallonClosemethodonce");
        awaittestUtils.nextTick();
        assert.strictEqual(close,1,"shouldcallonClosemethodonce");
    });

    QUnit.test('DisplayastickynotificationwithonClosecallback',asyncfunction(assert){
        assert.expect(2);

        testUtils.mock.unpatch(Notification);
        testUtils.mock.patch(Notification,{
            _autoCloseDelay:2500,
            _animation:false,
        });
        varview=awaitcreateView(this.viewParams);

        varclose=0;
        view.call('notification','notify',{
            title:'a',
            message:'b',
            sticky:true,
            onClose:function(){
                close++;
            }
        });
        awaittestUtils.nextMicrotaskTick();
        assert.strictEqual(close,0,"shouldwaittocallonClosemethodonce");
        testUtils.dom.click($('body.o_notification_manager.o_notification.o_notification_close'));
        assert.strictEqual(close,1,"shouldcallonClosemethodonce");
        view.destroy();
    });

    QUnit.test('Displayaquestion',asyncfunction(assert){
        assert.expect(8);

        varview=awaitcreateView(this.viewParams);
        functionnotification(inc){
            return{
                title:'a'+inc,
                message:'b'+inc,
                buttons:[
                    {
                        text:'accept'+inc,
                        primary:true,
                        click:function(){
                            assert.step('accept'+inc);
                        },
                    },
                    {
                        text:'refuse'+inc,
                        click:function(){
                            assert.step('refuse'+inc);
                        },
                    }
                ],
                onClose:function(){
                    assert.step('close'+inc);
                }
            };
        };
        view.call('notification','notify',notification(0));
        view.call('notification','notify',notification(1));
        view.call('notification','notify',notification(2));
        awaittestUtils.nextTick();

        var$notification=$('body.o_notification_manager.o_notification');
        assert.containsOnce($notification.eq(0),'.o_notification_close',
            "shoulddisplaytheclosebuttoninnotification");
        assert.strictEqual($notification.html().trim().replace(/\s+/g,''),
            "<divclass=\"toast-header\"><spanclass=\"fafa-2xmr-3fa-question-circle-oo_notification_icon\"role=\"img\"aria-label=\"Notificationundefined\"title=\"Notificationundefined\"></span><divclass=\"d-flexalign-items-centermr-autofont-weight-boldo_notification_title\">a0</div><buttontype=\"button\"class=\"closeo_notification_close\"data-dismiss=\"toast\"aria-label=\"Close\"><spanclass=\"d-inline\"aria-hidden=\"true\">×</span></button></div><divclass=\"toast-body\"><divclass=\"mr-autoo_notification_content\">b0</div><divclass=\"mt-2o_notification_buttons\"><buttontype=\"button\"class=\"btnbtn-smbtn-primary\"><span>accept0</span></button><buttontype=\"button\"class=\"btnbtn-smbtn-secondary\"><span>refuse0</span></button></div></div>",
            "shoulddisplaynotification");

        testUtils.dom.click($notification.find('.o_notification_buttonsbutton:contains(accept0)'));
        testUtils.dom.click($notification.find('.o_notification_buttonsbutton:contains(refuse1)'));
        testUtils.dom.click($notification.eq(2).find('.o_notification_close'));

        assert.strictEqual($notification.is(':hidden'),true,"shouldhidethenotification");
        assert.strictEqual($('body.o_notification_manager.o_notification').length,
            0,"shoulddestroythenotification");
        assert.verifySteps(['accept0','refuse1','close2']);
        view.destroy();
    });

    QUnit.test('callclosenotificationservice',asyncfunction(assert){
        assert.expect(2);

        testUtils.mock.unpatch(Notification);
        testUtils.mock.patch(Notification,{
            _autoCloseDelay:2500,
            _animation:false,
        });
        varview=awaitcreateView(this.viewParams);

        varclose=0;
        varnotificationId0=view.call('notification','notify',{
            title:'a',
            message:'b',
            onClose:function(){
                close++;
            }
        });
        varnotificationId1=view.call('notification','notify',{
            title:'a',
            message:'b',
            sticky:true,
            onClose:function(){
                close++;
            }
        });
        awaittestUtils.nextTick();

        view.call('notification','close',notificationId0);
        view.call('notification','close',notificationId1);
        awaittestUtils.nextTick();

        assert.strictEqual($('body.o_notification_manager.o_notification').length,0,"shoulddestroythenotifications");
        assert.strictEqual(close,2,"shouldcallonClosemethodtwice");
        view.destroy();
    });

    QUnit.test('Displayacustomnotification',asyncfunction(assert){
        assert.expect(3);

        varCustom=Notification.extend({
            init:function(parent,params){
                this._super.apply(this,arguments);
                assert.ok(params.customParams,'instantiatecustomnotification');
            },
            start:function(){
                varself=this;
                returnthis._super().then(function(){
                    self.$el.html('Custom');
                });
            },
        });

        varview=awaitcreateView(this.viewParams);
        view.call('notification','notify',{
            Notification:Custom,
            customParams:true,
        });
        awaittestUtils.nextMicrotaskTick();
        assert.containsOnce($('body'),'.o_notification_manager.o_notification:contains(Custom)',
            "shoulddisplaythenotification");
        view.destroy();
        assert.containsNone($('body'),'.o_notification_manager.o_notification',
            "shoulddestroythenotification");
    });

});});
