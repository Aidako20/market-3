flectra.define('web.ajax_external',function(require){
"usestrict";

varajax=require('web.ajax');

/**
  *Thisfileshouldbeusedinthecontextofanexternalwidgetloading(e.g:livechatinanon-Flectrawebsite)
  *Itoverridesthe'loadJS'methodthatissupposedtoloadadditionalscripts,basedonarelativeURL(e.g:'/web/webclient/locale/en_US')
  *Aswe'renotinanFlectrawebsitecontext,thecallswillnotwork,andweavoida404request.
  */
ajax.loadJS=function(url){
    console.warn('Triedtoloadthefollowingscriptonanexternalwebsite:'+url);
};
});
