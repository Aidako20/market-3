flectra.define('web.RainbowMan_tests',function(require){
"usestrict";

varRainbowMan=require('web.RainbowMan');

QUnit.module('widgets',{},function(){

QUnit.module('RainbowMan',{
    beforeEach:function(){
        this.data={
            message:'Congrats!',
        };
    },
},function(){

    QUnit.test("renderingarainbowman",function(assert){
        vardone=assert.async();
        assert.expect(2);

        var$target=$("#qunit-fixture");

        //Createanddisplayrainbowman
        varrainbowman=newRainbowMan(this.data);
        rainbowman.appendTo($target).then(function(){
            var$rainbow=rainbowman.$(".o_reward_rainbow");
            assert.strictEqual($rainbow.length,1,
                "Shouldhavedisplayedrainboweffect");

            assert.ok(rainbowman.$('.o_reward_msg_content').html()==='Congrats!',
                "Cardontherainbowmanshoulddisplay'Congrats!'message");

            rainbowman.destroy();
            done();
        });

    });
});
});
});
