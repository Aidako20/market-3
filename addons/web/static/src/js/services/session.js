flectra.define('web.session',function(require){
"usestrict";

varSession=require('web.Session');
varmodules=flectra._modules;

varsession=newSession(undefined,undefined,{modules:modules,use_cors:false});
session.is_bound=session.session_bind();

returnsession;

});
