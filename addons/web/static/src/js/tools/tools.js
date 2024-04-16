flectra.define('web.tools',function(require){
"usestrict";

/**
 *Wrapperfordeprecatedfunctionsthatdisplayawarningmessage.
 *
 *@param{Function}fnthedeprecatedfunction
 *@param{string}[message='']optionalmessagetodisplay
 *@returns{Function}
 */
functiondeprecated(fn,message){
    returnfunction(){
        console.warn(message||(fn.name+'isdeprecated.'));
        returnfn.apply(this,arguments);
    };
}

return{
    deprecated:deprecated,
};

});
