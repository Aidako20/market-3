flectra.define('web.sessionStorage',function(require){
'usestrict';

varRamStorage=require('web.RamStorage');
varmixins=require('web.mixins');

//useafakesessionStorageinRAMifthenativesessionStorageisunavailable
//(e.g.privatebrowsinginSafari)
varstorage;
varsessionStorage=window.sessionStorage;
try{
    varuid=newDate();
    sessionStorage.setItem(uid,uid);
    sessionStorage.removeItem(uid);

    /*
     *Wecreateanintermediateobjectinordertotriggeredthestorageon
     *thisobject.thesessionStorage.Thissimplifiestestingandusageas
     *staragesarecommutableinserviceswithoutchange.Also,objects
     *thatusestoragedonothavetoknowthateventsgothroughwindow,
     *it'snotuptothemtohandlethesecases.
     */
    storage=(function(){
        varstorage=Object.create(_.extend({
                getItem:sessionStorage.getItem.bind(sessionStorage),
                setItem:sessionStorage.setItem.bind(sessionStorage),
                removeItem:sessionStorage.removeItem.bind(sessionStorage),
                clear:sessionStorage.clear.bind(sessionStorage),
            },
            mixins.EventDispatcherMixin
        ));
        storage.init();
        $(window).on('storage',function(e){
            varkey=e.originalEvent.key;
            varnewValue=e.originalEvent.newValue;
            try{
                JSON.parse(newValue);
                if(sessionStorage.getItem(key)===newValue){
                    storage.trigger('storage',{
                        key:key,
                        newValue:newValue,
                    });
                }
            }catch(error){}
        });
        returnstorage;
    })();

}catch(exception){
    console.warn('FailtoloadsessionStorage');
    storage=newRamStorage();
}

returnstorage;

});
