flectra.define('mail/static/src/components/discuss/tests/discuss_moderation_tests.js',function(require){
'usestrict';

const{
    afterEach,
    afterNextRender,
    beforeEach,
    start,
}=require('mail/static/src/utils/test_utils.js');

QUnit.module('mail',{},function(){
QUnit.module('components',{},function(){
QUnit.module('discuss',{},function(){
QUnit.module('discuss_moderation_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.start=asyncparams=>{
            const{env,widget}=awaitstart(Object.assign({},params,{
                autoOpenDiscuss:true,
                data:this.data,
                hasDiscuss:true,
            }));
            this.env=env;
            this.widget=widget;
        };
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.test('asmoderator,moderatedchannelwithpendingmoderationmessage',asyncfunction(assert){
    assert.expect(37);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        is_moderator:true,//currentuserisexpectedtobemoderatorofchannel
        moderation:true,//forconsistency,butnotusedinthescopeofthistest
        name:"general",//randomname,willbeassertedinthetest
    });
    this.data['mail.message'].records.push({
        body:"<p>test</p>",//randombody,willbeassertedinthetest
        model:'mail.channel',//expectedvaluetolinkmessagetochannel
        moderation_status:'pending_moderation',//messageisexpectedtobependingmoderation
        res_id:20,//idofthechannel
    });
    awaitthis.start();

    assert.ok(
        document.querySelector(`
            .o_DiscussSidebar_item[data-thread-local-id="${
                this.env.messaging.moderation.localId
            }"]
        `),
        "shoulddisplaythemoderationboxinthesidebar"
    );
    constmailboxCounter=document.querySelector(`
        .o_DiscussSidebar_item[data-thread-local-id="${
            this.env.messaging.moderation.localId
        }"]
        .o_DiscussSidebarItem_counter
    `);
    assert.ok(
        mailboxCounter,
        "thereshouldbeacounternexttothemoderationmailboxinthesidebar"
    );
    assert.strictEqual(
        mailboxCounter.textContent.trim(),
        "1",
        "themailboxcounterofthemoderationmailboxshoulddisplay'1'"
    );

    //1.gotomoderationmailbox
    awaitafterNextRender(()=>
        document.querySelector(`
            .o_DiscussSidebar_item[data-thread-local-id="${
                this.env.messaging.moderation.localId
            }"]
        `).click()
    );
    //checkmessage
    assert.containsOnce(
        document.body,
        '.o_Message',
        "shouldbeonlyonemessageinmoderationbox"
    );
    assert.strictEqual(
        document.querySelector('.o_Message_content').textContent,
        "test",
        "thismessagependingmoderationshouldhavethecorrectcontent"
    );
    assert.containsOnce(
        document.body,
        '.o_Message_originThreadLink',
        "theemessageshouldhaveoneorigin"
    );
    assert.strictEqual(
        document.querySelector('.o_Message_originThreadLink').textContent,
        "#general",
        "themessagependingmoderationshouldhavecorrectoriginasitslinkeddocument"
    );
    assert.containsOnce(
        document.body,
        '.o_Message_checkbox',
        "thereshouldbeamoderationcheckboxnexttothemessage"
    );
    assert.notOk(
        document.querySelector('.o_Message_checkbox').checked,
        "themoderationcheckboxshouldbeuncheckedbydefault"
    );
    //checkselectall(enabled)/unselectall(disabled)buttons
    assert.containsOnce(
        document.body,
        '.o_widget_Discuss_controlPanelButtonSelectAll',
        "thereshouldbea'SelectAll'buttoninthecontrolpanel"
    );
    assert.doesNotHaveClass(
        document.querySelector('.o_widget_Discuss_controlPanelButtonSelectAll'),
        'disabled',
        "the'SelectAll'buttonshouldnotbedisabled"
    );
    assert.containsOnce(
        document.body,
        '.o_widget_Discuss_controlPanelButtonUnselectAll',
        "thereshouldbea'UnselectAll'buttoninthecontrolpanel"
    );
    assert.hasClass(
        document.querySelector('.o_widget_Discuss_controlPanelButtonUnselectAll'),
        'disabled',
        "the'UnselectAll'buttonshouldbedisabled"
    );
    //checkmoderateallbuttons(invisible)
    assert.containsN(
        document.body,
        '.o_widget_Discuss_controlPanelButtonModeration',
        3,
        "thereshouldbe3buttonstomoderateselectedmessagesinthecontrolpanel"
    );
    assert.containsOnce(
        document.body,
        '.o_widget_Discuss_controlPanelButtonModeration.o-accept',
        "thereshouldonemoderatebuttontoacceptmessagespendingmoderation"
    );
    assert.isNotVisible(
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-accept'),
        "themoderatebutton'Accept'shouldbeinvisiblebydefault"
    );
    assert.containsOnce(
        document.body,
        '.o_widget_Discuss_controlPanelButtonModeration.o-reject',
        "thereshouldonemoderatebuttontorejectmessagespendingmoderation"
    );
    assert.isNotVisible(
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-reject'),
        "themoderatebutton'Reject'shouldbeinvisiblebydefault"
    );
    assert.containsOnce(
        document.body,
        '.o_widget_Discuss_controlPanelButtonModeration.o-discard',
        "thereshouldonemoderatebuttontodiscardmessagespendingmoderation"
    );
    assert.isNotVisible(
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-discard'),
        "themoderatebutton'Discard'shouldbeinvisiblebydefault"
    );

    //clickonmessagemoderationcheckbox
    awaitafterNextRender(()=>document.querySelector('.o_Message_checkbox').click());
    assert.ok(
        document.querySelector('.o_Message_checkbox').checked,
        "themoderationcheckboxshouldbecomecheckedafterclick"
    );
    //checkselectall(disabled)/unselectallbuttons(enabled)
    assert.hasClass(
        document.querySelector('.o_widget_Discuss_controlPanelButtonSelectAll'),
        'disabled',
        "the'SelectAll'buttonshouldbedisabled"
    );
    assert.doesNotHaveClass(
        document.querySelector('.o_widget_Discuss_controlPanelButtonUnselectAll'),
        'disabled',
        "the'UnselectAll'buttonshouldnotbedisabled"
    );
    //checkmoderateallbuttonsupdated(visible)
    assert.isVisible(
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-accept'),
        "themoderatebutton'Accept'shouldbevisible"
    );
    assert.isVisible(
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-reject'),
        "themoderatebutton'Reject'shouldbevisible"
    );
    assert.isVisible(
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-discard'),
        "themoderatebutton'Discard'shouldbevisible"
    );

    //testselectbuttons
    awaitafterNextRender(()=>
        document.querySelector('.o_widget_Discuss_controlPanelButtonUnselectAll').click()
    );
    assert.notOk(
        document.querySelector('.o_Message_checkbox').checked,
        "themoderationcheckboxshouldbecomeuncheckedafterclick"
    );

    awaitafterNextRender(()=>
        document.querySelector('.o_widget_Discuss_controlPanelButtonSelectAll').click()
    );
    assert.ok(
        document.querySelector('.o_Message_checkbox').checked,
        "themoderationcheckboxshouldbecomecheckedagainafterclick"
    );

    //2.gotochannel'general'
    awaitafterNextRender(()=>
        document.querySelector(`
            .o_DiscussSidebar_item[data-thread-local-id="${
                this.env.models['mail.thread'].findFromIdentifyingData({
                    id:20,
                    model:'mail.channel',
                }).localId
            }"]
        `).click()
    );
    //checkcorrectmessage
    assert.containsOnce(
        document.body,
        '.o_Message',
        "shouldbeonlyonemessageingeneralchannel"
    );
    assert.containsOnce(
        document.body,
        '.o_Message_checkbox',
        "thereshouldbeamoderationcheckboxnexttothemessage"
    );
    assert.notOk(
        document.querySelector('.o_Message_checkbox').checked,
        "themoderationcheckboxshouldnotbecheckedhere"
    );
    awaitafterNextRender(()=>document.querySelector('.o_Message_checkbox').click());
    //Don'ttestmoderationactionsvisibility,sinceitissimilartomoderationbox.

    //3.testdiscardbutton
    awaitafterNextRender(()=>
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-discard').click()
    );
    assert.containsOnce(
        document.body,
        '.o_ModerationDiscardDialog',
        "discarddialogshouldbeopen"
    );
    //thedialogwillbetestedseparately
    awaitafterNextRender(()=>
        document.querySelector('.o_ModerationDiscardDialog.o-cancel').click()
    );
    assert.containsNone(
        document.body,
        '.o_ModerationDiscardDialog',
        "discarddialogshouldbeclosed"
    );

    //4.testrejectbutton
    awaitafterNextRender(()=>
        document.querySelector(`
            .o_widget_Discuss_controlPanelButtonModeration.o-reject
        `).click()
    );
    assert.containsOnce(
        document.body,
        '.o_ModerationRejectDialog',
        "rejectdialogshouldbeopen"
    );
    //thedialogwillbetestedseparately
    awaitafterNextRender(()=>
        document.querySelector('.o_ModerationRejectDialog.o-cancel').click()
    );
    assert.containsNone(
        document.body,
        '.o_ModerationRejectDialog',
        "rejectdialogshouldbeclosed"
    );

    //5.testacceptbutton
    awaitafterNextRender(()=>
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-accept').click()
    );
    assert.containsOnce(
        document.body,
        '.o_Message',
        "shouldstillbeonlyonemessageingeneralchannel"
    );
    assert.containsNone(
        document.body,
        '.o_Message_checkbox',
        "thereshouldnotbeamoderationcheckboxnexttothemessage"
    );
});

QUnit.test('asmoderator,acceptpendingmoderationmessage',asyncfunction(assert){
    assert.expect(12);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        is_moderator:true,//currentuserisexpectedtobemoderatorofchannel
        moderation:true,//forconsistency,butnotusedinthescopeofthistest
        name:"general",//randomname,willbeassertedinthetest
    });
    this.data['mail.message'].records.push({
        body:"<p>test</p>",//randombody,willbeassertedinthetest
        id:100,//randomuniqueid,willbeassertedduringthetest
        model:'mail.channel',//expectedvaluetolinkmessagetochannel
        moderation_status:'pending_moderation',//messageisexpectedtobependingmoderation
        res_id:20,//idofthechannel
    });
    awaitthis.start({
        asyncmockRPC(route,args){
            if(args.method==='moderate'){
                assert.step('moderate');
                constmessageIDs=args.args[0];
                constdecision=args.args[1];
                assert.strictEqual(
                    messageIDs.length,
                    1,
                    "shouldmoderateonemessage"
                );
                assert.strictEqual(
                    messageIDs[0],
                    100,
                    "shouldmoderatemessagewithID100"
                );
                assert.strictEqual(
                    decision,
                    'accept',
                    "shouldacceptthemessage"
                );
            }
            returnthis._super(...arguments);
        },
    });

    //1.gotomoderationbox
    constmoderationBox=document.querySelector(`
        .o_DiscussSidebar_item[data-thread-local-id="${
            this.env.messaging.moderation.localId
        }"]
    `);
    assert.ok(
        moderationBox,
        "shoulddisplaythemoderationbox"
    );

    awaitafterNextRender(()=>moderationBox.click());
    assert.ok(
        document.querySelector(`
            .o_Message[data-message-local-id="${
                this.env.models['mail.message'].findFromIdentifyingData({id:100}).localId
            }"]
        `),
        "shoulddisplaythemessagetomoderate"
    );
    constacceptButton=document.querySelector(`
        .o_Message[data-message-local-id="${
            this.env.models['mail.message'].findFromIdentifyingData({id:100}).localId
        }"]
        .o_Message_moderationAction.o-accept
    `);
    assert.ok(acceptButton,"shoulddisplaytheacceptbutton");

    awaitafterNextRender(()=>acceptButton.click());
    assert.verifySteps(['moderate']);
    assert.containsOnce(
        document.body,
        '.o_MessageList_emptyTitle',
        "shouldnowhavenomessagedisplayedinmoderationbox"
    );

    //2.gotochannel'general'
    constchannel=document.querySelector(`
        .o_DiscussSidebar_item[data-thread-local-id="${
            this.env.models['mail.thread'].findFromIdentifyingData({
                id:20,
                model:'mail.channel',
            }).localId
        }"]
    `);
    assert.ok(
        channel,
        "shoulddisplaythegeneralchannel"
    );

    awaitafterNextRender(()=>channel.click());
    constmessage=document.querySelector(`
        .o_Message[data-message-local-id="${
            this.env.models['mail.message'].findFromIdentifyingData({id:100}).localId
        }"]
    `);
    assert.ok(
        message,
        "shoulddisplaytheacceptedmessage"
    );
    assert.containsNone(
        message,
        '.o_Message_moderationPending',
        "themessageshouldnotbependingmoderation"
    );
});

QUnit.test('asmoderator,rejectpendingmoderationmessage(rejectwithexplanation)',asyncfunction(assert){
    assert.expect(23);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        is_moderator:true,//currentuserisexpectedtobemoderatorofchannel
        moderation:true,//forconsistency,butnotusedinthescopeofthistest
        name:"general",//randomname,willbeassertedinthetest
    });
    this.data['mail.message'].records.push({
        body:"<p>test</p>",//randombody,willbeassertedinthetest
        id:100,//randomuniqueid,willbeassertedduringthetest
        model:'mail.channel',//expectedvaluetolinkmessagetochannel
        moderation_status:'pending_moderation',//messageisexpectedtobependingmoderation
        res_id:20,//idofthechannel
    });
    awaitthis.start({
        asyncmockRPC(route,args){
            if(args.method==='moderate'){
                assert.step('moderate');
                constmessageIDs=args.args[0];
                constdecision=args.args[1];
                constkwargs=args.kwargs;
                assert.strictEqual(
                    messageIDs.length,
                    1,
                    "shouldmoderateonemessage"
                );
                assert.strictEqual(
                    messageIDs[0],
                    100,
                    "shouldmoderatemessagewithID100"
                );
                assert.strictEqual(
                    decision,
                    'reject',
                    "shouldrejectthemessage"
                );
                assert.strictEqual(
                    kwargs.title,
                    "MessageRejected",
                    "shouldhavecorrectrejectmessagetitle"
                );
                assert.strictEqual(
                    kwargs.comment,
                    "Yourmessagewasrejectedbymoderator.",
                    "shouldhavecorrectrejectmessagebody/comment"
                );
            }
            returnthis._super(...arguments);
        },
    });

    //1.gotomoderationbox
    constmoderationBox=document.querySelector(`
        .o_DiscussSidebar_item[data-thread-local-id="${
            this.env.messaging.moderation.localId
        }"]
    `);
    assert.ok(
        moderationBox,
        "shoulddisplaythemoderationbox"
    );

    awaitafterNextRender(()=>moderationBox.click());
    constpendingMessage=document.querySelector(`
        .o_Message[data-message-local-id="${
            this.env.models['mail.message'].findFromIdentifyingData({id:100}).localId
        }"]
    `);
    assert.ok(
        pendingMessage,
        "shoulddisplaythemessagetomoderate"
    );
    constrejectButton=pendingMessage.querySelector(':scope.o_Message_moderationAction.o-reject');
    assert.ok(
        rejectButton,
        "shoulddisplaytherejectbutton"
    );

    awaitafterNextRender(()=>rejectButton.click());
    constdialog=document.querySelector('.o_ModerationRejectDialog');
    assert.ok(
        dialog,
        "adialogshouldbeprompttothemoderatoronclickreject"
    );
    assert.strictEqual(
        dialog.querySelector('.modal-title').textContent,
        "Sendexplanationtoauthor",
        "dialogshouldhavecorrecttitle"
    );

    constmessageTitle=dialog.querySelector(':scope.o_ModerationRejectDialog_title');
    assert.ok(
        messageTitle,
        "shouldhaveatitleforrejecting"
    );
    assert.hasAttrValue(
        messageTitle,
        'placeholder',
        "Subject",
        "titleforrejectreasonshouldhavecorrectplaceholder"
    );
    assert.strictEqual(
        messageTitle.value,
        "MessageRejected",
        "titleforrejectreasonshouldhavecorrectdefaultvalue"
    );

    constmessageComment=dialog.querySelector(':scope.o_ModerationRejectDialog_comment');
    assert.ok(
        messageComment,
        "shouldhaveacommentforrejecting"
    );
    assert.hasAttrValue(
        messageComment,
        'placeholder',
        "MailBody",
        "commentforrejectreasonshouldhavecorrectplaceholder"
    );
    assert.strictEqual(
        messageComment.value,
        "Yourmessagewasrejectedbymoderator.",
        "commentforrejectreasonshouldhavecorrectdefaulttextcontent"
    );
    constconfirmReject=dialog.querySelector(':scope.o-reject');
    assert.ok(
        confirmReject,
        "shouldhaverejectbutton"
    );
    assert.strictEqual(
        confirmReject.textContent,
        "Reject"
    );

    awaitafterNextRender(()=>confirmReject.click());
    assert.verifySteps(['moderate']);
    assert.containsOnce(
        document.body,
        '.o_MessageList_emptyTitle',
        "shouldnowhavenomessagedisplayedinmoderationbox"
    );

    //2.gotochannel'general'
    constchannel=document.querySelector(`
        .o_DiscussSidebar_item[data-thread-local-id="${
            this.env.models['mail.thread'].findFromIdentifyingData({
                id:20,
                model:'mail.channel',
            }).localId
        }"]
    `);
    assert.ok(
        channel,
        'shoulddisplaythegeneralchannel'
    );

    awaitafterNextRender(()=>channel.click());
    assert.containsNone(
        document.body,
        '.o_Message',
        "shouldnowhavenomessageinchannel"
    );
});

QUnit.test('asmoderator,discardpendingmoderationmessage(rejectwithoutexplanation)',asyncfunction(assert){
    assert.expect(16);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        is_moderator:true,//currentuserisexpectedtobemoderatorofchannel
        moderation:true,//forconsistency,butnotusedinthescopeofthistest
        name:"general",//randomname,willbeassertedinthetest
    });
    this.data['mail.message'].records.push({
        body:"<p>test</p>",//randombody,willbeassertedinthetest
        id:100,//randomuniqueid,willbeassertedduringthetest
        model:'mail.channel',//expectedvaluetolinkmessagetochannel
        moderation_status:'pending_moderation',//messageisexpectedtobependingmoderation
        res_id:20,//idofthechannel
    });
    awaitthis.start({
        asyncmockRPC(route,args){
            if(args.method==='moderate'){
                assert.step('moderate');
                constmessageIDs=args.args[0];
                constdecision=args.args[1];
                assert.strictEqual(messageIDs.length,1,"shouldmoderateonemessage");
                assert.strictEqual(messageIDs[0],100,"shouldmoderatemessagewithID100");
                assert.strictEqual(decision,'discard',"shoulddiscardthemessage");
            }
            returnthis._super(...arguments);
        },
    });

    //1.gotomoderationbox
    constmoderationBox=document.querySelector(`
        .o_DiscussSidebar_item[data-thread-local-id="${
            this.env.messaging.moderation.localId
        }"]
    `);
    assert.ok(
        moderationBox,
        "shoulddisplaythemoderationbox"
    );

    awaitafterNextRender(()=>moderationBox.click());
    constpendingMessage=document.querySelector(`
        .o_Message[data-message-local-id="${
            this.env.models['mail.message'].findFromIdentifyingData({id:100}).localId
        }"]
    `);
    assert.ok(
        pendingMessage,
        "shoulddisplaythemessagetomoderate"
    );

    constdiscardButton=pendingMessage.querySelector(`
        :scope.o_Message_moderationAction.o-discard
    `);
    assert.ok(
        discardButton,
        "shoulddisplaythediscardbutton"
    );

    awaitafterNextRender(()=>discardButton.click());
    constdialog=document.querySelector('.o_ModerationDiscardDialog');
    assert.ok(
        dialog,
        "adialogshouldbeprompttothemoderatoronclickdiscard"
    );
    assert.strictEqual(
        dialog.querySelector('.modal-title').textContent,
        "Confirmation",
        "dialogshouldhavecorrecttitle"
    );
    assert.strictEqual(
        dialog.textContent,
        "Confirmation×Youaregoingtodiscard1message.Doyouconfirmtheaction?DiscardCancel",
        "shouldwarntheuserondiscardaction"
    );

    constconfirmDiscard=dialog.querySelector(':scope.o-discard');
    assert.ok(
        confirmDiscard,
        "shouldhavediscardbutton"
    );
    assert.strictEqual(
        confirmDiscard.textContent,
        "Discard"
    );

    awaitafterNextRender(()=>confirmDiscard.click());
    assert.verifySteps(['moderate']);
    assert.containsOnce(
        document.body,
        '.o_MessageList_emptyTitle',
        "shouldnowhavenomessagedisplayedinmoderationbox"
    );

    //2.gotochannel'general'
    constchannel=document.querySelector(`
        .o_DiscussSidebar_item[data-thread-local-id="${
            this.env.models['mail.thread'].findFromIdentifyingData({
                id:20,
                model:'mail.channel',
            }).localId
        }"]
    `);
    assert.ok(
        channel,
        "shoulddisplaythegeneralchannel"
    );

    awaitafterNextRender(()=>channel.click());
    assert.containsNone(
        document.body,
        '.o_Message',
        "shouldnowhavenomessageinchannel"
    );
});

