flectra.define('web.Session',function(require){
"usestrict";

varajax=require('web.ajax');
varconcurrency=require('web.concurrency');
varcore=require('web.core');
varmixins=require('web.mixins');
varutils=require('web.utils');

var_t=core._t;
varqweb=core.qweb;

//Todo:refactorsession.Sessionaccomplishesseveralconcerns(rpc,
//configuration,currencies(wtf?),userpermissions...).Theyshouldbe
//clarifiedandseparated.

varSession=core.Class.extend(mixins.EventDispatcherMixin,{
    /**

    @paramparentTheparentofthenewlycreatedobject.
    or`null`iftheservertocontactistheoriginserver.
    @param{Dict}optionsAdictionarythatcancontainthefollowingoptions:

        *"modules"
        *"use_cors"
     */
    init:function(parent,origin,options){
        mixins.EventDispatcherMixin.init.call(this);
        this.setParent(parent);
        options=options||{};
        this.module_list=(options.modules&&options.modules.slice())||(window.flectra._modules&&window.flectra._modules.slice())||[];
        this.server=null;
        this.avoid_recursion=false;
        this.use_cors=options.use_cors||false;
        this.setup(origin);

        //forhistoricreasons,thesessionrequiresanametoproperlywork
        //(seethemethodsget_cookieandset_cookie). Weshouldperhaps
        //removeittotally(butneedtomakesurethecookiesareproperlyset)
        this.name="instance0";
        //TODO:sessionstoreincookieshouldbeoptional
        this.qweb_mutex=newconcurrency.Mutex();
        this.currencies={};
        this._groups_def={};
        core.bus.on('invalidate_session',this,this._onInvalidateSession);
    },
    setup:function(origin,options){
        //mustbeabletocustomizeserver
        varwindow_origin=location.protocol+"//"+location.host;
        origin=origin?origin.replace(/\/+$/,''):window_origin;
        if(!_.isUndefined(this.origin)&&this.origin!==origin)
            thrownewError('Sessionalreadyboundto'+this.origin);
        else
            this.origin=origin;
        this.prefix=this.origin;
        this.server=this.origin;//keepchshappy
        options=options||{};
        if('use_cors'inoptions){
            this.use_cors=options.use_cors;
        }
    },
    /**
     *Setupasession
     */
    session_bind:function(origin){
        this.setup(origin);
        qweb.default_dict._s=this.origin;
        this.uid=null;
        this.username=null;
        this.user_context={};
        this.db=null;
        this.active_id=null;
        returnthis.session_init();
    },
    /**
     *Initasession,reloadsfromcookie,ifitexists
     */
    session_init:function(){
        varself=this;
        varprom=this.session_reload();

        if(this.is_frontend){
            returnprom.then(function(){
                returnself.load_translations();
            });
        }

        returnprom.then(function(){
            varmodules=self.module_list.join(',');
            varpromise=self.load_qweb(modules);
            if(self.session_is_valid()){
                returnpromise.then(function(){returnself.load_modules();});
            }
            returnPromise.all([
                    promise,
                    self.rpc('/web/webclient/bootstrap_translations',{mods:self.module_list})
                        .then(function(trans){
                            _t.database.set_bundle(trans);
                        })
                    ]);
        });
    },
    session_is_valid:function(){
        vardb=$.deparam.querystring().db;
        if(db&&this.db!==db){
            returnfalse;
        }
        return!!this.uid;
    },
    /**
     *Thesessionisvalidatedbyrestorationofaprevioussession
     */
    session_authenticate:function(){
        varself=this;
        returnPromise.resolve(this._session_authenticate.apply(this,arguments)).then(function(){
            returnself.load_modules();
        });
    },
    /**
     *Thesessionisvalidatedeitherbyloginorbyrestorationofaprevioussession
     */
    _session_authenticate:function(db,login,password){
        varself=this;
        varparams={db:db,login:login,password:password};
        returnthis.rpc("/web/session/authenticate",params).then(function(result){
            if(!result.uid){
                returnPromise.reject();
            }
            _.extend(self,result);
        });
    },
    session_logout:function(){
        $.bbq.removeState();
        returnthis.rpc("/web/session/destroy",{});
    },
    user_has_group:function(group){
        if(!this.uid){
            returnPromise.resolve(false);
        }
        vardef=this._groups_def[group];
        if(!def){
            def=this._groups_def[group]=this.rpc('/web/dataset/call_kw/res.users/has_group',{
                "model":"res.users",
                "method":"has_group",
                "args":[group],
                "kwargs":{}
            });
        }
        returndef;
    },
    get_cookie:function(name){
        if(!this.name){returnnull;}
        varnameEQ=this.name+'|'+name+'=';
        varcookies=document.cookie.split(';');
        for(vari=0;i<cookies.length;++i){
            varcookie=cookies[i].replace(/^\s*/,'');
            if(cookie.indexOf(nameEQ)===0){
                try{
                    returnJSON.parse(decodeURIComponent(cookie.substring(nameEQ.length)));
                }catch(err){
                    //wrongcookie,deleteit
                    this.set_cookie(name,'',-1);
                }
            }
        }
        returnnull;
    },
    /**
     *Createanewcookiewiththeprovidednameandvalue
     *
     *@private
     *@paramnamethecookie'sname
     *@paramvaluethecookie'svalue
     *@paramttlthecookie'stimetolive,1yearbydefault,setto-1todelete
     */
    set_cookie:function(name,value,ttl){
        if(!this.name){return;}
        ttl=ttl||24*60*60*365;
        utils.set_cookie(this.name+'|'+name,value,ttl);
    },
    /**
     *Loadadditionalwebaddonsofthatinstanceandinitthem
     *
     */
    load_modules:function(){
        varself=this;
        varmodules=flectra._modules;
        varall_modules=_.uniq(self.module_list.concat(modules));
        varto_load=_.difference(modules,self.module_list).join(',');
        this.module_list=all_modules;

        varloaded=Promise.resolve(self.load_translations());
        varlocale="/web/webclient/locale/"+self.user_context.lang||'en_US';
        varfile_list=[locale];
        if(to_load.length){
            loaded=Promise.all([
                loaded,
                self.rpc('/web/webclient/csslist',{mods:to_load})
                    .then(self.load_css.bind(self)),
                self.load_qweb(to_load),
                self.rpc('/web/webclient/jslist',{mods:to_load})
                    .then(function(files){
                        file_list=file_list.concat(files);
                    })
            ]);
        }
        returnloaded.then(function(){
            returnself.load_js(file_list);
        }).then(function(){
            self._configureLocale();
        });
    },
    load_translations:function(){
        varlang=this.user_context.lang
        /*Weneedtogetthewebsitelangatthislevel.
           TheonlywayistogetitistotaketheHTMLtaglang
           Withoutit,wewillalwayssendundefinedifthereisnolang
           intheuser_context.*/
        varhtml=document.documentElement,
            htmlLang=html.getAttribute('lang');
        if(!this.user_context.lang&&htmlLang){
            lang=htmlLang.replace('-','_');
        }

        return_t.database.load_translations(this,this.module_list,lang,this.translationURL);
    },
    load_css:function(files){
        varself=this;
        _.each(files,function(file){
            ajax.loadCSS(self.url(file,null));
        });
    },
    load_js:function(files){
        varself=this;
        returnnewPromise(function(resolve,reject){
            if(files.length!==0){
                varfile=files.shift();
                varurl=self.url(file,null);
                ajax.loadJS(url).then(resolve);
            }else{
                resolve();
            }
        });
    },
    load_qweb:function(mods){
        varself=this;
        varlock=this.qweb_mutex.exec(function(){
            varcacheId=self.cache_hashes&&self.cache_hashes.qweb;
            varroute ='/web/webclient/qweb/'+(cacheId?cacheId:Date.now())+'?mods='+mods;
            return$.get(route).then(function(doc){
                if(!doc){return;}
                constowlTemplates=[];
                for(letchildofdoc.querySelectorAll("templates>[owl]")){
                    child.removeAttribute('owl');
                    owlTemplates.push(child.outerHTML);
                    child.remove();
                }
                qweb.add_template(doc);
                self.owlTemplates=`<templates>${owlTemplates.join('\n')}</templates>`;
            });
        });
        returnlock;
    },
    get_currency:function(currency_id){
        returnthis.currencies[currency_id];
    },
    get_file:function(options){
        options.session=this;
        returnajax.get_file(options);
    },
    /**
     *(re)loadsthecontentofasession:dbname,username,userid,session
     *contextandstatusofthesupportcontract
     *
     *@returns{Promise}promiseindicatingthesessionisdonereloading
     */
    session_reload:function(){
        varresult=_.extend({},window.flectra.session_info);
        _.extend(this,result);
        returnPromise.resolve();
    },
    /**
     *ExecutesanRPCcall,registeringtheprovidedcallbacks.
     *
     *Registersadefaulterrorcallbackifnoneisprovided,andhandles
     *settingthecorrectsessionidandsessioncontextintheparameter
     *objects
     *
     *@param{String}urlRPCendpoint
     *@param{Object}paramscallparameters
     *@param{Object}optionsadditionaloptionsforrpccall
     *@returns{Promise}
     */
    rpc:function(url,params,options){
        varself=this;
        options=_.clone(options||{});
        options.headers=_.extend({},options.headers);

        //weaddheretheusercontextforALLqueries,mainlytopass
        //theallowed_company_idskey
        if(params&&params.kwargs){
            params.kwargs.context=_.extend(params.kwargs.context||{},this.user_context);
        }

        //TODO:remove
        if(!_.isString(url)){
            _.extend(options,url);
            url=url.url;
        }
        if(self.use_cors){
            url=self.url(url,null);
        }

        returnajax.jsonRpc(url,"call",params,options);
    },
    url:function(path,params){
        params=_.extend(params||{});
        varqs=$.param(params);
        if(qs.length>0)
            qs="?"+qs;
        varprefix=_.any(['http://','https://','//'],function(el){
            returnpath.length>=el.length&&path.slice(0,el.length)===el;
        })?'':this.prefix;
        returnprefix+path+qs;
    },
    /**
     *Returnsthetimezonedifference(inminutes)fromthecurrentlocale
     *(hostsystemsettings)toUTC,foragivendate.Theoffsetispositive
     *ifthelocaltimezoneisbehindUTC,andnegativeifitisahead.
     *
     *@param{string|moment}dateavalidstringdateormomentinstance
     *@returns{integer}
     */
    getTZOffset:function(date){
        return-newDate(newDate(date).toISOString().replace('Z','')).getTimezoneOffset();
    },
    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------
    /**
     *Replacesthevalueofakeyincache_hashes(thehashofsomeresourcecomputedontheback-endbyauniquevalue
     *@param{string}keythekeyinthecache_hashestoinvalidate
     */
    invalidateCacheKey:function(key){
        if(this.cache_hashes&&this.cache_hashes[key]){
            this.cache_hashes[key]=Date.now();
        }
    },

    /**
     *Reloadthecurrencies(initiallygiveninsession_info).Thisismeantto
     *becalledwhenchangesaremadeon'res.currency'records(e.g.when
     *(de-)activatingacurrency).Forthesakeofsimplicity,wereloadall
     *session_info.
     *
     *FIXME:thiswholecurrencieshandlingshouldbemovedoutofsession.
     *
     *@returns{$.promise}
     */
    reloadCurrencies:function(){
        varself=this;
        returnthis.rpc('/web/session/get_session_info').then(function(result){
            self.currencies=result.currencies;
        });
    },

    setCompanies:function(main_company_id,company_ids){
        varhash=$.bbq.getState()
        hash.cids=company_ids.sort(function(a,b){
            if(a===main_company_id){
                return-1;
            }elseif(b===main_company_id){
                return1;
            }else{
                returna-b;
            }
        }).join(',');
        utils.set_cookie('cids',hash.cids||String(main_company_id));
        $.bbq.pushState({'cids':hash.cids},0);
        location.reload();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Setsfirstdayofweekincurrentlocaleaccordingtotheuserlanguage.
     *
     *@private
     */
    _configureLocale:function(){
        constdow=(_t.database.parameters.week_start||0)%7;
        moment.updateLocale(moment.locale(),{
            week:{
                dow:dow,
                doy:7+dow-4//Note:ISO8601weekdate:https://momentjscom.readthedocs.io/en/latest/moment/07-customization/16-dow-doy/
            },
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onInvalidateSession:function(){
        this.uid=false;
    },
});

returnSession;

});
