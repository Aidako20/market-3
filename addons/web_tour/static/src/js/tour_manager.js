flectra.define('web_tour.TourManager',function(require){
"usestrict";

varcore=require('web.core');
varconfig=require('web.config');
varlocal_storage=require('web.local_storage');
varmixins=require('web.mixins');
varutils=require('web_tour.utils');
varTourStepUtils=require('web_tour.TourStepUtils');
varRainbowMan=require('web.RainbowMan');
varRunningTourActionHelper=require('web_tour.RunningTourActionHelper');
varServicesMixin=require('web.ServicesMixin');
varsession=require('web.session');
varTip=require('web_tour.Tip');

var_t=core._t;

varRUNNING_TOUR_TIMEOUT=10000;

varget_step_key=utils.get_step_key;
varget_debugging_key=utils.get_debugging_key;
varget_running_key=utils.get_running_key;
varget_running_delay_key=utils.get_running_delay_key;
varget_first_visible_element=utils.get_first_visible_element;
vardo_before_unload=utils.do_before_unload;
varget_jquery_element_from_selector=utils.get_jquery_element_from_selector;

returncore.Class.extend(mixins.EventDispatcherMixin,ServicesMixin,{
    init:function(parent,consumed_tours){
        mixins.EventDispatcherMixin.init.call(this);
        this.setParent(parent);

        this.$body=$('body');
        this.active_tooltips={};
        this.tours={};
        //removethetoursbeingdebugfromthelistofconsumedtours
        this.consumed_tours=(consumed_tours||[]).filter(tourName=>{
            return!local_storage.getItem(get_debugging_key(tourName));
        });
        this.running_tour=local_storage.getItem(get_running_key());
        this.running_step_delay=parseInt(local_storage.getItem(get_running_delay_key()),10)||0;
        this.edition=(_.last(session.server_version_info)==='e')?'enterprise':'community';
        this._log=[];
        console.log('TourManagerisready. running_tour='+this.running_tour);
    },
    /**
     *Registersatourdescribedbythefollowingarguments*inorder*
     *
     *@param{string}name-tour'sname
     *@param{Object}[options]-options(optional),availableoptionsare:
     *@param{boolean}[options.test=false]-trueifthisisonlyfortests
     *@param{boolean}[options.skip_enabled=false]
     *       truetoaddalinkinitstipstoconsumethewholetour
     *@param{string}[options.url]
     *       theurltoloadwhenmanuallyrunningthetour
     *@param{boolean}[options.rainbowMan=true]
     *       whetherornottherainbowmanmustbeshownattheendofthetour
     *@param{boolean}[options.sequence=1000]
     *       prioritysequenceofthetour(lowestisfirst,tourswiththesame
     *       sequencewillbeexecutedinanondeterministicorder).
     *@param{Promise}[options.wait_for]
     *       indicateswhenthetourcanbestarted
     *@param{string|function}[options.rainbowManMessage]
              textorfunctionreturningthetextdisplayedundertherainbowman
              attheendofthetour.
     *@param{string}[options.rainbowManFadeout]
     *@param{Object[]}steps-steps'descriptions,eachstepbeinganobject
     *                    containingatipdescription
     */
    register(){
        varargs=Array.prototype.slice.call(arguments);
        varlast_arg=args[args.length-1];
        varname=args[0];
        if(this.tours[name]){
            console.warn(_.str.sprintf("Tour%sisalreadydefined",name));
            return;
        }
        varoptions=args.length===2?{}:args[1];
        varsteps=last_arginstanceofArray?last_arg:[last_arg];
        vartour={
            name:options.saveAs||name,
            steps:steps,
            url:options.url,
            rainbowMan:options.rainbowMan===undefined?true:!!options.rainbowMan,
            rainbowManMessage:options.rainbowManMessage,
            rainbowManFadeout:options.rainbowManFadeout,
            sequence:options.sequence||1000,
            test:options.test,
            wait_for:options.wait_for||Promise.resolve(),
        };
        if(options.skip_enabled){
            tour.skip_link='<p><spanclass="o_skip_tour">'+_t('Skiptour')+'</span></p>';
            tour.skip_handler=function(tip){
                this._deactivate_tip(tip);
                this._consume_tour(name);
            };
        }
        this.tours[tour.name]=tour;
    },
    /**
     *Returnsapromisewhichisresolvedoncethetourcanbestarted.This
     *iswhentheDOMisreadyandattheendoftheexecutionstacksothat
     *alltourshavepotentiallybeenextendedbyallapps.
     *
     *@private
     *@returns{Promise}
     */
    _waitBeforeTourStart:function(){
        returnnewPromise(function(resolve){
            $(function(){
                setTimeout(resolve);
            });
        });
    },
    _register_all:function(do_update){
        varself=this;
        if(this._allRegistered){
            returnPromise.resolve();
        }
        this._allRegistered=true;
        returnself._waitBeforeTourStart().then(function(){
            returnPromise.all(_.map(self.tours,function(tour,name){
                returnself._register(do_update,tour,name);
            })).then(()=>self.update());
        });
    },
    _register:function(do_update,tour,name){
        if(tour.ready)returnPromise.resolve();

        consttour_is_consumed=this._isTourConsumed(name);

        returntour.wait_for.then((function(){
            tour.current_step=parseInt(local_storage.getItem(get_step_key(name)))||0;
            tour.steps=_.filter(tour.steps,(function(step){
                return(!step.edition||step.edition===this.edition)&&
                    (step.mobile===undefined||step.mobile===config.device.isMobile);
            }).bind(this));

            if(tour_is_consumed||tour.current_step>=tour.steps.length){
                local_storage.removeItem(get_step_key(name));
                tour.current_step=0;
            }

            tour.ready=true;

            constdebuggingTour=local_storage.getItem(get_debugging_key(name));
            if(debuggingTour||
                (do_update&&(this.running_tour===name||
                              (!this.running_tour&&!tour.test&&!tour_is_consumed)))){
                this._to_next_step(name,0);
            }
        }).bind(this));
    },
    /**
     *Resetsthegiventourtoitsinitialstep,andpreventitfrombeing
     *markedasconsumedatreload,bytheincludeintour_disable.js
     *
     *@param{string}tourName
     */
    reset:function(tourName){
        //removeitfromthelistofconsumedtours
        constindex=this.consumed_tours.indexOf(tourName);
        if(index>=0){
            this.consumed_tours.splice(index,1);
        }
        //markitasbeingdebugged
        local_storage.setItem(get_debugging_key(tourName),true);
        //resetittothefirststep
        consttour=this.tours[tourName];
        tour.current_step=0;
        local_storage.removeItem(get_step_key(tourName));
        this._to_next_step(tourName,0);
        //redirecttoitsstartingpoint(or/webbydefault)
        window.location.href=window.location.origin+(tour.url||'/web');
    },
    run:function(tour_name,step_delay){
        console.log(_.str.sprintf("Preparingtour%s",tour_name));
        if(this.running_tour){
            this._deactivate_tip(this.active_tooltips[this.running_tour]);
            this._consume_tour(this.running_tour,_.str.sprintf("Killingtour%s",this.running_tour));
            return;
        }
        vartour=this.tours[tour_name];
        if(!tour){
            console.warn(_.str.sprintf("UnknownTour%s",name));
            return;
        }
        console.log(_.str.sprintf("Runningtour%s",tour_name));
        this.running_tour=tour_name;
        this.running_step_delay=step_delay||this.running_step_delay;
        local_storage.setItem(get_running_key(),this.running_tour);
        local_storage.setItem(get_running_delay_key(),this.running_step_delay);

        this._deactivate_tip(this.active_tooltips[tour_name]);

        tour.current_step=0;
        this._to_next_step(tour_name,0);
        local_storage.setItem(get_step_key(tour_name),tour.current_step);

        if(tour.url){
            this.pause();
            do_before_unload(null,(function(){
                this.play();
                this.update();
            }).bind(this));

            window.location.href=window.location.origin+tour.url;
        }else{
            this.update();
        }
    },
    pause:function(){
        this.paused=true;
    },
    play:function(){
        this.paused=false;
    },
    /**
     *Checksfortooltipstoactivate(onlyfromtherunningtourorspecifiedtourifthere
     *isone,fromallactivetoursotherwise).ShouldbecalledeachtimetheDOMchanges.
     */
    update:function(tour_name){
        if(this.paused)return;

        this.$modal_displayed=$('.modal:visible').last();

        tour_name=this.running_tour||tour_name;
        if(tour_name){
            vartour=this.tours[tour_name];
            if(!tour||!tour.ready)return;

            if(this.running_tour&&this.running_tour_timeout===undefined){
                this._set_running_tour_timeout(this.running_tour,this.active_tooltips[this.running_tour]);
            }
            varself=this;
            setTimeout(function(){
                self._check_for_tooltip(self.active_tooltips[tour_name],tour_name);
            });
        }else{
            constsortedTooltips=Object.keys(this.active_tooltips).sort(
                (a,b)=>this.tours[a].sequence-this.tours[b].sequence
            );
            letvisibleTip=false;
            for(consttourNameofsortedTooltips){
                vartip=this.active_tooltips[tourName];
                tip.hidden=visibleTip;
                visibleTip=this._check_for_tooltip(tip,tourName)||visibleTip;
            }
        }
    },
    /**
     * Check(andactivateorupdate)ahelptooltipforatour.
     *
     *@param{Object}tip
     *@param{string}tour_name
     *@returns{boolean}trueifatipwasfoundandactivated/updated
     */
    _check_for_tooltip:function(tip,tour_name){
        if(tip===undefined){
            returntrue;
        }
        if($('body').hasClass('o_ui_blocked')){
            this._deactivate_tip(tip);
            this._log.push("blockUIispreventingthetiptobeconsumed");
            returnfalse;
        }

        var$trigger;
        if(tip.in_modal!==false&&this.$modal_displayed.length){
            $trigger=this.$modal_displayed.find(tip.trigger);
        }else{
            $trigger=get_jquery_element_from_selector(tip.trigger);
        }
        var$visible_trigger=get_first_visible_element($trigger);

        varextra_trigger=true;
        var$extra_trigger;
        if(tip.extra_trigger){
            $extra_trigger=get_jquery_element_from_selector(tip.extra_trigger);
            extra_trigger=get_first_visible_element($extra_trigger).length;
        }

        var$visible_alt_trigger=$();
        if(tip.alt_trigger){
            var$alt_trigger;
            if(tip.in_modal!==false&&this.$modal_displayed.length){
                $alt_trigger=this.$modal_displayed.find(tip.alt_trigger);
            }else{
                $alt_trigger=get_jquery_element_from_selector(tip.alt_trigger);
            }
            $visible_alt_trigger=get_first_visible_element($alt_trigger);
        }

        vartriggered=$visible_trigger.length&&extra_trigger;
        if(triggered){
            if(!tip.widget){
                this._activate_tip(tip,tour_name,$visible_trigger,$visible_alt_trigger);
            }else{
                tip.widget.update($visible_trigger,$visible_alt_trigger);
            }
        }else{
            if($trigger.iframeContainer||($extra_trigger&&$extra_trigger.iframeContainer)){
                var$el=$();
                if($trigger.iframeContainer){
                    $el=$el.add($trigger.iframeContainer);
                }
                if(($extra_trigger&&$extra_trigger.iframeContainer)&&$trigger.iframeContainer!==$extra_trigger.iframeContainer){
                    $el=$el.add($extra_trigger.iframeContainer);
                }
                varself=this;
                $el.off('load').one('load',function(){
                    $el.off('load');
                    if(self.active_tooltips[tour_name]===tip){
                        self.update(tour_name);
                    }
                });
            }
            this._deactivate_tip(tip);

            if(this.running_tour===tour_name){
                this._log.push("_check_for_tooltip");
                this._log.push("-modal_displayed:"+this.$modal_displayed.length);
                this._log.push("-trigger'"+tip.trigger+"':"+$trigger.length);
                this._log.push("-visibletrigger'"+tip.trigger+"':"+$visible_trigger.length);
                if($extra_trigger!==undefined){
                    this._log.push("-extra_trigger'"+tip.extra_trigger+"':"+$extra_trigger.length);
                    this._log.push("-visibleextra_trigger'"+tip.extra_trigger+"':"+extra_trigger);
                }
            }
        }
        return!!triggered;
    },
    /**
     *Activatestheprovidedtipfortheprovidedtour,$anchorand$alt_trigger.
     *$alt_triggerisanalternativetriggerthatcanconsumethestep.Thetipis
     *howeveronlydisplayedonthe$anchor.
     *
     *@param{Object}tip
     *@param{String}tour_name
     *@param{jQuery}$anchor
     *@param{jQuery}$alt_trigger
     *@private
     */
    _activate_tip:function(tip,tour_name,$anchor,$alt_trigger){
        vartour=this.tours[tour_name];
        vartip_info=tip;
        if(tour.skip_link){
            tip_info=_.extend(_.omit(tip_info,'content'),{
                content:tip.content+tour.skip_link,
                event_handlers:[{
                    event:'click',
                    selector:'.o_skip_tour',
                    handler:tour.skip_handler.bind(this,tip),
                }],
            });
        }
        tip.widget=newTip(this,tip_info);
        if(this.running_tour!==tour_name){
            tip.widget.on('tip_consumed',this,this._consume_tip.bind(this,tip,tour_name));
        }
        tip.widget.attach_to($anchor,$alt_trigger).then(this._to_next_running_step.bind(this,tip,tour_name));
    },
    _deactivate_tip:function(tip){
        if(tip&&tip.widget){
            tip.widget.destroy();
            deletetip.widget;
        }
    },
    _describeTip:function(tip){
        returntip.content?tip.content+'(trigger:'+tip.trigger+')':tip.trigger;
    },
    _consume_tip:function(tip,tour_name){
        this._deactivate_tip(tip);
        this._to_next_step(tour_name);

        varis_running=(this.running_tour===tour_name);
        if(is_running){
            varstepDescription=this._describeTip(tip);
            console.log(_.str.sprintf("Tour%s:step'%s'succeeded",tour_name,stepDescription));
        }

        if(this.active_tooltips[tour_name]){
            local_storage.setItem(get_step_key(tour_name),this.tours[tour_name].current_step);
            if(is_running){
                this._log=[];
                this._set_running_tour_timeout(tour_name,this.active_tooltips[tour_name]);
            }
            this.update(tour_name);
        }else{
            this._consume_tour(tour_name);
        }
    },
    _to_next_step:function(tour_name,inc){
        vartour=this.tours[tour_name];
        tour.current_step+=(inc!==undefined?inc:1);
        if(this.running_tour!==tour_name){
            varindex=_.findIndex(tour.steps.slice(tour.current_step),function(tip){
                return!tip.auto;
            });
            if(index>=0){
                tour.current_step+=index;
            }else{
                tour.current_step=tour.steps.length;
            }
        }
        this.active_tooltips[tour_name]=tour.steps[tour.current_step];
    },
    /**
     *@private
     *@param{string}tourName
     *@returns{boolean}
     */
    _isTourConsumed(tourName){
        returnthis.consumed_tours.includes(tourName);
    },
    _consume_tour:function(tour_name,error){
        deletethis.active_tooltips[tour_name];
        //displayrainbowattheendofanytour
        if(this.tours[tour_name].rainbowMan&&this.running_tour!==tour_name&&
            this.tours[tour_name].current_step===this.tours[tour_name].steps.length){
            letmessage=this.tours[tour_name].rainbowManMessage;
            if(message){
                message=typeofmessage==='function'?message():message;
            }else{
                message=_t('<strong><b>Goodjob!</b>Youwentthroughallstepsofthistour.</strong>');
            }
            newRainbowMan({
                message:message,
                fadeout:this.tours[tour_name].rainbowManFadeout||'medium',
            }).appendTo(this.$body);
        }
        this.tours[tour_name].current_step=0;
        local_storage.removeItem(get_step_key(tour_name));
        local_storage.removeItem(get_debugging_key(tour_name));
        if(this.running_tour===tour_name){
            this._stop_running_tour_timeout();
            local_storage.removeItem(get_running_key());
            local_storage.removeItem(get_running_delay_key());
            this.running_tour=undefined;
            this.running_step_delay=undefined;
            if(error){
                _.each(this._log,function(log){
                    console.log(log);
                });
                console.log(document.body.parentElement.outerHTML);
                console.error(error);//willbedisplayedaserrorinfo
            }else{
                console.log(_.str.sprintf("Tour%ssucceeded",tour_name));
                console.log("testsuccessful");//browser_jswaitformessage"testsuccessful"
            }
            this._log=[];
        }else{
            varself=this;
            this._rpc({
                    model:'web_tour.tour',
                    method:'consume',
                    args:[[tour_name]],
                })
                .then(function(){
                    self.consumed_tours.push(tour_name);
                });
        }
    },
    _set_running_tour_timeout:function(tour_name,step){
        this._stop_running_tour_timeout();
        this.running_tour_timeout=setTimeout((function(){
            vardescr=this._describeTip(step);
            this._consume_tour(tour_name,_.str.sprintf("Tour%sfailedatstep%s",tour_name,descr));
        }).bind(this),(step.timeout||RUNNING_TOUR_TIMEOUT)+this.running_step_delay);
    },
    _stop_running_tour_timeout:function(){
        clearTimeout(this.running_tour_timeout);
        this.running_tour_timeout=undefined;
    },
    _to_next_running_step:function(tip,tour_name){
        if(this.running_tour!==tour_name)return;
        varself=this;
        this._stop_running_tour_timeout();
        if(this.running_step_delay){
            //warning:duetothedelay,itmayhappenthatthe$anchorisn't
            //intheDOManymorewhenexeciscalled,eitherbecause:
            //-ithasbeenremovedfromtheDOMmeanwhileandthetip's
            //  selectordoesn'tmatchanythinganymore
            //-ithasbeenre-renderedandthustheselectorstillhasamatch
            //  intheDOM,butexecutingthestepwiththat$anchorwon'twork
            _.delay(exec,this.running_step_delay);
        }else{
            exec();
        }

        functionexec(){
            varaction_helper=newRunningTourActionHelper(tip.widget);
            do_before_unload(self._consume_tip.bind(self,tip,tour_name));

            vartour=self.tours[tour_name];
            if(typeoftip.run==="function"){
                tip.run.call(tip.widget,action_helper);
            }elseif(tip.run!==undefined){
                varm=tip.run.match(/^([a-zA-Z0-9_]+)*(?:\(?*(.+?)*\)?)?$/);
                action_helper[m[1]](m[2]);
            }elseif(tour.current_step===tour.steps.length-1){
                console.log('Tour%s:ignoringaction(auto)oflaststep',tour_name);
            }else{
                action_helper.auto();
            }
        }
    },
    stepUtils:newTourStepUtils(this)
});
});
