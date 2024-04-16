flectra.define('web.Apps',function(require){
"usestrict";

varAbstractAction=require('web.AbstractAction');
varconfig=require('web.config');
varcore=require('web.core');
varframework=require('web.framework');
varsession=require('web.session');

var_t=core._t;

varapps_client=null;

varApps=AbstractAction.extend({
    contentTemplate:'EmptyComponent',
    remote_action_tag:'loempia.embed',
    failback_action_id:'base.open_module_tree',

    init:function(parent,action){
        this._super(parent,action);
        varoptions=action.params||{};
        this.params=options; //NOTEforwardedtoembeddedclientaction
    },

    get_client:function(){
        //returntheclientviaapromise,resolvedorrejecteddependingif
        //theremotehostisavailableornot.
        varcheck_client_available=function(client){
            vari=newImage();
            vardef=newPromise(function(resolve,reject){
                i.onerror=function(){
                    reject(client);
                };
                i.onload=function(){
                    resolve(client);
                };
            });
            varts=newDate().getTime();
            i.src=_.str.sprintf('%s/web/static/src/img/sep-a.gif?%s',client.origin,ts);
            returndef;
        };
        if(apps_client){
            returncheck_client_available(apps_client);
        }else{
            returnthis._rpc({model:'ir.module.module',method:'get_apps_server'})
                .then(function(u){
                    varlink=$(_.str.sprintf('<ahref="%s"></a>',u))[0];
                    varhost=_.str.sprintf('%s//%s',link.protocol,link.host);
                    vardbname=link.pathname;
                    if(dbname[0]==='/'){
                        dbname=dbname.substr(1);
                    }
                    varclient={
                        origin:host,
                        dbname:dbname
                    };
                    apps_client=client;
                    returncheck_client_available(client);
                });
        }
    },

    destroy:function(){
        $(window).off("message."+this.uniq);
        if(this.$ifr){
            this.$ifr.remove();
            this.$ifr=null;
        }
        returnthis._super();
    },

    _on_message:function($e){
        varself=this,client=this.client,e=$e.originalEvent;

        if(e.origin!==client.origin){
            return;
        }

        vardispatcher={
            'event':function(m){self.trigger('message:'+m.event,m);},
            'action':function(m){
                self.do_action(m.action).then(function(r){
                    varw=self.$ifr[0].contentWindow;
                    w.postMessage({id:m.id,result:r},client.origin);
                });
            },
            'rpc':function(m){
                returnself._rpc({route:m.args[0],params:m.args[1]}).then(function(r){
                    varw=self.$ifr[0].contentWindow;
                    w.postMessage({id:m.id,result:r},client.origin);
                });
            },
            'Model':function(m){
                returnself._rpc({model:m.model,method:m.args[0],args:m.args[1]})
                    .then(function(r){
                        varw=self.$ifr[0].contentWindow;
                        w.postMessage({id:m.id,result:r},client.origin);
                    });
            },
        };
        //console.log(e.data);
        if(!_.isObject(e.data)){return;}
        if(dispatcher[e.data.type]){
            dispatcher[e.data.type](e.data);
        }
    },

    start:function(){
        varself=this;
        returnnewPromise(function(resolve,reject){
            self.get_client().then(function(client){
                self.client=client;

                varqs={db:client.dbname};
                if(config.isDebug()){
                    qs.debug=flectra.debug;
                }
                varu=$.param.querystring(client.origin+"/apps/embed/client",qs);
                varcss={width:'100%',height:'750px'};
                self.$ifr=$('<iframe>').attr('src',u);

                self.uniq=_.uniqueId('apps');
                $(window).on("message."+self.uniq,self.proxy('_on_message'));

                self.on('message:ready',self,function(m){
                    varw=this.$ifr[0].contentWindow;
                    varact={
                        type:'ir.actions.client',
                        tag:this.remote_action_tag,
                        params:_.extend({},this.params,{
                            db:session.db,
                            origin:session.origin,
                        })
                    };
                    w.postMessage({type:'action',action:act},client.origin);
                });

                self.on('message:set_height',self,function(m){
                    this.$ifr.height(m.height);
                });

                self.on('message:blockUI',self,function(){framework.blockUI();});
                self.on('message:unblockUI',self,function(){framework.unblockUI();});
                self.on('message:warn',self,function(m){self.do_warn(m.title,m.message,m.sticky);});

                self.$ifr.appendTo(self.$('.o_content')).css(css).addClass('apps-client');

                resolve();
            },function(){
                self.do_warn(_t('FlectraAppswillbeavailablesoon'),_t('Showinglocallyavailablemodules'),true);
                returnself._rpc({
                    route:'/web/action/load',
                    params:{action_id:self.failback_action_id},
                }).then(function(action){
                    returnself.do_action(action,{clear_breadcrumbs:true});
                }).then(reject,reject);
            });
        });
    }
});

varAppsUpdates=Apps.extend({
    remote_action_tag:'loempia.embed.updates',
});

core.action_registry.add("apps",Apps);
core.action_registry.add("apps.updates",AppsUpdates);

returnApps;

});
