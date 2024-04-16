flectra.define('mail.chatter_tests',function(require){
"usestrict";

const{afterEach,beforeEach,start}=require('mail/static/src/utils/test_utils.js');

varFormView=require('web.FormView');
varListView=require('web.ListView');
vartestUtils=require('web.test_utils');

QUnit.module('mail',{},function(){
QUnit.module('Chatter',{
    beforeEach:function(){
        beforeEach(this);

        this.data['res.partner'].records.push({id:11,im_status:'online'});
        this.data['mail.activity.type'].records.push(
            {id:1,name:"Type1"},
            {id:2,name:"Type2"},
            {id:3,name:"Type3",category:'upload_file'},
            {id:4,name:"Exception",decoration_type:"warning",icon:"fa-warning"}
        );
        this.data['ir.attachment'].records.push(
            {
                id:1,
                mimetype:'image/png',
                name:'filename.jpg',
                res_id:7,
                res_model:'res.users',
                type:'url',
            },
            {
                id:2,
                mimetype:"application/x-msdos-program",
                name:"file2.txt",
                res_id:7,
                res_model:'res.users',
                type:'binary',
            },
            {
                id:3,
                mimetype:"application/x-msdos-program",
                name:"file3.txt",
                res_id:5,
                res_model:'res.users',
                type:'binary',
            },
        );
        Object.assign(this.data['res.users'].fields,{
            activity_exception_decoration:{
                string:'Decoration',
                type:'selection',
                selection:[['warning','Alert'],['danger','Error']],
            },
            activity_exception_icon:{
                string:'icon',
                type:'char',
            },
            activity_ids:{
                string:'Activities',
                type:'one2many',
                relation:'mail.activity',
                relation_field:'res_id',
            },
            activity_state:{
                string:'State',
                type:'selection',
                selection:[['overdue','Overdue'],['today','Today'],['planned','Planned']],
            },
            activity_summary:{
                string:"NextActivitySummary",
                type:'char',
            },
            activity_type_icon:{
                string:"ActivityTypeIcon",
                type:'char',
            },
            activity_type_id:{
                string:"Activitytype",
                type:"many2one",
                relation:"mail.activity.type",
            },
            foo:{string:"Foo",type:"char",default:"MylittleFooValue"},
            message_attachment_count:{
                string:'Attachmentcount',
                type:'integer',
            },
            message_follower_ids:{
                string:"Followers",
                type:"one2many",
                relation:'mail.followers',
                relation_field:"res_id",
            },
            message_ids:{
                string:"messages",
                type:"one2many",
                relation:'mail.message',
                relation_field:"res_id",
            },
        });
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.test('listactivitywidgetwithnoactivity',asyncfunction(assert){
    assert.expect(5);

    const{widget:list}=awaitstart({
        hasView:true,
        View:ListView,
        model:'res.users',
        data:this.data,
        arch:'<list><fieldname="activity_ids"widget="list_activity"/></list>',
        mockRPC:function(route){
            assert.step(route);
            returnthis._super(...arguments);
        },
        session:{uid:2},
    });

    assert.containsOnce(list,'.o_mail_activity.o_activity_color_default');
    assert.strictEqual(list.$('.o_activity_summary').text(),'');

    assert.verifySteps([
        '/web/dataset/search_read',
        '/mail/init_messaging',
    ]);

    list.destroy();
});

QUnit.test('listactivitywidgetwithactivities',asyncfunction(assert){
    assert.expect(7);

    constcurrentUser=this.data['res.users'].records.find(user=>
        user.id===this.data.currentUserId
    );
    Object.assign(currentUser,{
        activity_ids:[1,4],
        activity_state:'today',
        activity_summary:'CallwithAl',
        activity_type_id:3,
        activity_type_icon:'fa-phone',
    });

    this.data['res.users'].records.push({
        id:44,
        activity_ids:[2],
        activity_state:'planned',
        activity_summary:false,
        activity_type_id:2,
    });

    const{widget:list}=awaitstart({
        hasView:true,
        View:ListView,
        model:'res.users',
        data:this.data,
        arch:'<list><fieldname="activity_ids"widget="list_activity"/></list>',
        mockRPC:function(route){
            assert.step(route);
            returnthis._super(...arguments);
        },
    });

    const$firstRow=list.$('.o_data_row:first');
    assert.containsOnce($firstRow,'.o_mail_activity.o_activity_color_today.fa-phone');
    assert.strictEqual($firstRow.find('.o_activity_summary').text(),'CallwithAl');

    const$secondRow=list.$('.o_data_row:nth(1)');
    assert.containsOnce($secondRow,'.o_mail_activity.o_activity_color_planned.fa-clock-o');
    assert.strictEqual($secondRow.find('.o_activity_summary').text(),'Type2');

    assert.verifySteps([
        '/web/dataset/search_read',
        '/mail/init_messaging',
    ]);

    list.destroy();
});

QUnit.test('listactivitywidgetwithexception',asyncfunction(assert){
    assert.expect(5);

    constcurrentUser=this.data['res.users'].records.find(user=>
        user.id===this.data.currentUserId
    );
    Object.assign(currentUser,{
        activity_ids:[1],
        activity_state:'today',
        activity_summary:'CallwithAl',
        activity_type_id:3,
        activity_exception_decoration:'warning',
        activity_exception_icon:'fa-warning',
    });

    const{widget:list}=awaitstart({
        hasView:true,
        View:ListView,
        model:'res.users',
        data:this.data,
        arch:'<list><fieldname="activity_ids"widget="list_activity"/></list>',
        mockRPC:function(route){
            assert.step(route);
            returnthis._super(...arguments);
        },
    });

    assert.containsOnce(list,'.o_activity_color_today.text-warning.fa-warning');
    assert.strictEqual(list.$('.o_activity_summary').text(),'Warning');

    assert.verifySteps([
        '/web/dataset/search_read',
        '/mail/init_messaging',
    ]);

    list.destroy();
});

QUnit.test('listactivitywidget:opendropdown',asyncfunction(assert){
    assert.expect(10);

    constcurrentUser=this.data['res.users'].records.find(user=>
        user.id===this.data.currentUserId
    );
    Object.assign(currentUser,{
        activity_ids:[1,4],
        activity_state:'today',
        activity_summary:'CallwithAl',
        activity_type_id:3,
    });
    this.data['mail.activity'].records.push(
        {
            id:1,
            display_name:"CallwithAl",
            date_deadline:moment().format("YYYY-MM-DD"),//now
            can_write:true,
            state:"today",
            user_id:this.data.currentUserId,
            create_uid:this.data.currentUserId,
            activity_type_id:3,
        },
        {
            id:4,
            display_name:"MeetFP",
            date_deadline:moment().add(1,'day').format("YYYY-MM-DD"),//tomorrow
            can_write:true,
            state:"planned",
            user_id:this.data.currentUserId,
            create_uid:this.data.currentUserId,
            activity_type_id:1,
        }
    );

    const{env,widget:list}=awaitstart({
        hasView:true,
        View:ListView,
        model:'res.users',
        data:this.data,
        arch:`
            <list>
                <fieldname="foo"/>
                <fieldname="activity_ids"widget="list_activity"/>
            </list>`,
        mockRPC:function(route,args){
            assert.step(args.method||route);
            if(args.method==='action_feedback'){
                constcurrentUser=this.data['res.users'].records.find(user=>
                    user.id===env.messaging.currentUser.id
                );
                Object.assign(currentUser,{
                    activity_ids:[4],
                    activity_state:'planned',
                    activity_summary:'MeetFP',
                    activity_type_id:1,
                });
                returnPromise.resolve();
            }
            returnthis._super(route,args);
        },
        intercepts:{
            switch_view:()=>assert.step('switch_view'),
        },
    });

    assert.strictEqual(list.$('.o_activity_summary').text(),'CallwithAl');

    //clickonthefirstrecordtoopenit,toensurethatthe'switch_view'
    //assertionisrelevant(itwon'tbeopenedasthereisnoactionmanager,
    //butwe'lllogthe'switch_view'event)
    awaittestUtils.dom.click(list.$('.o_data_cell:first'));

    //fromthispoint,no'switch_view'eventshouldbetriggered,aswe
    //interactwiththeactivitywidget
    assert.step('opendropdown');
    awaittestUtils.dom.click(list.$('.o_activity_btnspan'));//openthepopover
    awaittestUtils.dom.click(list.$('.o_mark_as_done:first'));//markthefirstactivityasdone
    awaittestUtils.dom.click(list.$('.o_activity_popover_done'));//confirm

    assert.strictEqual(list.$('.o_activity_summary').text(),'MeetFP');

    assert.verifySteps([
        '/web/dataset/search_read',
        '/mail/init_messaging',
        'switch_view',
        'opendropdown',
        'activity_format',
        'action_feedback',
        'read',
    ]);

    list.destroy();
});

QUnit.test('listactivityexceptionwidgetwithactivity',asyncfunction(assert){
    assert.expect(3);

    constcurrentUser=this.data['res.users'].records.find(user=>
        user.id===this.data.currentUserId
    );
    currentUser.activity_ids=[1];
    this.data['res.users'].records.push({
        id:13,
        message_attachment_count:3,
        display_name:"secondpartner",
        foo:"Tommy",
        message_follower_ids:[],
        message_ids:[],
        activity_ids:[2],
        activity_exception_decoration:'warning',
        activity_exception_icon:'fa-warning',
    });
    this.data['mail.activity'].records.push(
        {
            id:1,
            display_name:"Anactivity",
            date_deadline:moment().format("YYYY-MM-DD"),//now
            can_write:true,
            state:"today",
            user_id:2,
            create_uid:2,
            activity_type_id:1,
        },
        {
            id:2,
            display_name:"Anexceptionactivity",
            date_deadline:moment().format("YYYY-MM-DD"),//now
            can_write:true,
            state:"today",
            user_id:2,
            create_uid:2,
            activity_type_id:4,
        }
    );

    const{widget:list}=awaitstart({
        hasView:true,
        View:ListView,
        model:'res.users',
        data:this.data,
        arch:'<tree>'+
                '<fieldname="foo"/>'+
                '<fieldname="activity_exception_decoration"widget="activity_exception"/>'+
            '</tree>',
    });

    assert.containsN(list,'.o_data_row',2,"shouldhavetworecords");
    assert.doesNotHaveClass(list.$('.o_data_row:eq(0).o_activity_exception_celldiv'),'fa-warning',
        "thereisnoanyexceptionactivityonrecord");
    assert.hasClass(list.$('.o_data_row:eq(1).o_activity_exception_celldiv'),'fa-warning',
        "thereisanexceptiononarecord");

    list.destroy();
});

QUnit.module('FieldMany2ManyTagsEmail',{
    beforeEach(){
        beforeEach(this);

        Object.assign(this.data['res.users'].fields,{
            timmy:{string:"pokemon",type:"many2many",relation:'partner_type'},
        });
        this.data['res.users'].records.push({
            id:11,
            display_name:"firstrecord",
            timmy:[],
        });
        Object.assign(this.data,{
            partner_type:{
                fields:{
                    name:{string:"PartnerType",type:"char"},
                    email:{string:"Email",type:"char"},
                },
                records:[],
            },
        });
        this.data['partner_type'].records.push(
            {id:12,display_name:"gold",email:'coucou@petite.perruche'},
            {id:14,display_name:"silver",email:''}
        );
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.test('fieldmany2manytagsemail',function(assert){
    assert.expect(13);
    vardone=assert.async();

    constuser11=this.data['res.users'].records.find(user=>user.id===11);
    user11.timmy=[12,14];

    //themodalsneedtobeclosedbeforetheformviewrendering
    start({
        hasView:true,
        View:FormView,
        model:'res.users',
        data:this.data,
        res_id:11,
        arch:'<formstring="Partners">'+
                '<sheet>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="timmy"widget="many2many_tags_email"/>'+
                '</sheet>'+
            '</form>',
        viewOptions:{
            mode:'edit',
        },
        mockRPC:function(route,args){
            if(args.method==='read'&&args.model==='partner_type'){
                assert.step(JSON.stringify(args.args[0]));
                assert.deepEqual(args.args[1],['display_name','email'],"shouldreadtheemail");
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner_type,false,form':'<formstring="Types"><fieldname="display_name"/><fieldname="email"/></form>',
        },
    }).then(asyncfunction({widget:form}){
        //shouldreadit3times(1withtheformview,onewiththeformdialogandoneaftersave)
        assert.verifySteps(['[12,14]','[14]','[14]']);
        awaittestUtils.nextTick();
        assert.containsN(form,'.o_field_many2manytags[name="timmy"].badge.o_tag_color_0',2,
            "twotagsshouldbepresent");
        varfirstTag=form.$('.o_field_many2manytags[name="timmy"].badge.o_tag_color_0').first();
        assert.strictEqual(firstTag.find('.o_badge_text').text(),"gold",
            "tagshouldonlyshowdisplay_name");
        assert.hasAttrValue(firstTag.find('.o_badge_text'),'title',"coucou@petite.perruche",
            "tagshouldshowemailaddressonmousehover");
        form.destroy();
        done();
    });
    testUtils.nextTick().then(function(){
        assert.strictEqual($('.modal-body.o_act_window').length,1,
            "thereshouldbeonemodalopenedtoedittheemptyemail");
        assert.strictEqual($('.modal-body.o_act_windowinput[name="display_name"]').val(),"silver",
            "theopenedmodalshouldbeaformviewdialogwiththepartner_type14");
        assert.strictEqual($('.modal-body.o_act_windowinput[name="email"]').length,1,
            "thereshouldbeanemailfieldinthemodal");

        //settheemailandsavethemodal(willrendertheformview)
        testUtils.fields.editInput($('.modal-body.o_act_windowinput[name="email"]'),'coucou@petite.perruche');
        testUtils.dom.click($('.modal-footer.btn-primary'));
    });

});

QUnit.test('fieldmany2manytagsemail(edition)',asyncfunction(assert){
    assert.expect(15);

    constuser11=this.data['res.users'].records.find(user=>user.id===11);
    user11.timmy=[12];

    var{widget:form}=awaitstart({
        hasView:true,
        View:FormView,
        model:'res.users',
        data:this.data,
        res_id:11,
        arch:'<formstring="Partners">'+
                '<sheet>'+
                    '<fieldname="display_name"/>'+
                    '<fieldname="timmy"widget="many2many_tags_email"/>'+
                '</sheet>'+
            '</form>',
        viewOptions:{
            mode:'edit',
        },
        mockRPC:function(route,args){
            if(args.method==='read'&&args.model==='partner_type'){
                assert.step(JSON.stringify(args.args[0]));
                assert.deepEqual(args.args[1],['display_name','email'],"shouldreadtheemail");
            }
            returnthis._super.apply(this,arguments);
        },
        archs:{
            'partner_type,false,form':'<formstring="Types"><fieldname="display_name"/><fieldname="email"/></form>',
        },
    });

    assert.verifySteps(['[12]']);
    assert.containsOnce(form,'.o_field_many2manytags[name="timmy"].badge.o_tag_color_0',
        "shouldcontainonetag");

    //addanotherexistingtag
    awaittestUtils.fields.many2one.clickOpenDropdown('timmy');
    awaittestUtils.fields.many2one.clickHighlightedItem('timmy');

    assert.strictEqual($('.modal-body.o_act_window').length,1,
        "thereshouldbeonemodalopenedtoedittheemptyemail");
    assert.strictEqual($('.modal-body.o_act_windowinput[name="display_name"]').val(),"silver",
        "theopenedmodalineditmodeshouldbeaformviewdialogwiththepartner_type14");
    assert.strictEqual($('.modal-body.o_act_windowinput[name="email"]').length,1,
        "thereshouldbeanemailfieldinthemodal");

    //settheemailandsavethemodal(willrerendertheformview)
    awaittestUtils.fields.editInput($('.modal-body.o_act_windowinput[name="email"]'),'coucou@petite.perruche');
    awaittestUtils.dom.click($('.modal-footer.btn-primary'));

    assert.containsN(form,'.o_field_many2manytags[name="timmy"].badge.o_tag_color_0',2,
        "shouldcontainthesecondtag");
    //shouldhaveread[14]threetimes:whenopeningthedropdown,whenopeningthemodal,and
    //afterthesave
    assert.verifySteps(['[14]','[14]','[14]']);

    form.destroy();
});

QUnit.test('many2many_tags_emailwidgetcanloadmorethan40records',asyncfunction(assert){
    assert.expect(3);

    constuser11=this.data['res.users'].records.find(user=>user.id===11);
    this.data['res.users'].fields.partner_ids={string:"Partner",type:"many2many",relation:'res.users'};
    user11.partner_ids=[];
    for(leti=100;i<200;i++){
        this.data['res.users'].records.push({id:i,display_name:`partner${i}`});
        user11.partner_ids.push(i);
    }

    const{widget:form}=awaitstart({
        hasView:true,
        View:FormView,
        model:'res.users',
        data:this.data,
        arch:'<form><fieldname="partner_ids"widget="many2many_tags"/></form>',
        res_id:11,
    });

    assert.strictEqual(form.$('.o_field_widget[name="partner_ids"].badge').length,100);

    awaittestUtils.form.clickEdit(form);

    assert.hasClass(form.$('.o_form_view'),'o_form_editable');

    //addarecordtotherelation
    awaittestUtils.fields.many2one.clickOpenDropdown('partner_ids');
    awaittestUtils.fields.many2one.clickHighlightedItem('partner_ids');

    assert.strictEqual(form.$('.o_field_widget[name="partner_ids"].badge').length,101);

    form.destroy();
});

});

});
