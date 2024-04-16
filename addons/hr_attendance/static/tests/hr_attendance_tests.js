flectra.define('hr_attendance.tests',function(require){
"usestrict";

vartestUtils=require('web.test_utils');
varcore=require('web.core');

varMyAttendances=require('hr_attendance.my_attendances');
varKioskMode=require('hr_attendance.kiosk_mode');
varGreetingMessage=require('hr_attendance.greeting_message');


QUnit.module('HRAttendance',{
    beforeEach:function(){
        this.data={
            'hr.employee':{
                fields:{
                    name:{string:'Name',type:'char'},
                    attendance_state:{
                        string:'State',
                        type:'selection',
                        selection:[['checked_in',"In"],['checked_out',"Out"]],
                        default:1,
                    },
                    user_id:{string:'userID',type:'integer'},
                    barcode:{string:'barcode',type:'integer'},
                    hours_today:{string:'Hourstoday',type:'float'},
                },
                records:[{
                    id:1,
                    name:"EmployeeA",
                    attendance_state:'checked_out',
                    user_id:1,
                    barcode:1,
                },
                {
                    id:2,
                    name:"EmployeeB",
                    attendance_state:'checked_out',
                    user_id:2,
                    barcode:2,
                }],
            },
            'res.company':{
                fields:{
                    name:{string:'Name',type:'char'},
                },
                records:[{
                    id:1,
                    name:"CompanyA",
                }],
            },
        };
    },
},function(){
    QUnit.module('Myattendances(clientaction)');

    QUnit.test('simplerendering',asyncfunction(assert){
        assert.expect(1);

        var$target=$('#qunit-fixture');
        varclientAction=newMyAttendances(null,{});
        awaittestUtils.mock.addMockEnvironment(clientAction,{
            data:this.data,
            session:{
                uid:1,
            },
        });
        awaitclientAction.appendTo($target);

        assert.strictEqual(clientAction.$('.o_hr_attendance_kiosk_modeh1').text(),'EmployeeA',
            "shouldhaverenderedtheclientactionwithoutcrashing");

        clientAction.destroy();
    });

    QUnit.test('AttendanceKioskModeTest',asyncfunction(assert){
        assert.expect(2);

        var$target=$('#qunit-fixture');
        varself=this;
        varrpcCount=0;
        varclientAction=newKioskMode(null,{});
        awaittestUtils.mock.addMockEnvironment(clientAction,{
            data:this.data,
            session:{
                uid:1,
                user_context:{
                    allowed_company_ids:[1],
                }
            },
            mockRPC:function(route,args){
                if(args.method==='attendance_scan'&&args.model==='hr.employee'){

                    rpcCount++;
                    returnPromise.resolve(self.data['hr.employee'].records[0]);
                }
                returnthis._super(route,args);
            },
        });
        awaitclientAction.appendTo($target);
        core.bus.trigger('barcode_scanned',1);
        core.bus.trigger('barcode_scanned',1);
        assert.strictEqual(rpcCount,1,'RPCcallshouldhavebeendoneonlyonce.');

        core.bus.trigger('barcode_scanned',2);
        assert.strictEqual(rpcCount,1,'RPCcallshouldhavebeendoneonlyonce.');

        clientAction.destroy();
    });

    QUnit.test('AttendanceGreetingMessageTest',asyncfunction(assert){
        assert.expect(10);

        var$target=$('#qunit-fixture');
        varself=this;
        varrpcCount=0;

        varclientActions=[];
        asyncfunctioncreateGreetingMessage(target,barcode){
            varaction={
                attendance:{
                    check_in:"2018-09-2013:41:13",
                    employee_id:[barcode],
                },
                next_action:"hr_attendance.hr_attendance_action_kiosk_mode",
                barcode:barcode,
            };
            varclientAction=newGreetingMessage(null,action);
            awaittestUtils.mock.addMockEnvironment(clientAction,{
                data:self.data,
                session:{
                    uid:1,
                    company_id:1,
                },
                mockRPC:function(route,args){
                    if(args.method==='attendance_scan'&&args.model==='hr.employee'){
                        rpcCount++;
                        action.attendance.employee_id=[args.args[0],'Employee'];
                        /*
                            ifrpchavebeenmade,anewinstanceiscreatedtosimulatethesamebehaviour
                            asfunctionalflow.
                        */
                        createGreetingMessage(target,args.args[0]);
                        returnPromise.resolve({action:action});
                    }
                    returnthis._super(route,args);
                },
            });
            awaitclientAction.appendTo(target);

            clientActions.push(clientAction);
        }

        //init-mockcomingfromkiosk
        awaitcreateGreetingMessage($target,1);
        awaittestUtils.nextMicrotaskTick();
        assert.strictEqual(clientActions.length,1,'NumberofclientActionmust=1.');

        core.bus.trigger('barcode_scanned',1);
        /*
            AsactionisgivenwheninstantiateGreetingMessage,wesimulatethatwecomefromtheKioskMode
            Sorescanningthesamebarcodewon'tleadtoanotherRPC.
        */
        assert.strictEqual(clientActions.length,1,'NumberofclientActionsmust=1.');
        assert.strictEqual(rpcCount,0,'RPCcallshouldnothavebeendone.');

        core.bus.trigger('barcode_scanned',2);
        awaittestUtils.nextTick();
        assert.strictEqual(clientActions.length,2,'NumberofclientActionsmust=2.');
        assert.strictEqual(rpcCount,1,'RPCcallshouldhavebeendoneonlyonce.');
        core.bus.trigger('barcode_scanned',2);
        awaittestUtils.nextMicrotaskTick();
        assert.strictEqual(clientActions.length,2,'NumberofclientActionsmust=2.');
        assert.strictEqual(rpcCount,1,'RPCcallshouldhavebeendoneonlyonce.');

        core.bus.trigger('barcode_scanned',1);
        awaittestUtils.nextTick();
        assert.strictEqual(clientActions.length,3,'NumberofclientActionsmust=3.');
        core.bus.trigger('barcode_scanned',1);
        awaittestUtils.nextMicrotaskTick();
        assert.strictEqual(clientActions.length,3,'NumberofclientActionsmust=3.');
        assert.strictEqual(rpcCount,2,'RPCcallshouldhavebeendoneonlytwice.');

        _.each(clientActions.reverse(),function(clientAction){
            clientAction.destroy();
        });
    });

});

});
