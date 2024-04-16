flectra.define('web.concurrency',function(require){
"usestrict";

/**
 *ConcurrencyUtils
 *
 *Thisfilecontainsashortcollectionofusefulhelpersdesignedtohelpwith
 *everythingconcurrencyrelatedinFlectra.
 *
 *ThebasicconcurrencyprimitivesinFlectraJSarethecallback,andthe
 *promises. Promises(promise)aremorecomposable,soweusuallyusethem
 *wheneverpossible. WeusethejQueryimplementation.
 *
 *Thosefunctionsarereallynothingspecial,butaresimplytheresultofhow
 *wesolvedsomeconcurrencyissues,whenwenoticedthatapatternemerged.
 */

varClass=require('web.Class');

return{
    /**
     *Returnsapromiseresolvedafter'wait'milliseconds
     *
     *@param{int}[wait=0]thedelayinms
     *@return{Promise}
     */
    delay:function(wait){
        returnnewPromise(function(resolve){
            setTimeout(resolve,wait);
        });
    },
    /**
     *TheDropMisorderedabstractionisusefulforsituationswhereyouhave
     *asequenceofoperationsthatyouwanttodo,butifoneofthem
     *completesafterasubsequentoperation,thenitsresultisobsoleteand
     *shouldbeignored.
     *
     *NotethatisiskindofsimilartotheDropPreviousabstraction,but
     *subtlydifferent. TheDropMisorderedoperationswillallresolvesif
     *theycompleteinthecorrectorder.
     */
    DropMisordered:Class.extend({
        /**
         *@constructor
         *
         *@param{boolean}[failMisordered=false]whethermis-orderedresponses
         *  shouldbefailedorjustignored
         */
        init:function(failMisordered){
            //localsequencenumber,forrequestssent
            this.lsn=0;
            //remotesequencenumber,seqnumoflastreceivedrequest
            this.rsn=-1;
            this.failMisordered=failMisordered||false;
        },
        /**
         *Addsapromise(usuallyanasyncrequest)tothesequencer
         *
         *@param{Promise}promisetoensureadd
         *@returns{Promise}
         */
        add:function(promise){
            varself=this;
            varseq=this.lsn++;
            varres=newPromise(function(resolve,reject){
                promise.then(function(result){
                    if(seq>self.rsn){
                        self.rsn=seq;
                        resolve(result);
                    }elseif(self.failMisordered){
                        reject();
                    }
                }).guardedCatch(function(result){
                    reject(result);
                });
            });
            returnres;
        },
    }),
    /**
     *TheDropPreviousabstractionisusefulwhenyouhaveasequenceof
     *operationsthatyouwanttoexecute,butyouonlycareoftheresultof
     *thelastoperation.
     *
     *Forexample,letussaythatwehavea_fetchmethodonawidgetwhich
     *fetchesdata. Wewanttorerenderthewidgetafter. Wecoulddothis::
     *
     *     this._fetch().then(function(result){
     *         self.state=result;
     *         self.render();
     *     });
     *
     *Now,wehaveatleasttwoproblems:
     *
     *-ifthiscodeiscalledtwiceandthesecond_fetchcompletesbeforethe
     *  first,theendstatewillbetheresultofthefirst_fetch,whichis
     *  notwhatweexpect
     *-inanycases,theuserinterfacewillrerendertwice,whichisbad.
     *
     *Now,ifwehaveaDropPrevious::
     *
     *     this.dropPrevious=newDropPrevious();
     *
     *Thenwecanwrapthe_fetchinaDropPreviousandhavetheexpected
     *result::
     *
     *     this.dropPrevious
     *         .add(this._fetch())
     *         .then(function(result){
     *             self.state=result;
     *             self.render();
     *         });
     */
    DropPrevious:Class.extend({
        /**
         *Registersanewpromiseandrejectsthepreviousone
         *
         *@param{Promise}promisethenewpromise
         *@returns{Promise}
         */
        add:function(promise){
            if(this.currentDef){
                this.currentDef.reject();
            }
            varrejection;
            varres=newPromise(function(resolve,reject){
                rejection=reject;
                promise.then(resolve).catch(function(reason){
                    reject(reason);
                });
            });

            this.currentDef=res;
            this.currentDef.reject=rejection;
            returnres;
        }
    }),
    /**
     *A(Flectra)mutexisaprimitiveforserializingcomputations. Thisis
     *usefultoavoidasituationwheretwocomputationsmodifysomeshared
     *stateandcausesomecorruptedstate.
     *
     *Imaginethatwehaveafunctiontofetchsomedata_load(),whichreturns
     *apromisewhichresolvestosomethinguseful.Now,wehavesomecode
     *lookinglikethis::
     *
     *     returnthis._load().then(function(result){
     *         this.state=result;
     *     });
     *
     *Ifthiscodeisruntwice,butthesecondexecutionendsbeforethe
     *first,thenthefinalstatewillbetheresultofthefirstcallto
     *_load. However,ifwehaveamutex::
     *
     *     this.mutex=newMutex();
     *
     *andifwewrapthecallsto_loadinamutex::
     *
     *     returnthis.mutex.exec(function(){
     *         returnthis._load().then(function(result){
     *             this.state=result;
     *         });
     *     });
     *
     *Then,itisguaranteedthatthefinalstatewillbetheresultofthe
     *secondexecution.
     *
     *AMutexhastobeaclass,andnotafunction,becausewehavetokeep
     *trackofsomeinternalstate.
     */
    Mutex:Class.extend({
        init:function(){
            this.lock=Promise.resolve();
            this.queueSize=0;
            this.unlockedProm=undefined;
            this._unlock=undefined;
        },
        /**
         *Addacomputationtothequeue,itwillbeexecutedassoonasthe
         *previouscomputationsarecompleted.
         *
         *@param{function}actionafunctionwhichmayreturnaPromise
         *@returns{Promise}
         */
        exec:function(action){
            varself=this;
            varcurrentLock=this.lock;
            varresult;
            this.queueSize++;
            this.unlockedProm=this.unlockedProm||newPromise(function(resolve){
                self._unlock=resolve;
            });
            this.lock=newPromise(function(unlockCurrent){
                currentLock.then(function(){
                    result=action();
                    varalways=function(returnedResult){
                        unlockCurrent();
                        self.queueSize--;
                        if(self.queueSize===0){
                            self.unlockedProm=undefined;
                            self._unlock();
                        }
                        returnreturnedResult;
                    };
                    Promise.resolve(result).then(always).guardedCatch(always);
                });
            });
            returnthis.lock.then(function(){
                returnresult;
            });
        },
        /**
         *@returns{Promise}resolvedassoonastheMutexisunlocked
         *  (directlyifitiscurrentlyidle)
         */
        getUnlockedDef:function(){
            returnthis.unlockedProm||Promise.resolve();
        },
    }),
    /**
     *AMutexedDropPreviousisaprimitiveforserializingcomputationswhile
     *skippingtheonesthatwhereexecutedbetweenacurrentoneandbefore
     *theexecutionofanewone.ThisisusefultoavoiduselessRPCs.
     *
     *YoucanreadtheMutexdescriptiontounderstanditsrole;forthe
     *DropPreviouspartofthisabstraction,imaginethefollowingsituation:
     *youhaveacodethatcalltheserverwithafixedargumentandalistof
     *operationsthatonlygrowsaftereachcallandyouonlycareaboutthe
     *RPCresult(theservercodedoesn'tdoanything).Ifthiscodeiscalled
     *threetimes(ABC)andCisexecutedbeforeBhasstarted,it'suseless
     *tomakeanextraRPC(B)ifyouknowthatitwon'thaveanimpactandyou
     *won'tuseitsresult.
     *
     *Notethatthepromisereturnedbytheexeccallwon'tberesolvedif
     *execiscalledbeforethefirstexeccallresolution;onlythepromise
     *returnedbythelastexeccallwillberesolved(theotherarerejected);
     *
     *AMutexedDropPrevioushastobeaclass,andnotafunction,becausewe
     *havetokeeptrackofsomeinternalstate.Theexecfunctiontakesas
     *argumentanaction(andnotapromiseasDropPreviousforexample)
     *becauseit'stheMutexedDropPreviousroletotriggertheRPCcallthat
     *returnsapromisewhenit'stime.
     */
    MutexedDropPrevious:Class.extend({
        init:function(){
            this.locked=false;
            this.currentProm=null;
            this.pendingAction=null;
            this.pendingProm=null;
        },
        /**
         *@param{function}actionafunctionwhichmayreturnapromise
         *@returns{Promise}
         */
        exec:function(action){
            varself=this;
            varresolution;
            varrejection;
            if(this.locked){
                this.pendingAction=action;
                varoldPendingDef=this.pendingProm;

                this.pendingProm=newPromise(function(resolve,reject){
                    resolution=resolve;
                    rejection=reject;
                    if(oldPendingDef){
                        oldPendingDef.reject();
                    }
                    self.currentProm.reject();
                });
                this.pendingProm.resolve=resolution;
                this.pendingProm.reject=rejection;
                returnthis.pendingProm;
            }else{
                this.locked=true;
                this.currentProm=newPromise(function(resolve,reject){
                    resolution=resolve;
                    rejection=reject;
                    functionunlock(){
                        self.locked=false;
                        if(self.pendingAction){
                            varaction=self.pendingAction;
                            varprom=self.pendingProm;
                            self.pendingAction=null;
                            self.pendingProm=null;
                            self.exec(action)
                                .then(prom.resolve)
                                .guardedCatch(prom.reject);
                        }
                    }
                    Promise.resolve(action())
                        .then(function(result){
                            resolve(result);
                            unlock();
                        })
                        .guardedCatch(function(reason){
                            reject(reason);
                            unlock();
                        });
                });
                this.currentProm.resolve=resolution;
                this.currentProm.reject=rejection;
                returnthis.currentProm;
            }
        }
    }),
    /**
     *Rejectsapromiseassoonasareferencepromiseiseitherresolvedor
     *rejected
     *
     *@param{Promise}[target_def]thepromisetopotentiallyreject
     *@param{Promise}[reference_def]thereferencetarget
     *@returns{Promise}
     */
    rejectAfter:function(target_def,reference_def){
        returnnewPromise(function(resolve,reject){
            target_def.then(resolve).guardedCatch(reject);
            reference_def.then(reject).guardedCatch(reject);
        });
    }
};

});
