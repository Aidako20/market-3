flectra.define('crm.form_rainbowman_tests',function(require){
    "usestrict";

    varCrmFormView=require('crm.crm_form').CrmFormView;
    varCrmKanbanView=require('crm.crm_kanban').CrmKanbanView;
    vartestUtils=require('web.test_utils');
    varcreateView=testUtils.createView;

    QUnit.module('CrmRainbowmanTriggers',{
        beforeEach:function(){
            constformat="YYYY-MM-DDHH:mm:ss";
            this.data={
                'res.users':{
                    fields:{
                        display_name:{string:'Name',type:'char'},
                    },
                    records:[
                        {id:1,name:'Mario'},
                        {id:2,name:'Luigi'},
                        {id:3,name:'Link'},
                        {id:4,name:'Zelda'},
                    ],
                },
                'crm.team':{
                    fields:{
                        display_name:{string:'Name',type:'char'},
                        member_ids:{string:'Members',type:'many2many',relation:'res.users'},
                    },
                    records:[
                        {id:1,name:'MushroomKingdom',member_ids:[1,2]},
                        {id:2,name:'Hyrule',member_ids:[3,4]},
                    ],
                },
                'crm.stage':{
                    fields:{
                        display_name:{string:'Name',type:'char'},
                        is_won:{string:'Iswon',type:'boolean'},
                    },
                    records:[
                        {id:1,name:'Start'},
                        {id:2,name:'Middle'},
                        {id:3,name:'Won',is_won:true},
                    ],
                },
                'crm.lead':{
                    fields:{
                        display_name:{string:'Name',type:'char'},
                        planned_revenue:{string:'Revenue',type:'float'},
                        stage_id:{string:'Stage',type:'many2one',relation:'crm.stage'},
                        team_id:{string:'SalesTeam',type:'many2one',relation:'crm.team'},
                        user_id:{string:'Salesperson',type:'many2one',relation:'res.users'},
                        date_closed:{string:'Dateclosed',type:'datetime'},
                    },
                    records:[
                        {id:1,name:'Lead1',planned_revenue:5.0,stage_id:1,team_id:1,user_id:1},
                        {id:2,name:'Lead2',planned_revenue:5.0,stage_id:2,team_id:2,user_id:4},
                        {id:3,name:'Lead3',planned_revenue:3.0,stage_id:3,team_id:1,user_id:1,date_closed:moment().subtract(5,'days').format(format)},
                        {id:4,name:'Lead4',planned_revenue:4.0,stage_id:3,team_id:2,user_id:4,date_closed:moment().subtract(23,'days').format(format)},
                        {id:5,name:'Lead5',planned_revenue:7.0,stage_id:3,team_id:1,user_id:1,date_closed:moment().subtract(20,'days').format(format)},
                        {id:6,name:'Lead6',planned_revenue:4.0,stage_id:2,team_id:1,user_id:2},
                        {id:7,name:'Lead7',planned_revenue:1.8,stage_id:3,team_id:2,user_id:3,date_closed:moment().subtract(23,'days').format(format)},
                        {id:8,name:'Lead8',planned_revenue:1.9,stage_id:1,team_id:2,user_id:3},
                        {id:9,name:'Lead9',planned_revenue:1.5,stage_id:3,team_id:2,user_id:3,date_closed:moment().subtract(5,'days').format(format)},
                        {id:10,name:'Lead10',planned_revenue:1.7,stage_id:2,team_id:2,user_id:3},
                        {id:11,name:'Lead11',planned_revenue:2.0,stage_id:3,team_id:2,user_id:4,date_closed:moment().subtract(5,'days').format(format)},
                    ],
                },
            };
            this.testFormView={
                arch:`
                    <formjs_class="crm_form">
                        <header><fieldname="stage_id"widget="statusbar"options="{'clickable':'1'}"/></header>
                        <fieldname="name"/>
                        <fieldname="planned_revenue"/>
                        <fieldname="team_id"/>
                        <fieldname="user_id"/>
                    </form>`,
                data:this.data,
                model:'crm.lead',
                View:CrmFormView,
            };
            this.testKanbanView={
                arch:`
                    <kanbanjs_class="crm_kanban">
                        <templates>
                            <tt-name="kanban-box">
                                <div><fieldname="name"/></div>
                            </t>
                        </templates>
                    </kanban>`,
                data:this.data,
                model:'crm.lead',
                View:CrmKanbanView,
                groupBy:['stage_id'],
            };
        },
    },function(){
        QUnit.test("firstleadwon,clickonstatusbar",asyncfunction(assert){
            assert.expect(2);

            this.testFormView.res_id=6;
            this.testFormView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constform=awaitcreateView(this.testFormView);

            awaittestUtils.dom.click(form.$(".o_statusbar_statusbutton[data-value='3']"));
            assert.verifySteps(['Go,go,go!Congratsforyourfirstdeal.']);

            form.destroy();
        });

        QUnit.test("firstleadwon,clickonstatusbarineditmodethensave",asyncfunction(assert){
            assert.expect(3);

            constform=awaitcreateView(_.extend(this.testFormView,{
                res_id:6,
                mockRPC:asyncfunction(route,args){
                    constresult=awaitthis._super(...arguments);
                    if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                        assert.step(result||"norainbowman");
                    }
                    returnresult;
                },
                viewOptions:{mode:'edit'}
            }));

            awaittestUtils.dom.click(form.$(".o_statusbar_statusbutton[data-value='3']"));
            assert.verifySteps([]);//nomessagedisplayedyet

            awaittestUtils.form.clickSave(form);
            assert.verifySteps(['Go,go,go!Congratsforyourfirstdeal.']);

            form.destroy();
        });

        QUnit.test("teamrecord30days,clickonstatusbar",asyncfunction(assert){
            assert.expect(2);

            this.testFormView.res_id=2;
            this.testFormView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constform=awaitcreateView(this.testFormView);

            awaittestUtils.dom.click(form.$(".o_statusbar_statusbutton[data-value='3']"));
            assert.verifySteps(['Boom!Teamrecordforthepast30days.']);

            form.destroy();
        });

        QUnit.test("teamrecord7days,clickonstatusbar",asyncfunction(assert){
            assert.expect(2);

            this.testFormView.res_id=1;
            this.testFormView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constform=awaitcreateView(this.testFormView);

            awaittestUtils.dom.click(form.$(".o_statusbar_statusbutton[data-value='3']"));
            assert.verifySteps(['Yeah!Dealofthelast7daysfortheteam.']);

            form.destroy();
        });

        QUnit.test("userrecord30days,clickonstatusbar",asyncfunction(assert){
            assert.expect(2);

            this.testFormView.res_id=8;
            this.testFormView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constform=awaitcreateView(this.testFormView);

            awaittestUtils.dom.click(form.$(".o_statusbar_statusbutton[data-value='3']"));
            assert.verifySteps(['Youjustbeatyourpersonalrecordforthepast30days.']);

            form.destroy();
        });

        QUnit.test("userrecord7days,clickonstatusbar",asyncfunction(assert){
            assert.expect(2);

            this.testFormView.res_id=10;
            this.testFormView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constform=awaitcreateView(this.testFormView);

            awaittestUtils.dom.click(form.$(".o_statusbar_statusbutton[data-value='3']"));
            assert.verifySteps(['Youjustbeatyourpersonalrecordforthepast7days.']);

            form.destroy();
        });

        QUnit.test("clickonstage(notwon)onstatusbar",asyncfunction(assert){
            assert.expect(2);

            this.testFormView.res_id=1;
            this.testFormView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constform=awaitcreateView(this.testFormView);

            awaittestUtils.dom.click(form.$(".o_statusbar_statusbutton[data-value='2']"));
            assert.verifySteps(['norainbowman']);

            form.destroy();
        });

        QUnit.test("firstleadwon,drag&dropkanban",asyncfunction(assert){
            assert.expect(2);

            this.testKanbanView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constkanban=awaitcreateView(this.testKanbanView);

            kanban.model.defaultGroupedBy=['stage_id'];
            awaitkanban.reload();

            awaittestUtils.dom.dragAndDrop(kanban.$('.o_kanban_record:contains("Lead6")'),kanban.$('.o_kanban_group:eq(2)'));
            assert.verifySteps(['Go,go,go!Congratsforyourfirstdeal.']);

            kanban.destroy();
        });

        QUnit.test("teamrecord30days,drag&dropkanban",asyncfunction(assert){
            assert.expect(2);

            this.testKanbanView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constkanban=awaitcreateView(this.testKanbanView);

            kanban.model.defaultGroupedBy=['stage_id'];
            awaitkanban.reload();

            awaittestUtils.dom.dragAndDrop(kanban.$('.o_kanban_record:contains("Lead2")'),kanban.$('.o_kanban_group:eq(2)'));
            assert.verifySteps(['Boom!Teamrecordforthepast30days.']);

            kanban.destroy();
        });

        QUnit.test("teamrecord7days,drag&dropkanban",asyncfunction(assert){
            assert.expect(2);

            this.testKanbanView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constkanban=awaitcreateView(this.testKanbanView);

            kanban.model.defaultGroupedBy=['stage_id'];
            awaitkanban.reload();

            awaittestUtils.dom.dragAndDrop(kanban.$('.o_kanban_group:eq(0).o_kanban_record:contains("Lead1")'),kanban.$('.o_kanban_group:eq(2)'));
            assert.verifySteps(['Yeah!Dealofthelast7daysfortheteam.']);

            kanban.destroy();
        });

        QUnit.test("userrecord30days,drag&dropkanban",asyncfunction(assert){
            assert.expect(2);

            this.testKanbanView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constkanban=awaitcreateView(this.testKanbanView);

            kanban.model.defaultGroupedBy=['stage_id'];
            awaitkanban.reload();

            awaittestUtils.dom.dragAndDrop(kanban.$('.o_kanban_record:contains("Lead8")'),kanban.$('.o_kanban_group:eq(2)'));
            assert.verifySteps(['Youjustbeatyourpersonalrecordforthepast30days.']);

            kanban.destroy();
        });

        QUnit.test("userrecord7days,drag&dropkanban",asyncfunction(assert){
            assert.expect(2);

            this.testKanbanView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constkanban=awaitcreateView(this.testKanbanView);

            kanban.model.defaultGroupedBy=['stage_id'];
            awaitkanban.reload();

            awaittestUtils.dom.dragAndDrop(kanban.$('.o_kanban_record:contains("Lead10")'),kanban.$('.o_kanban_group:eq(2)'));
            assert.verifySteps(['Youjustbeatyourpersonalrecordforthepast7days.']);

            kanban.destroy();
        });

        QUnit.test("drag&droprecordkanbaninstagenotwon",asyncfunction(assert){
            assert.expect(2);

            this.testKanbanView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            constkanban=awaitcreateView(this.testKanbanView);

            kanban.model.defaultGroupedBy=['stage_id'];
            awaitkanban.reload();

            awaittestUtils.dom.dragAndDrop(kanban.$('.o_kanban_record:contains("Lead8")'),kanban.$('.o_kanban_group:eq(1)'));
            assert.verifySteps(["norainbowman"]);

            kanban.destroy();
        });

        QUnit.test("drag&droprecordinkanbannotgroupedbystage_id",asyncfunction(assert){
            assert.expect(1);

            this.testKanbanView.mockRPC=asyncfunction(route,args){
                constresult=awaitthis._super(...arguments);
                if(args.model==='crm.lead'&&args.method==='get_rainbowman_message'){
                    assert.step(result||"norainbowman");
                }
                returnresult;
            };
            this.testKanbanView.groupBy=['user_id'];
            constkanban=awaitcreateView(this.testKanbanView);

            kanban.model.defaultGroupedBy=['stage_id'];
            awaitkanban.reload();

            awaittestUtils.dom.dragAndDrop(kanban.$('.o_kanban_group:eq(0).o_kanban_record:first'),kanban.$('.o_kanban_group:eq(1)'));
            assert.verifySteps([]);//Shouldneverpassbytherpc

            kanban.destroy();
        });
    });
});
