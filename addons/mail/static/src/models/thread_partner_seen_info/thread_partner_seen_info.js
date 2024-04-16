flectra.define('mail/static/src/models/thread_partner_seen_info/thread_partner_seen_info.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr,many2one}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classThreadPartnerSeenInfoextendsdependencies['mail.model']{

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *@override
         */
        static_createRecordLocalId(data){
            const{channelId,partnerId}=data;
            return`${this.modelName}_${channelId}_${partnerId}`;
        }

        /**
         *@private
         *@returns{mail.partner|undefined}
         */
        _computePartner(){
            return[['insert',{id:this.partnerId}]];
        }

        /**
         *@private
         *@returns{mail.thread|undefined}
         */
        _computeThread(){
            return[['insert',{
                id:this.channelId,
                model:'mail.channel',
            }]];
        }

    }

    ThreadPartnerSeenInfo.modelName='mail.thread_partner_seen_info';

    ThreadPartnerSeenInfo.fields={
        /**
         *Theidofchannelthisseeninfoisrelatedto.
         *
         *Shouldwriteonthisfieldtosetrelationbetweenthechanneland
         *thisseeninfo,noton`thread`.
         *
         *Reasonfornotsettingtherelationdirectlyisthenecessityto
         *uniquelyidentifyaseeninfobasedonchannelandpartnerfromdata.
         *Relationaldataarelistofcommands,whichisproblematictodeduce
         *identifyingrecords.
         *
         *TODO:task-2322536(normalizerelationaldata)&task-2323665
         *(requiredfields)shouldimproveandletusjustusetherelational
         *fields.
         */
        channelId:attr(),
        lastFetchedMessage:many2one('mail.message'),
        lastSeenMessage:many2one('mail.message'),
        /**
         *Partnerthatthisseeninfoisrelatedto.
         *
         *Shouldnotwriteonthisfieldtoupdaterelation,andinstead
         *shouldwriteon@seepartnerIdfield.
         */
        partner:many2one('mail.partner',{
            compute:'_computePartner',
            dependencies:['partnerId'],
        }),
        /**
         *Theidofpartnerthisseeninfoisrelatedto.
         *
         *Shouldwriteonthisfieldtosetrelationbetweenthepartnerand
         *thisseeninfo,noton`partner`.
         *
         *Reasonfornotsettingtherelationdirectlyisthenecessityto
         *uniquelyidentifyaseeninfobasedonchannelandpartnerfromdata.
         *Relationaldataarelistofcommands,whichisproblematictodeduce
         *identifyingrecords.
         *
         *TODO:task-2322536(normalizerelationaldata)&task-2323665
         *(requiredfields)shouldimproveandletusjustusetherelational
         *fields.
         */
        partnerId:attr(),
        /**
         *Thread(channel)thatthisseeninfoisrelatedto.
         *
         *Shouldnotwriteonthisfieldtoupdaterelation,andinstead
         *shouldwriteon@seechannelIdfield.
         */
        thread:many2one('mail.thread',{
            compute:'_computeThread',
            dependencies:['channelId'],
            inverse:'partnerSeenInfos',
        }),
    };

    returnThreadPartnerSeenInfo;
}

registerNewModel('mail.thread_partner_seen_info',factory);

});
