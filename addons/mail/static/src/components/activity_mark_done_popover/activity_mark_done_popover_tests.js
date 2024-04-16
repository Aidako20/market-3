flectra.define('mail/static/src/components/activity_mark_done_popover/activity_mark_done_popover_tests.js',function(require){
'usestrict';

constcomponents={
    ActivityMarkDonePopover:require('mail/static/src/components/activity_mark_done_popover/activity_mark_done_popover.js'),
};

const{
    afterEach,
    afterNextRender,
    beforeEach,
    createRootComponent,
    start,
}=require('mail/static/src/utils/test_utils.js');

constBus=require('web.Bus');

QUnit.module('mail',{},function(){
QUnit.module('components',{},function(){
QUnit.module('activity_mark_done_popover',{},function(){
QUnit.module('activity_mark_done_popover_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.createActivityMarkDonePopoverComponent=asyncactivity=>{
            awaitcreateRootComponent(this,components.ActivityMarkDonePopover,{
                props:{activityLocalId:activity.localId},
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

QUnit.test('activitymarkdonepopoversimplestlayout',asyncfunction(assert){
    assert.expect(6);

    awaitthis.start();
    constactivity=this.env.models['mail.activity'].create({
        canWrite:true,
        category:'not_upload_file',
        id:12,
        thread:[['insert',{id:42,model:'res.partner'}]],
    });
    awaitthis.createActivityMarkDonePopoverComponent(activity);

    assert.containsOnce(
        document.body,
        '.o_ActivityMarkDonePopover',
        "Popovercomponentshouldbepresent"
    );
    assert.containsOnce(
        document.body,
        '.o_ActivityMarkDonePopover_feedback',
        "Popovercomponentshouldcontainthefeedbacktextarea"
    );
    assert.containsOnce(
        document.body,
        '.o_ActivityMarkDonePopover_buttons',
        "Popovercomponentshouldcontaintheactionbuttons"
    );
    assert.containsOnce(
        document.body,
        '.o_ActivityMarkDonePopover_doneScheduleNextButton',
        "Popovercomponentshouldcontainthedone&schedulenextbutton"
    );
    assert.containsOnce(
        document.body,
        '.o_ActivityMarkDonePopover_doneButton',
        "Popovercomponentshouldcontainthedonebutton"
    );
    assert.containsOnce(
        document.body,
        '.o_ActivityMarkDonePopover_discardButton',
        "Popovercomponentshouldcontainthediscardbutton"
    );
});

QUnit.test('activitywithforcenextmarkdonepopoversimplestlayout',asyncfunction(assert){
    assert.expect(6);

    awaitthis.start();
    constactivity=this.env.models['mail.activity'].create({
        canWrite:true,
        category:'not_upload_file',
        force_next:true,
        id:12,
        thread:[['insert',{id:42,model:'res.partner'}]],
    });
    awaitthis.createActivityMarkDonePopoverComponent(activity);

    assert.containsOnce(
        document.body,
        '.o_ActivityMarkDonePopover',
        "Popovercomponentshouldbepresent"
    );
    assert.containsOnce(
        document.body,
        '.o_ActivityMarkDonePopover_feedback',
        "Popovercomponentshouldcontainthefeedbacktextarea"
    );
    assert.containsOnce(
        document.body,
        '.o_ActivityMarkDonePopover_buttons',
        "Popovercomponentshouldcontaintheactionbuttons"
    );
    assert.containsOnce(
        document.body,
        '.o_ActivityMarkDonePopover_doneScheduleNextButton',
        "Popovercomponentshouldcontainthedone&schedulenextbutton"
    );
    assert.containsNone(
        document.body,
        '.o_ActivityMarkDonePopover_doneButton',
        "PopovercomponentshouldNOTcontainthedonebutton"
    );
    assert.containsOnce(
        document.body,
        '.o_ActivityMarkDonePopover_discardButton',
        "Popovercomponentshouldcontainthediscardbutton"
    );
});

QUnit.test('activitymarkdonepopovermarkdonewithoutfeedback',asyncfunction(assert){
    assert.expect(7);

    awaitthis.start({
        asyncmockRPC(route,args){
            if(route==='/web/dataset/call_kw/mail.activity/action_feedback'){
                assert.step('action_feedback');
                assert.strictEqual(args.args.length,1);
                assert.strictEqual(args.args[0].length,1);
                assert.strictEqual(args.args[0][0],12);
                assert.strictEqual(args.kwargs.attachment_ids.length,0);
                assert.notOk(args.kwargs.feedback);
                return;
            }
            if(route==='/web/dataset/call_kw/mail.activity/unlink'){
                //'unlink'onnon-existingrecordraisesaservercrash
                thrownewError("'unlink'RPConactivitymustnotbecalled(alreadyunlinkedfrommarkasdone)");
            }
            returnthis._super(...arguments);
        },
    });
    constactivity=this.env.models['mail.activity'].create({
        canWrite:true,
        category:'not_upload_file',
        id:12,
        thread:[['insert',{id:42,model:'res.partner'}]],
    });
    awaitthis.createActivityMarkDonePopoverComponent(activity);

    document.querySelector('.o_ActivityMarkDonePopover_doneButton').click();
    assert.verifySteps(
        ['action_feedback'],
        "Markdoneandschedulenextbuttonshouldcalltherightrpc"
    );
});

QUnit.test('activitymarkdonepopovermarkdonewithfeedback',asyncfunction(assert){
    assert.expect(7);

    awaitthis.start({
        asyncmockRPC(route,args){
            if(route==='/web/dataset/call_kw/mail.activity/action_feedback'){
                assert.step('action_feedback');
                assert.strictEqual(args.args.length,1);
                assert.strictEqual(args.args[0].length,1);
                assert.strictEqual(args.args[0][0],12);
                assert.strictEqual(args.kwargs.attachment_ids.length,0);
                assert.strictEqual(args.kwargs.feedback,'Thistaskisdone');
                return;
            }
            if(route==='/web/dataset/call_kw/mail.activity/unlink'){
                //'unlink'onnon-existingrecordraisesaservercrash
                thrownewError("'unlink'RPConactivitymustnotbecalled(alreadyunlinkedfrommarkasdone)");
            }
            returnthis._super(...arguments);
        },
    });
    constactivity=this.env.models['mail.activity'].create({
        canWrite:true,
        category:'not_upload_file',
        id:12,
        thread:[['insert',{id:42,model:'res.partner'}]],
    });
    awaitthis.createActivityMarkDonePopoverComponent(activity);

    letfeedbackTextarea=document.querySelector('.o_ActivityMarkDonePopover_feedback');
    feedbackTextarea.focus();
    document.execCommand('insertText',false,'Thistaskisdone');
    document.querySelector('.o_ActivityMarkDonePopover_doneButton').click();
    assert.verifySteps(
        ['action_feedback'],
        "Markdoneandschedulenextbuttonshouldcalltherightrpc"
    );
});

QUnit.test('activitymarkdonepopovermarkdoneandschedulenext',asyncfunction(assert){
    assert.expect(6);

    constbus=newBus();
    bus.on('do-action',null,payload=>{
        assert.step('activity_action');
        thrownewError("Thedo-actioneventshouldnotbetriggeredwhentheroutedoesn'treturnanaction");
    });
    awaitthis.start({
        asyncmockRPC(route,args){
            if(route==='/web/dataset/call_kw/mail.activity/action_feedback_schedule_next'){
                assert.step('action_feedback_schedule_next');
                assert.strictEqual(args.args.length,1);
                assert.strictEqual(args.args[0].length,1);
                assert.strictEqual(args.args[0][0],12);
                assert.strictEqual(args.kwargs.feedback,'Thistaskisdone');
                returnfalse;
            }
            if(route==='/web/dataset/call_kw/mail.activity/unlink'){
                //'unlink'onnon-existingrecordraisesaservercrash
                thrownewError("'unlink'RPConactivitymustnotbecalled(alreadyunlinkedfrommarkasdone)");
            }
            returnthis._super(...arguments);
        },
        env:{bus},
    });
    constactivity=this.env.models['mail.activity'].create({
        canWrite:true,
        category:'not_upload_file',
        id:12,
        thread:[['insert',{id:42,model:'res.partner'}]],
    });
    awaitthis.createActivityMarkDonePopoverComponent(activity);

    letfeedbackTextarea=document.querySelector('.o_ActivityMarkDonePopover_feedback');
    feedbackTextarea.focus();
    document.execCommand('insertText',false,'Thistaskisdone');
    awaitafterNextRender(()=>{
        document.querySelector('.o_ActivityMarkDonePopover_doneScheduleNextButton').click();
    });
    assert.verifySteps(
        ['action_feedback_schedule_next'],
        "Markdoneandschedulenextbuttonshouldcalltherightrpcandnottriggeranaction"
    );
});

QUnit.test('[technical]activitymarkdone&schedulenextwithnewaction',asyncfunction(assert){
    assert.expect(3);

    constbus=newBus();
    bus.on('do-action',null,payload=>{
        assert.step('activity_action');
        assert.deepEqual(
            payload.action,
            {type:'ir.actions.act_window'},
            "Thecontentoftheactionshouldbecorrect"
        );
    });
    awaitthis.start({
        asyncmockRPC(route,args){
            if(route==='/web/dataset/call_kw/mail.activity/action_feedback_schedule_next'){
                return{type:'ir.actions.act_window'};
            }
            returnthis._super(...arguments);
        },
        env:{bus},
    });
    constactivity=this.env.models['mail.activity'].create({
        canWrite:true,
        category:'not_upload_file',
        id:12,
        thread:[['insert',{id:42,model:'res.partner'}]],
    });
    awaitthis.createActivityMarkDonePopoverComponent(activity);

    awaitafterNextRender(()=>{
        document.querySelector('.o_ActivityMarkDonePopover_doneScheduleNextButton').click();
    });
    assert.verifySteps(
        ['activity_action'],
        "Theactionreturnedbytherouteshouldbeexecuted"
    );
});

});
});
});

});
