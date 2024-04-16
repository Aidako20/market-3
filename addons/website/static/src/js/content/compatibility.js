flectra.define('website.content.compatibility',function(require){
'usestrict';

/**
 *Tweaksthewebsiterenderingsothattheoldbrowserscorrectlyrenderthe
 *contenttoo.
 */

require('web.dom_ready');

//Checkthebrowseranditsversionandaddtheinfoasanattributeofthe
//HTMLelementsothatcssselectorscanmatchit
varbrowser=_.findKey($.browser,function(v){returnv===true;});
if($.browser.mozilla&&+$.browser.version.replace(/^([0-9]+\.[0-9]+).*/,'\$1')<20){
    browser='msie';
}
browser+=(','+$.browser.version);
varmobileRegex=/android|webos|iphone|ipad|ipod|blackberry|iemobile|operamini/i;
if(mobileRegex.test(window.navigator.userAgent.toLowerCase())){
    browser+=',mobile';
}
document.documentElement.setAttribute('data-browser',browser);

//CheckifflexissupportedandaddtheinfoasanattributeoftheHTML
//elementsothatcssselectorscanmatchit(onlyifnotsupported)
varhtmlStyle=document.documentElement.style;
varisFlexSupported=(('flexWrap'inhtmlStyle)
                    ||('WebkitFlexWrap'inhtmlStyle)
                    ||('msFlexWrap'inhtmlStyle));
if(!isFlexSupported){
    document.documentElement.setAttribute('data-no-flex','');
}

return{
    browser:browser,
    isFlexSupported:isFlexSupported,
};
});
