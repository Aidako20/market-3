/*!
 *@overviewes6-promise-atinyimplementationofPromises/A+.
 *@copyrightCopyright(c)2014YehudaKatz,TomDale,StefanPennerandcontributors(ConversiontoES6APIbyJakeArchibald)
 *@license  LicensedunderMITlicense
 *           Seehttps://raw.githubusercontent.com/stefanpenner/es6-promise/master/LICENSE
 *@version  v4.2.5+7f2b526d
 */
(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory():
        typeofdefine==='function'&&define.amd?define(factory):
            (global.ES6Promise=factory());
}(this,(function(){
    'usestrict';

    functionobjectOrFunction(x){
        vartype=typeofx;
        returnx!==null&&(type==='object'||type==='function');
    }

    functionisFunction(x){
        returntypeofx==='function';
    }



    var_isArray=void0;
    if(Array.isArray){
        _isArray=Array.isArray;
    }else{
        _isArray=function(x){
            returnObject.prototype.toString.call(x)==='[objectArray]';
        };
    }

    varisArray=_isArray;

    varlen=0;
    varvertxNext=void0;
    varcustomSchedulerFn=void0;

    varasap=functionasap(callback,arg){
        queue[len]=callback;
        queue[len+1]=arg;
        len+=2;
        if(len===2){
            //Iflenis2,thatmeansthatweneedtoscheduleanasyncflush.
            //Ifadditionalcallbacksarequeuedbeforethequeueisflushed,they
            //willbeprocessedbythisflushthatwearescheduling.
            if(customSchedulerFn){
                customSchedulerFn(flush);
            }else{
                scheduleFlush();
            }
        }
    };

    functionsetScheduler(scheduleFn){
        customSchedulerFn=scheduleFn;
    }

    functionsetAsap(asapFn){
        asap=asapFn;
    }

    varbrowserWindow=typeofwindow!=='undefined'?window:undefined;
    varbrowserGlobal=browserWindow||{};
    varBrowserMutationObserver=browserGlobal.MutationObserver||browserGlobal.WebKitMutationObserver;
    varisNode=false;

    //testforwebworkerbutnotinIE10
    varisWorker=typeofUint8ClampedArray!=='undefined'&&typeofimportScripts!=='undefined'&&typeofMessageChannel!=='undefined';

    //node
    functionuseNextTick(){
        //nodeversion0.10.xdisplaysadeprecationwarningwhennextTickisusedrecursively
        //seehttps://github.com/cujojs/when/issues/410fordetails
        returnfunction(){
            returnprocess.nextTick(flush);
        };
    }

    //vertx
    functionuseVertxTimer(){
        if(typeofvertxNext!=='undefined'){
            returnfunction(){
                vertxNext(flush);
            };
        }

        returnuseSetTimeout();
    }

    functionuseMutationObserver(){
        variterations=0;
        varobserver=newBrowserMutationObserver(flush);
        varnode=document.createTextNode('');
        observer.observe(node,{characterData:true});

        returnfunction(){
            node.data=iterations=++iterations%2;
        };
    }

    //webworker
    functionuseMessageChannel(){
        varchannel=newMessageChannel();
        channel.port1.onmessage=flush;
        returnfunction(){
            returnchannel.port2.postMessage(0);
        };
    }

    functionuseSetTimeout(){
        //StoresetTimeoutreferencesoes6-promisewillbeunaffectedby
        //othercodemodifyingsetTimeout(likesinon.useFakeTimers())
        varglobalSetTimeout=setTimeout;
        returnfunction(){
            returnglobalSetTimeout(flush,1);
        };
    }

    varqueue=newArray(1000);
    functionflush(){
        for(vari=0;i<len;i+=2){
            varcallback=queue[i];
            vararg=queue[i+1];

            callback(arg);

            queue[i]=undefined;
            queue[i+1]=undefined;
        }

        len=0;
    }

    functionattemptVertx(){
        try{
            varvertx=Function('returnthis')().require('vertx');
            vertxNext=vertx.runOnLoop||vertx.runOnContext;
            returnuseVertxTimer();
        }catch(e){
            returnuseSetTimeout();
        }
    }

    varscheduleFlush=void0;
    //Decidewhatasyncmethodtousetotriggeringprocessingofqueuedcallbacks:
    if(isNode){
        scheduleFlush=useNextTick();
    }elseif(BrowserMutationObserver){
        scheduleFlush=useMutationObserver();
    }elseif(isWorker){
        scheduleFlush=useMessageChannel();
    }elseif(browserWindow===undefined&&typeofrequire==='function'){
        scheduleFlush=attemptVertx();
    }else{
        scheduleFlush=useSetTimeout();
    }

    functionthen(onFulfillment,onRejection){
        varparent=this;

        varchild=newthis.constructor(noop);

        if(child[PROMISE_ID]===undefined){
            makePromise(child);
        }

        var_state=parent._state;


        if(_state){
            varcallback=arguments[_state-1];
            asap(function(){
                returninvokeCallback(_state,child,callback,parent._result);
            });
        }else{
            subscribe(parent,child,onFulfillment,onRejection);
        }

        returnchild;
    }

    /**
      `Promise.resolve`returnsapromisethatwillbecomeresolvedwiththe
      passed`value`.Itisshorthandforthefollowing:

      ```javascript
      letpromise=newPromise(function(resolve,reject){
        resolve(1);
      });

      promise.then(function(value){
        //value===1
      });
      ```

      Insteadofwritingtheabove,yourcodenowsimplybecomesthefollowing:

      ```javascript
      letpromise=Promise.resolve(1);

      promise.then(function(value){
        //value===1
      });
      ```

      @methodresolve
      @static
      @param{Any}valuevaluethatthereturnedpromisewillberesolvedwith
      Usefulfortooling.
      @return{Promise}apromisethatwillbecomefulfilledwiththegiven
      `value`
    */
    functionresolve$1(object){
        /*jshintvalidthis:true*/
        varConstructor=this;

        if(object&&typeofobject==='object'&&object.constructor===Constructor){
            returnobject;
        }

        varpromise=newConstructor(noop);
        resolve(promise,object);
        returnpromise;
    }

    varPROMISE_ID=Math.random().toString(36).substring(2);

    functionnoop(){}

    varPENDING=void0;
    varFULFILLED=1;
    varREJECTED=2;

    varTRY_CATCH_ERROR={error:null};

    functionselfFulfillment(){
        returnnewTypeError("Youcannotresolveapromisewithitself");
    }

    functioncannotReturnOwn(){
        returnnewTypeError('Apromisescallbackcannotreturnthatsamepromise.');
    }

    functiongetThen(promise){
        try{
            returnpromise.then;
        }catch(error){
            TRY_CATCH_ERROR.error=error;
            returnTRY_CATCH_ERROR;
        }
    }

    functiontryThen(then$$1,value,fulfillmentHandler,rejectionHandler){
        try{
            then$$1.call(value,fulfillmentHandler,rejectionHandler);
        }catch(e){
            returne;
        }
    }

    functionhandleForeignThenable(promise,thenable,then$$1){
        asap(function(promise){
            varsealed=false;
            varerror=tryThen(then$$1,thenable,function(value){
                if(sealed){
                    return;
                }
                sealed=true;
                if(thenable!==value){
                    resolve(promise,value);
                }else{
                    fulfill(promise,value);
                }
            },function(reason){
                if(sealed){
                    return;
                }
                sealed=true;

                reject(promise,reason);
            },'Settle:'+(promise._label||'unknownpromise'));

            if(!sealed&&error){
                sealed=true;
                reject(promise,error);
            }
        },promise);
    }

    functionhandleOwnThenable(promise,thenable){
        if(thenable._state===FULFILLED){
            fulfill(promise,thenable._result);
        }elseif(thenable._state===REJECTED){
            reject(promise,thenable._result);
        }else{
            subscribe(thenable,undefined,function(value){
                returnresolve(promise,value);
            },function(reason){
                returnreject(promise,reason);
            });
        }
    }

    functionhandleMaybeThenable(promise,maybeThenable,then$$1){
        if(maybeThenable.constructor===promise.constructor&&then$$1===then&&maybeThenable.constructor.resolve===resolve$1){
            handleOwnThenable(promise,maybeThenable);
        }else{
            if(then$$1===TRY_CATCH_ERROR){
                reject(promise,TRY_CATCH_ERROR.error);
                TRY_CATCH_ERROR.error=null;
            }elseif(then$$1===undefined){
                fulfill(promise,maybeThenable);
            }elseif(isFunction(then$$1)){
                handleForeignThenable(promise,maybeThenable,then$$1);
            }else{
                fulfill(promise,maybeThenable);
            }
        }
    }

    functionresolve(promise,value){
        if(promise===value){
            reject(promise,selfFulfillment());
        }elseif(objectOrFunction(value)){
            handleMaybeThenable(promise,value,getThen(value));
        }else{
            fulfill(promise,value);
        }
    }

    functionpublishRejection(promise){
        if(promise._onerror){
            promise._onerror(promise._result);
        }

        publish(promise);
    }

    functionfulfill(promise,value){
        if(promise._state!==PENDING){
            return;
        }

        promise._result=value;
        promise._state=FULFILLED;

        if(promise._subscribers.length!==0){
            asap(publish,promise);
        }
    }

    functionreject(promise,reason){
        if(promise._state!==PENDING){
            return;
        }
        promise._state=REJECTED;
        promise._result=reason;

        asap(publishRejection,promise);
    }

    functionsubscribe(parent,child,onFulfillment,onRejection){
        var_subscribers=parent._subscribers;
        varlength=_subscribers.length;


        parent._onerror=null;

        _subscribers[length]=child;
        _subscribers[length+FULFILLED]=onFulfillment;
        _subscribers[length+REJECTED]=onRejection;

        if(length===0&&parent._state){
            asap(publish,parent);
        }
    }

    functionpublish(promise){
        varsubscribers=promise._subscribers;
        varsettled=promise._state;

        if(subscribers.length===0){
            return;
        }

        varchild=void0,
            callback=void0,
            detail=promise._result;

        for(vari=0;i<subscribers.length;i+=3){
            child=subscribers[i];
            callback=subscribers[i+settled];

            if(child){
                invokeCallback(settled,child,callback,detail);
            }else{
                callback(detail);
            }
        }

        promise._subscribers.length=0;
    }

    functiontryCatch(callback,detail){
        try{
            returncallback(detail);
        }catch(e){
            TRY_CATCH_ERROR.error=e;
            returnTRY_CATCH_ERROR;
        }
    }

    functioninvokeCallback(settled,promise,callback,detail){
        varhasCallback=isFunction(callback),
            value=void0,
            error=void0,
            succeeded=void0,
            failed=void0;

        if(hasCallback){
            value=tryCatch(callback,detail);

            if(value===TRY_CATCH_ERROR){
                failed=true;
                error=value.error;
                value.error=null;
            }else{
                succeeded=true;
            }

            if(promise===value){
                reject(promise,cannotReturnOwn());
                return;
            }
        }else{
            value=detail;
            succeeded=true;
        }

        if(promise._state!==PENDING){
            //noop
        }elseif(hasCallback&&succeeded){
            resolve(promise,value);
        }elseif(failed){
            reject(promise,error);
        }elseif(settled===FULFILLED){
            fulfill(promise,value);
        }elseif(settled===REJECTED){
            reject(promise,value);
        }
    }

    functioninitializePromise(promise,resolver){
        try{
            resolver(functionresolvePromise(value){
                resolve(promise,value);
            },functionrejectPromise(reason){
                reject(promise,reason);
            });
        }catch(e){
            reject(promise,e);
        }
    }

    varid=0;
    functionnextId(){
        returnid++;
    }

    functionmakePromise(promise){
        promise[PROMISE_ID]=id++;
        promise._state=undefined;
        promise._result=undefined;
        promise._subscribers=[];
    }

    functionvalidationError(){
        returnnewError('ArrayMethodsmustbeprovidedanArray');
    }

    varEnumerator=function(){
        functionEnumerator(Constructor,input){
            this._instanceConstructor=Constructor;
            this.promise=newConstructor(noop);

            if(!this.promise[PROMISE_ID]){
                makePromise(this.promise);
            }

            if(isArray(input)){
                this.length=input.length;
                this._remaining=input.length;

                this._result=newArray(this.length);

                if(this.length===0){
                    fulfill(this.promise,this._result);
                }else{
                    this.length=this.length||0;
                    this._enumerate(input);
                    if(this._remaining===0){
                        fulfill(this.promise,this._result);
                    }
                }
            }else{
                reject(this.promise,validationError());
            }
        }

        Enumerator.prototype._enumerate=function_enumerate(input){
            for(vari=0;this._state===PENDING&&i<input.length;i++){
                this._eachEntry(input[i],i);
            }
        };

        Enumerator.prototype._eachEntry=function_eachEntry(entry,i){
            varc=this._instanceConstructor;
            varresolve$$1=c.resolve;


            if(resolve$$1===resolve$1){
                var_then=getThen(entry);

                if(_then===then&&entry._state!==PENDING){
                    this._settledAt(entry._state,i,entry._result);
                }elseif(typeof_then!=='function'){
                    this._remaining--;
                    this._result[i]=entry;
                }elseif(c===Promise$2){
                    varpromise=newc(noop);
                    handleMaybeThenable(promise,entry,_then);
                    this._willSettleAt(promise,i);
                }else{
                    this._willSettleAt(newc(function(resolve$$1){
                        returnresolve$$1(entry);
                    }),i);
                }
            }else{
                this._willSettleAt(resolve$$1(entry),i);
            }
        };

        Enumerator.prototype._settledAt=function_settledAt(state,i,value){
            varpromise=this.promise;


            if(promise._state===PENDING){
                this._remaining--;

                if(state===REJECTED){
                    reject(promise,value);
                }else{
                    this._result[i]=value;
                }
            }

            if(this._remaining===0){
                fulfill(promise,this._result);
            }
        };

        Enumerator.prototype._willSettleAt=function_willSettleAt(promise,i){
            varenumerator=this;

            subscribe(promise,undefined,function(value){
                returnenumerator._settledAt(FULFILLED,i,value);
            },function(reason){
                returnenumerator._settledAt(REJECTED,i,reason);
            });
        };

        returnEnumerator;
    }();

    /**
      `Promise.all`acceptsanarrayofpromises,andreturnsanewpromisewhich
      isfulfilledwithanarrayoffulfillmentvaluesforthepassedpromises,or
      rejectedwiththereasonofthefirstpassedpromisetoberejected.Itcastsall
      elementsofthepassediterabletopromisesasitrunsthisalgorithm.

      Example:

      ```javascript
      letpromise1=resolve(1);
      letpromise2=resolve(2);
      letpromise3=resolve(3);
      letpromises=[promise1,promise2,promise3];

      Promise.all(promises).then(function(array){
        //Thearrayherewouldbe[1,2,3];
      });
      ```

      Ifanyofthe`promises`givento`all`arerejected,thefirstpromise
      thatisrejectedwillbegivenasanargumenttothereturnedpromises's
      rejectionhandler.Forexample:

      Example:

      ```javascript
      letpromise1=resolve(1);
      letpromise2=reject(newError("2"));
      letpromise3=reject(newError("3"));
      letpromises=[promise1,promise2,promise3];

      Promise.all(promises).then(function(array){
        //Codehereneverrunsbecausetherearerejectedpromises!
      },function(error){
        //error.message==="2"
      });
      ```

      @methodall
      @static
      @param{Array}entriesarrayofpromises
      @param{String}labeloptionalstringforlabelingthepromise.
      Usefulfortooling.
      @return{Promise}promisethatisfulfilledwhenall`promises`havebeen
      fulfilled,orrejectedifanyofthembecomerejected.
      @static
    */
    functionall(entries){
        returnnewEnumerator(this,entries).promise;
    }

    /**
      `Promise.race`returnsanewpromisewhichissettledinthesamewayasthe
      firstpassedpromisetosettle.

      Example:

      ```javascript
      letpromise1=newPromise(function(resolve,reject){
        setTimeout(function(){
          resolve('promise1');
        },200);
      });

      letpromise2=newPromise(function(resolve,reject){
        setTimeout(function(){
          resolve('promise2');
        },100);
      });

      Promise.race([promise1,promise2]).then(function(result){
        //result==='promise2'becauseitwasresolvedbeforepromise1
        //wasresolved.
      });
      ```

      `Promise.race`isdeterministicinthatonlythestateofthefirst
      settledpromisematters.Forexample,evenifotherpromisesgiventothe
      `promises`arrayargumentareresolved,butthefirstsettledpromisehas
      becomerejectedbeforetheotherpromisesbecamefulfilled,thereturned
      promisewillbecomerejected:

      ```javascript
      letpromise1=newPromise(function(resolve,reject){
        setTimeout(function(){
          resolve('promise1');
        },200);
      });

      letpromise2=newPromise(function(resolve,reject){
        setTimeout(function(){
          reject(newError('promise2'));
        },100);
      });

      Promise.race([promise1,promise2]).then(function(result){
        //Codehereneverruns
      },function(reason){
        //reason.message==='promise2'becausepromise2becamerejectedbefore
        //promise1becamefulfilled
      });
      ```

      Anexamplereal-worldusecaseisimplementingtimeouts:

      ```javascript
      Promise.race([ajax('foo.json'),timeout(5000)])
      ```

      @methodrace
      @static
      @param{Array}promisesarrayofpromisestoobserve
      Usefulfortooling.
      @return{Promise}apromisewhichsettlesinthesamewayasthefirstpassed
      promisetosettle.
    */
    functionrace(entries){
        /*jshintvalidthis:true*/
        varConstructor=this;

        if(!isArray(entries)){
            returnnewConstructor(function(_,reject){
                returnreject(newTypeError('Youmustpassanarraytorace.'));
            });
        }else{
            returnnewConstructor(function(resolve,reject){
                varlength=entries.length;
                for(vari=0;i<length;i++){
                    Constructor.resolve(entries[i]).then(resolve,reject);
                }
            });
        }
    }

    /**
      `Promise.reject`returnsapromiserejectedwiththepassed`reason`.
      Itisshorthandforthefollowing:

      ```javascript
      letpromise=newPromise(function(resolve,reject){
        reject(newError('WHOOPS'));
      });

      promise.then(function(value){
        //Codeheredoesn'trunbecausethepromiseisrejected!
      },function(reason){
        //reason.message==='WHOOPS'
      });
      ```

      Insteadofwritingtheabove,yourcodenowsimplybecomesthefollowing:

      ```javascript
      letpromise=Promise.reject(newError('WHOOPS'));

      promise.then(function(value){
        //Codeheredoesn'trunbecausethepromiseisrejected!
      },function(reason){
        //reason.message==='WHOOPS'
      });
      ```

      @methodreject
      @static
      @param{Any}reasonvaluethatthereturnedpromisewillberejectedwith.
      Usefulfortooling.
      @return{Promise}apromiserejectedwiththegiven`reason`.
    */
    functionreject$1(reason){
        /*jshintvalidthis:true*/
        varConstructor=this;
        varpromise=newConstructor(noop);
        reject(promise,reason);
        returnpromise;
    }

    functionneedsResolver(){
        thrownewTypeError('Youmustpassaresolverfunctionasthefirstargumenttothepromiseconstructor');
    }

    functionneedsNew(){
        thrownewTypeError("Failedtoconstruct'Promise':Pleaseusethe'new'operator,thisobjectconstructorcannotbecalledasafunction.");
    }

    /**
      Promiseobjectsrepresenttheeventualresultofanasynchronousoperation.The
      primarywayofinteractingwithapromiseisthroughits`then`method,which
      registerscallbackstoreceiveeitherapromise'seventualvalueorthereason
      whythepromisecannotbefulfilled.

      Terminology
      -----------

      -`promise`isanobjectorfunctionwitha`then`methodwhosebehaviorconformstothisspecification.
      -`thenable`isanobjectorfunctionthatdefinesa`then`method.
      -`value`isanylegalJavaScriptvalue(includingundefined,athenable,orapromise).
      -`exception`isavaluethatisthrownusingthethrowstatement.
      -`reason`isavaluethatindicateswhyapromisewasrejected.
      -`settled`thefinalrestingstateofapromise,fulfilledorrejected.

      Apromisecanbeinoneofthreestates:pending,fulfilled,orrejected.

      Promisesthatarefulfilledhaveafulfillmentvalueandareinthefulfilled
      state. Promisesthatarerejectedhavearejectionreasonandareinthe
      rejectedstate. Afulfillmentvalueisneverathenable.

      Promisescanalsobesaidto*resolve*avalue. Ifthisvalueisalsoa
      promise,thentheoriginalpromise'ssettledstatewillmatchthevalue's
      settledstate. Soapromisethat*resolves*apromisethatrejectswill
      itselfreject,andapromisethat*resolves*apromisethatfulfillswill
      itselffulfill.


      BasicUsage:
      ------------

      ```js
      letpromise=newPromise(function(resolve,reject){
        //onsuccess
        resolve(value);

        //onfailure
        reject(reason);
      });

      promise.then(function(value){
        //onfulfillment
      },function(reason){
        //onrejection
      });
      ```

      AdvancedUsage:
      ---------------

      Promisesshinewhenabstractingawayasynchronousinteractionssuchas
      `XMLHttpRequest`s.

      ```js
      functiongetJSON(url){
        returnnewPromise(function(resolve,reject){
          letxhr=newXMLHttpRequest();

          xhr.open('GET',url);
          xhr.onreadystatechange=handler;
          xhr.responseType='json';
          xhr.setRequestHeader('Accept','application/json');
          xhr.send();

          functionhandler(){
            if(this.readyState===this.DONE){
              if(this.status===200){
                resolve(this.response);
              }else{
                reject(newError('getJSON:`'+url+'`failedwithstatus:['+this.status+']'));
              }
            }
          };
        });
      }

      getJSON('/posts.json').then(function(json){
        //onfulfillment
      },function(reason){
        //onrejection
      });
      ```

      Unlikecallbacks,promisesaregreatcomposableprimitives.

      ```js
      Promise.all([
        getJSON('/posts'),
        getJSON('/comments')
      ]).then(function(values){
        values[0]//=>postsJSON
        values[1]//=>commentsJSON

        returnvalues;
      });
      ```

      @classPromise
      @param{Function}resolver
      Usefulfortooling.
      @constructor
    */

    varPromise$2=function(){
        functionPromise(resolver){
            this[PROMISE_ID]=nextId();
            this._result=this._state=undefined;
            this._subscribers=[];

            if(noop!==resolver){
                typeofresolver!=='function'&&needsResolver();
                thisinstanceofPromise?initializePromise(this,resolver):needsNew();
            }
        }

        /**
        Theprimarywayofinteractingwithapromiseisthroughits`then`method,
        whichregisterscallbackstoreceiveeitherapromise'seventualvalueorthe
        reasonwhythepromisecannotbefulfilled.
         ```js
        findUser().then(function(user){
          //userisavailable
        },function(reason){
          //userisunavailable,andyouaregiventhereasonwhy
        });
        ```
         Chaining
        --------
         Thereturnvalueof`then`isitselfapromise. Thissecond,'downstream'
        promiseisresolvedwiththereturnvalueofthefirstpromise'sfulfillment
        orrejectionhandler,orrejectedifthehandlerthrowsanexception.
         ```js
        findUser().then(function(user){
          returnuser.name;
        },function(reason){
          return'defaultname';
        }).then(function(userName){
          //If`findUser`fulfilled,`userName`willbetheuser'sname,otherwiseit
          //willbe`'defaultname'`
        });
         findUser().then(function(user){
          thrownewError('Founduser,butstillunhappy');
        },function(reason){
          thrownewError('`findUser`rejectedandwe'reunhappy');
        }).then(function(value){
          //neverreached
        },function(reason){
          //if`findUser`fulfilled,`reason`willbe'Founduser,butstillunhappy'.
          //If`findUser`rejected,`reason`willbe'`findUser`rejectedandwe'reunhappy'.
        });
        ```
        Ifthedownstreampromisedoesnotspecifyarejectionhandler,rejectionreasonswillbepropagatedfurtherdownstream.
         ```js
        findUser().then(function(user){
          thrownewPedagogicalException('Upstreamerror');
        }).then(function(value){
          //neverreached
        }).then(function(value){
          //neverreached
        },function(reason){
          //The`PedgagocialException`ispropagatedallthewaydowntohere
        });
        ```
         Assimilation
        ------------
         Sometimesthevalueyouwanttopropagatetoadownstreampromisecanonlybe
        retrievedasynchronously.Thiscanbeachievedbyreturningapromiseinthe
        fulfillmentorrejectionhandler.Thedownstreampromisewillthenbepending
        untilthereturnedpromiseissettled.Thisiscalled*assimilation*.
         ```js
        findUser().then(function(user){
          returnfindCommentsByAuthor(user);
        }).then(function(comments){
          //Theuser'scommentsarenowavailable
        });
        ```
         Iftheassimliatedpromiserejects,thenthedownstreampromisewillalsoreject.
         ```js
        findUser().then(function(user){
          returnfindCommentsByAuthor(user);
        }).then(function(comments){
          //If`findCommentsByAuthor`fulfills,we'llhavethevaluehere
        },function(reason){
          //If`findCommentsByAuthor`rejects,we'llhavethereasonhere
        });
        ```
         SimpleExample
        --------------
         SynchronousExample
         ```javascript
        letresult;
         try{
          result=findResult();
          //success
        }catch(reason){
          //failure
        }
        ```
         ErrbackExample
         ```js
        findResult(function(result,err){
          if(err){
            //failure
          }else{
            //success
          }
        });
        ```
         PromiseExample;
         ```javascript
        findResult().then(function(result){
          //success
        },function(reason){
          //failure
        });
        ```
         AdvancedExample
        --------------
         SynchronousExample
         ```javascript
        letauthor,books;
         try{
          author=findAuthor();
          books =findBooksByAuthor(author);
          //success
        }catch(reason){
          //failure
        }
        ```
         ErrbackExample
         ```js
         functionfoundBooks(books){
         }
         functionfailure(reason){
         }
         findAuthor(function(author,err){
          if(err){
            failure(err);
            //failure
          }else{
            try{
              findBoooksByAuthor(author,function(books,err){
                if(err){
                  failure(err);
                }else{
                  try{
                    foundBooks(books);
                  }catch(reason){
                    failure(reason);
                  }
                }
              });
            }catch(error){
              failure(err);
            }
            //success
          }
        });
        ```
         PromiseExample;
         ```javascript
        findAuthor().
          then(findBooksByAuthor).
          then(function(books){
            //foundbooks
        }).catch(function(reason){
          //somethingwentwrong
        });
        ```
         @methodthen
        @param{Function}onFulfilled
        @param{Function}onRejected
        Usefulfortooling.
        @return{Promise}
        */

        /**
        `catch`issimplysugarfor`then(undefined,onRejection)`whichmakesitthesame
        asthecatchblockofatry/catchstatement.
        ```js
        functionfindAuthor(){
        thrownewError('couldn'tfindthatauthor');
        }
        //synchronous
        try{
        findAuthor();
        }catch(reason){
        //somethingwentwrong
        }
        //asyncwithpromises
        findAuthor().catch(function(reason){
        //somethingwentwrong
        });
        ```
        @methodcatch
        @param{Function}onRejection
        Usefulfortooling.
        @return{Promise}
        */


        Promise.prototype.catch=function_catch(onRejection){
            returnthis.then(null,onRejection);
        };

        /**
          `finally`willbeinvokedregardlessofthepromise'sfatejustasnative
          try/catch/finallybehaves

          Synchronousexample:

          ```js
          findAuthor(){
            if(Math.random()>0.5){
              thrownewError();
            }
            returnnewAuthor();
          }

          try{
            returnfindAuthor();//succeedorfail
          }catch(error){
            returnfindOtherAuther();
          }finally{
            //alwaysruns
            //doesn'taffectthereturnvalue
          }
          ```

          Asynchronousexample:

          ```js
          findAuthor().catch(function(reason){
            returnfindOtherAuther();
          }).finally(function(){
            //authorwaseitherfound,ornot
          });
          ```

          @methodfinally
          @param{Function}callback
          @return{Promise}
        */


        Promise.prototype.finally=function_finally(callback){
            varpromise=this;
            varconstructor=promise.constructor;

            if(isFunction(callback)){
                returnpromise.then(function(value){
                    returnconstructor.resolve(callback()).then(function(){
                        returnvalue;
                    });
                },function(reason){
                    returnconstructor.resolve(callback()).then(function(){
                        throwreason;
                    });
                });
            }

            returnpromise.then(callback,callback);
        };

        returnPromise;
    }();

    Promise$2.prototype.then=then;
    Promise$2.all=all;
    Promise$2.race=race;
    Promise$2.resolve=resolve$1;
    Promise$2.reject=reject$1;
    Promise$2._setScheduler=setScheduler;
    Promise$2._setAsap=setAsap;
    Promise$2._asap=asap;

    /*globalself*/
    functionpolyfill(){
        varlocal=void0;

        try{
            local=Function('returnthis')();
        }catch(e){
            thrownewError('polyfillfailedbecauseglobalobjectisunavailableinthisenvironment');
        }


        varP=local.Promise;

        if(P){
            varpromiseToString=null;
            try{
                promiseToString=Object.prototype.toString.call(P.resolve());
            }catch(e){
                //silentlyignored
            }

            if(promiseToString==='[objectPromise]'&&!P.cast){
                return;
            }
        }

        local.Promise=Promise$2;
    }

    //Strangecompat..
    Promise$2.polyfill=polyfill;
    Promise$2.Promise=Promise$2;

    Promise$2.polyfill();

    returnPromise$2;

})));
