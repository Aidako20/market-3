flectra.define('web.ajax',function(require){
"usestrict";

varconfig=require('web.config');
varconcurrency=require('web.concurrency');
varcore=require('web.core');
vartime=require('web.time');
vardownload=require('web.download');
varcontentdisposition=require('web.contentdisposition');

var_t=core._t;

//Createthefinalobjectcontainingallthefunctionsfirsttoallowmonkey
//patchingthemcorrectlyifeverneeded.
varajax={};

function_genericJsonRpc(fct_name,params,settings,fct){
    varshadow=settings.shadow||false;
    deletesettings.shadow;
    if(!shadow){
        core.bus.trigger('rpc_request');
    }

    vardata={
        jsonrpc:"2.0",
        method:fct_name,
        params:params,
        id:Math.floor(Math.random()*1000*1000*1000)
    };
    varxhr=fct(data);
    varresult=xhr.then(function(result){
        core.bus.trigger('rpc:result',data,result);
        if(result.error!==undefined){
            if(result.error.data.arguments[0]!=="bus.Busnotavailableintestmode"){
                console.debug(
                    "Serverapplicationerror\n",
                    "Errorcode:",result.error.code,"\n",
                    "Errormessage:",result.error.message,"\n",
                    "Errordatamessage:\n",result.error.data.message,"\n",
                    "Errordatadebug:\n",result.error.data.debug
                );
            }
            returnPromise.reject({type:"server",error:result.error});
        }else{
            returnresult.result;
        }
    },function(){
        //console.error("JsonRPCcommunicationerror",_.toArray(arguments));
        varreason={
            type:'communication',
            error:arguments[0],
            textStatus:arguments[1],
            errorThrown:arguments[2],
        };
        returnPromise.reject(reason);
    });

    varrejection;
    varpromise=newPromise(function(resolve,reject){
        rejection=reject;

        result.then(function(result){
            if(!shadow){
                core.bus.trigger('rpc_response');
            }
            resolve(result);
        },function(reason){
            vartype=reason.type;
            varerror=reason.error;
            vartextStatus=reason.textStatus;
            varerrorThrown=reason.errorThrown;
            if(type==="server"){
                if(!shadow){
                    core.bus.trigger('rpc_response');
                }
                if(error.code===100){
                    core.bus.trigger('invalidate_session');
                }
                reject({message:error,event:$.Event()});
            }else{
                if(!shadow){
                    core.bus.trigger('rpc_response_failed');
                }
                varnerror={
                    code:-32098,
                    message:"XmlHttpRequestError"+errorThrown,
                    data:{
                        type:"xhr"+textStatus,
                        debug:error.responseText,
                        objects:[error,errorThrown],
                        arguments:[reason||textStatus]
                    },
                };
                reject({message:nerror,event:$.Event()});
            }
        });
    });

    //FIXME:jsonp?
    promise.abort=function(){
        rejection({
            message:"XmlHttpRequestErrorabort",
            event:$.Event('abort')
        });

        if(!shadow){
            core.bus.trigger('rpc_response');
        }

        if(xhr.abort){
            xhr.abort();
        }
    };
    promise.guardedCatch(function(reason){//Allowpromiseusertodisablerpc_errorcallincaseoffailure
        setTimeout(function(){
            //wewanttoexecutethishandlerafterallothers(hence
            //setTimeout)tolettheotherhandlerspreventtheevent
            if(!reason.event.isDefaultPrevented()){
                core.bus.trigger('rpc_error',reason.message,reason.event);
            }
        },0);
    });
    returnpromise;
};

functionjsonRpc(url,fct_name,params,settings){
    settings=settings||{};
    return_genericJsonRpc(fct_name,params,settings,function(data){
        return$.ajax(url,_.extend({},settings,{
            url:url,
            dataType:'json',
            type:'POST',
            data:JSON.stringify(data,time.date_to_utc),
            contentType:'application/json'
        }));
    });
}

//helperfunctiontomakearpcwithafunctionnamehardcodedto'call'
functionrpc(url,params,settings){
    returnjsonRpc(url,'call',params,settings);
}


/**
 *Loadcssasynchronously:fetchitfromtheurlparameterandaddalinktag
 *to<head>.
 *Iftheurlhasalreadybeenrequestedandloaded,thepromisewillresolve
 *immediately.
 *
 *@param{String}urlofthecsstobefetched
 *@returns{Promise}resolvedwhenthecsshasbeenloaded.
 */
varloadCSS=(function(){
    varurlDefs={};

    returnfunctionloadCSS(url){
        if(urlinurlDefs){
            //nothingtodohere
        }elseif($('link[href="'+url+'"]').length){
            //thelinkisalreadyintheDOM,thepromisecanberesolved
            urlDefs[url]=Promise.resolve();
        }else{
            var$link=$('<link>',{
                'href':url,
                'rel':'stylesheet',
                'type':'text/css'
            });
            urlDefs[url]=newPromise(function(resolve,reject){
                $link.on('load',function(){
                    resolve();
                }).on('error',function(){
                    reject(newError("Couldn'tloadcssdependency:"+$link[0].href));
                });
            });
            $('head').append($link);
        }
        returnurlDefs[url];
    };
})();

varloadJS=(function(){
    vardependenciesPromise={};

    varload=functionloadJS(url){
        //ChecktheDOMtoseeifascriptwiththespecifiedurlisalreadythere
        varalreadyRequired=($('script[src="'+url+'"]').length>0);

        //IfloadJSwasalreadycalledwiththesameURL,itwillhavearegisteredpromiseindicatingif
        //thescripthasbeenfullyloaded.Ifnot,thepromisehastobeinitialized.
        //ThisisinitializedasalreadyresolvedifthescriptwasalreadytherewithouttheneedofloadJS.
        if(urlindependenciesPromise){
            returndependenciesPromise[url];
        }
        varscriptLoadedPromise=newPromise(function(resolve,reject){
            if(alreadyRequired){
                resolve();
            }else{
                //Getthescriptassociatedpromiseandreturnsitafterinitializingthescriptifneeded.The
                //promiseismarkedtoberesolvedonscriptloadandrejectedonscripterror.
                varscript=document.createElement('script');
                script.type='text/javascript';
                script.src=url;
                script.onload=script.onreadystatechange=function(){
                    if((script.readyState&&script.readyState!=="loaded"&&script.readyState!=="complete")||script.onload_done){
                        return;
                    }
                    script.onload_done=true;
                    resolve(url);
                };
                script.onerror=function(){
                    console.error("Errorloadingfile",script.src);
                    reject(url);
                };
                varhead=document.head||document.getElementsByTagName('head')[0];
                head.appendChild(script);
            }
        });

        dependenciesPromise[url]=scriptLoadedPromise;
        returnscriptLoadedPromise;
    };

    returnload;
})();


/**
 *Cooperativefiledownloadimplementation,forajaxyAPIs.
 *
 *Requiresthattheserversideimplementsanhttprequestcorrectly
 *settingthe`fileToken`cookietothevalueprovidedasthe`token`
 *parameter.Thecookie*must*besetonthe`/`pathand*mustnot*be
 *`httpOnly`.
 *
 *Itwouldprobablyalsobeagoodideafortheresponsetousea
 *`Content-Disposition:attachment`header,especiallyiftheMIMEisa
 *"known"type(e.g.text/plain,orforsomebrowsersapplication/json
 *
 *@param{Object}options
 *@param{String}[options.url]usedtodynamicallycreateaform
 *@param{Object}[options.data]datatoaddtotheformsubmission.Ifcanbeusedwithoutaform,inwhichcaseaformiscreatedfromscratch.Otherwise,addedtoformdata
 *@param{HTMLFormElement}[options.form]theformtosubmitinordertofetchthefile
 *@param{Function}[options.success]callbackincaseofdownloadsuccess
 *@param{Function}[options.error]callbackincaseofrequesterror,providedwiththeerrorbody
 *@param{Function}[options.complete]calledafterboth``success``and``error``callbackshaveexecuted
 *@returns{boolean}afalsevaluemeansthatapopupwindowwasblocked.This
 *  meanthatweprobablyneedtoinformtheuserthatsomethingneedstobe
 *  changedtomakeitwork.
 */
functionget_file(options){
    varxhr=newXMLHttpRequest();

    vardata;
    if(options.form){
        xhr.open(options.form.method,options.form.action);
        data=newFormData(options.form);
    }else{
        xhr.open('POST',options.url);
        data=newFormData();
        _.each(options.data||{},function(v,k){
            data.append(k,v);
        });
    }
    data.append('token','dummy-because-api-expects-one');
    if(core.csrf_token){
        data.append('csrf_token',core.csrf_token);
    }
    //IE11wantsthisafterxhr.openoritthrows
    xhr.responseType='blob';

    //onreadystatechange[readyState=4]
    //=>onload(success)|onerror(error)|onabort
    //=>onloadend
    xhr.onload=function(){
        varmimetype=xhr.response.type;
        if(xhr.status===200&&mimetype!=='text/html'){
            //replacebecauseapparentlywesendsomeC-Dheaderswithatrailing";"
            //todo:maybealackofCD[attachment]shouldbeinterpretedasanerrorcase?
            varheader=(xhr.getResponseHeader('Content-Disposition')||'').replace(/;$/,'');
            varfilename=header?contentdisposition.parse(header).parameters.filename:null;

            download(xhr.response,filename,mimetype);
            //notsuredownloadisgoingtobesyncsothismaybecalled
            //beforethefileisactuallyfetched(?)
            if(options.success){options.success();}
            returntrue;
        }

        if(!options.error){
            returntrue;
        }
        vardecoder=newFileReader();
        decoder.onload=function(){
            varcontents=decoder.result;

            varerr;
            vardoc=newDOMParser().parseFromString(contents,'text/html');
            varnodes=doc.body.children.length===0?doc.body.childNodes:doc.body.children;
            try{//CaseofaserializedFlectraException:ItisJsonParsable
                varnode=nodes[1]||nodes[0];
                err=JSON.parse(node.textContent);
            }catch(e){//Arbitraryuncaughtpythonsideexception
                err={
                    message:nodes.length>1?nodes[1].textContent:'',
                    data:{
                        name:String(xhr.status),
                        title:nodes.length>0?nodes[0].textContent:'',
                    }
                };
            }
            options.error(err);
        };
        decoder.readAsText(xhr.response);
    };
    xhr.onerror=function(){
        if(options.error){
            options.error({
                message:_t("Somethinghappenedwhiletryingtocontacttheserver,checkthattheserverisonlineandthatyoustillhaveaworkingnetworkconnection."),
                data:{title:_t("Couldnotconnecttotheserver")}
            });
        }
    };
    if(options.complete){
        xhr.onloadend=function(){options.complete();};
    }

    xhr.send(data);
    returntrue;
}

functionpost(controller_url,data){
    varpostData=newFormData();

    $.each(data,function(i,val){
        postData.append(i,val);
    });
    if(core.csrf_token){
        postData.append('csrf_token',core.csrf_token);
    }

    returnnewPromise(function(resolve,reject){
        $.ajax(controller_url,{
            data:postData,
            processData:false,
            contentType:false,
            type:'POST'
        }).then(resolve).fail(reject);
    });
}

/**
 *LoadsanXMLfileaccordingtothegivenURLandaddsitsassociatedqweb
 *templatestothegivenqwebengine.Thefunctioncanalsobeusedtoget
 *thepromisewhichindicateswhenallthecallstothefunctionarefinished.
 *
 *Note:"allthecalls"=thecallsthathappenedbeforethecurrentno-args
 *one+thecallsthatwillhappenafterbutwhenthepreviousonesarenot
 *finishedyet.
 *
 *@param{string}[url]-anURLwheretofindqwebtemplates
 *@param{QWeb}[qweb]-theenginetowhichthetemplatesneedtobeadded
 *@returns{Promise}
 *         Ifnoargumentisgiventothefunction,thepromise'sstate
 *         indicatesif"allthecalls"arefinished(seemaindescription).
 *         Otherwise,itindicateswhenthetemplatesassociatedtothegiven
 *         urlhavebeenloaded.
 */
varloadXML=(function(){
    //Some"static"variablesassociatedtotheloadXMLfunction
    varisLoading=false;
    varloadingsData=[];
    varseenURLs=[];

    returnfunction(url,qweb){
        function_load(){
            isLoading=true;
            if(loadingsData.length){
                //Thereissomethingtoload,loadit,resolvetheassociated
                //promisethenstartloadingthenextone
                varloadingData=loadingsData[0];
                loadingData.qweb.add_template(loadingData.url,function(){
                    //Removefromarrayonlynowsothatmultiplecallsto
                    //loadXMLwiththesameURLreturnstherightpromise
                    loadingsData.shift();
                    loadingData.resolve();
                    _load();
                });
            }else{
                //Thereisnothingtoloadanymore,soresolvethe
                //"allthecalls"promise
                isLoading=false;
            }
        }

        //Ifnoargument,simplyreturnsthepromisewhichindicateswhen
        //"allthecalls"arefinished
        if(!url||!qweb){
            returnPromise.resolve();
        }

        //IfthegivenURLhasalreadybeenseen,donothingbutreturningthe
        //associatedpromise
        if(_.contains(seenURLs,url)){
            varoldLoadingData=_.findWhere(loadingsData,{url:url});
            returnoldLoadingData?oldLoadingData.def:Promise.resolve();
        }
        seenURLs.push(url);


        //Addtheinformationaboutthenewdatatoload:theurl,theqweb
        //engineandtheassociatedpromise
        varnewLoadingData={
            url:url,
            qweb:qweb,
        };
        newLoadingData.def=newPromise(function(resolve,reject){
            newLoadingData.resolve=resolve;
            newLoadingData.reject=reject;
        });
        loadingsData.push(newLoadingData);

        //Ifnotalreadystarted,starttheloadingloop(reinitializethe
        //"allthecalls"promisetoanunresolvedstate)
        if(!isLoading){
            _load();
        }

        //ReturnthepromiseassociatedtothenewgivenURL
        returnnewLoadingData.def;
    };
})();

/**
 *LoadsatemplatefileaccordingtothegivenxmlId.
 *
 *@param{string}[xmlId]-thetemplatexmlId
 *@param{Object}[context]
 *       additionnalrpccontexttobemergedwiththedefaultone
 *@param{string}[tplRoute='/web/dataset/call_kw/']
 *@returns{Deferred}resolvedwithanobject
 *         cssLibs:listofcssfiles
 *         cssContents:listofstyletagcontents
 *         jsLibs:listofJSfiles
 *         jsContents:listofscripttagcontents
 */
varloadAsset=(function(){
    varcache={};

    varload=functionloadAsset(xmlId,context,tplRoute='/web/dataset/call_kw/'){
        if(cache[xmlId]){
            returncache[xmlId];
        }
        context=_.extend({},flectra.session_info.user_context,context);
        constparams={
            args:[xmlId,{
                debug:config.isDebug()
            }],
            kwargs:{
                context:context,
            },
        };
        if(tplRoute==='/web/dataset/call_kw/'){
            Object.assign(params,{
                model:'ir.ui.view',
                method:'render_public_asset',
            });
        }
        cache[xmlId]=rpc(tplRoute,params).then(function(xml){
            var$xml=$(xml);
            return{
                cssLibs:$xml.filter('link[href]:not([type="image/x-icon"])').map(function(){
                    return$(this).attr('href');
                }).get(),
                cssContents:$xml.filter('style').map(function(){
                    return$(this).html();
                }).get(),
                jsLibs:$xml.filter('script[src]').map(function(){
                    return$(this).attr('src');
                }).get(),
                jsContents:$xml.filter('script:not([src])').map(function(){
                    return$(this).html();
                }).get(),
            };
        }).guardedCatch(reason=>{
            reason.event.preventDefault();
            throw`Unabletorendertherequiredtemplatesfortheassetstoload:${reason.message.message}`;
        });
        returncache[xmlId];
    };

    returnload;
})();

/**
 *Loadsthegivenjs/csslibrariesandassetbundles.Notethatnolibraryor
 *assetwillbeloadedifitwasalreadydonebefore.
 *
 *@param{Object}libs
 *@param{Array<string|string[]>}[libs.assetLibs=[]]
 *     Thelistofassetstoload.Eachlistitemmaybeastring(thexmlID
 *     oftheassettoload)oralistofstrings.Thefirstlevelisloaded
 *     sequentially(sousethisiftheordermatters)whiletheassetsin
 *     innerlistsareloadedinparallel(usethisforefficiencybutonly
 *     iftheorderdoesnotmatter,shouldrarelybethecaseforassets).
 *@param{string[]}[libs.cssLibs=[]]
 *     ThelistofCSSfilestoload.Theywillallbeloadedinparallelbut
 *     putintheDOMinthegivenorder(onlytheorderintheDOMisused
 *     todeterminepriorityofCSSrules,notloadedtime).
 *@param{Array<string|string[]>}[libs.jsLibs=[]]
 *     ThelistofJSfilestoload.Eachlistitemmaybeastring(theURL
 *     ofthefiletoload)oralistofstrings.Thefirstlevelisloaded
 *     sequentially(sousethisiftheordermatters)whilethefilesininner
 *     listsareloadedinparallel(usethisforefficiencybutonly
 *     iftheorderdoesnotmatter).
 *@param{string[]}[libs.cssContents=[]]
 *     ListofinlinestylestoaddafterloadingtheCSSfiles.
 *@param{string[]}[libs.jsContents=[]]
 *     ListofinlinescriptstoaddafterloadingtheJSfiles.
 *@param{Object}[context]
 *       additionnalrpccontexttobemergedwiththedefaultone
 *@param{string}[tplRoute]
 *     Customroutetousefortemplaterenderingofthepotentialassets
 *     toload(seelibs.assetLibs).
 *
 *@returns{Promise}
 */
functionloadLibs(libs,context,tplRoute){
    varmutex=newconcurrency.Mutex();
    mutex.exec(function(){
        vardefs=[];
        varcssLibs=[libs.cssLibs||[]]; //Forceloadinginparallel
        defs.push(_loadArray(cssLibs,ajax.loadCSS).then(function(){
            if(libs.cssContents&&libs.cssContents.length){
                $('head').append($('<style/>',{
                    html:libs.cssContents.join('\n'),
                }));
            }
        }));
        defs.push(_loadArray(libs.jsLibs||[],ajax.loadJS).then(function(){
            if(libs.jsContents&&libs.jsContents.length){
                $('head').append($('<script/>',{
                    html:libs.jsContents.join('\n'),
                }));
            }
        }));
        returnPromise.all(defs);
    });
    mutex.exec(function(){
        return_loadArray(libs.assetLibs||[],function(xmlID){
            returnajax.loadAsset(xmlID,context,tplRoute).then(function(asset){
                returnajax.loadLibs(asset);
            });
        });
    });

    function_loadArray(array,loadCallback){
        var_mutex=newconcurrency.Mutex();
        array.forEach(function(urlData){
            _mutex.exec(function(){
                if(typeofurlData==='string'){
                    returnloadCallback(urlData);
                }
                returnPromise.all(urlData.map(loadCallback));
            });
        });
        return_mutex.getUnlockedDef();
    }

    returnmutex.getUnlockedDef();
}

_.extend(ajax,{
    jsonRpc:jsonRpc,
    rpc:rpc,
    loadCSS:loadCSS,
    loadJS:loadJS,
    loadXML:loadXML,
    loadAsset:loadAsset,
    loadLibs:loadLibs,
    get_file:get_file,
    post:post,
});

returnajax;

});
