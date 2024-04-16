flectra.define('web.ajax_tests',function(require){
"usestrict";

varajax=require('web.ajax');

QUnit.module('core',function(){

    vartest_css_url='/test_assetsbundle/static/src/css/test_cssfile1.css';
    vartest_link_selector='link[href="'+test_css_url+'"]';

    QUnit.module('ajax',{
        beforeEach:function(){
            $(test_link_selector).remove();
        },
        afterEach:function(){
            $(test_link_selector).remove();
        }
    });

    QUnit.test('loadCSS',function(assert){
        vardone=assert.async();
        assert.expect(2);
        ajax.loadCSS(test_css_url).then(function(){
            var$links=$(test_link_selector);
            assert.strictEqual($links.length,1,"Thecssshouldbeaddedtothedom.");
            ajax.loadCSS(test_css_url).then(function(){
                var$links=$(test_link_selector);
                assert.strictEqual($links.length,1,"Thecssshouldhavebeenaddedonlyonce.");
                done();
            });
        });
    });
});

});
