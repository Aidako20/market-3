flectra.define('mail/static/src/component_hooks/use_refs/use_refs.js',function(require){
'usestrict';

const{Component}=owl;

/**
 *Thishookprovidessupportfordynamic-refs.
 *
 *@returns{function}returnsobjectwhosekeysaret-refvaluesofactiverefs.
 *  andvaluesarerefs.
 */
functionuseRefs(){
    constcomponent=Component.current;
    returnfunction(){
        returncomponent.__owl__.refs||{};
    };
}

returnuseRefs;

});
