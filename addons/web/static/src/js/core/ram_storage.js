flectra.define('web.RamStorage',function(require){
'usestrict';

/**
 *ThismoduledefinesanalternativeoftheStorageobjects(localStorage,
 *sessionStorage),storedinRAM.ItisusedwhenthosenativeStorageobjects
 *areunavailable(e.g.inprivatebrowsingonSafari).
 */

varClass=require('web.Class');
varmixins=require('web.mixins');


varRamStorage=Class.extend(mixins.EventDispatcherMixin,{
    /**
     *@constructor
     */
    init:function(){
        mixins.EventDispatcherMixin.init.call(this);
        if(!this.storage){
            this.clear();
        }
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Removesalldatafromthestorage
     */
    clear:function(){
        this.storage=Object.create(null);
        this.length=0;
    },
    /**
     *Returnsthevalueassociatedwithagivenkeyinthestorage
     *
     *@param{string}key
     *@returns{string}
     */
    getItem:function(key){
        returnthis.storage[key];
    },
    /**
     *@param{integer}index
     *@return{string}
     */
    key:function(index){
        return_.keys(this.storage)[index];
    },
    /**
     *Removesthegivenkeyfromthestorage
     *
     *@param{string}key
     */
    removeItem:function(key){
        if(keyinthis.storage){
            this.length--;
        }
        deletethis.storage[key];
        this.trigger('storage',{key:key,newValue:null});
    },
    /**
     *Addsagivenkey-valuepairtothestorage,orupdatethevalueofthe
     *givenkeyifitalreadyexists
     *
     *@param{string}key
     *@param{string}value
     */
    setItem:function(key,value){
        if(!(keyinthis.storage)){
            this.length++;
        }
        this.storage[key]=value;
        this.trigger('storage',{key:key,newValue:value});
    },
});

returnRamStorage;

});