QUnit.test('asauthor,sendmessageinmoderatedchannel',asyncfunction(assert){
    assert.expect(4);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        moderation:true,//channelmustbemoderatedtotestthefeature
        name:"general",//randomname,willbeassertedinthetest
    });
    awaitthis.start();
    constchannel=document.querySelector(`
        .o_DiscussSidebar_item[data-thread-local-id="${
            this.env.models['mail.thread'].findFromIdentifyingData({
                id:20,
                model:'mail.channel',
            }).localId
        }"]
    `);
    assert.ok(
        channel,
        "shoulddisplaythegeneralchannel"
    );

    //gotochannel'general'
    awaitafterNextRender(()=>channel.click());
    assert.containsNone(
        document.body,
        '.o_Message',
        "shouldhavenomessageinchannel"
    );

    //postamessage
    awaitafterNextRender(()=>{
        consttextInput=document.querySelector('.o_ComposerTextInput_textarea');
        textInput.focus();
        document.execCommand('insertText',false,"SomeText");
    });
    awaitafterNextRender(()=>document.querySelector('.o_Composer_buttonSend').click());
    constmessagePending=document.querySelector('.o_Message_moderationPending');
    assert.ok(
        messagePending,
        "shoulddisplaythependingmessagewithpendinginfo"
    );
    assert.hasClass(
        messagePending,
        'o-author',
        "themessageshouldbependingmoderationasauthor"
    );
});

