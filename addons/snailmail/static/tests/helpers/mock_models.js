flectra.define('snailmail/static/tests/helpers/mock_models.js',function(require){
'usestrict';

constMockModels=require('mail/static/tests/helpers/mock_models.js');

MockModels.patch('snailmail/static/tests/helpers/mock_models.js',T=>
    classextendsT{

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *@override
         */
        staticgenerateData(){
            constdata=super.generateData(...arguments);
            Object.assign(data,{
                'snailmail.letter':{
                    fields:{
                        message_id:{string:'SnailmailStatusMessage',type:'many2one',relation:'mail.message'},
                    },
                    records:[],
                },
            });
            returndata;
        }

    }
);

});
