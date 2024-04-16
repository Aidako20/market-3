flectra.define('web.bus_tests',function(require){
"usestrict";

varBusService=require('bus.BusService');
varCrossTabBus=require('bus.CrossTab');
varAbstractStorageService=require('web.AbstractStorageService');
varRamStorage=require('web.RamStorage');
vartestUtils=require('web.test_utils');
varWidget=require('web.Widget');


varLocalStorageServiceMock;

BusService=BusService.extend({
    TAB_HEARTBEAT_PERIOD:10,
    MASTER_TAB_HEARTBEAT_PERIOD:1,
});


QUnit.module('Bus',{
    beforeEach:function(){
        LocalStorageServiceMock=AbstractStorageService.extend({storage:newRamStorage()});
    },
},function(){
    QUnit.test('notificationsreceivedfromthelongpollingchannel',asyncfunction(assert){
        assert.expect(6);

        varpollPromise=testUtils.makeTestPromise();

        varparent=newWidget();
        awaittestUtils.mock.addMockEnvironment(parent,{
            data:{},
            services:{
                bus_service:BusService,
                local_storage:LocalStorageServiceMock,
            },
            mockRPC:function(route,args){
                if(route==='/longpolling/poll'){
                    assert.step(route+'-'+args.channels.join(','));

                    pollPromise=testUtils.makeTestPromise();
                    pollPromise.abort=(function(){
                        this.reject({message:"XmlHttpRequestErrorabort"},$.Event());
                    }).bind(pollPromise);
                    returnpollPromise;
                }
                returnthis._super.apply(this,arguments);
            }
        });

        varwidget=newWidget(parent);
        awaitwidget.appendTo($('#qunit-fixture'));

        widget.call('bus_service','onNotification',this,function(notifications){
            assert.step('notification-'+notifications.toString());
        });
        widget.call('bus_service','addChannel','lambda');

        pollPromise.resolve([{
            id:1,
            channel:'lambda',
            message:'beta',
        }]);
        awaittestUtils.nextTick();

        pollPromise.resolve([{
            id:2,
            channel:'lambda',
            message:'epsilon',
        }]);
        awaittestUtils.nextTick();

        assert.verifySteps([
            '/longpolling/poll-lambda',
            'notification-lambda,beta',
            '/longpolling/poll-lambda',
            'notification-lambda,epsilon',
            '/longpolling/poll-lambda',
        ]);

        parent.destroy();
    });

    QUnit.test('providenotificationIDof0bydefault',asyncfunction(assert){
        //Thistestisimportantinordertoensurethatweprovidethecorrect
        //sentinelvalue0whenwearenotawareofthelastnotificationID
        //thatwehavereceived.WecannotprovideanIDof-1,otherwiseit
        //maylikelybehandledincorrectly(beforethistestwaswritten,
        //itwasproviding-1totheserver,whichinreturnsenteverystored
        //notificationsrelatedtothisuser).
        assert.expect(3);

        //SimulatenoIDoflastnotificationinthelocalstorage
        testUtils.mock.patch(LocalStorageServiceMock,{
            getItem:function(key){
                if(key==='last_ts'){
                    return0;
                }
                returnthis._super.apply(this,arguments);
            },
        });

        varpollPromise=testUtils.makeTestPromise();
        varparent=newWidget();
        awaittestUtils.mock.addMockEnvironment(parent,{
            data:{},
            services:{
                bus_service:BusService,
                local_storage:LocalStorageServiceMock,
            },
            mockRPC:function(route,args){
                if(route==='/longpolling/poll'){
                    assert.step(route);
                    assert.strictEqual(args.last,0,
                        "providedlastnotificationIDshouldbe0");

                    pollPromise=testUtils.makeTestPromise();
                    pollPromise.abort=(function(){
                        this.reject({message:"XmlHttpRequestErrorabort"},$.Event());
                    }).bind(pollPromise);
                    returnpollPromise;
                }
                returnthis._super.apply(this,arguments);
            }
        });

        varwidget=newWidget(parent);
        awaitwidget.appendTo($('#qunit-fixture'));

        //triggerlongpollingpollRPC
        widget.call('bus_service','addChannel','lambda');
        assert.verifySteps(['/longpolling/poll']);

        testUtils.mock.unpatch(LocalStorageServiceMock);
        parent.destroy();
    });

    QUnit.test('crosstabbussharemessagefromachannel',asyncfunction(assert){
        assert.expect(5);

        //master

        varpollPromiseMaster=testUtils.makeTestPromise();

        varparentMaster=newWidget();
        awaittestUtils.mock.addMockEnvironment(parentMaster,{
            data:{},
            services:{
                bus_service:BusService,
                local_storage:LocalStorageServiceMock,
            },
            mockRPC:function(route,args){
                if(route==='/longpolling/poll'){
                    assert.step('master'+'-'+route+'-'+args.channels.join(','));

                    pollPromiseMaster=testUtils.makeTestPromise();
                    pollPromiseMaster.abort=(function(){
                        this.reject({message:"XmlHttpRequestErrorabort"},$.Event());
                    }).bind(pollPromiseMaster);
                    returnpollPromiseMaster;
                }
                returnthis._super.apply(this,arguments);
            }
        });

        varmaster=newWidget(parentMaster);
        awaitmaster.appendTo($('#qunit-fixture'));

        master.call('bus_service','onNotification',master,function(notifications){
            assert.step('master-notification-'+notifications.toString());
        });
        master.call('bus_service','addChannel','lambda');

        //slave
        awaittestUtils.nextTick();
        varparentSlave=newWidget();
        awaittestUtils.mock.addMockEnvironment(parentSlave,{
            data:{},
            services:{
                bus_service:BusService,
                local_storage:LocalStorageServiceMock,
            },
            mockRPC:function(route,args){
                if(route==='/longpolling/poll'){
                    thrownewError("Cannotusethelongpollingoftheslaveclient");
                }
                returnthis._super.apply(this,arguments);
            }
        });

        varslave=newWidget(parentSlave);
        awaitslave.appendTo($('#qunit-fixture'));

        slave.call('bus_service','onNotification',slave,function(notifications){
            assert.step('slave-notification-'+notifications.toString());
        });
        slave.call('bus_service','addChannel','lambda');

        pollPromiseMaster.resolve([{
            id:1,
            channel:'lambda',
            message:'beta',
        }]);
        awaittestUtils.nextTick();

        assert.verifySteps([
            'master-/longpolling/poll-lambda',
            'master-notification-lambda,beta',
            'slave-notification-lambda,beta',
            'master-/longpolling/poll-lambda',
        ]);

        parentMaster.destroy();
        parentSlave.destroy();
    });

    QUnit.test('crosstabbuselectnewmasteronmasterunload',asyncfunction(assert){
        assert.expect(8);

        //master
        varpollPromiseMaster=testUtils.makeTestPromise();

        varparentMaster=newWidget();
        awaittestUtils.mock.addMockEnvironment(parentMaster,{
            data:{},
            services:{
                bus_service:BusService,
                local_storage:LocalStorageServiceMock,
            },
            mockRPC:function(route,args){
                if(route==='/longpolling/poll'){
                    assert.step('master-'+route+'-'+args.channels.join(','));

                    pollPromiseMaster=testUtils.makeTestPromise();
                    pollPromiseMaster.abort=(function(){
                        this.reject({message:"XmlHttpRequestErrorabort"},$.Event());
                    }).bind(pollPromiseMaster);
                    returnpollPromiseMaster;
                }
                returnthis._super.apply(this,arguments);
            }
        });

        varmaster=newWidget(parentMaster);
        awaitmaster.appendTo($('#qunit-fixture'));

        master.call('bus_service','onNotification',master,function(notifications){
            assert.step('master-notification-'+notifications.toString());
        });
        master.call('bus_service','addChannel','lambda');

        //slave
        awaittestUtils.nextTick();
        varparentSlave=newWidget();
        varpollPromiseSlave=testUtils.makeTestPromise();
        awaittestUtils.mock.addMockEnvironment(parentSlave,{
            data:{},
            services:{
                bus_service:BusService,
                local_storage:LocalStorageServiceMock,
            },
            mockRPC:function(route,args){
                if(route==='/longpolling/poll'){
                    assert.step('slave-'+route+'-'+args.channels.join(','));

                    pollPromiseSlave=testUtils.makeTestPromise();
                    pollPromiseSlave.abort=(function(){
                        this.reject({message:"XmlHttpRequestErrorabort"},$.Event());
                    }).bind(pollPromiseSlave);
                    returnpollPromiseSlave;
                }
                returnthis._super.apply(this,arguments);
            }
        });

        varslave=newWidget(parentSlave);
        awaitslave.appendTo($('#qunit-fixture'));

        slave.call('bus_service','onNotification',slave,function(notifications){
            assert.step('slave-notification-'+notifications.toString());
        });
        slave.call('bus_service','addChannel','lambda');

        pollPromiseMaster.resolve([{
            id:1,
            channel:'lambda',
            message:'beta',
        }]);
        awaittestUtils.nextTick();

        //simulateunloadingmaster
        master.call('bus_service','_onUnload');

        pollPromiseSlave.resolve([{
            id:2,
            channel:'lambda',
            message:'gamma',
        }]);
        awaittestUtils.nextTick();

        assert.verifySteps([
            'master-/longpolling/poll-lambda',
            'master-notification-lambda,beta',
            'slave-notification-lambda,beta',
            'master-/longpolling/poll-lambda',
            'slave-/longpolling/poll-lambda',
            'slave-notification-lambda,gamma',
            'slave-/longpolling/poll-lambda',
        ]);

        parentMaster.destroy();
        parentSlave.destroy();
    });

    QUnit.test('twotabscallingaddChannelsimultaneously',asyncfunction(assert){
        assert.expect(5);

        letid=1;
        testUtils.patch(CrossTabBus,{
            init:function(){
                this._super.apply(this,arguments);
                this.__tabId__=id++;
            },
            addChannel:function(channel){
                assert.step('Tab'+this.__tabId__+':addChannel'+channel);
                this._super.apply(this,arguments);
            },
            deleteChannel:function(channel){
                assert.step('Tab'+this.__tabId__+':deleteChannel'+channel);
                this._super.apply(this,arguments);
            },
        });

        letpollPromise;
        constparentTab1=newWidget();
        awaittestUtils.addMockEnvironment(parentTab1,{
            data:{},
            services:{
                local_storage:LocalStorageServiceMock,
            },
            mockRPC:function(route){
                if(route==='/longpolling/poll'){
                    pollPromise=testUtils.makeTestPromise();
                    pollPromise.abort=(function(){
                        this.reject({message:"XmlHttpRequestErrorabort"},$.Event());
                    }).bind(pollPromise);
                    returnpollPromise;
                }
                returnthis._super.apply(this,arguments);
            }
        });
        constparentTab2=newWidget();
        awaittestUtils.addMockEnvironment(parentTab2,{
            data:{},
            services:{
                local_storage:LocalStorageServiceMock,
            },
            mockRPC:function(route){
                if(route==='/longpolling/poll'){
                    pollPromise=testUtils.makeTestPromise();
                    pollPromise.abort=(function(){
                        this.reject({message:"XmlHttpRequestErrorabort"},$.Event());
                    }).bind(pollPromise);
                    returnpollPromise;
                }
                returnthis._super.apply(this,arguments);
            }
        });

        consttab1=newCrossTabBus(parentTab1);
        consttab2=newCrossTabBus(parentTab2);

        tab1.addChannel("alpha");
        tab2.addChannel("alpha");
        tab1.addChannel("beta");
        tab2.addChannel("beta");

        assert.verifySteps([
            "Tab1:addChannelalpha",
            "Tab2:addChannelalpha",
            "Tab1:addChannelbeta",
            "Tab2:addChannelbeta",
        ]);

        testUtils.unpatch(CrossTabBus);
        parentTab1.destroy();
        parentTab2.destroy();
    });
});

});
