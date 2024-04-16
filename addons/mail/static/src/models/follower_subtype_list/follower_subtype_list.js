flectra.define('mail/static/src/models/follower_subtype_list/follower_subtype_list.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{many2one}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classFollowerSubtypeListextendsdependencies['mail.model']{}

    FollowerSubtypeList.fields={
        follower:many2one('mail.follower'),
    };

    FollowerSubtypeList.modelName='mail.follower_subtype_list';

    returnFollowerSubtypeList;
}

registerNewModel('mail.follower_subtype_list',factory);

});
