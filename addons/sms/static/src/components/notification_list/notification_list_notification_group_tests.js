flectra.define('sms/static/src/components/notification_list/notification_list_notification_group_tests.js',function(require){
'usestrict';

constcomponents={
    NotificationList:require('mail/static/src/components/notification_list/notification_list.js'),
};

const{
    afterEach,
    beforeEach,
    createRootComponent,
    start,
}=require('mail/static/src/utils/test_utils.js');

constBus=require('web.Bus');

QUnit.module('sms',{},function(){
QUnit.module('components',{},function(){
QUnit.module('notification_list',{},function(){
QUnit.module('notification_list_notification_group_tests.js',{
    beforeEach(){
        beforeEach(this);

        /**
         *@param{Object}param0
         *@param{string}[param0.filter='all']
         */
        this.createNotificationListComponent=async({filter='all'}={})=>{
            awaitcreateRootComponent(this,components.NotificationList,{
                props:{filter},
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

QUnit.test('markasread',asyncfunction(assert){
    assert.expect(6);

    this.data['mail.message'].records.push(
        //messagethatisexpectedtohaveafailure
        {
            id:11,//randomuniqueid,willbeusedtolinkfailuretomessage
            message_type:'sms',//messagemustbesms(goalofthetest)
            model:'mail.channel',//expectedvaluetolinkmessagetochannel
            res_id:31,//idofarandomchannel
        }
    );
    this.data['mail.notification'].records.push(
        //failurethatisexpectedtobeusedinthetest
        {
            mail_message_id:11,//idoftherelatedmessage
            notification_status:'exception',//necessaryvaluetohaveafailure
            notification_type:'sms',//expectedfailuretypeforsmsmessage
        }
    );
    constbus=newBus();
    bus.on('do-action',null,payload=>{
        assert.step('do_action');
        assert.strictEqual(
            payload.action,
            'sms.sms_cancel_action',
            "actionshouldbetheonetocancelsms"
        );
        assert.strictEqual(
            payload.options.additional_context.default_model,
            'mail.channel',
            "actionshouldhavethegroupmodelasdefault_model"
        );
        assert.strictEqual(
            payload.options.additional_context.unread_counter,
            1,
            "actionshouldhavethegroupnotificationlengthasunread_counter"
        );
    });

    awaitthis.start({env:{bus}});
    awaitthis.createNotificationListComponent();

    assert.containsOnce(
        document.body,
        '.o_NotificationGroup_markAsRead',
        "shouldhave1markasreadbutton"
    );

    document.querySelector('.o_NotificationGroup_markAsRead').click();
    assert.verifySteps(
        ['do_action'],
        "shoulddoanactiontodisplaythecancelsmsdialog"
    );
});

QUnit.test('notificationsgroupedbynotification_type',asyncfunction(assert){
    assert.expect(11);

    this.data['mail.message'].records.push(
        //firstmessagethatisexpectedtohaveafailure
        {
            id:11,//randomuniqueid,willbeusedtolinkfailuretomessage
            message_type:'sms',//differenttypefromsecondmessage
            model:'res.partner',//samemodelassecondmessage(andnot`mail.channel`)
            res_id:31,//sameres_idassecondmessage
            res_model_name:"Partner",//randomrelatedmodelname
        },
        //secondmessagethatisexpectedtohaveafailure
        {
            id:12,//randomuniqueid,willbeusedtolinkfailuretomessage
            message_type:'email',//differenttypefromfirstmessage
            model:'res.partner',//samemodelasfirstmessage(andnot`mail.channel`)
            res_id:31,//sameres_idasfirstmessage
            res_model_name:"Partner",//samerelatedmodelnameforconsistency
        }
    );
    this.data['mail.notification'].records.push(
        //firstfailurethatisexpectedtobeusedinthetest
        {
            mail_message_id:11,//idoftherelatedfirstmessage
            notification_status:'exception',//necessaryvaluetohaveafailure
            notification_type:'sms',//differenttypefromsecondfailure
        },
        //secondfailurethatisexpectedtobeusedinthetest
        {
            mail_message_id:12,//idoftherelatedsecondmessage
            notification_status:'exception',//necessaryvaluetohaveafailure
            notification_type:'email',//differenttypefromfirstfailure
        }
    );
    awaitthis.start();
    awaitthis.createNotificationListComponent();

    assert.containsN(
        document.body,
        '.o_NotificationGroup',
        2,
        "shouldhave2notificationsgroup"
    );
    constgroups=document.querySelectorAll('.o_NotificationGroup');
    assert.containsOnce(
        groups[0],
        '.o_NotificationGroup_name',
        "shouldhave1groupnameinfirstgroup"
    );
    assert.strictEqual(
        groups[0].querySelector('.o_NotificationGroup_name').textContent,
        "Partner",
        "shouldhavemodelnameasgroupname"
    );
    assert.containsOnce(
        groups[0],
        '.o_NotificationGroup_counter',
        "shouldhave1groupcounterinfirstgroup"
    );
    assert.strictEqual(
        groups[0].querySelector('.o_NotificationGroup_counter').textContent.trim(),
        "(1)",
        "shouldhave1notificationinfirstgroup"
    );
    assert.strictEqual(
        groups[0].querySelector('.o_NotificationGroup_inlineText').textContent.trim(),
        "Anerroroccurredwhensendinganemail.",
        "shouldhavethegrouptextcorrespondingtoemail"
    );
    assert.containsOnce(
        groups[1],
        '.o_NotificationGroup_name',
        "shouldhave1groupnameinsecondgroup"
    );
    assert.strictEqual(
        groups[1].querySelector('.o_NotificationGroup_name').textContent,
        "Partner",
        "shouldhavesecondmodelnameasgroupname"
    );
    assert.containsOnce(
        groups[1],
        '.o_NotificationGroup_counter',
        "shouldhave1groupcounterinsecondgroup"
    );
    assert.strictEqual(
        groups[1].querySelector('.o_NotificationGroup_counter').textContent.trim(),
        "(1)",
        "shouldhave1notificationinsecondgroup"
    );
    assert.strictEqual(
        groups[1].querySelector('.o_NotificationGroup_inlineText').textContent.trim(),
        "AnerroroccurredwhensendinganSMS.",
        "shouldhavethegrouptextcorrespondingtosms"
    );
});

QUnit.test('groupednotificationsbydocumentmodel',asyncfunction(assert){
    //Ifallfailureslinkedtoadocumentmodelreferstodifferentdocuments,
    //asinglenotificationshouldgroupallfailuresthatarelinkedtothis
    //documentmodel.
    assert.expect(12);

    this.data['mail.message'].records.push(
        //firstmessagethatisexpectedtohaveafailure
        {
            id:11,//randomuniqueid,willbeusedtolinkfailuretomessage
            message_type:'sms',//messagemustbesms(goalofthetest)
            model:'res.partner',//samemodelassecondmessage(andnot`mail.channel`)
            res_id:31,//differentres_idfromsecondmessage
            res_model_name:"Partner",//randomrelatedmodelname
        },
        //secondmessagethatisexpectedtohaveafailure
        {
            id:12,//randomuniqueid,willbeusedtolinkfailuretomessage
            message_type:'sms',//messagemustbesms(goalofthetest)
            model:'res.partner',//samemodelasfirstmessage(andnot`mail.channel`)
            res_id:32,//differentres_idfromfirstmessage
            res_model_name:"Partner",//samerelatedmodelnameforconsistency
        }
    );
    this.data['mail.notification'].records.push(
        //firstfailurethatisexpectedtobeusedinthetest
        {
            mail_message_id:11,//idoftherelatedfirstmessage
            notification_status:'exception',//necessaryvaluetohaveafailure
            notification_type:'sms',//expectedfailuretypeforsmsmessage
        },
        //secondfailurethatisexpectedtobeusedinthetest
        {
            mail_message_id:12,//idoftherelatedsecondmessage
            notification_status:'exception',//necessaryvaluetohaveafailure
            notification_type:'sms',//expectedfailuretypeforsmsmessage
        }
    );
    constbus=newBus();
    bus.on('do-action',null,payload=>{
        assert.step('do_action');
        assert.strictEqual(
            payload.action.name,
            "SMSFailures",
            "actionshouldhave'SMSFailures'asname",
        );
        assert.strictEqual(
            payload.action.type,
            'ir.actions.act_window',
            "actionshouldhavethetypeact_window"
        );
        assert.strictEqual(
            payload.action.view_mode,
            'kanban,list,form',
            "actionshouldhave'kanban,list,form'asview_mode"
        );
        assert.strictEqual(
            JSON.stringify(payload.action.views),
            JSON.stringify([[false,'kanban'],[false,'list'],[false,'form']]),
            "actionshouldhavecorrectviews"
        );
        assert.strictEqual(
            payload.action.target,
            'current',
            "actionshouldhave'current'astarget"
        );
        assert.strictEqual(
            payload.action.res_model,
            'res.partner',
            "actionshouldhavethegroupmodelasres_model"
        );
        assert.strictEqual(
            JSON.stringify(payload.action.domain),
            JSON.stringify([['message_has_sms_error','=',true]]),
            "actionshouldhave'message_has_sms_error'asdomain"
        );
    });

    awaitthis.start({env:{bus}});
    awaitthis.createNotificationListComponent();

    assert.containsOnce(
        document.body,
        '.o_NotificationGroup',
        "shouldhave1notificationgroup"
    );
    assert.containsOnce(
        document.body,
        '.o_NotificationGroup_counter',
        "shouldhave1groupcounter"
    );
    assert.strictEqual(
        document.querySelector('.o_NotificationGroup_counter').textContent.trim(),
        "(2)",
        "shouldhave2notificationsinthegroup"
    );

    document.querySelector('.o_NotificationGroup').click();
    assert.verifySteps(
        ['do_action'],
        "shoulddoanactiontodisplaytherelatedrecords"
    );
});

});
});
});

});
