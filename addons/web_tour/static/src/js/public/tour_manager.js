flectra.define('web_tour.public.TourManager',function(require){
'usestrict';

varTourManager=require('web_tour.TourManager');
varlazyloader=require('web.public.lazyloader');

TourManager.include({
    /**
     *@override
     */
    _waitBeforeTourStart:function(){
        returnthis._super.apply(this,arguments).then(function(){
            returnlazyloader.allScriptsLoaded;
        }).then(function(){
            returnnewPromise(function(resolve){
                setTimeout(resolve);
            });
        });
    },
});
});
