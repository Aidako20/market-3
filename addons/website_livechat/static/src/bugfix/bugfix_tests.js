flectra.define('website_livechat/static/src/bugfix/bugfix_tests.js',function(require){
'usestrict';

/**
 *ThisfileallowsintroducingnewQUnittestmoduleswithoutcontaminating
 *othertestfiles.Thisisusefulwhenbugfixingrequiresaddingnew
 *componentsforinstanceinstableversionsofFlectra.Anytestthatisdefined
 *inthisfileshouldbeisolatedinitsownfileinmaster.
 */
QUnit.module('website_livechat',{},function(){
QUnit.module('bugfix',{},function(){
QUnit.module('bugfix_tests.js',{

});
});
});

});
