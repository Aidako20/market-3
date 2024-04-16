flectra.define('hr/static/src/bugfix/bugfix_tests.js',function(require){
'usestrict';

/**
 *ThisfileallowsintroducingnewQUnittestmoduleswithoutcontaminating
 *othertestfiles.Thisisusefulwhenbugfixingrequiresaddingnew
 *componentsforinstanceinstableversionsofFlectra.Anytestthatisdefined
 *inthisfileshouldbeisolatedinitsownfileinmaster.
 */
QUnit.module('hr',{},function(){
QUnit.module('bugfix',{},function(){
QUnit.module('bugfix_tests.js',{

});
});
});

});
