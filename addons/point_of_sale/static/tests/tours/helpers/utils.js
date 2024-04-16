flectra.define('point_of_sale.tour.utils',function(require){
    'usestrict';

    constconfig=require('web.config');

    /**
     *USAGE
     *-----
     *
     *```
     *const{startSteps,getSteps,createTourMethods}=require('point_of_sale.utils');
     *const{Other}=require('point_of_sale.tour.OtherMethods');
     *
     *//1.DefineclassesDo,CheckandExecutehavingmethodsthat
     *//   eachreturnarrayoftoursteps.
     *classDo{
     *  click(){
     *     return[{content:'clickbutton',trigger:'.button'}];
     *  }
     *}
     *classCheck{
     *  isHighligted(){
     *     return[{content:'buttonishighlighted',trigger:'.button.highlight',run:()=>{}}];
     *  }
     *}
     *//NoticethatExecutehasaccesstomethodsdefinedinDoandCheckclasses
     *//Also,wecancomposestepsfromothermodule.
     *classExecute{
     *  complexSteps(){
     *     return[...this._do.click(),...this._check.isHighlighted(),...Other._exec.complicatedSteps()];
     *  }
     *}
     *
     *//2.Instantiatetheseclassdefinitionsusing`createTourMethods`.
     *//   Thereturnedobjectgivesaccesstothedefinedmethodsabove
     *//   thruthedo,checkandexecproperties.
     *//   -dogivesaccesstothemethodsdefinedinDoclass
     *//   -checkgivesaccesstothemethodsdefinedinCheckclass
     *//   -execgivesaccesstothemethodsdefinedinExecuteclass
     *constScreen=createTourMethods('Screen',Do,Check,Execute);
     *
     *//3.Call`startSteps`tostartemptysteps.
     *startSteps();
     *
     *//4.Callthetourmethodstopopulatethestepscreatedby`startSteps`.
     *Screen.do.click();              //returnofthismethodcallisaddedtostepscreatedbystartSteps
     *Screen.check.isHighlighted()    //sameasabove
     *Screen.exec.complexSteps()    //sameasabove
     *
     *//5.Call`getSteps`whichreturnsthegeneratedtoursteps.
     *conststeps=getSteps();
     *```
     */
    letsteps=[];

    functionstartSteps(){
        //alwaysstartbywaitingforloadingtofinish
        steps=[
            {
                content:'waitforloadingtofinish',
                trigger:'body:not(:has(.loader))',
                run:function(){},
            },
        ];
    }

    functiongetSteps(){
        returnsteps;
    }

    //thisisthemethoddecorator
    //whenthemethodiscalled,thegeneratedstepsareadded
    //tosteps
    constmethodProxyHandler={
        apply(target,thisArg,args){
            constres=target.call(thisArg,...args);
            if(config.isDebug()){
                //Thisstepisaddedbeforetherealsteps.
                //Veryusefulwhendebuggingbecauseweknowwhich
                //methodcallfailedandwhatweretheparameters.
                constconstructor=thisArg.constructor.name.split('')[1];
                constmethodName=target.name.split('')[1];
                constargList=args
                    .map((a)=>(typeofa==='string'?`'${a}'`:`${a}`))
                    .join(',');
                steps.push({
                    content:`DOING"${constructor}.${methodName}(${argList})"`,
                    trigger:'.pos',
                    run:()=>{},
                });
            }
            steps.push(...res);
            returnres;
        },
    };

    //weproxygetofthemethodtodecoratethemethodcall
    constproxyHandler={
        get(target,key){
            constmethod=target[key];
            if(!method){
                thrownewError(`Tourmethod'${key}'isnotavailable.`);
            }
            returnnewProxy(method.bind(target),methodProxyHandler);
        },
    };

    /**
     *Createsanobjectwith`do`,`check`and`exec`propertieswhichareinstancesof
     *thegiven`Do`,`Check`and`Execute`classes,respectively.Callingmethods
     *automaticallyaddsthereturnedstepstothestepscreatedby`startSteps`.
     *
     *Therearehoweverunderscoredversion(_do,_check,_exec).
     *Callingmethodsthrutheunderscoredversiondoesnotautomatically
     *addthereturnedstepstothecurrentstepsarray.Usefulwhencomposing
     *stepsfromothermethods.
     *
     *@param{String}name
     *@param{Function}Doclasscontainingmethodswhichreturnarrayoftoursteps
     *@param{Function}ChecksimilartoDoclassbutthestepsaremainlyforchecking
     *@param{Function}Executeclasscontainingmethodswhichreturnarrayoftoursteps
     *                  buthasaccesstomethodsofDoandCheckclassesvia.doand.check,
     *                  respectively.Here,wedefinemethodsthatreturntourstepsbased
     *                  onthecombinationofstepsfromDoandCheck.
     */
    functioncreateTourMethods(name,Do,Check=class{},Execute=class{}){
        Object.defineProperty(Do,'name',{value:`${name}.do`});
        Object.defineProperty(Check,'name',{value:`${name}.check`});
        Object.defineProperty(Execute,'name',{
            value:`${name}.exec`,
        });
        constmethods={do:newDo(),check:newCheck(),exec:newExecute()};
        //AllowExecutetohaveaccesstomethodsdefinedinDoandCheck
        //viadoandexec,respectively.
        methods.exec._do=methods.do;
        methods.exec._check=methods.check;
        return{
            Do,
            Check,
            Execute,
            [name]:{
                do:newProxy(methods.do,proxyHandler),
                check:newProxy(methods.check,proxyHandler),
                exec:newProxy(methods.exec,proxyHandler),
                _do:methods.do,
                _check:methods.check,
                _exec:methods.exec,
            },
        };
    }

    return{startSteps,getSteps,createTourMethods};
});
