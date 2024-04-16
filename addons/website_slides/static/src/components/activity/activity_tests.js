flectra.define('website_slides/static/src/tests/activity_tests.js',function(require){
'usestrict';

constcomponents={
    Activity:require('mail/static/src/components/activity/activity.js'),
};

const{
    afterEach,
    beforeEach,
    createRootComponent,
    start,
}=require('mail/static/src/utils/test_utils.js');

QUnit.module('website_slides',{},function(){
QUnit.module('components',{},function(){
QUnit.module('activity',{},function(){
QUnit.module('activity_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.createActivityComponent=asyncactivity=>{
            awaitcreateRootComponent(this,components.Activity,{
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

QUnit.test('grantcourseaccess',asyncfunction(assert){
    assert.expect(8);

    awaitthis.start({
        asyncmockRPC(route,args){
            if(args.method==='action_grant_access'){
                assert.strictEqual(args.args.length,1);
                assert.strictEqual(args.args[0].length,1);
                assert.strictEqual(args.args[0][0],100);
                assert.strictEqual(args.kwargs.partner_id,5);
                assert.step('access_grant');
            }
            returnthis._super(...arguments);
        },
    });
    constactivity=this.env.models['mail.activity'].create({
        id:100,
        canWrite:true,
        thread:[['insert',{
            id:100,
            model:'slide.channel',
        }]],
        requestingPartner:[['insert',{
            id:5,
            displayName:"Pauvrepomme",
        }]],
        type:[['insert',{
            id:1,
            displayName:"AccessRequest",
        }]],
    });
    awaitthis.createActivityComponent(activity);

    assert.containsOnce(document.body,'.o_Activity',"shouldhaveactivitycomponent");
    assert.containsOnce(document.body,'.o_Activity_grantAccessButton',"shouldhavegrantaccessbutton");

    document.querySelector('.o_Activity_grantAccessButton').click();
    assert.verifySteps(['access_grant'],"Grantbuttonshouldtriggertherightrpccall");
});

QUnit.test('refusecourseaccess',asyncfunction(assert){
    assert.expect(8);

    awaitthis.start({
        asyncmockRPC(route,args){
            if(args.method==='action_refuse_access'){
                assert.strictEqual(args.args.length,1);
                assert.strictEqual(args.args[0].length,1);
                assert.strictEqual(args.args[0][0],100);
                assert.strictEqual(args.kwargs.partner_id,5);
                assert.step('access_refuse');
            }
            returnthis._super(...arguments);
        },
    });
    constactivity=this.env.models['mail.activity'].create({
        id:100,
        canWrite:true,
        thread:[['insert',{
            id:100,
            model:'slide.channel',
        }]],
        requestingPartner:[['insert',{
            id:5,
            displayName:"Pauvrepomme",
        }]],
        type:[['insert',{
            id:1,
            displayName:"AccessRequest",
        }]],
    });
    awaitthis.createActivityComponent(activity);

    assert.containsOnce(document.body,'.o_Activity',"shouldhaveactivitycomponent");
    assert.containsOnce(document.body,'.o_Activity_refuseAccessButton',"shouldhaverefuseaccessbutton");

    document.querySelector('.o_Activity_refuseAccessButton').click();
    assert.verifySteps(['access_refuse'],"refusebuttonshouldtriggertherightrpccall");
});

});
});
});

});
