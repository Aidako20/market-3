flectra.define('mail/static/src/model/model_field_command.js',function(require){
'usestrict';

/**
 *Allowsfieldupdatetodetectifthevalueitreceivedisacommandto
 *execute(inwhichwasitwillbeaninstanceofthisclass)oranactual
 *valuetoset(inallothercases).
 */
classFieldCommand{
    /**
     *@constructor
     *@param{function}funcfunctiontocallwhenexecutingthiscommand.
     *ThefunctionshouldALWAYSreturnabooleanvalue
     *toindicatewhetherthevaluechanged.
     */
    constructor(func){
        this.func=func;
    }

    /**
     *@param{ModelField}field
     *@param{mail.model}record
     *@param{options}[options]
     *@returns{boolean}whetherthevaluechangedforthecurrentfield
     */
    execute(field,record,options){
        returnthis.func(field,record,options);
    }
}

/**
 *Returnsaclearcommandtogivetothemodelmanageratcreate/update.
 */
functionclear(){
    returnnewFieldCommand((field,record,options)=>
        field.clear(record,options)
    );
}

/**
 *Returnsadecrementcommandtogivetothemodelmanageratcreate/update.
 *
 *@param{number}[amount=1]
 */
functiondecrement(amount=1){
    returnnewFieldCommand((field,record,options)=>{
        constoldValue=field.get(record);
        returnfield.set(record,oldValue-amount,options);
    });
}

/**
 *Returnsaincrementcommandtogivetothemodelmanageratcreate/update.
 *
 *@param{number}[amount=1]
 */
functionincrement(amount=1){
    returnnewFieldCommand((field,record,options)=>{
        constoldValue=field.get(record);
        returnfield.set(record,oldValue+amount,options);
    });
}

return{
    //class
    FieldCommand,
    //shortcuts
    clear,
    decrement,
    increment,
};

});
