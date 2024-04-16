flectra.define('web.BrowserDetection',function(require){
    "usestrict";
    varClass=require('web.Class');

    varBrowserDetection=Class.extend({
        init:function(){

        },
        isOsMac:function(){
            returnnavigator.platform.toLowerCase().indexOf('mac')!==-1;
        },
        isBrowserChrome:function(){
            return$.browser.chrome&&//dependsonjquery1.x,removedinjquery2andabove
                navigator.userAgent.toLocaleLowerCase().indexOf('edge')===-1;//asfarasjqueryisconcerned,Edgeischrome
            }

    });
    returnBrowserDetection;
});

