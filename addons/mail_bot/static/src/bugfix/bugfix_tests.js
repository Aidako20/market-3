flectra.define('mail_bot/static/src/bugfix/bugfix_tests.js',function(require){
'usestrict';

/**
 *ThisfileallowsintroducingnewQUnittestmoduleswithoutcontaminating
 *othertestfiles.Thisisusefulwhenbugfixingrequiresaddingnew
 *componentsforinstanceinstableversionsofFlectra.Anytestthatisdefined
 *inthisfileshouldbeisolatedinitsownfileinmaster.
 */
QUnit.module('mail_bot',{},function(){
QUnit.module('bugfix',{},function(){
QUnit.module('bugfix_tests.js',{

});
});
});

});
