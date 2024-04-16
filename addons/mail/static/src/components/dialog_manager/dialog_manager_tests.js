flectra.define('mail/static/src/components/dialog_manager/dialog_manager_tests.js',function(require){
'usestrict';

const{makeDeferred}=require('mail/static/src/utils/deferred/deferred.js');
const{
    afterEach,
    beforeEach,
    nextAnimationFrame,
    start,
}=require('mail/static/src/utils/test_utils.js');

QUnit.module('mail',{},function(){
QUnit.module('components',{},function(){
QUnit.module('dialog_manager',{},function(){
QUnit.module('dialog_manager_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.start=asyncparams=>{
            const{env,widget}=awaitstart(Object.assign(
                {hasDialog:true},
                params,
                {data:this.data}
            ));
            this.env=env;
            this.widget=widget;
        };
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.test('[technical]messagingnotcreated',asyncfunction(assert){
    /**
     *Creationofmessaginginenvisasyncduetogenerationofmodelsbeing
     *async.Generationofmodelsisasyncbecauseitrequiresparsingofall
     *JSmodulesthatcontainpiecesofmodeldefinitions.
     *
     *Timeofhavingnomessagingisveryshort,almostimperceptiblebyuser
     *onUI,butthedisplayshouldnotcrashduringthiscriticaltimeperiod.
     */
    assert.expect(2);

    constmessagingBeforeCreationDeferred=makeDeferred();
    awaitthis.start({
        messagingBeforeCreationDeferred,
        waitUntilMessagingCondition:'none',
    });
    assert.containsOnce(
        document.body,
        '.o_DialogManager',
        "shouldhavedialogmanagerevenwhenmessagingisnotyetcreated"
    );

    //simulatemessagingbeingcreated
    messagingBeforeCreationDeferred.resolve();
    awaitnextAnimationFrame();

    assert.containsOnce(
        document.body,
        '.o_DialogManager',
        "shouldstillcontaindialogmanageraftermessaginghasbeencreated"
    );
});

QUnit.test('initialmount',asyncfunction(assert){
    assert.expect(1);

    awaitthis.start();
    assert.containsOnce(
        document.body,
        '.o_DialogManager',
        "shouldhavedialogmanager"
    );
});

});
});
});

});
