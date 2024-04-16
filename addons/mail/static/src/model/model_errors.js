flectra.define('mail/static/src/model/model_errors.js',function(require){
'usestrict';

classRecordDeletedErrorextendsError{

    /**
     *@override
     *@param{string}recordLocalIdlocalidofrecordthathasbeendeleted
     *@param {...any}args
     */
    constructor(recordLocalId,...args){
        super(...args);
        this.recordLocalId=recordLocalId;
        this.name='RecordDeletedError';
    }
}

return{
    RecordDeletedError,
};

});
