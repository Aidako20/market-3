flectra.define('utm.campaing_kanban_examples',function(require){
'usestrict';

varcore=require('web.core');
varkanbanExamplesRegistry=require('web.kanban_examples_registry');

var_lt=core._lt;

kanbanExamplesRegistry.add('utm_campaign',{
    ghostColumns:[_lt('Ideas'),_lt('Design'),_lt('Review'),_lt('Send'),_lt('Done')],
    applyExamplesText:_lt("UseThisForMyCampaigns"),
    examples:[{
        name:_lt('CreativeFlow'),
        columns:[_lt('Ideas'),_lt('Design'),_lt('Review'),_lt('Send'),_lt('Done')],
        description:_lt("Collectideas,designcreativecontentandpublishitoncereviewed."),
    },{
        name:_lt('Event-drivenFlow'),
        columns:[_lt('Later'),_lt('ThisMonth'),_lt('ThisWeek'),_lt('Running'),_lt('Sent')],
        description:_lt("Trackincomingevents(e.g.:Christmas,BlackFriday,...)andpublishtimelycontent."),
    },{
        name:_lt('Soft-LaunchFlow'),
        columns:[_lt('Pre-Launch'),_lt('Soft-Launch'),_lt('Deploy'),_lt('Report'),_lt('Done')],
        description:_lt("PrepareyourCampaign,testitwithpartofyouraudienceanddeployitfullyafterwards."),
    },{
        name:_lt('Audience-drivenFlow'),
        columns:[_lt('GatherData'),_lt('List-Building'),_lt('Copywriting'),_lt('Sent')],
        description:_lt("Gatherdata,buildarecipientlistandwritecontentbasedonyourMarketingtarget."),
    },{
        name:_lt('Approval-basedFlow'),
        columns:[_lt('TobeApproved'),_lt('Approved'),_lt('Deployed')],
        description:_lt("PrepareCampaignsandgetthemapprovedbeforemakingthemgolive."),
    }],
});
});