QUnit.test('asauthor,sentmessageacceptedinmoderatedchannel',asyncfunction(assert){
    assert.expect(5);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        moderation:true,//forconsistency,butnotusedinthescopeofthistest
        name:"general",//randomname,willbeassertedinthetest
    });
    this.data['mail.message'].records.push({
        body:"notempty",
        id:100,//randomuniqueid,willbereferencedinthetest
        model:'mail.channel',//expectedvaluetolinkmessagetochannel
        moderation_status:'pending_moderation',//messageisexpectedtobepending
        res_id:20,//idofthechannel
    });
    awaitthis.start();

    constchannel=document.querySelector(`
        .o_DiscussSidebar_item[data-thread-local-id="${
            this.env.models['mail.thread'].findFromIdentifyingData({
                id:20,
                model:'mail.channel',
            }).localId
        }"]
    `);
    assert.ok(
        channel,
        "shoulddisplaythegeneralchannel"
    );

    awaitafterNextRender(()=>channel.click());
    constmessagePending=document.querySelector(`
        .o_Message[data-message-local-id="${
            this.env.models['mail.message'].findFromIdentifyingData({id:100}).localId
        }"]
        .o_Message_moderationPending
    `);
    assert.ok(
        messagePending,
        "shoulddisplaythependingmessagewithpendinginfo"
    );
    assert.hasClass(
        messagePending,
        'o-author',
        "themessageshouldbependingmoderationasauthor"
    );

    //simulateacceptedmessage
    awaitafterNextRender(()=>{
        constmessageData={
            id:100,
            moderation_status:'accepted',
        };
        constnotification=[[false,'mail.channel',20],messageData];
        this.widget.call('bus_service','trigger','notification',[notification]);
    });

    //checkmessageisaccepted
    constmessage=document.querySelector(`
        .o_Message[data-message-local-id="${
            this.env.models['mail.message'].findFromIdentifyingData({id:100}).localId
        }"]
    `);
    assert.ok(
        message,
        "shouldstilldisplaythemessage"
    );
    assert.containsNone(
        message,
        '.o_Message_moderationPending',
        "themessageshouldnotbeinpendingmoderationanymore"
    );
});

