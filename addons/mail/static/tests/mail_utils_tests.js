flectra.define('mail.mail_utils_tests',function(require){
"usestrict";

varutils=require('mail.utils');

QUnit.module('mail',{},function(){

QUnit.module('Mailutils');

QUnit.test('add_linkutilityfunction',function(assert){
    assert.expect(19);

    vartestInputs={
        'http://admin:password@example.com:8/%2020':true,
        'https://admin:password@example.com/test':true,
        'www.example.com:8/test':true,
        'https://127.0.0.5:7073':true,
        'www.127.0.0.5':false,
        'should.notmatch':false,
        'fhttps://test.example.com/test':false,
        "https://www.transifex.com/flectra/flectra-11/translate/#fr/lunch?q=text%3A'La+Tartiflette'":true,
        'https://www.transifex.com/flectra/flectra-11/translate/#fr/$/119303430?q=text%3ATartiflette':true,
        'https://tenor.com/view/chỗgiặt-dog-smile-gif-13860250':true,
        'http://www.boîtenoire.be':true,
    };

    _.each(testInputs,function(willLinkify,content){
        varoutput=utils.parseAndTransform(content,utils.addLink);
        if(willLinkify){
            assert.strictEqual(output.indexOf('<a'),0,"Thereshouldbealink");
            assert.strictEqual(output.indexOf('</a>'),(output.length-4),"Linkshouldmatchthewholetext");
        }else{
            assert.strictEqual(output.indexOf('<a'),-1,"Thereshouldbenolink");
        }
    });
});

QUnit.test('addLink:utilityfunctionandspecialentities',function(assert){
    assert.expect(8);

    vartestInputs={
        //textContentnotunescaped
        '<p>https://example.com/?&amp;currency_id</p>':
        '<p><atarget="_blank"rel="noreferrernoopener"href="https://example.com/?&amp;currency_id">https://example.com/?&amp;currency_id</a></p>',
        //entitiesnotunescaped
        '&amp;&amp;amp;&gt;&lt;':'&amp;&amp;amp;&gt;&lt;',
        //>and"notlinkifiedsincetheyarenotinURLregex
        '<p>https://example.com/&gt;</p>':
        '<p><atarget="_blank"rel="noreferrernoopener"href="https://example.com/">https://example.com/</a>&gt;</p>',
        '<p>https://example.com/"hello"&gt;</p>':
        '<p><atarget="_blank"rel="noreferrernoopener"href="https://example.com/">https://example.com/</a>"hello"&gt;</p>',
        //&and'linkifiedsincetheyareinURLregex
        '<p>https://example.com/&amp;hello</p>':
        '<p><atarget="_blank"rel="noreferrernoopener"href="https://example.com/&amp;hello">https://example.com/&amp;hello</a></p>',
        '<p>https://example.com/\'yeah\'</p>':
        '<p><atarget="_blank"rel="noreferrernoopener"href="https://example.com/\'yeah\'">https://example.com/\'yeah\'</a></p>',
        //normalcharactershouldnotbeescaped
        ':\'(':':\'(',
        //specialcharacterinsmileysshouldbeescaped
        '&lt;3':'&lt;3',
    };

    _.each(testInputs,function(result,content){
        varoutput=utils.parseAndTransform(content,utils.addLink);
        assert.strictEqual(output,result);
    });
});

QUnit.test('addLink:linkifyinsidetextnode(1occurrence)',function(assert){
    assert.expect(5);

    constcontent='<p>sometexthttps://somelink.com</p>';
    constlinkified=utils.parseAndTransform(content,utils.addLink);
    assert.ok(
        linkified.startsWith('<p>sometext<a'),
        "linkifiedtextshouldstartwithnon-linkifiedstartpart,followedbyan'<a>'tag"
    );
    assert.ok(
        linkified.endsWith('</a></p>'),
        "linkifiedtextshouldendwithclosing'<a>'tag"
    );

    //linkifymayaddsomeattributes.Sincewedonotcareoftheirexact
    //stringifiedrepresentation,wecontinuedeeperassertionwithquery
    //selectors.
    constfragment=document.createDocumentFragment();
    constdiv=document.createElement('div');
    fragment.appendChild(div);
    div.innerHTML=linkified;
    assert.strictEqual(
        div.textContent,
        'sometexthttps://somelink.com',
        "linkifiedtextshouldhavesametextcontentasnon-linkifiedversion"
    );
    assert.strictEqual(
        div.querySelectorAll(':scopea').length,
        1,
        "linkifiedtextshouldhavean<a>tag"
    );
    assert.strictEqual(
        div.querySelector(':scopea').textContent,
        'https://somelink.com',
        "textcontentoflinkshouldbeequivalentofitsnon-linkifiedversion"
    );
});

QUnit.test('addLink:linkifyinsidetextnode(2occurrences)',function(assert){
    assert.expect(4);

    //linkifymayaddsomeattributes.Sincewedonotcareoftheirexact
    //stringifiedrepresentation,wecontinuedeeperassertionwithquery
    //selectors.
    constcontent='<p>sometexthttps://somelink.comandagainhttps://somelink2.com...</p>';
    constlinkified=utils.parseAndTransform(content,utils.addLink);
    constfragment=document.createDocumentFragment();
    constdiv=document.createElement('div');
    fragment.appendChild(div);
    div.innerHTML=linkified;
    assert.strictEqual(
        div.textContent,
        'sometexthttps://somelink.comandagainhttps://somelink2.com...',
        "linkifiedtextshouldhavesametextcontentasnon-linkifiedversion"
    );
    assert.strictEqual(
        div.querySelectorAll(':scopea').length,
        2,
        "linkifiedtextshouldhave2<a>tags"
    );
    assert.strictEqual(
        div.querySelectorAll(':scopea')[0].textContent,
        'https://somelink.com',
        "textcontentof1stlinkshouldbeequivalenttoitsnon-linkifiedversion"
    );
    assert.strictEqual(
        div.querySelectorAll(':scopea')[1].textContent,
        'https://somelink2.com',
        "textcontentof2ndlinkshouldbeequivalenttoitsnon-linkifiedversion"
    );
});

});
});
