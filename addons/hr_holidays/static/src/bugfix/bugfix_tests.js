flectra.define('hr_holidays/static/src/bugfix/bugfix_tests.js',function(require){
'usestrict';

/**
 *ThisfileallowsintroducingnewQUnittestmoduleswithoutcontaminating
 *othertestfiles.Thisisusefulwhenbugfixingrequiresaddingnew
 *componentsforinstanceinstableversionsofFlectra.Anytestthatisdefined
 *inthisfileshouldbeisolatedinitsownfileinmaster.
 */
QUnit.module('hr_holidays',{},function(){
QUnit.module('bugfix',{},function(){
QUnit.module('bugfix_tests.js',{

});
});
});

});

//FIXMEmovemeinhr_holidays/static/src/components/thread_view/thread_view_tests.js
flectra.define('hr_holidays/static/src/components/thread_view/thread_view_tests.js',function(require){
'usestrict';

constcomponents={
    ThreadView:require('mail/static/src/components/thread_view/thread_view.js'),
};
const{
    afterEach,
    beforeEach,
    createRootComponent,
    start,
}=require('mail/static/src/utils/test_utils.js');

QUnit.module('hr_holidays',{},function(){
QUnit.module('components',{},function(){
QUnit.module('thread_view',{},function(){
QUnit.module('thread_view_tests.js',{
    beforeEach(){
        beforeEach(this);

        /**
         *@param{mail.thread_view}threadView
         *@param{Object}[otherProps={}]
         */
        this.createThreadViewComponent=async(threadView,otherProps={})=>{
            consttarget=this.widget.el;
            constprops=Object.assign({threadViewLocalId:threadView.localId},otherProps);
            awaitcreateRootComponent(this,components.ThreadView,{props,target});
        };

        this.start=asyncparams=>{
            const{afterEvent,env,widget}=awaitstart(Object.assign({},params,{
                data:this.data,
            }));
            this.afterEvent=afterEvent;
            this.env=env;
            this.widget=widget;
        };
    },
    afterEach(){
        afterEach(this);
    },
});

QUnit.test('outofofficemessageondirectchatwithoutofofficepartner',asyncfunction(assert){
    assert.expect(2);

    //Returningdateoftheoutofofficepartner,simulateshe'llbebackinamonth
    constreturningDate=moment.utc().add(1,'month');
    //Neededpartner&usertoallowsimulationofmessagereception
    this.data['res.partner'].records.push({
        id:11,
        name:"Foreignerpartner",
        out_of_office_date_end:returningDate.format("YYYY-MM-DDHH:mm:ss"),
    });
    this.data['mail.channel'].records=[{
        channel_type:'chat',
        id:20,
        members:[this.data.currentPartnerId,11],
    }];
    awaitthis.start();
    constthread=this.env.models['mail.thread'].findFromIdentifyingData({
        id:20,
        model:'mail.channel'
    });
    constthreadViewer=this.env.models['mail.thread_viewer'].create({
        hasThreadView:true,
        thread:[['link',thread]],
    });
    awaitthis.createThreadViewComponent(threadViewer.threadView,{hasComposer:true});
    assert.containsOnce(
        document.body,
        '.o_ThreadView_outOfOffice',
        "shouldhaveanoutofofficealertonthreadview"
    );
    constformattedDate=returningDate.toDate().toLocaleDateString(
        this.env.messaging.locale.language.replace(/_/g,'-'),
        {day:'numeric',month:'short'}
    );
    assert.ok(
        document.querySelector('.o_ThreadView_outOfOffice').textContent.includes(formattedDate),
        "outofofficemessageshouldmentionthereturningdate"
    );
});

});
});
});

});