QUnit.test('asauthor,sentmessagerejectedinmoderatedchannel',asyncfunction(assert){
    assert.expect(4);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        moderation:true,//forconsistency,butnotusedinthescopeofthistest
        name:"general",//randomname,willbeassertedinthetest
    });
    this.data['mail.message'].records.push({
        body:"notempty",
        id:100,//randomuniqueid,willbereferencedinthetest
        model:'mail.channel',//expectedvaluetolinkmessagetochannel
        moderation_status:'pending_moderation',//messageisexpectedtobepending
        res_id:20,//idofthechannel
    });
    awaitthis.start();

    constchannel=document.querySelector(`
        .o_DiscussSidebar_item[data-thread-local-id="${
            this.env.models['mail.thread'].findFromIdentifyingData({
                id:20,
                model:'mail.channel',
            }).localId
        }"]
    `);
    assert.ok(
        channel,
        "shoulddisplaythegeneralchannel"
    );

    awaitafterNextRender(()=>channel.click());
    constmessagePending=document.querySelector(`
        .o_Message[data-message-local-id="${
            this.env.models['mail.message'].findFromIdentifyingData({id:100}).localId
        }"]
        .o_Message_moderationPending
    `);
    assert.ok(
        messagePending,
        "shoulddisplaythependingmessagewithpendinginfo"
    );
    assert.hasClass(
        messagePending,
        'o-author',
        "themessageshouldbependingmoderationasauthor"
    );

    //simulaterejectfrommoderator
    awaitafterNextRender(()=>{
        constnotifData={
            type:'deletion',
            message_ids:[100],
        };
        constnotification=[[false,'res.partner',this.env.messaging.currentPartner.id],notifData];
        this.widget.call('bus_service','trigger','notification',[notification]);
    });
    //checknomessage
    assert.containsNone(
        document.body,
        '.o_Message',
        "messageshouldberemovedfromchannelafterreject"
    );
});

