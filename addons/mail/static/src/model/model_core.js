flectra.define('mail/static/src/model/model_core.js',function(require){
'usestrict';

/**
 *Modulethatcontainsregistryforaddingnewmodelsorpatchingmodels.
 *Usefulformodelmanagerinordertogeneratemodelclasses.
 *
 *ThiscodeisnotinmodelmanagerbecauseotherJSmodulesshouldpopulate
 *aregistry,andit'sdifficulttoensureavailabilityofthemodelmanager
 *whentheseJSmodulesaredeployed.
 */

constregistry={};

//------------------------------------------------------------------------------
//Private
//------------------------------------------------------------------------------

/**
 *@private
 *@param{string}modelName
 *@returns{Object}
 */
function_getEntryFromModelName(modelName){
    if(!registry[modelName]){
        registry[modelName]={
            dependencies:[],
            factory:undefined,
            name:modelName,
            patches:[],
        };
    }
    returnregistry[modelName];
}

/**
 *@private
 *@param{string}modelName
 *@param{string}patchName
 *@param{Object}patch
 *@param{Object}[param3={}]
 *@param{string}[param3.type='instance']'instance','class'or'field'
 */
function_registerPatchModel(modelName,patchName,patch,{type='instance'}={}){
    constentry=_getEntryFromModelName(modelName);
    Object.assign(entry,{
        patches:(entry.patches||[]).concat([{
            name:patchName,
            patch,
            type,
        }]),
    });
}

//------------------------------------------------------------------------------
//Public
//------------------------------------------------------------------------------

/**
 *Registerapatchforstaticmethodsinmodel.
 *
 *@param{string}modelName
 *@param{string}patchName
 *@param{Object}patch
 */
functionregisterClassPatchModel(modelName,patchName,patch){
    _registerPatchModel(modelName,patchName,patch,{type:'class'});
}

/**
 *Registerapatchforfieldsinmodel.
 *
 *@param{string}modelName
 *@param{string}patchName
 *@param{Object}patch
 */
functionregisterFieldPatchModel(modelName,patchName,patch){
    _registerPatchModel(modelName,patchName,patch,{type:'field'});
}

/**
 *Registerapatchforinstancemethodsinmodel.
 *
 *@param{string}modelName
 *@param{string}patchName
 *@param{Object}patch
 */
functionregisterInstancePatchModel(modelName,patchName,patch){
    _registerPatchModel(modelName,patchName,patch,{type:'instance'});
}

/**
 *@param{string}name
 *@param{function}factory
 *@param{string[]}[dependencies=[]]
 */
functionregisterNewModel(name,factory,dependencies=[]){
    constentry=_getEntryFromModelName(name);
    letentryDependencies=[...dependencies];
    if(name!=='mail.model'){
        entryDependencies=[...newSet(entryDependencies.concat(['mail.model']))];
    }
    if(entry.factory){
        thrownewError(`Model"${name}"hasalreadybeenregistered!`);
    }
    Object.assign(entry,{
        dependencies:entryDependencies,
        factory,
        name,
    });
}

//------------------------------------------------------------------------------
//Export
//------------------------------------------------------------------------------

return{
    registerClassPatchModel,
    registerFieldPatchModel,
    registerInstancePatchModel,
    registerNewModel,
    registry,
};

});
