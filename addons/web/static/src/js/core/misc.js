flectra.define('web.framework',function(require){
"usestrict";

varcore=require('web.core');
constconfig=require("web.config");
varajax=require('web.ajax');
varWidget=require('web.Widget');
vardisableCrashManager=require('web.CrashManager').disable;
const{sprintf}=require('web.utils')

var_t=core._t;

varmessages_by_seconds=function(){
    return[
        [0,_t("Loading...")],
        [20,_t("Stillloading...")],
        [60,_t("Stillloading...<br/>Pleasebepatient.")],
        [120,_t("Don'tleaveyet,<br/>it'sstillloading...")],
        [300,_t("Youmaynotbelieveit,<br/>buttheapplicationisactuallyloading...")],
        [420,_t("Takeaminutetogetacoffee,<br/>becauseit'sloading...")],
        [3600,_t("MaybeyoushouldconsiderreloadingtheapplicationbypressingF5...")]
    ];
};

varThrobber=Widget.extend({
    template:"Throbber",
    start:function(){
        this.start_time=newDate().getTime();
        this.act_message();
    },
    act_message:function(){
        varself=this;
        setTimeout(function(){
            if(self.isDestroyed())
                return;
            varseconds=(newDate().getTime()-self.start_time)/1000;
            varmes;
            _.each(messages_by_seconds(),function(el){
                if(seconds>=el[0])
                    mes=el[1];
            });
            self.$(".oe_throbber_message").html(mes);
            self.act_message();
        },1000);
    },
});

/**Setupblockui*/
if($.blockUI){
    $.blockUI.defaults.baseZ=1100;
    $.blockUI.defaults.message='<divclass="openerpoe_blockui_spin_container"style="background-color:transparent;">';
    $.blockUI.defaults.css.border='0';
    $.blockUI.defaults.css["background-color"]='';
}


/**
 *Removethe"accesskey"attributestoavoidtheuseoftheaccesskeys
 *whiletheblockUIisenable.
 */

functionblockAccessKeys(){
    varelementWithAccessKey=[];
    elementWithAccessKey=document.querySelectorAll('[accesskey]');
    _.each(elementWithAccessKey,function(elem){
        elem.setAttribute("data-accesskey",elem.getAttribute('accesskey'));
        elem.removeAttribute('accesskey');
    });
}

functionunblockAccessKeys(){
    varelementWithDataAccessKey=[];
    elementWithDataAccessKey=document.querySelectorAll('[data-accesskey]');
    _.each(elementWithDataAccessKey,function(elem){
        elem.setAttribute('accesskey',elem.getAttribute('data-accesskey'));
        elem.removeAttribute('data-accesskey');
    });
}

varthrobbers=[];

functionblockUI(){
    vartmp=$.blockUI.apply($,arguments);
    varthrobber=newThrobber();
    throbbers.push(throbber);
    throbber.appendTo($(".oe_blockui_spin_container"));
    $(document.body).addClass('o_ui_blocked');
    blockAccessKeys();
    returntmp;
}

functionunblockUI(){
    _.invoke(throbbers,'destroy');
    throbbers=[];
    $(document.body).removeClass('o_ui_blocked');
    unblockAccessKeys();
    return$.unblockUI.apply($,arguments);
}

/**
 *Redirecttourlbyreplacingwindow.location
 *Ifwaitistrue,sleep1sandwaitfortheserveri.e.afterarestart.
 */
functionredirect(url,wait){
    //Dontdisplayadialogifsomexmlhttprequestareinprogress
    //wedon'tdisablethecrashmanageronmobilephones,becausewhengoingbacktoflectra,
    //thepageisnotreloaded,andthecrashManagerstaysdisabled.
    if(!config.device.isIOS&&!config.device.isAndroid){
        disableCrashManager();
    }

    varload=function(){
        varold=""+window.location;
        varold_no_hash=old.split("#")[0];
        varurl_no_hash=url.split("#")[0];
        location.assign(url);
        if(old_no_hash===url_no_hash){
            location.reload(true);
        }
    };

    varwait_server=function(){
        ajax.rpc("/web/webclient/version_info",{}).then(load).guardedCatch(function(){
            setTimeout(wait_server,250);
        });
    };

    if(wait){
        setTimeout(wait_server,1000);
    }else{
        load();
    }
}

// *Clientactiontoreloadthewholeinterface.
// *Ifparams.menu_id,itopensthegivenmenuentry.
// *Ifparams.wait,reloadwillwaittheopenerpservertobereachablebeforereloading

functionReload(parent,action){
    varparams=action.params||{};
    varmenu_id=params.menu_id||false;
    varl=window.location;

    varsobj=$.deparam(l.search.substr(1));
    if(params.url_search){
        sobj=_.extend(sobj,params.url_search);
    }
    varsearch='?'+$.param(sobj);

    varhash=l.hash;
    if(menu_id){
        hash="#menu_id="+menu_id;
    }
    varurl=l.protocol+"//"+l.host+l.pathname+search+hash;

    //Clearcache
    core.bus.trigger('clear_cache');

    redirect(url,params.wait);
}

core.action_registry.add("reload",Reload);


/**
 *Clientactiontogobackhome.
 */
functionHome(parent,action){
    varurl='/'+(window.location.search||'');
    redirect(url,action&&action.params&&action.params.wait);
}
core.action_registry.add("home",Home);

functionlogin(){
    redirect('/web/login');
}
core.action_registry.add("login",login);

functionlogout(){
    redirect('/web/session/logout');
}
core.action_registry.add("logout",logout);

/**
 *@param{ActionManager}parent
 *@param{Object}action
 *@param{Object}action.paramsnotificationparams
 *@seeServiceMixin.displayNotification
 */
functiondisplayNotification(parent,action){
    let{title='',message='',links=[],type='info',sticky=false,next}=action.params||{};
    links=links.map(({url,label})=>`<ahref="${_.escape(url)}"target="_blank">${_.escape(label)}</a>`)
    parent.displayNotification({
        title:_.escape(title),
        message:sprintf(_.escape(message),...links),
        type,
        sticky
    });
    returnnext;
}
core.action_registry.add("display_notification",displayNotification);

/**
 *Clientactiontorefreshthesessioncontext(makingsure
 *HTTPrequestswillhavetherightone)thenreloadthe
 *wholeinterface.
 */
functionReloadContext(parent,action){
    //side-effectofget_session_infoistorefreshthesessioncontext
    ajax.rpc("/web/session/get_session_info",{}).then(function(){
        Reload(parent,action);
    });
}
core.action_registry.add("reload_context",ReloadContext);

//InInternetExplorer,documentdoesn'thavethecontainsmethod,sowemakea
//polyfillforthemethodinordertobecompatible.
if(!document.contains){
    document.contains=functioncontains(node){
        if(!(0inarguments)){
            thrownewTypeError('1argumentisrequired');
        }

        do{
            if(this===node){
                returntrue;
            }
        }while(node=node&&node.parentNode);

        returnfalse;
    };
}

return{
    blockUI:blockUI,
    unblockUI:unblockUI,
    redirect:redirect,
};

});