QUnit.test('asmoderator,pendingmoderationmessageaccessibility',asyncfunction(assert){
    //pendingmoderationmessageshouldappearinmoderationboxandinoriginthread
    assert.expect(3);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        is_moderator:true,//currentuserisexpectedtobemoderatorofchannel
        moderation:true,//channelmustbemoderatedtotestthefeature
    });
    this.data['mail.message'].records.push({
        body:"notempty",
        id:100,//randomuniqueid,willbereferencedinthetest
        model:'mail.channel',//expectedvaluetolinkmessagetochannel
        moderation_status:'pending_moderation',//messageisexpectedtobepending
        res_id:20,//idofthechannel
    });
    awaitthis.start();

    constthread=this.env.models['mail.thread'].findFromIdentifyingData({id:20,model:'mail.channel'});
    assert.ok(
        document.querySelector(`
            .o_DiscussSidebar_item[data-thread-local-id="${
                this.env.messaging.moderation.localId
            }"]
        `),
        "shoulddisplaythemoderationboxinthesidebar"
    );

    awaitafterNextRender(()=>
        document.querySelector(`
            .o_DiscussSidebar_item[data-thread-local-id="${thread.localId}"]
        `).click()
    );
    constmessage=this.env.models['mail.message'].findFromIdentifyingData({id:100});
    assert.containsOnce(
        document.body,
        `.o_Message[data-message-local-id="${message.localId}"]`,
        "thependingmoderationmessageshouldbeinthechannel"
    );

    awaitafterNextRender(()=>
        document.querySelector(`
            .o_DiscussSidebar_item[data-thread-local-id="${
                this.env.messaging.moderation.localId
            }"]
        `).click()
    );
    assert.containsOnce(
        document.body,
        `.o_Message[data-message-local-id="${message.localId}"]`,
        "thependingmoderationmessageshouldbeinmoderationbox"
    );
});

