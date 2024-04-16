flectra.define('web.dom_tests',function(require){
"usestrict";

vardom=require('web.dom');
vartestUtils=require('web.test_utils');

/**
 *Createanautoresizetextareawith'border-box'asboxsizingrule.
 *Theminimumheightofthisautoresizetextareis1px.
 *
 *@param{Object}[options={}]
 *@param{integer}[options.borderBottomWidth=0]
 *@param{integer}[options.borderTopWidth=0]
 *@param{integer}[options.padding=0]
 */
functionprepareAutoresizeTextArea(options){
    options=options||{};
    var$textarea=$('<textarea>');
    $textarea.css('box-sizing','border-box');
    $textarea.css({
        padding:options.padding||0,
        borderTopWidth:options.borderTopWidth||0,
        borderBottomWidth:options.borderBottomWidth||0,
    });
    $textarea.appendTo($('#qunit-fixture'));
    dom.autoresize($textarea,{min_height:1});
    return$textarea;
}

QUnit.module('core',{},function(){
QUnit.module('dom',{},function(){

    QUnit.module('autoresize',{
        afterEach:function(){
            $('#qunit-fixture').find('textarea').remove();
        },
    });

    QUnit.test('autoresize(border-box):nopadding+noborder',function(assert){
        assert.expect(3);
        var$textarea=prepareAutoresizeTextArea();
        assert.strictEqual($('textarea').length,2,
            "thereshouldbetwotextareasintheDOM");

        $textarea=$('textarea:eq(0)');
        var$fixedTextarea=$('textarea:eq(1)');
        assert.strictEqual($textarea.css('height'),
            $fixedTextarea[0].scrollHeight+'px',
            "autoresizedtextareashouldhaveheightoffixedtextarea+padding(0line)");

        testUtils.fields.editInput($textarea,'a\nb\nc\nd');
        assert.strictEqual($textarea.css('height'),
            $fixedTextarea[0].scrollHeight+'px',
            "autoresizedtextareashouldhaveheightoffixedtextarea+padding(4lines)");
    });

    QUnit.test('autoresize(border-box):padding+noborder',function(assert){
        assert.expect(3);
        var$textarea=prepareAutoresizeTextArea({padding:10});
        assert.strictEqual($('textarea').length,2,
            "thereshouldbetwotextareasintheDOM");

        $textarea=$('textarea:eq(0)');
        var$fixedTextarea=$('textarea:eq(1)');
        //twicethepaddingof10px
        varexpectedTextAreaHeight=$fixedTextarea[0].scrollHeight+2*10;
        assert.strictEqual($textarea.css('height'),
            expectedTextAreaHeight+'px',
            "autoresizedtextareashouldhaveheightoffixedtextarea+padding(0line)");

        testUtils.fields.editInput($textarea,'a\nb\nc\nd');
        //twicethepaddingof10px
        expectedTextAreaHeight=$fixedTextarea[0].scrollHeight+2*10;
        assert.strictEqual($textarea.css('height'),
            expectedTextAreaHeight+'px',
            "autoresizedtextareashouldhaveheightoffixedtextarea+padding(4lines)");
    });

    QUnit.test('autoresize(border-box):nopadding+border',function(assert){
        assert.expect(3);
        var$textarea=prepareAutoresizeTextArea({
            borderTopWidth:2,
            borderBottomWidth:3,
        });
        assert.strictEqual($('textarea').length,2,
            "thereshouldbetwotextareasintheDOM");

        $textarea=$('textarea:eq(0)');
        var$fixedTextarea=$('textarea:eq(1)');
        //top(2px)+bottom(3px)borders
        varexpectedTextAreaHeight=$fixedTextarea[0].scrollHeight+(2+3);
        assert.strictEqual($textarea.css('height'),
            expectedTextAreaHeight+'px',
            "autoresizedtextareashouldhaveheightoffixedtextarea+border(0line)");

        testUtils.fields.editInput($textarea,'a\nb\nc\nd');
        //top(2px)+bottom(3px)borders
        expectedTextAreaHeight=$fixedTextarea[0].scrollHeight+(2+3);
        assert.strictEqual($textarea.css('height'),
            expectedTextAreaHeight+'px',
            "autoresizedtextareashouldhaveheightoffixedtextarea+border(4lines)");
    });

    QUnit.test('autoresize(border-box):padding+border',function(assert){
        assert.expect(3);
        var$textarea=prepareAutoresizeTextArea({
            padding:10,
            borderTopWidth:2,
            borderBottomWidth:3,
        });
        assert.strictEqual($('textarea').length,2,
            "thereshouldbetwotextareasintheDOM");

        $textarea=$('textarea:eq(0)');
        var$fixedTextarea=$('textarea:eq(1)');
        //twicepadding(10px)+top(2px)+bottom(3px)borders
        varexpectedTextAreaHeight=$fixedTextarea[0].scrollHeight+(2*10+2+3);
        assert.strictEqual($textarea.css('height'),
            expectedTextAreaHeight+'px',
            "autoresizedtextareashouldhaveheightoffixedtextarea+border(0line)");

        testUtils.fields.editInput($textarea,'a\nb\nc\nd');
        //twicepadding(10px)+top(2px)+bottom(3px)borders
        expectedTextAreaHeight=$fixedTextarea[0].scrollHeight+(2*10+2+3);
        assert.strictEqual($textarea.css('height'),
            expectedTextAreaHeight+'px',
            "autoresizedtextareashouldhaveheightoffixedtextarea+border(4lines)");
    });

});

});
});
