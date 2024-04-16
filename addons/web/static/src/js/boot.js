/**
 *------------------------------------------------------------------------------
 *FlectraWebBoostrapCode
 *------------------------------------------------------------------------------
 *
 *Eachmodulecanreturnapromise.Inthatcase,themoduleismarkedasloaded
 *onlywhenthepromiseisresolved,anditsvalueisequaltotheresolvedvalue.
 *Themodulecanberejected(unloaded).Thiswillbeloggedintheconsoleasinfo.
 *
 *logs:
 *     Missingdependencies:
 *         Thesemodulesdonotappearinthepage.Itispossiblethatthe
 *         JavaScriptfileisnotinthepageorthatthemodulenameiswrong
 *     Failedmodules:
 *         Ajavascripterrorisdetected
 *     Rejectedmodules:
 *         Themodulereturnsarejectedpromise.It(anditsdependentmodules)
 *         isnotloaded.
 *     Rejectedlinkedmodules:
 *         Moduleswhodependonarejectedmodule
 *     Nonloadedmodules:
 *         Moduleswhodependonamissingorafailedmodule
 *     Debug:
 *         Nonloadedorfailedmoduleinformationsfordebugging
 */
(function(){
    "usestrict";

    varjobUID=Date.now();

    varjobs=[];
    varfactories=Object.create(null);
    varjobDeps=[];
    varjobPromises=[];

    varservices=Object.create({});

    varcommentRegExp=/(\/\*([\s\S]*?)\*\/|([^:]|^)\/\/(.*)$)/mg;
    varcjsRequireRegExp=/[^.]\s*require\s*\(\s*["']([^'"\s]+)["']\s*\)/g;

    if(!window.flectra){
        window.flectra={};
    }
    varflectra=window.flectra;

    vardidLogInfoResolve;
    vardidLogInfoPromise=newPromise(function(resolve){
        didLogInfoResolve=resolve;
    });

    flectra.testing=typeofQUnit==='object';
    flectra.remainingJobs=jobs;
    flectra.__DEBUG__={
        didLogInfo:didLogInfoPromise,
        getDependencies:function(name,transitive){
            vardeps=nameinstanceofArray?name:[name];
            varchanged;
            do{
                changed=false;
                jobDeps.forEach(function(dep){
                    if(deps.indexOf(dep.to)>=0&&deps.indexOf(dep.from)<0){
                        deps.push(dep.from);
                        changed=true;
                    }
                });
            }while(changed&&transitive);
            returndeps;
        },
        getDependents:function(name){
            returnjobDeps.filter(function(dep){
                returndep.from===name;
            }).map(function(dep){
                returndep.to;
            });
        },
        getWaitedJobs:function(){
            returnjobs.map(function(job){
                returnjob.name;
            }).filter(function(item,index,self){//uniq
                returnself.indexOf(item)===index;
            });
        },
        getMissingJobs:function(){
            varself=this;
            varwaited=this.getWaitedJobs();
            varmissing=[];
            waited.forEach(function(job){
                self.getDependencies(job).forEach(function(job){
                    if(!(jobinself.services)){
                        missing.push(job);
                    }
                });
            });
            returnmissing.filter(function(item,index,self){
                returnself.indexOf(item)===index;
            }).filter(function(item){
                returnwaited.indexOf(item)<0;
            }).filter(function(job){
                return!job.error;
            });
        },
        getFailedJobs:function(){
            returnjobs.filter(function(job){
                return!!job.error;
            });
        },
        factories:factories,
        services:services,
    };
    flectra.define=function(){
        varargs=Array.prototype.slice.call(arguments);
        varname=typeofargs[0]==='string'?args.shift():('__flectra_job'+(jobUID++));
        varfactory=args[args.length-1];
        vardeps;
        if(args[0]instanceofArray){
            deps=args[0];
        }else{
            deps=[];
            factory.toString()
                .replace(commentRegExp,'')
                .replace(cjsRequireRegExp,function(match,dep){
                    deps.push(dep);
                });
        }

        if(flectra.debug){
            if(!(depsinstanceofArray)){
                thrownewError('Dependenciesshouldbedefinedbyanarray',deps);
            }
            if(typeoffactory!=='function'){
                thrownewError('Factoryshouldbedefinedbyafunction',factory);
            }
            if(typeofname!=='string'){
                thrownewError("Invalidnamedefinition(shouldbeastring",name);
            }
            if(nameinfactories){
                thrownewError("Service"+name+"alreadydefined");
            }
        }

        factory.deps=deps;
        factories[name]=factory;

        jobs.push({
            name:name,
            factory:factory,
            deps:deps,
        });

        deps.forEach(function(dep){
            jobDeps.push({from:dep,to:name});
        });

        this.processJobs(jobs,services);
    };
    flectra.log=function(){
        varmissing=[];
        varfailed=[];

        if(jobs.length){
            vardebugJobs={};
            varrejected=[];
            varrejectedLinked=[];
            varjob;
            varjobdep;

            for(vark=0;k<jobs.length;k++){
                debugJobs[jobs[k].name]=job={
                    dependencies:jobs[k].deps,
                    dependents:flectra.__DEBUG__.getDependents(jobs[k].name),
                    name:jobs[k].name
                };
                if(jobs[k].error){
                    job.error=jobs[k].error;
                }
                if(jobs[k].rejected){
                    job.rejected=jobs[k].rejected;
                    rejected.push(job.name);
                }
                vardeps=flectra.__DEBUG__.getDependencies(job.name);
                for(vari=0;i<deps.length;i++){
                    if(job.name!==deps[i]&&!(deps[i]inservices)){
                        jobdep=debugJobs[deps[i]];
                        if(!jobdep&&deps[i]infactories){
                            for(varj=0;j<jobs.length;j++){
                                if(jobs[j].name===deps[i]){
                                    jobdep=jobs[j];
                                    break;
                                }
                            }
                        }
                        if(jobdep&&jobdep.rejected){
                            if(!job.rejected){
                                job.rejected=[];
                                rejectedLinked.push(job.name);
                            }
                            job.rejected.push(deps[i]);
                        }else{
                            if(!job.missing){
                                job.missing=[];
                            }
                            job.missing.push(deps[i]);
                        }
                    }
                }
            }
            missing=flectra.__DEBUG__.getMissingJobs();
            failed=flectra.__DEBUG__.getFailedJobs();
            varunloaded=Object.keys(debugJobs)//Object.valuesisnotsupported
                .map(function(key){
                    returndebugJobs[key];
                }).filter(function(job){
                    returnjob.missing;
                });

            if(flectra.debug||failed.length||unloaded.length){
                varlog=window.console[!failed.length||!unloaded.length?'info':'error'].bind(window.console);
                log((failed.length?'error':(unloaded.length?'warning':'info'))+':Somemodulescouldnotbestarted');
                if(missing.length){
                    log('Missingdependencies:   ',missing);
                }
                if(failed.length){
                    log('Failedmodules:         ',failed.map(function(fail){
                        returnfail.name;
                    }));
                }
                if(rejected.length){
                    log('Rejectedmodules:       ',rejected);
                }
                if(rejectedLinked.length){
                    log('Rejectedlinkedmodules:',rejectedLinked);
                }
                if(unloaded.length){
                    log('Nonloadedmodules:     ',unloaded.map(function(unload){
                        returnunload.name;
                    }));
                }
                if(flectra.debug&&Object.keys(debugJobs).length){
                    log('Debug:                  ',debugJobs);
                }
            }
        }
        flectra.__DEBUG__.jsModules={
            missing:missing,
            failed:failed.map(function(fail){
                returnfail.name;
            }),
        };
        didLogInfoResolve();
    };
    flectra.processJobs=function(jobs,services){
        varjob;

        functionprocessJob(job){
            varrequire=makeRequire(job);

            varjobExec;
            vardef=newPromise(function(resolve){
                try{
                    jobExec=job.factory.call(null,require);
                    jobs.splice(jobs.indexOf(job),1);
                }catch(e){
                    job.error=e;
                    console.error('Errorwhileloading'+job.name+':'+e.stack);
                }
                if(!job.error){
                    Promise.resolve(jobExec).then(
                        function(data){
                            services[job.name]=data;
                            resolve();
                            flectra.processJobs(jobs,services);
                        }).guardedCatch(function(e){
                            job.rejected=e||true;
                            jobs.push(job);
                            resolve();
                        }
                    );
                }
            });
            jobPromises.push(def);
        }

        functionisReady(job){
            return!job.error&&!job.rejected&&job.factory.deps.every(function(name){
                returnnameinservices;
            });
        }

        functionmakeRequire(job){
            vardeps={};
            Object.keys(services).filter(function(item){
                returnjob.deps.indexOf(item)>=0;
            }).forEach(function(key){
                deps[key]=services[key];
            });

            returnfunctionrequire(name){
                if(!(nameindeps)){
                    console.error('Undefineddependency:',name);
                }
                returndeps[name];
            };
        }

        while(jobs.length){
            job=undefined;
            for(vari=0;i<jobs.length;i++){
                if(isReady(jobs[i])){
                    job=jobs[i];
                    break;
                }
            }
            if(!job){
                break;
            }
            processJob(job);
        }

        returnservices;
    };

    //Automaticallylogerrorsdetectedwhenloadingmodules
    window.addEventListener('load',functionlogWhenLoaded(){
        setTimeout(function(){
            varlen=jobPromises.length;
            Promise.all(jobPromises).then(function(){
                if(len===jobPromises.length){
                    flectra.log();
                }else{
                    logWhenLoaded();
                }
            });
        },9999);
    });
})();