QUnit.test('asauthor,pendingmoderationmessageshouldappearinoriginthread',asyncfunction(assert){
    assert.expect(1);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        moderation:true,//channelmustbemoderatedtotestthefeature
    });
    this.data['mail.message'].records.push({
        author_id:this.data.currentPartnerId,//testasauthorofmessage
        body:"notempty",
        id:100,//randomuniqueid,willbereferencedinthetest
        model:'mail.channel',//expectedvaluetolinkmessagetochannel
        moderation_status:'pending_moderation',//messageisexpectedtobepending
        res_id:20,//idofthechannel
    });
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({id:20,model:'mail.channel'});

    awaitafterNextRender(()=>
        document.querySelector(`
            .o_DiscussSidebar_item[data-thread-local-id="${thread.localId}"]
        `).click()
    );
    constmessage=this.env.models['mail.message'].findFromIdentifyingData({id:100});
    assert.containsOnce(
        document.body,
        `.o_Message[data-message-local-id="${message.localId}"]`,
        "thependingmoderationmessageshouldbeinthechannel"
    );
});

QUnit.test('asmoderator,newpendingmoderationmessagepostedbysomeoneelse',asyncfunction(assert){
    //themessageshouldappearinoriginthreadandmoderationboxifImoderateit
    assert.expect(3);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        is_moderator:true,//currentuserisexpectedtobemoderatorofchannel
        moderation:true,//channelmustbemoderatedtotestthefeature
    });
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({id:20,model:'mail.channel'});

    awaitafterNextRender(()=>
        document.querySelector(`
            .o_DiscussSidebar_item[data-thread-local-id="${thread.localId}"]
        `).click()
    );
    assert.containsNone(
        document.body,
        `.o_Message`,
        "shouldhavenomessageinthechannelinitially"
    );

    //simulatereceivingthemessage
    constmessageData={
        author_id:[10,'johndoe'],//randomid,differentthancurrentpartner
        body:"notempty",
        channel_ids:[],//serverdoNOTreturnchannel_idofthemessageifpendingmoderation
        id:1,//randomuniqueid
        model:'mail.channel',//expectedvaluetolinkmessagetochannel
        moderation_status:'pending_moderation',//messageisexpectedtobepending
        res_id:20,//idofthechannel
    };
    awaitafterNextRender(()=>{
        constnotifications=[[
            ['my-db','res.partner',this.env.messaging.currentPartner.id],
            {type:'moderator',message:messageData},
        ]];
        this.widget.call('bus_service','trigger','notification',notifications);
    });
    constmessage=this.env.models['mail.message'].findFromIdentifyingData({id:1});
    assert.containsOnce(
        document.body,
        `.o_Message[data-message-local-id="${message.localId}"]`,
        "thependingmoderationmessageshouldbeinthechannel"
    );

    awaitafterNextRender(()=>
        document.querySelector(`
            .o_DiscussSidebar_item[data-thread-local-id="${
                this.env.messaging.moderation.localId
            }"]
        `).click()
    );
    assert.containsOnce(
        document.body,
        `.o_Message[data-message-local-id="${message.localId}"]`,
        "thependingmoderationmessageshouldbeinmoderationbox"
    );
});

