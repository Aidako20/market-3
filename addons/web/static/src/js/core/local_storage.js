flectra.define('web.local_storage',function(require){
'usestrict';

varRamStorage=require('web.RamStorage');
varmixins=require('web.mixins');

//useafakelocalStorageinRAMifthenativelocalStorageisunavailable
//(e.g.privatebrowsinginSafari)
varstorage;
varlocalStorage=window.localStorage;
try{
    varuid=newDate();
    localStorage.setItem(uid,uid);
    localStorage.removeItem(uid);

    /*
     *Wecreateanintermediateobjectinordertotriggeredthestorageon
     *thisobject.thelocalStorage.Thissimplifiestestingandusageas
     *staragesarecommutableinserviceswithoutchange.Also,objects
     *thatusestoragedonothavetoknowthateventsgothroughwindow,
     *it'snotuptothemtohandlethesecases.
     */
    storage=(function(){
        varstorage=Object.create(_.extend({
                getItem:localStorage.getItem.bind(localStorage),
                setItem:localStorage.setItem.bind(localStorage),
                removeItem:localStorage.removeItem.bind(localStorage),
                clear:localStorage.clear.bind(localStorage),
            },
            mixins.EventDispatcherMixin
        ));
        storage.init();
        $(window).on('storage',function(e){
            varkey=e.originalEvent.key;
            varnewValue=e.originalEvent.newValue;
            try{
                JSON.parse(newValue);
                storage.trigger('storage',{
                    key:key,
                    newValue:newValue,
                });
            }catch(error){}
        });
        returnstorage;
    })();

}catch(exception){
	console.warn('FailtoloadlocalStorage');
    storage=newRamStorage();
}

returnstorage;

});
