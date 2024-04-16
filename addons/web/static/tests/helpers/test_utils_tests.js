flectra.define('web.testUtilsTests',function(require){
"usestrict";

vartestUtils=require('web.test_utils');

QUnit.module('web',{},function(){
QUnit.module('testUtils',{},function(){

QUnit.module('patchdate');

QUnit.test('newdate',function(assert){
    assert.expect(5);
    constunpatchDate=testUtils.mock.patchDate(2018,9,23,14,50,0);

    constdate=newDate();

    assert.strictEqual(date.getFullYear(),2018);
    assert.strictEqual(date.getMonth(),9);
    assert.strictEqual(date.getDate(),23);
    assert.strictEqual(date.getHours(),14);
    assert.strictEqual(date.getMinutes(),50);
    unpatchDate();
});

QUnit.test('newmoment',function(assert){
    assert.expect(1);
    constunpatchDate=testUtils.mock.patchDate(2018,9,23,14,50,0);

    constm=moment();
    assert.strictEqual(m.format('YYYY-MM-DDHH:mm'),'2018-10-2314:50');
    unpatchDate();
});

});
});
});