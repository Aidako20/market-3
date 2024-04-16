flectra.define('im_livechat/static/src/bugfix/bugfix_tests.js',function(require){
'usestrict';

/**
 *ThisfileallowsintroducingnewQUnittestmoduleswithoutcontaminating
 *othertestfiles.Thisisusefulwhenbugfixingrequiresaddingnew
 *componentsforinstanceinstableversionsofFlectra.Anytestthatisdefined
 *inthisfileshouldbeisolatedinitsownfileinmaster.
 */
QUnit.module('im_livechat',{},function(){
QUnit.module('bugfix',{},function(){
QUnit.module('bugfix_tests.js',{

});
});
});

});
