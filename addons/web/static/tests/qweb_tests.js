flectra.define('web.qweb_tests',function(require){
"usestrict";

varqwebPath='/web/static/lib/qweb/';

functiontrim(s){
    returns.replace(/(^\s+|\s+$)/g,'');
}

/**
 *Loadsthetemplatefile,andexecutesallthetesttemplateina
 *qunitmodule$title
 */
functionloadTest(assert,template,context){
    vardone=assert.async();
    assert.expect(1);

    varqweb=newwindow.QWeb2.Engine();
    varprom=newPromise(function(resolve,reject){
        qweb.add_template(qwebPath+template,function(error,doc){
            if(error){
                returnreject(error);
            }
            resolve({
                qweb:qweb,
                doc:doc
            });
        });
    });

    prom.then(function(r){
        varqweb=r.qweb;
        vardoc=r.doc;
        assert.expect(doc.querySelectorAll('result').length);

        vartemplates=qweb.templates;
        for(vartemplateintemplates){
            try{
                if(!templates.hasOwnProperty(template)){
                    continue;
                }
                //ignoretemplateswhosenamestartswith_,they're
                //helpers/internal
                if(/^_/.test(template)){
                    continue;
                }

                varparams=doc.querySelector('params#'+template);
                varargs=params?JSON.parse(params.textContent):(context?_.clone(context):{});

                varresults=doc.querySelector('result#'+template);

                assert.equal(
                    trim(qweb.render(template,args)),
                    trim(results.textContent.replace(newRegExp(String.fromCharCode(13),'g'),'')),
                    template);
            }catch(error){
                assert.notOk(error.stack||error,'Renderingerror');
            }
        }
        done();
    });
    returnprom;
}

QUnit.module('QWeb',{},function(){
    QUnit.test('Output',function(assert){
        loadTest(assert,'qweb-test-output.xml');
    });
    QUnit.test('Context-setting',function(assert){
        loadTest(assert,'qweb-test-set.xml');
    });
    QUnit.test('Conditionals',function(assert){
        loadTest(assert,'qweb-test-conditionals.xml');
    });
    QUnit.test('Attributesmanipulation',function(assert){
        loadTest(assert,'qweb-test-attributes.xml');
    });
    QUnit.test('Templatecalling(tothefarawaypages)',function(assert){
        loadTest(assert,'qweb-test-call.xml',{True:true});
    });
    QUnit.test('Foreach',function(assert){
        loadTest(assert,'qweb-test-foreach.xml');
    });
    QUnit.test('Global',function(assert){
        //testusepythonsyntax
        varWORD_REPLACEMENT=window.QWeb2.WORD_REPLACEMENT;
        window.QWeb2.WORD_REPLACEMENT=_.extend({not:'!',None:'undefined'},WORD_REPLACEMENT);
        loadTest(assert,'qweb-test-global.xml',{bool:function(v){return!!v?'True':'False';}})
            .then(function(){
                window.QWeb2.WORD_REPLACEMENT=WORD_REPLACEMENT;
            },function(){
                window.QWeb2.WORD_REPLACEMENT=WORD_REPLACEMENT;
            });
    });
    QUnit.test('Templateinheritance',function(assert){
        loadTest(assert,'qweb-test-extend.xml');
    });
});
});
