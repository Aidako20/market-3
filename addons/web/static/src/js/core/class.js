flectra.define('web.Class',function(){
"usestrict";
/**
 *ImprovedJohnResig'sinheritance,basedon:
 *
 *SimpleJavaScriptInheritance
 *ByJohnResighttp://ejohn.org/
 *MITLicensed.
 *
 *Adds"include()"
 *
 *DefinesTheClassobject.Thatobjectcanbeusedtodefineandinheritclassesusing
 *theextend()method.
 *
 *Example::
 *
 *    varPerson=Class.extend({
 *     init:function(isDancing){
 *        this.dancing=isDancing;
 *      },
 *      dance:function(){
 *        returnthis.dancing;
 *      }
 *    });
 *
 *Theinit()methodactasaconstructor.Thisclasscanbeinstancedthisway::
 *
 *    varperson=newPerson(true);
 *    person.dance();
 *
 *    ThePersonclasscanalsobeextendedagain:
 *
 *    varNinja=Person.extend({
 *      init:function(){
 *        this._super(false);
 *      },
 *      dance:function(){
 *        //Calltheinheritedversionofdance()
 *        returnthis._super();
 *      },
 *      swingSword:function(){
 *        returntrue;
 *      }
 *    });
 *
 *Whenextendingaclass,eachre-definedmethodcanusethis._super()tocalltheprevious
 *implementationofthatmethod.
 *
 *@classClass
 */
functionFlectraClass(){}

varinitializing=false;
varfnTest=/xyz/.test(function(){xyz();})?/\b_super\b/:/.*/;

/**
 *Subclassanexistingclass
 *
 *@param{Object}propclass-levelproperties(classattributesandinstancemethods)tosetonthenewclass
 */
FlectraClass.extend=function(){
    var_super=this.prototype;
    //Supportmixinsarguments
    varargs=_.toArray(arguments);
    args.unshift({});
    varprop=_.extend.apply(_,args);

    //Instantiateawebclass(butonlycreatetheinstance,
    //don'truntheinitconstructor)
    initializing=true;
    varThis=this;
    varprototype=newThis();
    initializing=false;

    //Copythepropertiesoverontothenewprototype
    _.each(prop,function(val,name){
        //Checkifwe'reoverwritinganexistingfunction
        prototype[name]=typeofprop[name]=="function"&&
                          fnTest.test(prop[name])?
                (function(name,fn){
                    returnfunction(){
                        vartmp=this._super;

                        //Addanew._super()methodthatisthesame
                        //methodbutonthesuper-class
                        this._super=_super[name];

                        //Themethodonlyneedtobeboundtemporarily,so
                        //weremoveitwhenwe'redoneexecuting
                        varret=fn.apply(this,arguments);
                        this._super=tmp;

                        returnret;
                    };
                })(name,prop[name]):
                prop[name];
    });

    //Thedummyclassconstructor
    functionClass(){
        if(this.constructor!==FlectraClass){
            thrownewError("Youcanonlyinstanciateobjectswiththe'new'operator");
        }
        //Allconstructionisactuallydoneintheinitmethod
        this._super=null;
        if(!initializing&&this.init){
            varret=this.init.apply(this,arguments);
            if(ret){returnret;}
        }
        returnthis;
    }
    Class.include=function(properties){
        _.each(properties,function(val,name){
            if(typeofproperties[name]!=='function'
                    ||!fnTest.test(properties[name])){
                prototype[name]=properties[name];
            }elseif(typeofprototype[name]==='function'
                       &&prototype.hasOwnProperty(name)){
                prototype[name]=(function(name,fn,previous){
                    returnfunction(){
                        vartmp=this._super;
                        this._super=previous;
                        varret=fn.apply(this,arguments);
                        this._super=tmp;
                        returnret;
                    };
                })(name,properties[name],prototype[name]);
            }elseif(typeof_super[name]==='function'){
                prototype[name]=(function(name,fn){
                    returnfunction(){
                        vartmp=this._super;
                        this._super=_super[name];
                        varret=fn.apply(this,arguments);
                        this._super=tmp;
                        returnret;
                    };
                })(name,properties[name]);
            }
        });
    };

    //Populateourconstructedprototypeobject
    Class.prototype=prototype;

    //Enforcetheconstructortobewhatweexpect
    Class.constructor=Class;

    //Andmakethisclassextendable
    Class.extend=this.extend;

    returnClass;
};

returnFlectraClass;
});
