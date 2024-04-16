flectra.define('web.AbstractStorageService',function(require){
'usestrict';

/**
 *ThismoduledefinesanabstractionforservicesthatwriteintoStorage
 *objects(e.g.localStorageorsessionStorage).
 */

varAbstractService=require('web.AbstractService');

varAbstractStorageService=AbstractService.extend({
    //the'storage'attributemustbesetbyactualStorageServicesextending
    //thisabstraction
    storage:null,

    /**
     *@override
     */
    destroy:function(){
        //storagecanbepermanentortransient,destroytransientones
        if((this.storage||{}).destroy){
            this.storage.destroy();
        }
        this._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Removesalldatafromthestorage
     */
    clear:function(){
        this.storage.clear();
    },
    /**
     *Returnsthevalueassociatedwithagivenkeyinthestorage
     *
     *@param{string}key
     *@returns{string}
     */
    getItem:function(key,defaultValue){
        varval=this.storage.getItem(key);
        returnval?JSON.parse(val):defaultValue;
    },
    /**
     *@param{integer}index
     *@return{string}
     */
    key:function(index){
        returnthis.storage.key(index);
    },
    /**
     *@return{integer}
     */
    length:function(){
        returnthis.storage.length;
    },
    /**
     *Removesthegivenkeyfromthestorage
     *
     *@param{string}key
     */
    removeItem:function(key){
        this.storage.removeItem(key);
    },
    /**
     *Setsthevalueofagivenkeyinthestorage
     *
     *@param{string}key
     *@param{string}value
     */
    setItem:function(key,value){
        this.storage.setItem(key,JSON.stringify(value));
    },
    /**
     *Addanhandleronstorageevent
     *
     */
    onStorage:function(){
        this.storage.on.apply(this.storage,["storage"].concat(Array.prototype.slice.call(arguments)));
    },
});

returnAbstractStorageService;

});
