(function(){
    /**reimportdeprecated$.browser,removemewhenjquery.ba-bqqisdropped*/
    $.uaMatch=function(ua){
        varua=ua.toLowerCase();

        varmatch=/(chrome)[\/]([\w.]+)/.exec(ua)||
            /(webkit)[\/]([\w.]+)/.exec(ua)||
            /(opera)(?:.*version|)[\/]([\w.]+)/.exec(ua)||
            /(msie)([\w.]+)/.exec(ua)||
            ua.indexOf("compatible")<0&&/(mozilla)(?:.*?rv:([\w.]+)|)/.exec(ua)||
            [];

        return{
            browser:match[1]||"",
            version:match[2]||"0"
        };
    };
    //Don'tclobberanyexistingjQuery.browserincaseit'sdifferent
    if(!$.browser){
        varmatched=$.uaMatch(navigator.userAgent);
        varbrowser={};

        if(matched.browser){
            browser[matched.browser]=true;
            browser.version=matched.version;
        }

        //ChromeisWebkit,butWebkitisalsoSafari.
        if(browser.chrome){
            browser.webkit=true;
        }elseif(browser.webkit){
            browser.safari=true;
        }

        $.browser=browser;
    }
})();
