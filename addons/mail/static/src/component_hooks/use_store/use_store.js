flectra.define('mail/static/src/component_hooks/use_store/use_store.js',function(require){
'usestrict';

/**
 *Similartoowl.hooks.useStorebuttodecideifanewrenderhastobedoneit
 *comparesthekeysontheresult,withanoptionallevelofdepthforeach
 *key,givenasoptions`compareDepth`.
 *
 *Itassumesthattheresultoftheselectorisalwaysanobject(orarray).
 *
 *@param{function}selectorfunctionpassedasselectoroforiginal`useStore`
 *  with1stparameterextendedasstorestate.@seeowl.hooks.useStore
 *@param{object}[options={}]@seeowl.hooks.useStore
 *@param{number|object}[options.compareDepth=0]thecomparisondepth,either
 * asnumber(appliestoallkeys)orasanobject(depthforspecifickeys)
 *@returns{Proxy}@seeowl.hooks.useStore
 */
functionuseStore(selector,options={}){
    conststore=options.store||owl.Component.current.env.store;
    consthashFn=store.observer.revNumber.bind(store.observer);
    constisEqual=options.isEqual||((a,b)=>a===b);

    /**
     *Returnsafunctioncomparingwhethertwovaluesarethesame,whichisjust
     *calling`isEqual`onprimitivevaluesandobjects,butwhichalsoworksfor
     *OwlProxyinatemporalway:thecurrentresultofhashFniscomparedtothe
     *previousresultofhashFn(fromthelasttimethefunctionwascalled).
     *
     *ItmeansthatwhenthisfunctionisgivenProxythefirstcallwillalways
     *returnfalse,andconsecutivecallswillnotleadtothesameresult:
     *itreturnstruethefirsttimeafterachangehappendedinsidetheProxy,and
     *thenalwaysreturnsfalseuntilanewchangeismade.
     *
     *@returns{function}functiontakingtwoarguments,andcomparingthemas
     * explainedabove.
     */
    functionproxyComparator(){
        /**
         *Itisimportanttolocallysavetheold`revNumber`ofeachresulting
         *valuebecausewhenthe"old"and"new"valuesarethesameproxyitis
         *impossibletocomparethembasedontheircurrentvalue(sinceitwas
         *updatedin"both"duetothefactitisaproxyinthefirstplace).
         *
         *Andifthevaluesarenotproxy,`revNumber`willbe0andthe`isEqual`
         *willbeusedtocomparethem.
         */
        letoldRevNumber;

        functioncompare(a,b){
            letok=true;
            constnewRevNumber=hashFn(b);
            if(a===b&&newRevNumber>0){
                ok=oldRevNumber===newRevNumber;
            }else{
                ok=isEqual(a,b);
            }
            oldRevNumber=newRevNumber;
            returnok;
        }

        returncompare;
    }

    /**
     *@seeproxyComparator,butinsteadofcomparingthegivenvalues,itcompares
     *theirrespectivekeys,with`compareDepth`levelofdepth.
     *0=comparekey,1=alsocomparesubkeys,...
     *
     *Thisassumesthegivenvaluesareobjectsorarrays.
     *
     *@param{number|object}compareDepththecomparisondepth,eitherasnumber
     * (appliestoallkeys)orasanobject(depthforspecifickeys)
     *@returns{function}
     */
    functionproxyComparatorDeep(compareDepth=0){
        constcomparator=proxyComparator();
        constcomparators={};

        functioncompare(a,b){
            //Ifaandbare(thesame)proxy,itisalreadymanagingthedepth
            //byitself,andasimplecomparatorcanbeused.
            if(a===b&&hashFn(b)>0){
                returncomparator(a,b);
            }
            letok=true;
            constnewKeys=Object.keys(b);
            if(!a||(Object.keys(a).length!==newKeys.length)){
                ok=false;
            }
            for(constkeyofnewKeys){
                //thedepthcanbegiveneitherasanumber(forallkeys)oras
                //anobject(foreachkey)
                letdepth;
                if(typeofcompareDepth==='number'){
                    depth=compareDepth;
                }else{
                    depth=compareDepth[key]||0;
                }
                if(!(keyincomparators)){
                    if(depth>0){
                        comparators[key]=proxyComparatorDeep(depth-1);
                    }else{
                        comparators[key]=proxyComparator();
                    }
                }
                //Itisimportanttonotbreaktooearly,thecomparatorhasto
                //becalledforeverykeytoremembertheircurrentstates.
                if(!comparators[key](a?a[key]:a,b[key])){
                    ok=false;
                }
            }
            returnok;
        }

        returncompare;
    }

    constextendedSelector=(state,props)=>selector(props);
    returnowl.hooks.useStore(extendedSelector,Object.assign({},options,{
        isEqual:proxyComparatorDeep(options.compareDepth),
    }));
}

returnuseStore;

});
