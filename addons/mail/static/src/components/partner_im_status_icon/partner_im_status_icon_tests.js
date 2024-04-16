flectra.define('mail/static/src/components/partner_im_status_icon/partner_im_status_icon_tests.js',function(require){
'usestrict';

constcomponents={
    PartnerImStatusIcon:require('mail/static/src/components/partner_im_status_icon/partner_im_status_icon.js'),
};
const{
    afterEach,
    afterNextRender,
    beforeEach,
    createRootComponent,
    start,
}=require('mail/static/src/utils/test_utils.js');

QUnit.module('mail',{},function(){
QUnit.module('components',{},function(){
QUnit.module('partner_im_status_icon',{},function(){
QUnit.module('partner_im_status_icon_tests.js',{
    beforeEach(){
        beforeEach(this);

        this.createPartnerImStatusIcon=asyncpartner=>{
            awaitcreateRootComponent(this,components.PartnerImStatusIcon,{
                props:{partnerLocalId:partner.localId},
                target:this.widget.el
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

QUnit.test('initiallyonline',asyncfunction(assert){
    assert.expect(3);

    awaitthis.start();
    constpartner=this.env.models['mail.partner'].create({
        id:7,
        name:"DemoUser",
        im_status:'online',
    });
    awaitthis.createPartnerImStatusIcon(partner);
    assert.strictEqual(
        document.querySelectorAll(`.o_PartnerImStatusIcon`).length,
        1,
        "shouldhavepartnerIMstatusicon"
    );
    assert.strictEqual(
        document.querySelector(`.o_PartnerImStatusIcon`).dataset.partnerLocalId,
        partner.localId,
        "partnerIMstatusiconshouldbelinkedtopartnerwithID7"
    );
    assert.strictEqual(
        document.querySelectorAll(`.o_PartnerImStatusIcon.o-online`).length,
        1,
        "partnerIMstatusiconshouldhaveonlinestatusrendering"
    );
});

QUnit.test('initiallyoffline',asyncfunction(assert){
    assert.expect(1);

    awaitthis.start();
    constpartner=this.env.models['mail.partner'].create({
        id:7,
        name:"DemoUser",
        im_status:'offline',
    });
    awaitthis.createPartnerImStatusIcon(partner);
    assert.strictEqual(
        document.querySelectorAll(`.o_PartnerImStatusIcon.o-offline`).length,
        1,
        "partnerIMstatusiconshouldhaveofflinestatusrendering"
    );
});

QUnit.test('initiallyaway',asyncfunction(assert){
    assert.expect(1);

    awaitthis.start();
    constpartner=this.env.models['mail.partner'].create({
        id:7,
        name:"DemoUser",
        im_status:'away',
    });
    awaitthis.createPartnerImStatusIcon(partner);
    assert.strictEqual(
        document.querySelectorAll(`.o_PartnerImStatusIcon.o-away`).length,
        1,
        "partnerIMstatusiconshouldhaveawaystatusrendering"
    );
});

QUnit.test('changeicononchangepartnerim_status',asyncfunction(assert){
    assert.expect(4);

    awaitthis.start();
    constpartner=this.env.models['mail.partner'].create({
        id:7,
        name:"DemoUser",
        im_status:'online',
    });
    awaitthis.createPartnerImStatusIcon(partner);
    assert.strictEqual(
        document.querySelectorAll(`.o_PartnerImStatusIcon.o-online`).length,
        1,
        "partnerIMstatusiconshouldhaveonlinestatusrendering"
    );

    awaitafterNextRender(()=>partner.update({im_status:'offline'}));
    assert.strictEqual(
        document.querySelectorAll(`.o_PartnerImStatusIcon.o-offline`).length,
        1,
        "partnerIMstatusiconshouldhaveofflinestatusrendering"
    );

    awaitafterNextRender(()=>partner.update({im_status:'away'}));
    assert.strictEqual(
        document.querySelectorAll(`.o_PartnerImStatusIcon.o-away`).length,
        1,
        "partnerIMstatusiconshouldhaveawaystatusrendering"
    );

    awaitafterNextRender(()=>partner.update({im_status:'online'}));
    assert.strictEqual(
        document.querySelectorAll(`.o_PartnerImStatusIcon.o-online`).length,
        1,
        "partnerIMstatusiconshouldhaveonlinestatusrenderingintheend"
    );
});

});
});
});

});