QUnit.test('acceptmultiplemoderationmessages',asyncfunction(assert){
    assert.expect(5);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        is_moderator:true,//currentuserisexpectedtobemoderatorofchannel
        moderation:true,//channelmustbemoderatedtotestthefeature
    });
    this.data['mail.message'].records.push(
        {
            body:"notempty",
            model:'mail.channel',
            moderation_status:'pending_moderation',
            res_id:20,
        },
        {
            body:"notempty",
            model:'mail.channel',
            moderation_status:'pending_moderation',
            res_id:20,
        },
        {
            body:"notempty",
            model:'mail.channel',
            moderation_status:'pending_moderation',
            res_id:20,
        }
    );

    awaitthis.start({
        discuss:{
            params:{
                default_active_id:'mail.box_moderation',
            },
        },
    });

    assert.containsN(
        document.body,
        '.o_Message',
        3,
        "shouldinitiallydisplay3messages"
    );

    awaitafterNextRender(()=>{
        document.querySelectorAll('.o_Message_checkbox')[0].click();
        document.querySelectorAll('.o_Message_checkbox')[1].click();
    });
    assert.containsN(
        document.body,
        '.o_Message_checkbox:checked',
        2,
        "2messagesshouldhavebeencheckedafterclickingontheirrespectivecheckbox"
    );
    assert.doesNotHaveClass(
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-accept'),
        'o_hidden',
        "globalacceptbuttonshouldbedisplayedastwomessagesareselected"
    );

    awaitafterNextRender(()=>
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-accept').click()
    );
    assert.containsN(
        document.body,
        '.o_Message',
        1,
        "shoulddisplay1messageasthe2othershavebeenaccepted"
    );
    assert.hasClass(
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-accept'),
        'o_hidden',
        "globalacceptbuttonshouldnolongerbedisplayedasmessageshavebeenunselected"
    );
});

