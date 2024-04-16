flectra.define('im_livechat/static/tests/helpers/mock_models.js',function(require){
'usestrict';

constMockModels=require('mail/static/tests/helpers/mock_models.js');

MockModels.patch('im_livechat/static/tests/helpers/mock_models.js',T=>
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
                'im_livechat.channel':{
                    fields:{
                        user_ids:{string:"Operators",type:'many2many',relation:'res.users'}
                    },
                    records:[],
                }
            });
            Object.assign(data['mail.channel'].fields,{
                anonymous_name:{string:"AnonymousName",type:'char'},
                country_id:{string:"Country",type:'many2one',relation:'res.country'},
                livechat_active:{string:"Islivechatongoing?",type:'boolean',default:false},
                livechat_channel_id:{string:"Channel",type:'many2one',relation:'im_livechat.channel'},
                livechat_operator_id:{string:"Operator",type:'many2one',relation:'res.partner'},
            });
            Object.assign(data['res.users'].fields,{
                livechat_username:{string:'LivechatUsername',type:'string'},
            });
            returndata;
        }

    }
);

});
