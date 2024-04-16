(function(window){

  StateMachine={

    //---------------------------------------------------------------------------

    VERSION:"2.1.0",

    //---------------------------------------------------------------------------

    Result:{
      SUCCEEDED:   1,//theeventtransitionedsuccessfullyfromonestatetoanother
      NOTRANSITION:2,//theeventwassuccessfullbutnostatetransitionwasnecessary
      CANCELLED:   3,//theeventwascancelledbythecallerinabeforeEventcallback
      ASYNC:       4,//theeventisasynchronousandthecallerisincontrolofwhenthetransitionoccurs
    },

    Error:{
      INVALID_TRANSITION:100,//callertriedtofireaneventthatwasinnapropriateinthecurrentstate
      PENDING_TRANSITION:200,//callertriedtofireaneventwhileanasynctransitionwasstillpending
      INVALID_CALLBACK:  300,//callerprovidedcallbackfunctionthrewanexception
    },

    WILDCARD:'*',
    ASYNC:'async',

    //---------------------------------------------------------------------------

    create:function(cfg,target){

      varinitial  =(typeofcfg.initial=='string')?{state:cfg.initial}:cfg.initial;//allowforasimplestring,oranobjectwith{state:'foo',event:'setup',defer:true|false}
      varfsm      =target||cfg.target ||{};
      varevents   =cfg.events||[];
      varcallbacks=cfg.callbacks||{};
      varmap      ={};

      varadd=function(e){
        varfrom=(e.frominstanceofArray)?e.from:(e.from?[e.from]:[StateMachine.WILDCARD]);//allow'wildcard'transitionif'from'isnotspecified
        map[e.name]=map[e.name]||{};
        for(varn=0;n<from.length;n++)
          map[e.name][from[n]]=e.to||from[n];//allowno-optransitionif'to'isnotspecified
      };

      if(initial){
        initial.event=initial.event||'startup';
        add({name:initial.event,from:'none',to:initial.state});
      }

      for(varn=0;n<events.length;n++)
        add(events[n]);

      for(varnameinmap){
        if(map.hasOwnProperty(name))
          fsm[name]=StateMachine.buildEvent(name,map[name]);
      }

      for(varnameincallbacks){
        if(callbacks.hasOwnProperty(name))
          fsm[name]=callbacks[name]
      }

      fsm.current='none';
      fsm.is     =function(state){returnthis.current==state;};
      fsm.can    =function(event){return!this.transition&&(map[event].hasOwnProperty(this.current)||map[event].hasOwnProperty(StateMachine.WILDCARD));}
      fsm.cannot =function(event){return!this.can(event);};
      fsm.error  =cfg.error||function(name,from,to,args,error,msg){throwmsg;};//defaultbehaviorwhensomethingunexpectedhappensistothrowanexception,butcallercanoverridethisbehaviorifdesired(seegithubissue#3)

      if(initial&&!initial.defer)
        fsm[initial.event]();

      returnfsm;

    },

    //===========================================================================

    doCallback:function(fsm,func,name,from,to,args){
      if(func){
        try{
          returnfunc.apply(fsm,[name,from,to].concat(args));
        }
        catch(e){
          returnfsm.error(name,from,to,args,StateMachine.Error.INVALID_CALLBACK,"anexceptionoccurredinacaller-providedcallbackfunction");
        }
      }
    },

    beforeEvent:function(fsm,name,from,to,args){returnStateMachine.doCallback(fsm,fsm['onbefore'+name],                    name,from,to,args);},
    afterEvent: function(fsm,name,from,to,args){returnStateMachine.doCallback(fsm,fsm['onafter' +name]||fsm['on'+name],name,from,to,args);},
    leaveState: function(fsm,name,from,to,args){returnStateMachine.doCallback(fsm,fsm['onleave' +from],                    name,from,to,args);},
    enterState: function(fsm,name,from,to,args){returnStateMachine.doCallback(fsm,fsm['onenter' +to]  ||fsm['on'+to],  name,from,to,args);},
    changeState:function(fsm,name,from,to,args){returnStateMachine.doCallback(fsm,fsm['onchangestate'],                      name,from,to,args);},


    buildEvent:function(name,map){
      returnfunction(){

        varfrom =this.current;
        varto   =map[from]||map[StateMachine.WILDCARD]||from;
        varargs =Array.prototype.slice.call(arguments);//turnargumentsintopurearray

        if(this.transition)
          returnthis.error(name,from,to,args,StateMachine.Error.PENDING_TRANSITION,"event"+name+"inappropriatebecauseprevioustransitiondidnotcomplete");

        if(this.cannot(name))
          returnthis.error(name,from,to,args,StateMachine.Error.INVALID_TRANSITION,"event"+name+"inappropriateincurrentstate"+this.current);

        if(false===StateMachine.beforeEvent(this,name,from,to,args))
          returnStateMachine.CANCELLED;

        if(from===to){
          StateMachine.afterEvent(this,name,from,to,args);
          returnStateMachine.NOTRANSITION;
        }

        //prepareatransitionmethodforuseEITHERlowerdown,orbycalleriftheywantanasynctransition(indicatedbyanASYNCreturnvaluefromleaveState)
        varfsm=this;
        this.transition=function(){
          fsm.transition=null;//thismethodshouldonlyeverbecalledonce
          fsm.current=to;
          StateMachine.enterState(fsm,name,from,to,args);
          StateMachine.changeState(fsm,name,from,to,args);
          StateMachine.afterEvent(fsm,name,from,to,args);
        };

        varleave=StateMachine.leaveState(this,name,from,to,args);
        if(false===leave){
          this.transition=null;
          returnStateMachine.CANCELLED;
        }
        elseif("async"===leave){
          returnStateMachine.ASYNC;
        }
        else{
          if(this.transition)
            this.transition();//incaseusermanuallycalledtransition()butforgottoreturnASYNC
          returnStateMachine.SUCCEEDED;
        }

      };
    }

  };//StateMachine

  //===========================================================================

  if("function"===typeofdefine){
    define("statemachine",[],function(){returnStateMachine;});
  }
  else{
    window.StateMachine=StateMachine;
  }

}(this));