QUnit.test('acceptmultiplemoderationmessagesafterhavingacceptedothermessages',asyncfunction(assert){
    assert.expect(5);

    this.data['mail.channel'].records.push({
        id:20,//randomuniqueid,willbeusedtolinkmessageandwillbereferencedinthetest
        is_moderator:true,//currentuserisexpectedtobemoderatorofchannel
        moderation:true,//channelmustbemoderatedtotestthefeature
    });
    this.data['mail.message'].records.push(
        {
            body:"notempty",
            model:'mail.channel',
            moderation_status:'pending_moderation',
            res_id:20,
        },
        {
            body:"notempty",
            model:'mail.channel',
            moderation_status:'pending_moderation',
            res_id:20,
        },
        {
            body:"notempty",
            model:'mail.channel',
            moderation_status:'pending_moderation',
            res_id:20,
        }
    );
    awaitthis.start({
        discuss:{
            params:{
                default_active_id:'mail.box_moderation',
            },
        },
    });
    assert.containsN(
        document.body,
        '.o_Message',
        3,
        "shouldinitiallydisplay3messages"
    );

    awaitafterNextRender(()=>{
        document.querySelectorAll('.o_Message_checkbox')[0].click();
    });
    awaitafterNextRender(()=>
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-accept').click()
    );
    awaitafterNextRender(()=>document.querySelectorAll('.o_Message_checkbox')[0].click());
    assert.containsOnce(
        document.body,
        '.o_Message_checkbox:checked',
        "amessageshouldhavebeencheckedafterclickingonitscheckbox"
    );
    assert.doesNotHaveClass(
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-accept'),
        'o_hidden',
        "globalacceptbuttonshouldbedisplayedasamessageisselected"
    );

    awaitafterNextRender(()=>
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-accept').click()
    );
    assert.containsOnce(
        document.body,
        '.o_Message',
        "shoulddisplayonlyonemessageleftafterthetwoothershasbeenaccepted"
    );
    assert.hasClass(
        document.querySelector('.o_widget_Discuss_controlPanelButtonModeration.o-accept'),
        'o_hidden',
        "globalacceptbuttonshouldnolongerbedisplayedasmessagehasbeenunselected"
    );
});

});
});
});

});
