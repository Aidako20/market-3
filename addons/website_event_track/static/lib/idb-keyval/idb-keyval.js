//    idb-keyval.js3.2.0
//    https://github.com/jakearchibald/idb-keyval
//    Copyright2016,JakeArchibald
//    LicensedundertheApacheLicense,Version2.0

varidbKeyval=(function(exports){
    'usestrict';
    
    classStore{
        constructor(dbName='keyval-store',storeName='keyval'){
            this.storeName=storeName;
            this._dbp=newPromise((resolve,reject)=>{
                constopenreq=indexedDB.open(dbName,1);
                openreq.onerror=()=>reject(openreq.error);
                openreq.onsuccess=()=>resolve(openreq.result);
                //Firsttimesetup:createanemptyobjectstore
                openreq.onupgradeneeded=()=>{
                    openreq.result.createObjectStore(storeName);
                };
            });
        }
        _withIDBStore(type,callback){
            returnthis._dbp.then(db=>newPromise((resolve,reject)=>{
                consttransaction=db.transaction(this.storeName,type);
                transaction.oncomplete=()=>resolve();
                transaction.onabort=transaction.onerror=()=>reject(transaction.error);
                callback(transaction.objectStore(this.storeName));
            }));
        }
    }
    letstore;
    functiongetDefaultStore(){
        if(!store)
            store=newStore();
        returnstore;
    }
    functionget(key,store=getDefaultStore()){
        letreq;
        returnstore._withIDBStore('readonly',store=>{
            req=store.get(key);
        }).then(()=>req.result);
    }
    functionset(key,value,store=getDefaultStore()){
        returnstore._withIDBStore('readwrite',store=>{
            store.put(value,key);
        });
    }
    functiondel(key,store=getDefaultStore()){
        returnstore._withIDBStore('readwrite',store=>{
            store.delete(key);
        });
    }
    functionclear(store=getDefaultStore()){
        returnstore._withIDBStore('readwrite',store=>{
            store.clear();
        });
    }
    functionkeys(store=getDefaultStore()){
        constkeys=[];
        returnstore._withIDBStore('readonly',store=>{
            //Thiswouldbestore.getAllKeys(),butitisn'tsupportedbyEdgeorSafari.
            //AndopenKeyCursorisn'tsupportedbySafari.
            (store.openKeyCursor||store.openCursor).call(store).onsuccess=function(){
                if(!this.result)
                    return;
                keys.push(this.result.key);
                this.result.continue();
            };
        }).then(()=>keys);
    }
    
    exports.Store=Store;
    exports.get=get;
    exports.set=set;
    exports.del=del;
    exports.clear=clear;
    exports.keys=keys;
    
    returnexports;
    
    }({}));
